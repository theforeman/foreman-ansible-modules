#!/usr/bin/env python

import sys
import simplejson

message = """WARNING: You are trying to run unfit playbooks in automated testing.
Have a look at: https://github.com/theforeman/foreman-ansible-modules/blob/master/test/README.md
"""
sys.stdout.write(simplejson.dumps({'failed': True, 'stdout': message}))
sys.stdout.write('\n')
