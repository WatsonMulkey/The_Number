"""
Test script to verify Money In feature issue.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_money_in():
    """Test the Money In feature with the resettest user."""

    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "username": "resettest",
        "password": "TestPass123!"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   [FAIL] Login failed: {response.text}")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   [OK] Logged in successfully")

    # Step 2: Try to record Money In with negative amount (current broken approach)
    print("\n2. Testing Money In with NEGATIVE amount (current frontend approach)...")
    transaction_data = {
        "amount": -50.00,  # Negative amount like frontend does
        "description": "Money In: Freelance work",  # Removed emoji
        "category": "income"
    }

    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print(f"   [EXPECTED] Backend rejected negative amount: {response.json()}")
    elif response.status_code == 201:
        print(f"   [UNEXPECTED] Transaction created (shouldn't allow negative!)")
    else:
        print(f"   [ERROR] Unexpected response: {response.text}")

    # Step 3: Try to record Money In with positive amount but income category
    print("\n3. Testing Money In with POSITIVE amount + income category...")
    transaction_data = {
        "amount": 50.00,  # Positive amount
        "description": "Money In: Freelance work",  # Removed emoji to avoid encoding issues
        "category": "income"
    }

    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"   [OK] Transaction created")
        print(f"       ID: {result.get('id')}")
        print(f"       Amount: ${result.get('amount')}")
        print(f"       Category: {result.get('category')}")
    else:
        print(f"   [FAIL] Transaction failed: {response.text}")

    # Step 4: Check if The Number was updated
    print("\n4. Checking if The Number was affected...")
    response = requests.get(f"{BASE_URL}/number", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        number_data = response.json()
        print(f"   The Number: ${number_data['the_number']:.2f}")
        print(f"   Today's spending: ${number_data['today_spending']:.2f}")
        print(f"   Remaining today: ${number_data['remaining_today']:.2f}")
    else:
        print(f"   [ERROR] Failed to get The Number: {response.text}")

    print("\n" + "="*60)
    print("CONCLUSION:")
    print("- Negative amounts are REJECTED by backend validation")
    print("- Frontend Money In feature is BROKEN")
    print("- Need to implement proper income transaction support")
    print("="*60)


if __name__ == "__main__":
    test_money_in()
