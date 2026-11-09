import requests

headers = {
    'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'
}

try:
    # Test dashboard overview
    r = requests.get('http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/dashboard/overview/', headers=headers, timeout=5)
    print(f'Dashboard Status: {r.status_code}')
    print(r.text[:1000])
except Exception as e:
    print(f'Error: {e}')