import requests
import os

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

# Use the Demo Project (which has environments and works with the demo token)
demo_project_id = "773599bf-25b7-4e19-abcb-6cd2593ca1e6"

# Get environments for Demo Project
r = requests.get('http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/environments/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"Environments Status: {r.status_code}")
envs = r.json()
for env in envs.get('results', envs):
    print(f"  - {env['name']} (type: {env['type']}) ID: {env['id']}")

# Find production environment
prod_env = None
for env in envs.get('results', envs):
    if env.get('type') == 'PRODUCTION' or env.get('slug') == 'production':
        prod_env_id = env['id']
        print(f"Found Production env: {env['name']} ID: {env['id']}")

# Create release
if 'prod_env_id' in locals():
    release_data = {
        "version": "v1.0.0-demo",
        "environment_id": prod_env_id,
        "commit_sha": "abc123def",
        "branch": "main"
    }
    r = requests.post(
        'http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/releases/',
        headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'},
        json={'version': 'v1.0.0-demo', 'environment_id': prod_env_id, 'commit_sha': 'abc123def', 'branch': 'main'},
        timeout=5
    )
    print(f"Create Release Status: {r.status_code}")
    if r.status_code == 201:
        release = r.json()
        release_id = release['id']
        print(f"Release ID: {release_id}")
        
        # Upload test results
        results_path = r"C:\Users\mitta\OneDrive\Documents\DEFAUL~1\shopapi_project\results.xml"
        if os.path.exists(results_path):
            with open(results_path, 'rb') as f:
                files = {
                    'junit_xml': ('results.xml', f, 'application/xml'),
                    'test_run_name': (None, 'shopapi-tests'),
                }
                r = requests.post(
                    f'http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/releases/{release_id}/test-runs/',
                    files=files,
                    timeout=30
                )
                print(f"Upload Status: {r.status_code}")
                print(r.text[:500])
        else:
            print(f"Results file not found at: {results_path}")