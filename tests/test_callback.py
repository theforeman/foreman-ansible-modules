import distutils.version
import os
import re
import json

import pytest

from .conftest import run_playbook, get_ansible_version


def run_playbook_callback(tmpdir):
    extra_env = {}
    ansible_version = get_ansible_version()
    if ansible_version is None:
        pytest.skip("Couldn't figure out Ansible version?!")
    if distutils.version.LooseVersion(ansible_version) < distutils.version.LooseVersion('2.11'):
        extra_env['ANSIBLE_CALLBACK_WHITELIST'] = "theforeman.foreman.foreman"
    else:
        extra_env['ANSIBLE_CALLBACKS_ENABLED'] = "theforeman.foreman.foreman"
    extra_env['ANSIBLE_STDOUT_CALLBACK'] = "theforeman.foreman.foreman"
    extra_env['ANSIBLE_LOAD_CALLBACK_PLUGINS'] = "1"
    # No connection is actually performed during the test
    extra_env['FOREMAN_URL'] = "http://localhost"
    extra_env['FOREMAN_SSL_CERT'] = "/dev/zero"
    extra_env['FOREMAN_SSL_KEY'] = "/dev/zero"
    extra_env['FOREMAN_DIR_STORE'] = tmpdir.strpath
    playbook = os.path.join('..', 'callback', 'three_hosts')
    inventory = os.path.join(os.getcwd(), 'tests', 'callback', 'three_hosts')
    return run_playbook(playbook, inventory=inventory, extra_env=extra_env)


def test_callback(tmpdir, vcrmode):
    run = run_playbook_callback(tmpdir)
    assert run.rc == 0
    for real_file in tmpdir.listdir(sort=True):
        contents = real_file.read()
        contents = re.sub(r"\d+-\d+-\d+[ T]\d+:\d+:\d+\.\d+", "2000-01-01 12:00:00.0000", contents)
        contents = re.sub(r"\d+:\d+:\d+\.\d+", "12:00:00.0000", contents)
        fixture_name = real_file.basename
        fixture = os.path.join(os.getcwd(), 'tests', 'fixtures', fixture_name)
        if vcrmode == "record":
            print("Writing: ", str(fixture))
            with open(fixture, 'w') as f:
                f.write(contents)
        else:
            with open(fixture, 'r') as f:
                expected_contents = json.load(f)
                real_contents = json.loads(contents)
                assert expected_contents == real_contents, "Fixture {fixture_name} differs, run with -vvvv to see the diff".format(fixture_name=fixture_name)
