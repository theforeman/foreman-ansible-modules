#!/usr/bin/env python

import os
import sys
import vcr
import json
import re


# We need our own json level2 matcher, because, python2 and python3 do not save
# dictionaries in the same order
def body_json_l2_matcher(r1, r2):
    if r1.headers.get('content-type') == 'application/json' and r2.headers.get('content-type') == 'application/json':
        if r1.body is None or r2.body is None:
            return r1.body == r2.body
        body1 = json.loads(r1.body.decode('utf8'))
        body2 = json.loads(r2.body.decode('utf8'))
        if 'search' in body1:
            body1['search'] = ','.join(sorted(re.findall(r'([^=,]*="(?:[^"]|\\")*")', body1['search'])))
        if 'search' in body2:
            body2['search'] = ','.join(sorted(re.findall(r'([^=,]*="(?:[^"]|\\")*")', body2['search'])))
        return body1 == body2
    elif r1.headers.get('content-type') == 'multipart/form-data' and r2.headers.get('content-type') == 'multipart/form-data':
        if r1.body is None or r2.body is None:
            return r1.body == r2.body
        body1 = sorted(r1.body.replace(b'~', b'%7E').split(b'&'))
        body2 = sorted(r2.body.replace(b'~', b'%7E').split(b'&'))
        if len(body1) != len(body2):
            return False
        for i, v in enumerate(body1):
            if body1[i] != body2[i]:
                return False
        return True
    else:
        return r1.body == r2.body


def domain_query_matcher(r1, r2):
    if r1.path == '/api/smart_proxies' and r2.path == '/api/smart_proxies':
        return [q for q in r1.query if q[0] != 'search'] == [q for q in r2.query if q[0] != 'search']
    return r1.query == r2.query


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
    fam_vcr.register_matcher('body_json_l2', body_json_l2_matcher)

    query_matcher = 'query'
    if test_params['test_name'] == 'domain':
        fam_vcr.register_matcher('domain_query', domain_query_matcher)
        query_matcher = 'domain_query'

    with fam_vcr.use_cassette(cassette_file,
                              record_mode=test_params['record_mode'],
                              match_on=['method', 'scheme', 'port', 'path', query_matcher, 'body_json_l2'],
                              filter_headers=['Authorization'],
                              ):
        with open(sys.argv[0]) as f:
            code = compile(f.read(), sys.argv[0], 'exec')
            exec(code)
