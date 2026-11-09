import requests

headers = {
    'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII',
    'Content-Type': 'application/json'
}

# Create ShopAPI project with unique slug
data = {
    "name": "ShopAPI Demo",
    "slug": "shopapi-demo-v3",
    "description": "E-commerce demo with 6 regressions",
    "organisation": "f26f2c3c-f054-4341-8ccb-a8e2a926a2e6"
}

r = requests.post(
    'http://127.0.0.1:8000/api/v1/projects/',
    headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'},
    json=data,
    timeout=5
)

print(f"Status: {r.status_code}")
print(r.text)

if r.status_code == 201:
    data = r.json()
    print(f"\nProject ID: {data['id']}")
    print(f"Project Slug: {data['slug']}")
    
    # Get environments for this project
    env_r = requests.get(f"http://127.0.0.1:8000/api/v1/projects/{data['id']}/environments/", headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'})
    print(f"\nEnvironments: {env_r.json()}")