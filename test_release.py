import requests
import os

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'}
project_id = "a6d06794-58bc-43ca-b5e1-def37f109075"
prod_env_id = "4eaeef11-ba7b-4e4a-8881-88bd0dd6f023"

# Test release creation
release_data = {
    "version": "shopapi-v1.0.0",
    "environment_id": prod_env_id,
    "commit_sha": "abc123def",
    "branch": "main"
}

r = requests.post(
    'http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/releases/',
    json={'version': 'shopapi-v1.0.0', 'environment_id': prod_env_id, 'commit_sha': 'abc123def', 'branch': 'main'},
    timeout=5
)
print(f"Create Release Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 201:
    release = r.json()
    release_id = release['id']
    print(f"Release ID: {release_id}")