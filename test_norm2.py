import re

# Test the issue
tb = 'File "/home/user/project/tests/test_math.py", line 10'

# Step 1: Normalize strings FIRST
line = re.sub(r'"[^"]*"', '"..."', tb)
print('After string norm:', repr(line))

# Step 2: Try file path regex
result = re.sub(r'File\s+"(?:[A-Za-z]:)?[/\\](?:[\w.-]+[/\\])*([\w.-]+\.py)"', r'File "\1"', line)
print('After file path:', repr(result))