import requests

headers = {
    'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII',
    'Content-Type': 'application/json'
}

# Test 1: List projects
print("=== Test 1: List Projects ===")
r = requests.get('http://127.0.0.1:8000/api/v1/projects/', headers=headers, timeout=5)
print(f"Status: {r.status_code}")
print(r.text[:500])

# Test 2: Create project
print("\n=== Test 2: Create Project ===")
data = {
    "name": "ShopAPI Demo",
    "slug": "shopapi-demo",
    "description": "E-commerce demo with 6 regressions",
    "organisation": "f26f2c3c-f054-4341-8ccb-a8e2a926a2e6"
}
r = requests.post('http://127.0.0.1:8000/api/v1/projects/', headers=headers, json=data, timeout=5)
print(f"Status: {r.status_code}")
print(r.text[:500])

# Test 3: List organizations
print("\n=== Test 3: List Organizations ===")
r = requests.get('http://127.0.0.1:8000/api/v1/organisations/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"Status: {r.status_code}")
print(r.text[:500])

# Test 4: Create organization
print("\n=== Test 4: Create Organization ===")
data = {
    "name": "My New Org",
    "slug": "my-new-org",
    "description": "Test organization"
}
r = requests.post('http://127.0.0.1:8000/api/v1/organisations/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'}, json=data, timeout=5)
print(f"Status: {r.status_code}")
print(r.text[:500])

# Test 5: Test project creation with session auth (via admin)
print("\n=== Test 5: Create project with session auth ===")
# First login
login_data = {"username": "admin@example.com", "password": "admin123"}
s = requests.Session()
r = s.post('http://127.0.0.1:8000/api-auth/login/', data=login_data, timeout=5)
print(f"Login Status: {r.status_code}")

# Create project with session
data = {
    "name": "Test Project",
    "slug": "test-project",
    "description": "Test project via session"
}
r = s.post('http://127.0.0.1:8000/api/v1/projects/', json=data, timeout=5)
print(f"Create Project Status: {r.status_code}")
print(r.text[:500])