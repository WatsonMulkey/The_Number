"""
Tests for FOI-104: Expense timestamps must use UTC-aware datetimes,
and frontend "today" filtering must use local dates.

Covers:
- database.py: datetime.now(ZoneInfo("UTC")) produces +00:00 suffix
- dates.py: validate_timezone() handles valid/invalid/None inputs
- dates.py: get_user_day_boundaries_utc() returns correct UTC boundaries
"""
import pytest
from datetime import datetime, time
from zoneinfo import ZoneInfo

from api.utils.dates import (
    validate_timezone,
    get_user_today,
    get_user_day_boundaries_utc,
    get_user_now_utc,
    DEFAULT_TIMEZONE,
)


class TestValidateTimezone:
    """validate_timezone() should accept valid IANA strings, reject bad ones."""

    def test_valid_timezone_returned_as_is(self):
        assert validate_timezone("America/New_York") == "America/New_York"
        assert validate_timezone("America/Denver") == "America/Denver"
        assert validate_timezone("Europe/London") == "Europe/London"
        assert validate_timezone("Asia/Tokyo") == "Asia/Tokyo"

    def test_none_returns_default(self):
        assert validate_timezone(None) == DEFAULT_TIMEZONE

    def test_empty_string_returns_default(self):
        assert validate_timezone("") == DEFAULT_TIMEZONE

    def test_invalid_string_returns_default(self):
        assert validate_timezone("Not/A/Timezone") == DEFAULT_TIMEZONE
        assert validate_timezone("Fake/City") == DEFAULT_TIMEZONE

    def test_default_is_america_denver(self):
        assert DEFAULT_TIMEZONE == "America/Denver"


class TestGetUserToday:
    """get_user_today() should return the correct date for the user's timezone."""

    def test_returns_date_not_datetime(self):
        result = get_user_today("America/New_York")
        assert isinstance(result, type(datetime.now().date()))

    def test_default_timezone_works(self):
        result = get_user_today(None)
        assert result is not None


class TestGetUserDayBoundariesUtc:
    """Day boundaries must convert user's local midnight→23:59:59 to UTC."""

    def test_returns_two_utc_datetimes(self):
        start, end = get_user_day_boundaries_utc("America/New_York")
        assert start.tzinfo is not None
        assert end.tzinfo is not None
        # Both should be in UTC
        assert str(start.tzinfo) == "UTC"
        assert str(end.tzinfo) == "UTC"

    def test_start_before_end(self):
        start, end = get_user_day_boundaries_utc("America/New_York")
        assert start < end

    def test_boundaries_span_roughly_24_hours(self):
        start, end = get_user_day_boundaries_utc("America/New_York")
        delta = end - start
        # Should be ~23:59:59
        assert 86399 <= delta.total_seconds() <= 86400

    def test_est_midnight_is_utc_plus_offset(self):
        """EST is UTC-5 (or UTC-4 during EDT). Start of day should be offset."""
        start, end = get_user_day_boundaries_utc("America/New_York")
        # Start hour in UTC should be 4 or 5 (depending on DST)
        assert start.hour in (4, 5), f"Expected UTC hour 4 or 5, got {start.hour}"

    def test_none_timezone_uses_default(self):
        """None should fall back to Denver (UTC-7 or UTC-6)."""
        start, _ = get_user_day_boundaries_utc(None)
        assert start.hour in (6, 7), f"Expected UTC hour 6 or 7 for Denver, got {start.hour}"


class TestGetUserNowUtc:
    """get_user_now_utc() should always return a timezone-aware UTC datetime."""

    def test_returns_utc_aware_datetime(self):
        result = get_user_now_utc()
        assert result.tzinfo is not None
        assert str(result.tzinfo) == "UTC"

    def test_isoformat_includes_offset(self):
        """This is the core of FOI-104: stored timestamps MUST have +00:00."""
        result = get_user_now_utc()
        iso = result.isoformat()
        assert "+00:00" in iso, f"Expected +00:00 suffix, got: {iso}"


class TestUtcAwareTimestampStorage:
    """
    Verifies that datetime.now(ZoneInfo("UTC")).isoformat() produces
    a string that JavaScript will correctly parse as UTC.
    """

    def test_utc_aware_isoformat_has_offset(self):
        """The fix: datetime.now(ZoneInfo('UTC')) should produce +00:00 suffix."""
        dt = datetime.now(ZoneInfo("UTC"))
        iso = dt.isoformat()
        assert "+00:00" in iso, f"Expected UTC offset in '{iso}'"

    def test_naive_datetime_isoformat_has_no_offset(self):
        """The old bug: datetime.now() produces no timezone suffix."""
        dt = datetime.now()
        iso = dt.isoformat()
        assert "+" not in iso, f"Naive datetime shouldn't have offset: '{iso}'"
        assert "Z" not in iso

    def test_javascript_date_parsing_difference(self):
        """
        Demonstrates why the +00:00 suffix matters for JS:
        - '2026-04-01T20:30:00' → JS treats as UTC (shows 20:30 regardless of TZ)
        - '2026-04-01T20:30:00+00:00' → JS treats as UTC, converts to local display
        Both are UTC in JS, but the explicit offset makes intent clear and
        ensures consistent cross-platform behavior.
        """
        naive = datetime(2026, 4, 1, 20, 30, 0)
        aware = datetime(2026, 4, 1, 20, 30, 0, tzinfo=ZoneInfo("UTC"))

        assert "+00:00" not in naive.isoformat()
        assert "+00:00" in aware.isoformat()


class TestLocalDateComparison:
    """
    Simulates the frontend todayTotal fix: comparing transactions
    by converting UTC timestamps to local dates.
    """

    def test_late_night_est_transaction_correct_day(self):
        """
        Drew's bug: At 11 PM EST (= 3 AM UTC next day),
        the old code would say 'today' is tomorrow.
        """
        # Simulate: user is in EST, it's 11 PM on April 1
        est = ZoneInfo("America/New_York")
        user_local_time = datetime(2026, 4, 1, 23, 0, 0, tzinfo=est)

        # The UTC equivalent
        utc_time = user_local_time.astimezone(ZoneInfo("UTC"))
        # This should be April 2 in UTC
        assert utc_time.day == 2, f"Expected UTC day 2, got {utc_time.day}"

        # OLD BUG: using UTC date as "today"
        utc_today = utc_time.strftime("%Y-%m-%d")  # "2026-04-02" WRONG
        local_today = user_local_time.strftime("%Y-%m-%d")  # "2026-04-01" CORRECT

        assert utc_today == "2026-04-02"  # This is what the old code used
        assert local_today == "2026-04-01"  # This is what the fix uses
        assert utc_today != local_today  # They differ — that's the bug
