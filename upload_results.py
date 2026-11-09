import requests
import os

# Configuration
headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}
project_id = "a6d06794-58bc-43ca-b5e1-def37f109075"
prod_env_id = "4eaeef11-ba7b-4e4a-8881-88bd0dd6f023"  # Production environment ID

# 1. Create release
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
release = r.json()
release_id = release['id']
print(f"Release ID: {release_id}")

# 2. Upload test results
results_path = r"C:\Users\mitta\OneDrive\Documents\DEFAUL~1\shopapi_project\results.xml"
if os.path.exists(results_path):
    with open(results_path, 'rb') as f:
        files = {
            'junit_xml': ('results.xml', f, 'application/xml'),
            'test_run_name': (None, 'shopapi-tests'),
        }
        r = requests.post(
            f'http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/releases/{release_id}/test-runs/',
            files=files,
            timeout=30
        )
        print(f"Upload Status: {r.status_code}")
        print(r.text[:500])
else:
    print(f"Results file not found at: {results_path}")