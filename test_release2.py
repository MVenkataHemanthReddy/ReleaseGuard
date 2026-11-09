import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'}

r = requests.post(
    'http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/releases/',
    json={'version': 'shopapi-v1.0.0', 'environment_id': '4eaeef11-ba7b-4e4a-8881-88bd0dd6f023', 'commit_sha': 'abc123def', 'branch': 'main'},
    headers=headers,
    timeout=5
)

print(f"Status: {r.status_code}")
print(r.text)