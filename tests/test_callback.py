import os
import re

from .conftest import run_playbook


def run_playbook_callback(tmpdir):
    extra_env = {}
    extra_env['ANSIBLE_STDOUT_CALLBACK'] = "theforeman.foreman.foreman"
    extra_env['ANSIBLE_CALLBACK_WHITELIST'] = "theforeman.foreman.foreman"
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
    for file in os.listdir(tmpdir.strpath):
        with open(os.path.join(tmpdir, file), 'r') as f:
            contents = f.read()
            contents = re.sub(r"\d+-\d+-\d+[ T]\d+:\d+:\d+\.\d+", "2000-01-01 12:00:00.0000", contents)
            contents = re.sub(r"\d+:\d+:\d+\.\d+", "12:00:00.0000", contents)
        fixture = os.path.join(os.getcwd(), 'tests', 'fixtures', file)
        if vcrmode == "record":
            print("Writing: ", str(fixture))
            with open(fixture, 'w') as f:
                f.write(contents)
        else:
            with open(fixture, 'r') as f:
                expected_contents = f.read()
                assert expected_contents == contents
