import requests

headers = {'Authorization': 'Token E2JdUHIZPD46CKwtFDcPXhgXkuvs0r94jmDGSOgGsLw'}

# Test the token by getting project info
r = requests.get('http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/', headers={'Authorization': 'Token E2JdUHIZPD46CKwtFDcPXhgXkuvs0r94jmDGSOgGsLw'}, timeout=5)
print(f"Project Status: {r.status_code}")
print(r.text)

# Test creating a release
r = requests.post(
    'http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/releases/',
    headers={'Authorization': 'Token E2JdUHIZPD46CKwtFDcPXhgXkuvs0r94jmDGSOgGsLw', 'Content-Type': 'application/json'},
    json={
        'version': 'shopapi-v1.0.0',
        'environment': 'Production',
        'commit_sha': 'abc123def',
        'branch': 'main',
        'workflow_run_id': 'shopapi-run-123'
    },
    timeout=5
)
print(f"Create Release Status: {r.status_code}")
print(r.text)