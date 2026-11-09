import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

# Create token for ShopAPI project
shopai_id = "99158aa5-a0c3-4ebe-980c-a5d8b154d370"
r = requests.post(
    f'http://127.0.0.1:8000/api/v1/projects/{shopai_id}/tokens/',
    headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'},
    json={'name': 'ShopAPI CI Token'},
    timeout=5
)

print(f"Status: {r.status_code}")
print(r.text)

# If successful, test environments with new token
if r.status_code == 201:
    new_token = r.json()['token']
    print(f"\nNew token: {new_token}")
    
    # Test environments with new token
    r = requests.get(
        f'http://127.0.0.1:8000/api/v1/projects/99158aa5-a0c3-4ebe-980c-a5d8b154d370/environments/',
        headers={'Authorization': f'Token {new_token}'},
        timeout=5
    )
    print(f"\nEnvironments Status: {r.status_code}")
    print(r.text)