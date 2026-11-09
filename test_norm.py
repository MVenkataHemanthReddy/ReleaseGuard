import sys
sys.path.insert(0, '.')
from apps.releases.parsers import normalize_traceback

tb = 'File "/home/user/project/tests/test_math.py", line 10'
result = normalize_traceback(tb)
print('Result:', repr(result))