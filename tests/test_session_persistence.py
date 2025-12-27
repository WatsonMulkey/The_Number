"""
Test script to verify JWT tokens persist across server restarts.

This test ensures that the JWT_SECRET_KEY is loaded from environment
variables and doesn't change when the server restarts.
"""

import requests
import time
import sys
import os

API_URL = "http://localhost:8000"

def test_session_persistence():
    """Test that user sessions persist across server restart."""

    print("=" * 60)
    print("JWT Session Persistence Test")
    print("=" * 60)
    print()

    # Step 1: Register a new user
    print("Step 1: Registering new test user...")
    username = f"testuser_{int(time.time())}"
    password = "testpass123"

    try:
        resp = requests.post(
            f"{API_URL}/api/auth/register",
            json={
                "username": username,
                "password": password,
                "email": f"{username}@example.com"
            },
            timeout=5
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Registration failed: {e}")
        return False

    token = resp.json()["access_token"]
    print(f"[OK] User registered: {username}")
    print(f"  Token (first 20 chars): {token[:20]}...")
    print()

    # Step 2: Verify token works initially
    print("Step 2: Verifying token works...")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(f"{API_URL}/api/auth/me", headers=headers, timeout=5)
        resp.raise_for_status()
        user_data = resp.json()
        print(f"[OK] Token verified - User: {user_data['username']}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Token verification failed: {e}")
        return False
    print()

    # Step 3: Wait and tell user to restart server
    print("=" * 60)
    print("MANUAL STEP REQUIRED:")
    print("Please restart the backend server now.")
    print()
    print("In another terminal, run:")
    print("  1. Stop server (Ctrl+C)")
    print("  2. cd api")
    print("  3. python -m uvicorn main:app --reload --port 8000")
    print()
    input("Press Enter after restarting the server...")
    print("=" * 60)
    print()

    # Step 4: Wait for server to be ready
    print("Step 3: Waiting for server to restart...")
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            resp = requests.get(f"{API_URL}/health", timeout=2)
            if resp.status_code == 200:
                print(f"[OK] Server is back online (attempt {attempt + 1})")
                break
        except requests.exceptions.RequestException:
            if attempt < max_attempts - 1:
                print(f"  Waiting for server... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
            else:
                print(f"[FAIL] Server did not come back online after {max_attempts} attempts")
                return False
    print()

    # Step 5: Verify token still works after restart
    print("Step 4: Verifying token still works after restart...")
    try:
        resp = requests.get(f"{API_URL}/api/auth/me", headers=headers, timeout=5)
        resp.raise_for_status()
        user_data = resp.json()
        print(f"[OK] Token still valid - User: {user_data['username']}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Token invalid after restart: {e}")
        print()
        print("FAILURE: JWT secret likely changed on restart!")
        print("This means JWT_SECRET_KEY is not being loaded from .env properly.")
        return False
    print()

    # Success!
    print("=" * 60)
    print("SUCCESS: Session Persisted Across Restart!")
    print("=" * 60)
    print()
    print("This confirms that:")
    print("  - JWT_SECRET_KEY is loaded from environment variables")
    print("  - Tokens remain valid after server restarts")
    print("  - User sessions are properly persisted")
    return True

if __name__ == "__main__":
    try:
        success = test_session_persistence()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
