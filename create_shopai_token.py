import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

# Get ShopAPI project ID
shopai_id = "a6d06794-58bc-43ca-b5e1-def37f109075"

# Create token for ShopAPI project
r = requests.post(
    f'http://127.0.0.1:8000/api/v1/projects/{shopai_id}/tokens/',
    headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'},
    json={'name': 'ShopAPI CI Token'},
    timeout=5
)

print(f"Status: {r.status_code}")
print(r.text)

if r.status_code == 201:
    token_data = r.json()
    print(f"\nShopAPI Token: {token_data.get('token')}")
    print(f"Token ID: {token_data.get('id')}")