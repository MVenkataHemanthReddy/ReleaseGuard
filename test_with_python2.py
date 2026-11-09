import requests

headers = {
    'Authorization': 'Token SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'
}

# Test projects list
response = requests.get(
    'http://127.0.0.1:8000/api/v1/projects/',
    headers=headers
)

print(f"Projects List Status: {response.status_code}")
print(f"Projects List: {response.text}")
print()

# Test project detail
response = requests.get(
    'http://127.0.0.1:8000/api/v1/projects/773599bf-25b7-4e19-abcb-6cd2593ca1e6/',
    headers=headers
)

print(f"Project Detail Status: {response.status_code}")
print(f"Project Detail: {response.text}")