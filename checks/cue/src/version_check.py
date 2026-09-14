
import sys
import os
import subprocess
import re
import json


def version(s):
    # dotted numeric version -> tuple of ints; trailing zeros dropped so that 4.4.0 == 4.4
    parts = [int(x) for x in s.split('.')]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


tool = json.loads(sys.argv[1])

try:
    ver_opt = tool['veropt']
except:
    ver_opt = '--version'

try:
    options = tool['options']
except:
    options = ""

cmd = f"{tool['exe']} {ver_opt} {options}"
out = subprocess.run([cmd],shell=True, stdout=subprocess.PIPE)
out = out.stdout.decode('utf-8')

try:
    regular = tool['re']
except:
    regular = r'(?:(\d+\.(?:\d+\.)*\d+))'
match = re.findall(regular, out)

print(version(tool['minver']) <= version(match[0]))  # True
