import requests

# Try to login as admin
s = requests.Session()
r = s.post('http://127.0.0.1:8000/api-auth/login/', data={'username': 'admin@example.com', 'password': 'admin123'}, timeout=5)
print(f"Login Status: {r.status_code}")
print(r.text[:200])

# Create token for ShopAPI project
shopai_id = "a6d06794-58bc-43ca-b5e1-def37f109075"
r = requests.post(
    'http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/tokens/',
    json={'name': 'ShopAPI CI Token'},
    timeout=5
)
print(f"Create Token Status: {r.status_code}")
print(r.text)