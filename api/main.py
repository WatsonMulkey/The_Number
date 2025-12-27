"""
FastAPI main application for The Number budgeting app.

This API provides REST endpoints for the Vue.js frontend,
wrapping the existing Python backend (database.py, calculator.py).
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables FIRST - before any imports that depend on them
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add parent directory to path to import existing backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import EncryptedDatabase
from src.calculator import BudgetCalculator
from src.import_expenses import import_expenses_from_file
from src.export_expenses import export_to_csv, export_to_excel
from api.models import (
    ExpenseCreate, ExpenseResponse, TransactionCreate, TransactionResponse,
    BudgetModeConfig, BudgetNumberResponse, ImportExpensesResponse, ErrorResponse,
    UserRegister, UserLogin, UserResponse, TokenResponse
)
from api.auth import (
    hash_password, verify_password, create_access_token, get_current_user_id, check_rate_limit
)

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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup validation for required environment variables
@app.on_event("startup")
async def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = ["DB_ENCRYPTION_KEY", "JWT_SECRET_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Copy .env.example to .env and fill in all values.\n"
            f"See SETUP_GUIDE.md for instructions."
        )
        raise RuntimeError(error_msg)

    print("Environment validation passed - DB_ENCRYPTION_KEY and JWT_SECRET_KEY configured")


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
    """
    Health check endpoint.

    Verifies that critical environment variables are configured.
    """
    # Verify critical env vars exist
    has_db_key = bool(os.getenv("DB_ENCRYPTION_KEY"))
    has_jwt_key = bool(os.getenv("JWT_SECRET_KEY"))

    # Determine overall status
    is_healthy = has_db_key and has_jwt_key

    return {
        "status": "healthy" if is_healthy else "degraded",
        "encryption_configured": has_db_key,
        "auth_configured": has_jwt_key
    }


# ============================================================================
# BUDGET & "THE NUMBER" ENDPOINTS
# ============================================================================

@app.get("/api/number", response_model=BudgetNumberResponse)
async def get_the_number(
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Get "The Number" - your daily spending limit.

    This is the main feature of the app!
    Requires authentication.
    """
    try:
        # Get budget mode configuration for this user
        budget_mode = db.get_setting("budget_mode", user_id)

        if not budget_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget mode not configured. Please configure your budget first."
            )

        # Load expenses into calculator
        calc = BudgetCalculator()
        expenses = db.get_expenses(user_id)
        for exp in expenses:
            calc.add_expense(exp["name"], exp["amount"], exp["is_fixed"])

        # Calculate "The Number" based on mode
        if budget_mode == "paycheck":
            monthly_income = db.get_setting("monthly_income", user_id)
            days_until_paycheck = db.get_setting("days_until_paycheck", user_id)
            result = calc.calculate_paycheck_mode(
                monthly_income=monthly_income,
                days_until_paycheck=days_until_paycheck
            )
        else:  # fixed_pool
            total_money = db.get_setting("total_money", user_id)
            target_end_date_str = db.get_setting("target_end_date", user_id)
            daily_spending_limit = db.get_setting("daily_spending_limit", user_id)

            # Parse target_end_date if it exists
            target_end_date = None
            if target_end_date_str:
                from datetime import datetime
                target_end_date = datetime.fromisoformat(target_end_date_str)
            result = calc.calculate_fixed_pool_mode(
                total_money=total_money,
                target_end_date=target_end_date,
                daily_spending_limit=daily_spending_limit
            )


        # Get today's spending
        today_spending = db.get_total_spending_today(user_id)
        remaining_today = result["daily_limit"] - today_spending

        import sys
        sys.stderr.write(f"\n{'='*60}\n")
        sys.stderr.write(f"[DEBUG] Budget calculation for user {user_id}:\n")
        sys.stderr.write(f"  - Mode: {budget_mode}\n")
        sys.stderr.write(f"  - Daily limit: {result['daily_limit']}\n")
        sys.stderr.write(f"  - Today's spending: {today_spending}\n")
        sys.stderr.write(f"  - Remaining today: {remaining_today}\n")
        sys.stderr.write(f"{'='*60}\n\n")
        sys.stderr.flush()

        return BudgetNumberResponse(
            the_number=remaining_today,
            mode=budget_mode,
            total_income=result.get("total_income"),
            total_money=result.get("total_money"),
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
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Configure budget mode and settings for the authenticated user.
    Requires authentication.
    """
    print(f"[DEBUG] configure_budget called for user_id={user_id}, mode={config.mode}")
    try:
        # Validate configuration based on mode
        if config.mode == "paycheck":
            if not config.monthly_income or not config.days_until_paycheck:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Paycheck mode requires monthly_income and days_until_paycheck"
                )
            db.set_setting("monthly_income", config.monthly_income, user_id)
            db.set_setting("days_until_paycheck", config.days_until_paycheck, user_id)

        elif config.mode == "fixed_pool":
            if config.total_money is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Fixed pool mode requires total_money"
                )
            db.set_setting("total_money", config.total_money, user_id)

            # Save fixed pool options (Option B and C)
            if config.target_end_date:
                db.set_setting("target_end_date", config.target_end_date.isoformat(), user_id)
            else:
                # Clear it if not provided
                db.set_setting("target_end_date", None, user_id)

            if config.daily_spending_limit:
                db.set_setting("daily_spending_limit", config.daily_spending_limit, user_id)
            else:
                # Clear it if not provided
                db.set_setting("daily_spending_limit", None, user_id)

        # Save budget mode
        db.set_setting("budget_mode", config.mode, user_id)

        return {"message": f"Budget configured successfully in {config.mode} mode"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring budget: {str(e)}"
        )


@app.get("/api/budget/config")
async def get_budget_config(
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Get current budget configuration for the authenticated user.
    Requires authentication.
    """
    mode = db.get_setting("budget_mode", user_id)
    if not mode:
        return {"configured": False}

    config = {"configured": True, "mode": mode}

    if mode == "paycheck":
        config["monthly_income"] = db.get_setting("monthly_income", user_id)
        config["days_until_paycheck"] = db.get_setting("days_until_paycheck", user_id)
    else:
        config["total_money"] = db.get_setting("total_money", user_id)
        target_end_date = db.get_setting("target_end_date", user_id)
        daily_spending_limit = db.get_setting("daily_spending_limit", user_id)
        if target_end_date:
            config["target_end_date"] = target_end_date
        if daily_spending_limit:
            config["daily_spending_limit"] = daily_spending_limit

    return config


# ============================================================================
# EXPENSE ENDPOINTS
# ============================================================================

@app.get("/api/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Get all expenses for the authenticated user.
    Requires authentication.
    """
    return db.get_expenses(user_id)


@app.post("/api/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Create a new expense for the authenticated user.
    Requires authentication.
    """
    try:
        expense_id = db.add_expense(
            name=expense.name,
            amount=expense.amount,
            user_id=user_id,
            is_fixed=expense.is_fixed
        )

        # Retrieve the created expense
        created_expense = db.get_expense_by_id(expense_id, user_id)
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
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Delete an expense for the authenticated user.
    Requires authentication.
    """
    try:
        db.delete_expense(expense_id, user_id)
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
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Import expenses from CSV or Excel file for the authenticated user.
    Requires authentication.

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
            existing = db.get_expenses(user_id)
            for exp in existing:
                db.delete_expense(exp["id"], user_id)

        # Add imported expenses
        imported_count = 0
        for exp in expenses:
            try:
                db.add_expense(exp["name"], exp["amount"], user_id, exp["is_fixed"])
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
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Export expenses to CSV or Excel for the authenticated user.
    Requires authentication.

    - **format**: Either 'csv' or 'excel'
    """
    try:
        expenses = db.get_expenses(user_id)

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
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Get recent transactions for the authenticated user.
    Requires authentication.
    """
    return db.get_transactions(user_id, limit=limit)


@app.post("/api/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Record a spending transaction for the authenticated user.
    Requires authentication.
    """
    try:
        txn_id = db.add_transaction(
            amount=transaction.amount,
            description=transaction.description,
            user_id=user_id,
            date=transaction.date,
            category=transaction.category
        )

        # Retrieve all transactions and find the one we just created
        transactions = db.get_transactions(user_id, limit=1)
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
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Delete a transaction for the authenticated user.
    Requires authentication.
    """
    try:
        db.delete_transaction(transaction_id, user_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting transaction: {str(e)}"
        )


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account and returns an access token.
    Rate limited: 5 requests per 60 seconds per IP.
    """
    # Rate limiting: 5 requests per minute
    check_rate_limit(request, max_requests=5, window_seconds=60)

    try:
        # Check if username already exists
        existing_user = db.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user
        user_id = db.create_user(
            username=user_data.username,
            password_hash=password_hash,
            email=user_data.email
        )

        # Get created user
        user = db.get_user_by_id(user_id)

        # Create access token
        access_token = create_access_token(data={"user_id": user_id})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                created_at=user["created_at"]
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Login with username and password.

    Returns an access token on successful authentication.
    Rate limited: 5 requests per 60 seconds per IP.
    """
    # Rate limiting: 5 requests per minute to prevent brute force
    check_rate_limit(request, max_requests=5, window_seconds=60)

    try:
        # Get user by username
        user = db.get_user_by_username(credentials.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Create access token
        access_token = create_access_token(data={"user_id": user["id"]})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                created_at=user["created_at"]
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {str(e)}"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: EncryptedDatabase = Depends(get_db)
):
    """
    Get current authenticated user.

    Requires valid JWT token in Authorization header.
    """
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.post("/api/auth/logout")
async def logout():
    """
    Logout endpoint.

    Since we're using JWT, logout is handled client-side by removing the token.
    This endpoint exists for consistency and future server-side logout logic.
    """
    return {"message": "Logged out successfully"}


# ============================================================================
# ADMIN / BACKUP ENDPOINTS
# ============================================================================

@app.post("/api/admin/backup")
async def create_backup(user_id: int = Depends(get_current_user_id)):
    """
    Create a manual database backup.

    Creates a timestamped backup in the backups/manual directory.
    Requires authentication.
    """
    import sqlite3
    import shutil
    from datetime import datetime
    from pathlib import Path as PathLib

    try:
        # Use absolute paths from the file location
        api_dir = PathLib(__file__).parent
        project_root = api_dir.parent

        db_path = api_dir / "budget.db"
        backup_dir = project_root / "backups" / "manual"

        # Create backup directory if needed
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"budget_backup_{timestamp}.db"
        backup_path = backup_dir / backup_name

        # Create backup using SQLite's backup API
        src = sqlite3.connect(str(db_path))
        dst = sqlite3.connect(str(backup_path))

        with dst:
            src.backup(dst)

        src.close()
        dst.close()

        return {
            "success": True,
            "backup_path": str(backup_path),
            "backup_filename": backup_name,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup failed: {str(e)}"
        )


@app.get("/api/admin/backups")
async def list_backups(user_id: int = Depends(get_current_user_id)):
    """
    List all available database backups.

    Returns backups from both manual and automatic directories,
    sorted by creation time (newest first).
    """
    from pathlib import Path
    from datetime import datetime

    # Use absolute path to backups directory
    backup_root = Path(__file__).parent.parent / "backups"
    if not backup_root.exists():
        return {"backups": []}

    all_backups = []

    # Scan both manual and automatic directories
    for subdir in ["manual", "automatic"]:
        subdir_path = backup_root / subdir
        if subdir_path.exists():
            for backup in subdir_path.glob("budget_backup_*.db"):
                stat = backup.stat()
                all_backups.append({
                    "filename": backup.name,
                    "path": str(backup),
                    "type": subdir,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

    # Sort by creation time (newest first)
    all_backups.sort(key=lambda b: b["created_at"], reverse=True)

    # Limit to most recent 20
    return {"backups": all_backups[:20]}


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
