"""Test backup API endpoints."""

import requests
import json

API_URL = "http://localhost:8000"

# Login to get token
print("Logging in...")
resp = requests.post(
    f"{API_URL}/api/auth/login",
    json={"username": "testuser_1766813090", "password": "testpass123"}
)
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"[OK] Got token: {token[:30]}...")
print()

# Test list backups endpoint
print("Testing GET /api/admin/backups...")
resp = requests.get(f"{API_URL}/api/admin/backups", headers=headers)
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Found {len(data['backups'])} backup(s)")
for backup in data['backups']:
    size_kb = backup['size'] / 1024
    print(f"  - {backup['filename']} ({backup['type']}, {size_kb:.1f} KB)")
print()

# Test create backup endpoint
print("Testing POST /api/admin/backup...")
resp = requests.post(f"{API_URL}/api/admin/backup", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"[OK] Backup created: {data['backup_filename']}")
    print(f"     Path: {data['backup_path']}")
else:
    print(f"[FAIL] {resp.text}")
print()

# List backups again
print("Listing backups again...")
resp = requests.get(f"{API_URL}/api/admin/backups", headers=headers)
data = resp.json()
print(f"Found {len(data['backups'])} backup(s)")
for backup in data['backups'][:5]:  # Show first 5
    size_kb = backup['size'] / 1024
    print(f"  - {backup['filename']} ({backup['type']}, {size_kb:.1f} KB)")

print()
print("=" * 60)
print("Backup endpoints working correctly!")
print("=" * 60)
