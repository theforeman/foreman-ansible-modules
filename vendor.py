import fileinput
import os.path

# header lines we want to have, disabling some annoying pylint checks
# and adhering to Ansible standards
header_lines = [
    '# pylint: disable=ansible-format-automatic-specification,raise-missing-from',
    'from __future__ import absolute_import, division, print_function',
    '__metaclass__ = type',
]

# buffer to store lines we might want to adjust/drop
buffer_lines = []

# normal output
output_lines = []

# typing imports
typing_imports = set()

with fileinput.input() as f:
    for line in f:
        if os.path.basename(fileinput.filename()) == '__init__.py':
            fileinput.nextfile()
            continue
        if fileinput.isfirstline():
            output_lines.extend(['', ''])
        line = line.rstrip()

        # empty lines trigger buffer flushes
        if line == '':
            # we got an empty try/except because we dropped all code inbetween
            if len(buffer_lines) >= 2 and buffer_lines[0] == 'try:' and buffer_lines[1].startswith('except'):
                buffer_lines.clear()
            output_lines.extend(buffer_lines)
            buffer_lines.clear()
            if output_lines and output_lines[-1] != '':
                output_lines.append(line)
        # drop apypie imports (we have one file now) and future imports (they are already present in the header)
        elif line.startswith('from apypie') or line.startswith('from __future__'):
            continue
        # drop requests imports, we use a different implementation
        elif line in ['import requests', '    from requests_gssapi import HTTPKerberosAuth  # type: ignore',
                      '        from requests_kerberos import HTTPKerberosAuth  # type: ignore']:
            continue
        elif line == '        HTTPKerberosAuth = None':
            output_lines.append(line.strip())
        # drop blocks that only handle typing imports (fenced by either try or if TYPE_CHECKING)
        elif line in ['try:', 'if TYPE_CHECKING:'] or buffer_lines:
            buffer_lines.append(line)
            if "from typing" in line:
                typing_imports.update([element.strip(',') for element in line.split('#')[0].strip().split(' ')[3:]
                                       if not element.strip(',') == 'TYPE_CHECKING'])
            if (('pass' in line or 'TYPE_CHECKING =' in line or ('from apypie' in line and 'if TYPE_CHECKING:' in buffer_lines)) and
               ('from typing' in buffer_lines[1] or 'from apypie' in buffer_lines[1])):
                buffer_lines.clear()
        elif "from typing" in line:
            typing_imports.update([element.strip(',') for element in line.split('#')[0].strip().split(' ')[3:] if not element.strip(',') == 'TYPE_CHECKING'])
        else:
            # inject a blank line before class or import statements
            if (line.startswith('class ') or line.startswith('import ') or line.startswith('def ')) and not output_lines[-1].startswith('import '):
                output_lines.append('')
            if line.endswith(' or requests.Session()'):
                line = line.replace(' or requests.Session()', '')
            output_lines.append(line)

    # anything left in the buffer? flush it!
    if buffer_lines:
        output_lines.extend(buffer_lines)
        buffer_lines.clear()

typing_lines = ['from typing import {}  # pylint: disable=unused-import  # noqa: F401'.format(', '.join(sorted(typing_imports)))]
print("\n".join(header_lines + typing_lines + output_lines))
