import requests

headers = {'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'}
r = requests.get('http://127.0.0.1:8000/api/v1/projects/a6d06794-58bc-43ca-b5e1-def37f109075/environments/', headers=headers, timeout=5)
print(f"Status: {r.status_code}")
print(r.text)