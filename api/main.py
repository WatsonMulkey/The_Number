"""
FastAPI main application for The Number budgeting app.

This API provides REST endpoints for the Vue.js frontend,
wrapping the existing Python backend (database.py, calculator.py).
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    UserRegister, UserLogin, UserResponse, TokenResponse,
    ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse
)
from api.auth import (
    hash_password, verify_password, create_access_token, get_current_user_id, check_rate_limit,
    generate_reset_token, verify_reset_token, invalidate_reset_token
)

# Create FastAPI app
app = FastAPI(
    title="The Number API",
    description="REST API for The Number budgeting app",
    version="0.9.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
# Read allowed origins from environment variable
# For development: defaults to localhost on any port
# For production: set CORS_ORIGINS to your frontend URL(s)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176")
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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

    logger.info("Environment validation passed - encryption and auth configured")


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

        return BudgetNumberResponse(
            the_number=result["daily_limit"],
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
    logger.info(f"Budget configured for user {user_id} in {config.mode} mode")
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


@app.post("/api/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: Request,
    forgot_request: ForgotPasswordRequest
):
    """
    Request a password reset token.

    Generates a password reset token for the given username.
    The token is valid for 1 hour.

    Rate limited to prevent abuse.
    """
    # Apply rate limiting
    check_rate_limit(request, max_requests=5, window_seconds=300)  # 5 requests per 5 minutes

    # Verify username exists
    db = EncryptedDatabase()
    user = db.get_user_by_username(forgot_request.username)

    if not user:
        # Don't reveal if username exists or not (security best practice)
        # Return success even if user doesn't exist
        pass

    # Generate reset token
    reset_token = generate_reset_token(forgot_request.username)

    return ForgotPasswordResponse(
        reset_token=reset_token,
        message="Password reset token generated. Use this token to reset your password within 1 hour.",
        expires_in=3600  # 1 hour in seconds
    )


@app.post("/api/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: Request,
    reset_request: ResetPasswordRequest
):
    """
    Reset password using a reset token.

    Validates the reset token and updates the user's password.
    The token is invalidated after successful password reset.
    """
    # Verify reset token
    username = verify_reset_token(reset_request.reset_token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    db = EncryptedDatabase()
    user = db.get_user_by_username(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Hash new password
    hashed_password = hash_password(reset_request.new_password)

    # Update password in database
    db.update_user_password(user["id"], hashed_password)

    # Invalidate the reset token
    invalidate_reset_token(reset_request.reset_token)

    return ResetPasswordResponse(
        message="Password has been reset successfully. You can now login with your new password."
    )


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


@app.get("/api/export/{format}")
async def export_budget_data(format: str, user_id: int = Depends(get_current_user_id)):
    """
    Export all budget data (config, expenses, transactions) in CSV or Excel format.

    Supported formats: 'csv', 'excel'
    """
    import csv
    import io
    from datetime import datetime
    from fastapi.responses import StreamingResponse

    if format not in ['csv', 'excel']:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'excel'")

    db = get_db()

    # Get budget configuration
    settings = {}
    for row in db.execute('SELECT key, value FROM settings WHERE user_id = ?', (user_id,)):
        settings[row[0]] = row[1]

    # Get expenses
    expenses = list(db.execute('SELECT name, amount, is_fixed FROM expenses WHERE user_id = ? ORDER BY name', (user_id,)))

    # Get transactions
    transactions = list(db.execute(
        'SELECT date, amount, description, category FROM transactions WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    ))

    if format == 'csv':
        # Create CSV with multiple sections
        output = io.StringIO()
        writer = csv.writer(output)

        # Budget Configuration Section
        writer.writerow(['BUDGET CONFIGURATION'])
        writer.writerow(['Setting', 'Value'])
        for key, value in settings.items():
            writer.writerow([key, value])
        writer.writerow([])  # Blank line

        # Expenses Section
        writer.writerow(['MONTHLY EXPENSES'])
        writer.writerow(['Name', 'Amount', 'Type'])
        for exp in expenses:
            exp_type = 'Fixed' if exp[2] else 'Variable'
            writer.writerow([exp[0], f'${exp[1]:.2f}', exp_type])
        writer.writerow([])

        # Transactions Section
        writer.writerow(['TRANSACTIONS'])
        writer.writerow(['Date', 'Amount', 'Description', 'Category'])
        for txn in transactions:
            category = txn[3] if txn[3] else ''
            writer.writerow([txn[0], f'${txn[1]:.2f}', txn[2], category])

        # Return CSV file
        output.seek(0)
        filename = f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:  # Excel format
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="Excel export requires openpyxl. Please install it."
            )

        # Create workbook with multiple sheets
        wb = openpyxl.Workbook()

        # Sheet 1: Budget Configuration
        ws_config = wb.active
        ws_config.title = "Budget Config"
        ws_config['A1'] = 'Budget Configuration'
        ws_config['A1'].font = Font(bold=True, size=14)
        ws_config['A3'] = 'Setting'
        ws_config['B3'] = 'Value'
        ws_config['A3'].font = Font(bold=True)
        ws_config['B3'].font = Font(bold=True)

        row = 4
        for key, value in settings.items():
            ws_config[f'A{row}'] = key
            ws_config[f'B{row}'] = value
            row += 1

        # Sheet 2: Expenses
        ws_expenses = wb.create_sheet("Expenses")
        ws_expenses['A1'] = 'Monthly Expenses'
        ws_expenses['A1'].font = Font(bold=True, size=14)
        ws_expenses['A3'] = 'Name'
        ws_expenses['B3'] = 'Amount'
        ws_expenses['C3'] = 'Type'
        for col in ['A3', 'B3', 'C3']:
            ws_expenses[col].font = Font(bold=True)

        row = 4
        total = 0
        for exp in expenses:
            exp_type = 'Fixed' if exp[2] else 'Variable'
            ws_expenses[f'A{row}'] = exp[0]
            ws_expenses[f'B{row}'] = exp[1]
            ws_expenses[f'B{row}'].number_format = '$#,##0.00'
            ws_expenses[f'C{row}'] = exp_type
            total += exp[1]
            row += 1

        # Add total
        ws_expenses[f'A{row}'] = 'TOTAL'
        ws_expenses[f'A{row}'].font = Font(bold=True)
        ws_expenses[f'B{row}'] = total
        ws_expenses[f'B{row}'].number_format = '$#,##0.00'
        ws_expenses[f'B{row}'].font = Font(bold=True)

        # Sheet 3: Transactions
        ws_txns = wb.create_sheet("Transactions")
        ws_txns['A1'] = 'Transaction History'
        ws_txns['A1'].font = Font(bold=True, size=14)
        ws_txns['A3'] = 'Date'
        ws_txns['B3'] = 'Amount'
        ws_txns['C3'] = 'Description'
        ws_txns['D3'] = 'Category'
        for col in ['A3', 'B3', 'C3', 'D3']:
            ws_txns[col].font = Font(bold=True)

        row = 4
        for txn in transactions:
            ws_txns[f'A{row}'] = txn[0]
            ws_txns[f'B{row}'] = txn[1]
            ws_txns[f'B{row}'].number_format = '$#,##0.00'
            ws_txns[f'C{row}'] = txn[2]
            ws_txns[f'D{row}'] = txn[3] if txn[3] else ''
            row += 1

        # Auto-size columns
        for ws in [ws_config, ws_expenses, ws_txns]:
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@app.get("/api/admin/backups/download/{filename}")
async def download_backup(filename: str, user_id: int = Depends(get_current_user_id)):
    """
    Download a specific backup file.

    Security: Validates filename to prevent directory traversal attacks.
    Returns the backup file as a downloadable attachment.
    """
    from pathlib import Path
    from fastapi.responses import FileResponse
    import os

    # Validate filename to prevent directory traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    # Only allow .db files with correct naming pattern
    if not filename.startswith("budget_backup_") or not filename.endswith(".db"):
        raise HTTPException(
            status_code=400,
            detail="Invalid backup filename format"
        )

    # Use same path logic as create_backup
    api_dir = Path(__file__).parent
    project_root = api_dir.parent

    # Search for the backup in both manual and automatic directories
    backup_path = None
    for subdir in ["manual", "automatic"]:
        potential_path = project_root / "backups" / subdir / filename
        logger.info(f"Checking backup path: {potential_path}")
        logger.info(f"File exists: {potential_path.exists()}")
        if potential_path.exists():
            backup_path = potential_path
            logger.info(f"Found backup at: {backup_path}")
            break

    if not backup_path:
        logger.error(f"Backup file not found in {project_root / 'backups'}")
        raise HTTPException(
            status_code=404,
            detail="Backup file not found"
        )

    # Return file as download
    return FileResponse(
        path=str(backup_path),
        filename=filename,
        media_type="application/x-sqlite3",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
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
