"""
Pydantic models for API request/response validation.

These models match the existing data structures from calculator.py and database.py
and provide automatic validation and OpenAPI schema generation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Import validation constants from existing backend
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.calculator import MAX_AMOUNT, MAX_STRING_LENGTH


class ExpenseCreate(BaseModel):
    """Request model for creating an expense."""
    name: str = Field(..., max_length=MAX_STRING_LENGTH, description="Expense name")
    amount: float = Field(..., gt=0, le=MAX_AMOUNT, description="Monthly expense amount")
    is_fixed: bool = Field(..., description="True for fixed monthly expenses, False for variable")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Rent",
                "amount": 1500.00,
                "is_fixed": True
            }
        }


class ExpenseResponse(BaseModel):
    """Response model for expense data."""
    id: int
    name: str
    amount: float
    is_fixed: bool
    created_at: str
    updated_at: str


class ExpenseUpdate(BaseModel):
    """Request model for updating an expense (partial update supported)."""
    name: Optional[str] = Field(None, max_length=MAX_STRING_LENGTH, description="Expense name")
    amount: Optional[float] = Field(None, gt=0, le=MAX_AMOUNT, description="Monthly expense amount")
    is_fixed: Optional[bool] = Field(None, description="True for fixed monthly expenses, False for variable")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Utilities",
                "amount": 150.00
            }
        }


class TransactionCreate(BaseModel):
    """Request model for creating a transaction."""
    amount: float = Field(..., gt=0, le=MAX_AMOUNT, description="Transaction amount")
    description: str = Field(..., max_length=MAX_STRING_LENGTH, description="Transaction description")
    category: Optional[str] = Field(None, max_length=MAX_STRING_LENGTH, description="Optional category")
    date: Optional[datetime] = Field(None, description="Transaction date (defaults to now)")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 45.50,
                "description": "Grocery shopping",
                "category": "Food"
            }
        }


class TransactionResponse(BaseModel):
    """Response model for transaction data."""
    id: int
    date: str
    amount: float
    description: str
    category: Optional[str]
    created_at: str


class BudgetModeConfig(BaseModel):
    """Configuration for budget mode."""
    mode: str = Field(..., pattern="^(paycheck|fixed_pool)$", description="Budget mode: 'paycheck' or 'fixed_pool'")
    monthly_income: Optional[float] = Field(None, gt=0, description="Monthly income (paycheck mode only)")
    days_until_paycheck: Optional[int] = Field(None, gt=0, le=365, description="Days until next paycheck (paycheck mode only)")
    total_money: Optional[float] = Field(None, ge=0, description="Total money available (fixed_pool mode only)")
    target_end_date: Optional[datetime] = Field(None, description="Target end date for fixed pool (Option B)")
    daily_spending_limit: Optional[float] = Field(None, gt=0, description="Daily spending limit for fixed pool (Option C)")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "mode": "paycheck",
                    "monthly_income": 4000.00,
                    "days_until_paycheck": 14
                },
                {
                    "mode": "fixed_pool",
                    "total_money": 5000.00
                }
            ]
        }


class BudgetNumberResponse(BaseModel):
    """Response model for 'The Number' - daily spending limit."""
    the_number: float = Field(..., description="Daily spending limit")
    mode: str = Field(..., description="Current budget mode")
    total_income: Optional[float] = Field(None, description="Total monthly income (paycheck mode)")
    total_money: Optional[float] = Field(None, description="Total money available (fixed_pool mode)")
    total_expenses: Optional[float] = Field(None, description="Total monthly expenses")
    remaining_money: Optional[float] = Field(None, description="Money remaining after expenses")
    days_remaining: Optional[float] = Field(None, description="Days remaining in budget period")
    today_spending: float = Field(..., description="Amount spent today")
    remaining_today: float = Field(..., description="Remaining daily budget for today")
    is_over_budget: bool = Field(..., description="True if over budget today")

    class Config:
        json_schema_extra = {
            "example": {
                "the_number": 38.50,
                "mode": "paycheck",
                "total_income": 4000.00,
                "total_expenses": 2500.00,
                "remaining_money": 1500.00,
                "days_remaining": 14,
                "today_spending": 12.00,
                "remaining_today": 26.50,
                "is_over_budget": False
            }
        }


class ImportExpensesResponse(BaseModel):
    """Response model for expense import."""
    imported_count: int = Field(..., description="Number of expenses successfully imported")
    errors: list[str] = Field(default_factory=list, description="List of import errors")


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Error type classification")


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class UserRegister(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, max_length=72, description="Password (6-72 characters)")
    email: Optional[str] = Field(None, max_length=100, description="Email (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure_password123",
                "email": "john@example.com"
            }
        }


class UserLogin(BaseModel):
    """Request model for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure_password123"
            }
        }


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    username: str
    email: Optional[str]
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")


class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password."""
    username: str = Field(..., min_length=3, description="Username for password reset")


class ForgotPasswordResponse(BaseModel):
    """Response model for forgot password."""
    reset_token: str = Field(..., description="Password reset token")
    message: str = Field(..., description="Instructions for password reset")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class ResetPasswordRequest(BaseModel):
    """Request model for reset password."""
    reset_token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=72, description="New password (8-72 characters)")


class ResetPasswordResponse(BaseModel):
    """Response model for reset password."""
    message: str = Field(..., description="Success message")
