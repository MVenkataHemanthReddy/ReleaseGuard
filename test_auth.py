import requests

headers = {
    'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'
}

try:
    r = requests.get('http://127.0.0.1:8000/api/v1/projects/', headers=headers, timeout=5)
    print(f'Status: {r.status_code}')
    print(r.text[:500])
except Exception as e:
    print(f'Error: {e}')