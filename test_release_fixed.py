import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'}

# Test release creation with all required fields
release_data = {
    "version": "v1.0.0-demo",
    "environment": "Production",  # Use name/slug, not ID
    "commit_sha": "abc123def",
    "branch": "main",
    "workflow_run_id": "demo-run-123"  # Required field!
}

r = requests.post(
    'http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/releases/',
    headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'},
    json={
        'version': 'v1.0.0-demo',
        'environment': 'Production',
        'commit_sha': 'abc123def',
        'branch': 'main',
        'workflow_run_id': 'demo-run-123'
    },
    timeout=5
)

print(f"Create Release Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 201:
    release = r.json()
    release_id = release['id']
    print(f"Release ID: {release_id}")
    
    # Upload test results
    import os
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