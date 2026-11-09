import requests

# First, login as admin to get session
session = requests.Session()
login_data = {"username": "admin@example.com", "password": "admin123"}
r = requests.post('http://127.0.0.1:8000/api-auth/login/', data=login_data, timeout=5)
print(f"Login Status: {r.status_code}")

# Create ShopAPI project
project_data = {
    "name": "ShopAPI Demo",
    "slug": "shopapi-demo-v4",
    "description": "E-commerce demo with 6 regressions",
    "organisation": "f26f2c3c-f054-4341-8ccb-a8e2a926a2e6"
}
r = requests.post('http://127.0.0.1:8000/api/v1/projects/', json=project_data, timeout=5)
print(f"Create Project Status: {r.status_code}")
project = r.json()
project_id = project['id']
print(f"Project ID: {project_id}")

# Create token for this project
token_data = {"name": "ShopAPI CI Token"}
r = requests.post(f'http://127.0.0.1:8000/api/v1/projects/{project_id}/tokens/', json={"name": "ShopAPI CI Token"}, timeout=5)
print(f"Create Token Status: {r.status_code}")
token_data = r.json()
print(f"Token: {token_data}")

# Get environments
r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/{project_id}/environments/')
print(f"Environments: {r.status_code}")
envs = r.json()
print(r.text)

# Find production environment
prod_env = None
for env in envs.get('results', envs):
    if env.get('type') == 'PRODUCTION' or 'production' in env.get('name', '').lower():
        prod_env = env['id']
        print(f"Found production env: {env['name']} ({prod_env})")

# Create release
if prod_env:
    release_data = {
        "version": "shopapi-v1.0.0",
        "environment_id": prod_env,
        "commit_sha": "abc123def",
        "branch": "main"
    }
    r = requests.post(f'http://127.0.0.1:8000/api/v1/projects/{project_id}/releases/', json=release_data)
    print(f"Create Release Status: {r.status_code}")
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
                f'http://127.0.0.1:8000/api/v1/projects/{project_id}/releases/{release_id}/test-runs/',
                files=files,
                timeout=30
            )
            print(f"Upload Status: {r.status_code}")
            print(r.text[:500])
    else:
        print(f"Results file not found at: {results_path}")