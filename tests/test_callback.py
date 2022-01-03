import distutils.version
import os
import re
import json

import pytest

from .conftest import run_playbook, get_ansible_version


def run_playbook_callback(tmpdir, report_type):
    extra_env = {}
    ansible_version = get_ansible_version()
    if ansible_version is None:
        pytest.skip("Couldn't figure out Ansible version?!")
    if distutils.version.LooseVersion(ansible_version) < distutils.version.LooseVersion('2.11'):
        extra_env['ANSIBLE_CALLBACK_WHITELIST'] = "theforeman.foreman.foreman"
        extra_env['ANSIBLE_COMMAND_WARNINGS'] = "0"
    else:
        extra_env['ANSIBLE_CALLBACKS_ENABLED'] = "theforeman.foreman.foreman"
    extra_env['ANSIBLE_STDOUT_CALLBACK'] = "theforeman.foreman.foreman"
    extra_env['ANSIBLE_LOAD_CALLBACK_PLUGINS'] = "1"
    # No connection is actually performed during the test
    extra_env['FOREMAN_REPORT_TYPE'] = report_type
    extra_env['FOREMAN_URL'] = "http://localhost"
    if report_type == "proxy":
        extra_env['FOREMAN_PROXY_URL'] = "http://localhost"
    extra_env['FOREMAN_SSL_CERT'] = "/dev/zero"
    extra_env['FOREMAN_SSL_KEY'] = "/dev/zero"
    extra_env['FOREMAN_DIR_STORE'] = tmpdir.strpath
    playbook = os.path.join('..', 'callback', 'three_hosts')
    inventory = os.path.join(os.getcwd(), 'tests', 'callback', 'three_hosts')
    return run_playbook(playbook, inventory=inventory, extra_env=extra_env)


def drop_incompatible_items(d):
    """
    Recursively drop report items that vary on invocations
    and versions and cannot be reasonably fixed
    """
    dd = {}
    for k, v in d.items():
        if isinstance(v, dict):
            dd[k] = drop_incompatible_items(v)
        elif isinstance(v, (list, set, tuple)):
            dd[k] = type(v)(drop_incompatible_items(vv) if isinstance(vv, dict) else vv
                            for vv in v)
        elif k not in ['msg', 'start', 'end', 'delta', 'uuid', 'timeout']:
            dd[k] = v
    return dd


def run_callback(tmpdir, report_type, vcrmode):
    run = run_playbook_callback(tmpdir, report_type)
    assert run.rc == 0
    assert len(tmpdir.listdir()) > 0, "Directory with results is empty"
    for real_file in tmpdir.listdir(sort=True):
        contents = real_file.read()
        contents = re.sub(r"\d+-\d+-\d+ \d+:\d+:\d+\+\d+:\d+", "2000-01-01 12:00:00+00:00", contents)
        contents = re.sub(r"\d+-\d+-\d+[ T]\d+:\d+:\d+\.\d+", "2000-01-01 12:00:00.0000", contents)
        contents = re.sub(r"\d+:\d+:\d+\.\d+", "12:00:00.0000", contents)
        if report_type == "foreman":
            # drop_incompatible_items cannot be used for the legacy format
            contents = re.sub(r", \\\"msg\\\": \\\"\\\"", "", contents)
        real_contents = json.loads(contents)
        if report_type == "foreman":
            real_contents['config_report']['metrics']['time']['total'] = 1
        else:
            real_contents['metrics']['time']['total'] = 1
            real_contents = drop_incompatible_items(real_contents)
        fixture_name = real_file.basename
        fixture = os.path.join(os.getcwd(), 'tests', 'fixtures', 'callback', 'dir_store', report_type, fixture_name)
        if vcrmode == "record":
            print("Writing: ", str(fixture))
            with open(fixture, 'w') as f:
                json.dump(real_contents, f, indent=2, sort_keys=True)
        else:
            with open(fixture, 'r') as f:
                expected_contents = json.load(f)
                expected_contents = drop_incompatible_items(expected_contents)
                real_contents = drop_incompatible_items(real_contents)
                assert expected_contents == real_contents, "Fixture {fixture_name} differs, run with -vvvv to see the diff".format(fixture_name=fixture_name)


def test_callback_foreman(tmpdir, vcrmode):
    run_callback(tmpdir, "foreman", vcrmode)


def test_callback_proxy(tmpdir, vcrmode):
    run_callback(tmpdir, "proxy", vcrmode)
