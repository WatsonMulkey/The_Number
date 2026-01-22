"""
Timezone-aware date utilities for The Number budget app.

Design principle: Store all timestamps in UTC, convert to user timezone only at query time.
This ensures data consistency and allows multi-timezone support.
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo, available_timezones
from typing import Tuple

# Cache the set of valid timezones at module load
VALID_TIMEZONES = available_timezones()

# Default timezone for users who haven't set one (MST - Mountain Standard Time)
DEFAULT_TIMEZONE = "America/Denver"


def validate_timezone(tz_str: str | None) -> str:
    """
    Validate a timezone string and return it if valid, otherwise return default.

    Args:
        tz_str: Timezone string like "America/Denver" or "America/New_York"

    Returns:
        Valid timezone string (input or default)
    """
    if tz_str and tz_str in VALID_TIMEZONES:
        return tz_str
    return DEFAULT_TIMEZONE


def get_user_today(user_timezone: str | None = None) -> date:
    """
    Get today's date in the user's timezone.

    Args:
        user_timezone: User's timezone string (e.g., "America/Denver")

    Returns:
        Today's date in user's local timezone
    """
    tz = ZoneInfo(validate_timezone(user_timezone))
    return datetime.now(tz).date()


def get_user_day_boundaries_utc(user_timezone: str | None = None) -> Tuple[datetime, datetime]:
    """
    Get UTC timestamps for start and end of 'today' in user's timezone.

    This is used for database queries - transactions are stored in UTC,
    but we want to find all transactions that fall within the user's local "today".

    Args:
        user_timezone: User's timezone string (e.g., "America/Denver")

    Returns:
        Tuple of (start_of_day_utc, end_of_day_utc) as timezone-aware datetimes

    Example:
        For a user in MST (UTC-7) at 8 AM local time on Jan 22:
        - User's "today" is Jan 22
        - Start of day in MST: Jan 22 00:00:00 MST = Jan 22 07:00:00 UTC
        - End of day in MST: Jan 22 23:59:59 MST = Jan 23 06:59:59 UTC
    """
    tz = ZoneInfo(validate_timezone(user_timezone))
    user_now = datetime.now(tz)
    user_today = user_now.date()

    # Start of day in user's timezone (midnight)
    start_local = datetime.combine(user_today, time.min, tzinfo=tz)
    # End of day in user's timezone (23:59:59.999999)
    end_local = datetime.combine(user_today, time.max, tzinfo=tz)

    # Convert to UTC for database queries
    utc = ZoneInfo("UTC")
    start_utc = start_local.astimezone(utc)
    end_utc = end_local.astimezone(utc)

    return (start_utc, end_utc)


def get_user_now_utc(user_timezone: str | None = None) -> datetime:
    """
    Get current UTC datetime (for storing timestamps).

    Note: This always returns UTC regardless of user timezone.
    The user_timezone parameter is accepted but unused - it's here for API consistency.

    Returns:
        Current UTC datetime (timezone-aware)
    """
    return datetime.now(ZoneInfo("UTC"))
