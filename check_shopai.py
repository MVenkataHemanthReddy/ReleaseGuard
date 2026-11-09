import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

# Check ShopAPI project
shopai_id = "99158aa5-a0c3-4ebe-980c-a5d8b154d370"
r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/{shopai_id}/', headers=headers, timeout=5)
print(f"Project Status: {r.status_code}")
print(r.text)

# Get environments
r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/99158aa5-a0c3-4ebe-980c-a5d8b154d370/environments/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"Environments Status: {r.status_code}")
print(r.text)