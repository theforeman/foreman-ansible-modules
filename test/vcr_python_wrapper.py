#!/usr/bin/env python

import os
import sys
import vcr
import json
import re


VCR_PARAMS_FILE = os.environ.get('FAM_TEST_VCR_PARAMS_FILE')

# Remove the name of the wrapper from argv
# (to make it look like the module had been called directly)
sys.argv.pop(0)

if VCR_PARAMS_FILE is None:
    # Run the program as if nothing had happened
    with open(sys.argv[0]) as f:
        code = compile(f.read(), sys.argv[0], 'exec')
        exec(code)
else:
    # Run the program wrapped within vcr cassette recorder
    # Load recording parameters from file
    with open(VCR_PARAMS_FILE, 'r') as params_file:
        test_params = json.load(params_file)
    cassette_file = 'fixtures/{}-{}.yml'.format(test_params['test_name'], test_params['serial'])
    # Increase serial and dump back to file
    test_params['serial'] += 1
    with open(VCR_PARAMS_FILE, 'w') as params_file:
        json.dump(test_params, params_file)

    # Call the original python script with vcr-cassette in place
    fam_vcr = vcr.VCR()
    with fam_vcr.use_cassette(cassette_file,
                              record_mode=test_params['record_mode'],
                              match_on=['method', 'scheme', 'port', 'path', 'query'],
                              filter_headers=['Authorization'],
                              ):
        with open(sys.argv[0]) as f:
            code = compile(f.read(), sys.argv[0], 'exec')
            exec(code)
