"""
Test script for password reset endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_password_reset():
    """Test the complete password reset flow."""

    # Step 1: Register a test user
    print("1. Registering test user...")
    register_data = {
        "username": "resettest",
        "password": "OldPassword123",
        "email": "reset@test.com"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   [OK] User registered successfully")
    elif "already exists" in response.text:
        print("   [INFO] User already exists, continuing with reset test...")
    else:
        print(f"   [FAIL] Registration failed: {response.text}")
        return

    # Step 2: Request password reset token
    print("\n2. Requesting password reset token...")
    forgot_data = {
        "username": "resettest"
    }

    response = requests.post(f"{BASE_URL}/auth/forgot-password", json=forgot_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        reset_token = result["reset_token"]
        print(f"   [OK] Reset token generated: {reset_token[:20]}...")
        print(f"   Message: {result['message']}")
        print(f"   Expires in: {result['expires_in']} seconds")
    else:
        print(f"   [FAIL] Request failed: {response.text}")
        return

    # Step 3: Reset password with token
    print("\n3. Resetting password...")
    reset_data = {
        "reset_token": reset_token,
        "new_password": "NewPassword456!"
    }

    response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   [OK] {result['message']}")
    else:
        print(f"   [FAIL] Reset failed: {response.text}")
        return

    # Step 4: Try logging in with new password
    print("\n4. Testing login with new password...")
    login_data = {
        "username": "resettest",
        "password": "NewPassword456!"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   [OK] Login successful with new password!")
    else:
        print(f"   [FAIL] Login failed: {response.text}")
        return

    # Step 5: Verify old password doesn't work
    print("\n5. Verifying old password is rejected...")
    login_data["password"] = "OldPassword123"

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   [OK] Old password correctly rejected")
    else:
        print(f"   [FAIL] Unexpected result: {response.status_code}")

    # Step 6: Test invalid token
    print("\n6. Testing invalid reset token...")
    reset_data = {
        "reset_token": "invalid_token_12345",
        "new_password": "AnotherPassword789!"
    }

    response = requests.post(f"{BASE_URL}/auth/reset-password", json=reset_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print("   [OK] Invalid token correctly rejected")
    else:
        print(f"   [FAIL] Unexpected result: {response.status_code}")

    print("\n" + "="*50)
    print("Password reset flow test completed successfully!")
    print("="*50)


if __name__ == "__main__":
    test_password_reset()
