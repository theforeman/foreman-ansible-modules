#!/usr/bin/env python

import os
import re
import sys
import json
try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

FILTER_REQUEST_HEADERS = ['Authorization', 'Cookie']
FILTER_RESPONSE_HEADERS = ['Apipie-Checksum', 'Date', 'ETag', 'Server', 'Set-Cookie', 'Via', 'X-Powered-By', 'X-Request-Id', 'X-Runtime']


def safe_method_matcher(r1, r2):
    assert r1.method not in ['POST', 'PUT', 'PATCH', 'DELETE'], 'Method {0} not allowed in check_mode'.format(r1.method)
    assert r1.method == r2.method


# We need our own json level2 matcher, because, python2 and python3 do not save
# dictionaries in the same order
def body_json_l2_matcher(r1, r2):
    if r1.headers.get('content-type') == r2.headers.get('content-type') == 'application/json':
        if r1.body is None or r2.body is None:
            assert r1.body == r2.body, "{} != {}".format(r1.body, r2.body)
        body1 = json.loads(r1.body.decode('utf8'))
        body2 = json.loads(r2.body.decode('utf8'))
        if 'common_parameter' in body1 and 'common_parameter' in body2:
            if body1['common_parameter'].get('parameter_type') == body2['common_parameter'].get('parameter_type') in ['hash', 'json', 'yaml']:
                body1['common_parameter']['value'] = json.loads(body1['common_parameter'].get('value'))
                body2['common_parameter']['value'] = json.loads(body2['common_parameter'].get('value'))
        assert body1 == body2, "{} != {}".format(body1, body2)
    elif (r1.headers.get('content-type') == r2.headers.get('content-type')
            and r1.headers.get('content-type') in ['multipart/form-data', 'application/x-www-form-urlencoded']):
        if r1.body is None or r2.body is None:
            assert r1.body == r2.body, "{} != {}".format(r1.body, r2.body)
        body1 = sorted(r1.body.replace(b'~', b'%7E').split(b'&'))
        body2 = sorted(r2.body.replace(b'~', b'%7E').split(b'&'))
        assert len(body1) == len(body2), "the body lengths don't match"
        for i, v in enumerate(body1):
            assert body1[i] == body2[i], "body contents at position {} dont't match: '{}' vs '{}'".format(i, body1[i], body2[i])
    else:
        assert r1.body == r2.body, "{} != {}".format(r1.body, r2.body)


def _query_without_search_matcher(r1, r2, path):
    if r1.path == r2.path == path:
        query1 = [q for q in r1.query if q[0] != 'search']
        query2 = [q for q in r2.query if q[0] != 'search']
        assert query1 == query2, "{} != {}".format(query1, query2)
    else:
        vcr.matchers.query(r1, r2)


def snapshot_query_matcher(r1, r2):
    _query_without_search_matcher(r1, r2, '/api/hosts')


def query_matcher_ignore_proxy(r1, r2):
    _query_without_search_matcher(r1, r2, '/api/smart_proxies')


def subscription_manifest_body_matcher(r1, r2):
    if r1.path.endswith('/subscriptions/upload') and r2.path.endswith('/subscriptions/upload'):
        if r1.headers.get('content-type').startswith('multipart/form-data') and r2.headers.get('content-type').startswith('multipart/form-data'):
            r1_copy = vcr.request.Request(r1.method, r1.uri, r1.body, r1.headers)
            r2_copy = vcr.request.Request(r2.method, r2.uri, r2.body, r2.headers)
            # the body is a huge binary blob, which seems to differ on every run, so we just ignore it
            body1 = body2 = {}
            r1_copy.body = json.dumps(body1)
            r2_copy.body = json.dumps(body2)
            return body_json_l2_matcher(r1_copy, r2_copy)
    return body_json_l2_matcher(r1, r2)


