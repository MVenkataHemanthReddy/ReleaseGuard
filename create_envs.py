import requests

headers = {'Content-Type': 'application/json'}

# Create environments for ShopAPI project
project_id = "a6d06794-58bc-43ca-b5e1-def37f109075"

environments = [
    {"name": "Production", "type": "PRODUCTION", "is_default": False},
    {"name": "Staging", "type": "STAGING", "is_default": False},
    {"name": "Development", "type": "DEVELOPMENT", "is_default": True}
]

for env in environments:
    r = requests.post(
        f'http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/environments/',
        json=env,
        timeout=5
    )
    print(f"Create {env['name']} Status: {r.status_code}")
    print(r.text)