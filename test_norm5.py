import re

tb = 'File "/home/user/project/tests/test_math.py", line 10'

# Extract all quoted strings that look like file paths
file_paths = []
def extract_file_paths(match):
    content = match.group(1)
    # Check if it looks like a file path (contains / or \ and ends with .py)
    if ('/' in content or '\\' in content) and content.endswith('.py'):
        filename = content.split('/')[-1].split('\\')[-1]
        file_paths.append(filename)
        return f'__FILE_PATH_{len(file_paths)-1}__'
    return match.group(0)

line = re.sub(r'"([^"]*)"', extract_file_paths, tb)
print('After extract:', repr(line))
print('File paths:', file_paths)

# Now normalize other strings
line = re.sub(r'"[^"]*"', '"..."', line)
print('After string norm:', repr(line))

# Restore file paths
for i, filename in enumerate(file_paths):
    line = line.replace(f'__FILE_PATH_{i}__', filename)
print('After restore:', repr(line))