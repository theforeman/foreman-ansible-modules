#!/usr/bin/env python3

import sys

role_examples = sys.argv[1]
role_rst = sys.argv[2]

try:
    with open(role_examples) as examples_file:
        examples_lines = examples_file.readlines()
except:
    sys.exit(0)

try:
    with open(role_rst) as rst_file:
        rst_lines = rst_file.readlines()
except:
    sys.exit(0)

examples_header = ['.. Examples\n\n', 'Examples\n', '^^^^^^^^\n', '\n']
examples_footer = ['\n']

with open(role_rst, 'w') as rst_file:
    for line in rst_lines:
        if line.strip() == '.. Seealso':
            rst_file.writelines(examples_header)
            rst_file.writelines(examples_lines)
            rst_file.writelines(examples_footer)
        rst_file.write(line)
