"""
FastAPI main application for The Number budgeting app.

This API provides REST endpoints for the Vue.js frontend,
wrapping the existing Python backend (database.py, calculator.py).
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
from dotenv import load_dotenv

# Add parent directory to path to import existing backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import EncryptedDatabase
from src.calculator import BudgetCalculator
from src.import_expenses import import_expenses_from_file
from src.export_expenses import export_to_csv, export_to_excel
from api.models import (
    ExpenseCreate, ExpenseResponse, TransactionCreate, TransactionResponse,
    BudgetModeConfig, BudgetNumberResponse, ImportExpensesResponse, ErrorResponse
)

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Create FastAPI app
app = FastAPI(
    title="The Number API",
    description="REST API for The Number budgeting app",
    version="0.9.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS - Allow all localhost ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency: Get database instance
def get_db() -> EncryptedDatabase:
    """
    Dependency that provides a database instance.

    Uses the encryption key from environment variables.
    """
    encryption_key = os.getenv("DB_ENCRYPTION_KEY")
    if not encryption_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database encryption key not configured"
        )
    return EncryptedDatabase(encryption_key=encryption_key)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "app": "The Number API",
        "version": "0.9.0",
        "docs": "/api/docs",
        "status": "running"
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# ============================================================================
# BUDGET & "THE NUMBER" ENDPOINTS
# ============================================================================

@app.get("/api/number", response_model=BudgetNumberResponse)
async def get_the_number(db: EncryptedDatabase = Depends(get_db)):
    """
    Get "The Number" - your daily spending limit.

    This is the main feature of the app!
    """
    try:
        # Get budget mode configuration
        budget_mode = db.get_setting("budget_mode")

        if not budget_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget mode not configured. Please configure your budget first."
            )

        # Load expenses into calculator
        calc = BudgetCalculator()
        expenses = db.get_expenses()
        for exp in expenses:
            calc.add_expense(exp["name"], exp["amount"], exp["is_fixed"])

        # Calculate "The Number" based on mode
        if budget_mode == "paycheck":
            monthly_income = db.get_setting("monthly_income")
            days_until_paycheck = db.get_setting("days_until_paycheck")
            result = calc.calculate_paycheck_mode(
                monthly_income=monthly_income,
                days_until_paycheck=days_until_paycheck
            )
        else:  # fixed_pool
            total_money = db.get_setting("total_money")
            result = calc.calculate_fixed_pool_mode(total_money=total_money)

        # Get today's spending
        today_spending = db.get_total_spending_today()
        remaining_today = result["daily_limit"] - today_spending

        return BudgetNumberResponse(
            the_number=result["daily_limit"],
            mode=budget_mode,
            total_income=result.get("total_income"),
            total_expenses=result.get("total_expenses", result.get("monthly_expenses", 0)),
            remaining_money=result.get("remaining_money"),
            days_remaining=result.get("days_remaining"),
            today_spending=today_spending,
            remaining_today=remaining_today,
            is_over_budget=(remaining_today < 0)
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating budget: {str(e)}"
        )


@app.post("/api/budget/configure", status_code=status.HTTP_200_OK)
async def configure_budget(
    config: BudgetModeConfig,
    db: EncryptedDatabase = Depends(get_db)
):
    """Configure budget mode and settings."""
    try:
        # Validate configuration based on mode
        if config.mode == "paycheck":
            if not config.monthly_income or not config.days_until_paycheck:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Paycheck mode requires monthly_income and days_until_paycheck"
                )
            db.set_setting("monthly_income", config.monthly_income)
            db.set_setting("days_until_paycheck", config.days_until_paycheck)

        elif config.mode == "fixed_pool":
            if config.total_money is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Fixed pool mode requires total_money"
                )
            db.set_setting("total_money", config.total_money)

        # Save budget mode
        db.set_setting("budget_mode", config.mode)

        return {"message": f"Budget configured successfully in {config.mode} mode"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring budget: {str(e)}"
        )


@app.get("/api/budget/config")
async def get_budget_config(db: EncryptedDatabase = Depends(get_db)):
    """Get current budget configuration."""
    mode = db.get_setting("budget_mode")
    if not mode:
        return {"configured": False}

    config = {"configured": True, "mode": mode}

    if mode == "paycheck":
        config["monthly_income"] = db.get_setting("monthly_income")
        config["days_until_paycheck"] = db.get_setting("days_until_paycheck")
    else:
        config["total_money"] = db.get_setting("total_money")

    return config


# ============================================================================
# EXPENSE ENDPOINTS
# ============================================================================

@app.get("/api/expenses", response_model=List[ExpenseResponse])
async def get_expenses(db: EncryptedDatabase = Depends(get_db)):
    """Get all expenses."""
    return db.get_expenses()


@app.post("/api/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    db: EncryptedDatabase = Depends(get_db)
):
    """Create a new expense."""
    try:
        expense_id = db.add_expense(
            name=expense.name,
            amount=expense.amount,
            is_fixed=expense.is_fixed
        )

        # Retrieve the created expense
        created_expense = db.get_expense_by_id(expense_id)
        return created_expense

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating expense: {str(e)}"
        )


@app.delete("/api/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: EncryptedDatabase = Depends(get_db)
):
    """Delete an expense."""
    try:
        db.delete_expense(expense_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting expense: {str(e)}"
        )


# SECURITY: File upload validation constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
ALLOWED_CONTENT_TYPES = {
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/csv',
    'text/plain',  # Some systems send CSV as text/plain
}


@app.post("/api/expenses/import", response_model=ImportExpensesResponse)
async def import_expenses(
    file: UploadFile = File(...),
    replace: bool = False,
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Import expenses from CSV or Excel file.

    - **file**: CSV or Excel file containing expenses (max 10MB, .csv or .xlsx only)
    - **replace**: If True, replaces all existing expenses. If False, adds to existing.
    """
    try:
        # SECURITY FIX: Validate file before processing
        # 1. Validate file extension
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )

        # 2. Validate content type
        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {file.content_type}. Expected CSV or Excel file."
            )

        # 3. Validate file size by reading content
        # Read file content to check size (also needed for processing)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB"
            )

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        # Reset file position for processing (create a BytesIO object)
        from io import BytesIO
        file_obj = BytesIO(content)

        # Import expenses using existing backend
        expenses, errors = import_expenses_from_file(file_obj)

        # Replace existing expenses if requested
        if replace:
            existing = db.get_expenses()
            for exp in existing:
                db.delete_expense(exp["id"])

        # Add imported expenses
        imported_count = 0
        for exp in expenses:
            try:
                db.add_expense(exp["name"], exp["amount"], exp["is_fixed"])
                imported_count += 1
            except Exception as e:
                errors.append(f"Failed to import {exp['name']}: {str(e)}")

        return ImportExpensesResponse(
            imported_count=imported_count,
            errors=errors
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing expenses: {str(e)}"
        )


