import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

print("=" * 60)
print("COMPREHENSIVE API VERIFICATION")
print("=" * 60)

# 1. Health check
print("\n1. HEALTH CHECK")
r = requests.get('http://127.0.0.1:8000/api/v1/health/', timeout=5)
print(f"  Status: {r.status_code} - {r.json()}")

# 2. List projects
print("\n2. LIST PROJECTS")
r = requests.get('http://127.0.0.1:8000/api/v1/projects/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"  Status: {r.status_code}")
data = r.json()
for p in data['results']:
    print(f"  - {p['name']} (slug: {p['slug']}) ID: {p['id']}")

# 3. List organizations
print("\n3. LIST ORGANIZATIONS")
r = requests.get('http://127.0.0.1:8000/api/v1/organisations/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"  Status: {r.status_code}")
data = r.json()
for org in data['results']:
    print(f"  - {org['name']} (slug: {org['slug']}) ID: {org['id']}")

# 4. Get environments for ShopAPI project
print("\n4. SHOPAPI PROJECT ENVIRONMENTS")
shopai_id = "99158aa5-a0c3-4ebe-980c-a5d8b154d370"
r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/{shopai_id}/environments/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"  Status: {r.status_code}")
data = r.json()
for env in data.get('results', data):
    print(f"  - {env['name']} (type: {env.get('type', env.get('slug'))}) ID: {env['id']}")

# 5. Create release for ShopAPI
print("\n5. CREATE RELEASE")
prod_env = None
r = requests.get(f'http://127.0.0.1:8000/api/v1/projects/{shopai_id}/environments/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
envs = r.json().get('results', r.json())
for env in envs:
    if env.get('type') == 'PRODUCTION' or env.get('slug') == 'production':
        prod_env = env['id']
        print(f"  Found Production env: {env['name']} ID: {env['id']}")

if prod_env:
    release_data = {
        "version": "shopapi-v1.0.0",
        "environment_id": prod_env,
        "commit_sha": "abc123def",
        "branch": "main"
    }
    r = requests.post(
        f'http://127.0.0.1:8000/api/v1/projects/{shopai_id}/releases/',
        headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII', 'Content-Type': 'application/json'},
        json={'version': 'shopapi-v1.0.0', 'environment_id': prod_env, 'commit_sha': 'abc123def', 'branch': 'main'},
        timeout=5
    )
    print(f"  Create Release Status: {r.status_code}")
    if r.status_code == 201:
        release = r.json()
        release_id = release['id']
        print(f"  Release ID: {release_id}")
        
        # 6. Upload test results
        print("\n6. UPLOAD TEST RESULTS")
        # Use the results.xml from ShopAPI tests
        import os
        results_path = r"C:\Users\mitta\OneDrive\Documents\DEFAUL~1\shopapi_project\results.xml"
        if os.path.exists(results_path):
            with open(results_path, 'rb') as f:
                files = {
                    'junit_xml': ('results.xml', f, 'application/xml'),
                    'test_run_name': (None, 'shopapi-tests'),
                }
                r = requests.post(
                    f'http://127.0.0.1:8000/api/v1/projects/99158aa5-a0c3-4ebe-980c-a5d8b154d370/releases/{release_id}/test-runs/',
                    headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'},
                    files=files,
                    timeout=30
                )
                print(f"  Upload Status: {r.status_code}")
                print(f"  Response: {r.text[:500]}")
        else:
            print(f"  Results file not found at: {results_path}")
else:
    print("  No production environment found!")

# 6. Dashboard check
print("\n7. DASHBOARD OVERVIEW")
r = requests.get('http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/dashboard/overview/', headers={'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}, timeout=5)
print(f"  Status: {r.status_code}")
print(f"  Response: {r.text[:300]}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)