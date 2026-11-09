import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

r = requests.get('http://127.0.0.1:8000/api/v1/projects/', headers=headers, timeout=5)
data = r.json()
for p in data['results']:
    print(f"Project: {p['name']} (slug: {p['slug']})")
    print(f"  ID: {p['id']}")