def host_body_matcher(r1, r2):
    if r1.headers.get('content-type') == r2.headers.get('content-type') == 'application/json':
        if r1.path == r2.path == '/api/v2/hostgroups':
            r1_copy = vcr.request.Request(r1.method, r1.uri, r1.body, r1.headers)
            r2_copy = vcr.request.Request(r2.method, r2.uri, r2.body, r2.headers)
            body1 = json.loads(r1_copy.body.decode('utf8'))
            body2 = json.loads(r2_copy.body.decode('utf8'))
            body1['search'] = 'name="test_group"'
            body2['search'] = 'name="test_group"'
            r1_copy.body = json.dumps(body1)
            r2_copy.body = json.dumps(body2)
            return body_json_l2_matcher(r1_copy, r2_copy)
    return body_json_l2_matcher(r1, r2)


def job_invocation_body_matcher(r1, r2):
    if r1.path == r2.path == '/api/job_invocations':
        r1_copy = vcr.request.Request(r1.method, r1.uri, r1.body, r1.headers)
        r2_copy = vcr.request.Request(r2.method, r2.uri, r2.body, r2.headers)
        body1 = json.loads(r1_copy.body.decode('utf8'))
        body2 = json.loads(r2_copy.body.decode('utf8'))
        if 'search_query' in body1['job_invocation']:
            body1['job_invocation']['search_query'] = body2['job_invocation']['search_query']
        r1_copy.body = json.dumps(body1)
        return body_json_l2_matcher(r1_copy, r2_copy)
    return body_json_l2_matcher(r1, r2)


def filter_response(response):
    for header in FILTER_RESPONSE_HEADERS:
        # headers should be case insensitive, but for some reason they weren't for me
        response['headers'].pop(header.lower(), None)
        response['headers'].pop(header, None)
    return response


def filter_request_uri(request):
    uri = urlparse(request.uri)
    if uri.hostname != 'subscription.rhsm.redhat.com':
        uri = uri._replace(netloc="foreman.example.org")
    if uri.hostname == 'subscription.rhsm.redhat.com' and re.match('/subscription/users/[^/]+/owners', uri.path):
        uri = uri._replace(path='/subscription/users/john-smith/owners')
    request.uri = urlunparse(uri)
    return request


def filter_request_manifest(request):
    if request.method == 'POST' and request.path.endswith('/subscriptions/upload'):
        request.body = 'FAKE_MANIFEST'
    return request


def filter_request(request):
    request = filter_request_uri(request)
    request = filter_request_manifest(request)
    return request


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
    import vcr
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

    method_matcher = 'method'
    if test_params['check_mode']:
        fam_vcr.register_matcher('safe_method_matcher', safe_method_matcher)
        method_matcher = 'safe_method_matcher'

    query_matcher = 'query'
    if test_params['test_name'] in ['domain', 'hostgroup', 'katello_hostgroup', 'luna_hostgroup', 'realm', 'subnet', 'puppetclasses_import']:
        fam_vcr.register_matcher('query_ignore_proxy', query_matcher_ignore_proxy)
        query_matcher = 'query_ignore_proxy'
    elif test_params['test_name'] in ['snapshot', 'snapshot_info']:
        fam_vcr.register_matcher('snapshot_query', snapshot_query_matcher)
        query_matcher = 'snapshot_query'

    fam_vcr.register_matcher('body_json_l2', body_json_l2_matcher)

    body_matcher = 'body_json_l2'
    if test_params['test_name'] == 'host':
        fam_vcr.register_matcher('host_body', host_body_matcher)
        body_matcher = 'host_body'
    elif test_params['test_name'] in ['subscription_manifest', 'manifest_role', 'content_rhel_role']:
        fam_vcr.register_matcher('subscription_manifest_body', subscription_manifest_body_matcher)
        body_matcher = 'subscription_manifest_body'
    elif test_params['test_name'] == 'job_invocation':
        fam_vcr.register_matcher('job_invocation_body', job_invocation_body_matcher)
        body_matcher = 'job_invocation_body'

    with fam_vcr.use_cassette(cassette_file,
                              record_mode=test_params['record_mode'],
                              match_on=[method_matcher, 'path', query_matcher, body_matcher],
                              filter_headers=FILTER_REQUEST_HEADERS,
                              before_record_request=filter_request,
                              before_record_response=filter_response,
                              decode_compressed_response=True,
                              ):
        with open(sys.argv[0]) as f:
            code = compile(f.read(), sys.argv[0], 'exec')
            exec(code)
