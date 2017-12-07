#!/usr/bin/env python

import os
import sys
import vcr
import json

VCR_PARAMS_FILE = os.environ['FAM_TEST_VCR_PARAMS_FILE']

# Remove the name of the wrapper from argv
# (to make it look like the module had been called directly)
sys.argv.pop(0)

# Load recording parameters from file
with open(VCR_PARAMS_FILE, 'r') as params_file:
    test_params = json.load(params_file)
cassette_file = 'fixtures/{}-{}.yml'.format(test_params['test_name'], test_params['serial'])
# Increase serial and dump back to file
test_params['serial'] += 1
with open(VCR_PARAMS_FILE, 'w') as params_file:
    json.dump(test_params, params_file)

# Call the original python script with vcr-cassette in place
with vcr.use_cassette(cassette_file,
                      record_mode=test_params['record_mode'],
                      match_on=['method', 'scheme', 'port', 'path', 'query'],
                      filter_headers=['Authorization'],
                      ):
    with open(sys.argv[0]) as f:
        code = compile(f.read(), sys.argv[0], 'exec')
        exec(code)
