import re

FILE_PLACEHOLDER = '___FILE_PATH___'

tb = 'File "/home/user/project/tests/test_math.py", line 10'

# Step 1
def protect_file_path(match):
    full_path = match.group(1)
    filename = full_path.split('/')[-1].split('\\')[-1]
    print(f'Match: {full_path} -> filename: {filename}')
    return f'File "{FILE_PLACEHOLDER}{filename}"'

line = re.sub(
    r'File\s+"((?:[A-Za-z]:)?[/\\](?:[\w.-]+[/\\])*([\w.-]+\.py))"',
    protect_file_path,
    tb
)
print('After step 1:', repr(line))

# Step 2
line = re.sub(r'"[^"]*"', '"..."', line)
print('After step 2:', repr(line))

# Step 3
line = line.replace(f'File "{FILE_PLACEHOLDER}', 'File "')
print('After step 3:', repr(line))