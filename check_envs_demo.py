import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}

# Check environments for Demo Project (which has environments)
r = requests.get('http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/environments/', headers=headers, timeout=5)
print(f"Demo Project Environments Status: {r.status_code}")
print(r.text)