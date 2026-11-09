import re

tb = 'File "/home/user/project/tests/test_math.py", line 10'

# Test the regex
pattern = r'File\s+"(?:[A-Za-z]:)?[/\\](?:[\w.-]+[/\\])*([\w.-]+\.py)"'
result = re.sub(pattern, r'File "\1"', tb)
print('Result:', repr(result))

# Test with single quotes too
tb2 = "File '/home/user/project/tests/test_math.py', line 10"
pattern2 = r"File\s+'(?:[A-Za-z]:)?[/\\](?:[\w.-]+[/\\])*([\w.-]+\.py)'"
result2 = re.sub(pattern2, r"File '\1'", tb2)
print('Result2:', repr(result2))