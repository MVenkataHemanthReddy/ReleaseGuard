import requests

# First, login as admin to get session cookie
session = requests.Session()
login_data = {"username": "admin@example.com", "password": "admin123"}
r = requests.post('http://127.0.0.1:8000/api-auth/login/', data={"username": "admin@example.com", "password": "admin123"}, timeout=5)
print(f"Login Status: {r.status_code}")

# Check environments for ShopAPI project
project_id = "a6d06794-58bc-43ca-b5e1-def37f109075"
r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/{project_id}/environments/')
print(f"Environments Status: {r.status_code}")
print(r.text)