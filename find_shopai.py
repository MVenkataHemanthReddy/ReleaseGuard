import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

# Get all projects
r = requests.get('http://127.0.0.1:8000/api/v1/projects/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
data = r.json()
for p in data['results']:
    if 'shopapi' in p['slug'].lower():
        print(f"Found ShopAPI project: {p['name']}")
        print(f"  ID: {p['id']}")
        print(f"  Slug: {p['slug']}")
        print()
        
        # Get environments for this project
        env_r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/{p["id"]}/environments/', headers=headers)
        print(f"Environments: {env_r.json()}")
        break