@app.get("/api/expenses/export/{format}")
async def export_expenses(
    format: str,
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Export expenses to CSV or Excel.

    - **format**: Either 'csv' or 'excel'
    """
    try:
        expenses = db.get_expenses()

        if format.lower() == "csv":
            file_path = export_to_csv(expenses)
        elif format.lower() in ["excel", "xlsx"]:
            file_path = export_to_excel(expenses)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format must be 'csv' or 'excel'"
            )

        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=Path(file_path).name
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting expenses: {str(e)}"
        )


# ============================================================================
# TRANSACTION ENDPOINTS
# ============================================================================

@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: Optional[int] = 20,
    db: EncryptedDatabase = Depends(get_db)
):
    """Get recent transactions."""
    return db.get_transactions(limit=limit)


@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    db: EncryptedDatabase = Depends(get_db)
):
    """Record a spending transaction."""
    try:
        txn_id = db.add_transaction(
            amount=transaction.amount,
            description=transaction.description,
            date=transaction.date,
            category=transaction.category
        )

        # Retrieve all transactions and find the one we just created
        transactions = db.get_transactions(limit=1)
        return transactions[0] if transactions else None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating transaction: {str(e)}"
        )


@app.delete("/api/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: EncryptedDatabase = Depends(get_db)
):
    """Delete a transaction."""
    try:
        db.delete_transaction(transaction_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting transaction: {str(e)}"
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
