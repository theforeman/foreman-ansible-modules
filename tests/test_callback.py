import os
import re
import ansible_runner


def run_playbook(tmpdir):
    os.environ['ANSIBLE_STDOUT_CALLBACK'] = "foreman"
    os.environ['ANSIBLE_LOAD_CALLBACK_PLUGINS'] = "1"
    # No connection is actually performed during the test
    os.environ['FOREMAN_URL'] = "http://localhost"
    os.environ['FOREMAN_SSL_CERT'] = "/dev/zero"
    os.environ['FOREMAN_SSL_KEY'] = "/dev/zero"
    os.environ['FOREMAN_DIR_STORE'] = str(tmpdir)
    kwargs = {}
    kwargs['playbook'] = os.path.join(os.getcwd(), 'tests', 'callback', 'three_hosts.yml')
    kwargs['inventory'] = os.path.join(os.getcwd(), 'tests', 'callback', 'three_hosts')
    kwargs['verbosity'] = 4
    return ansible_runner.run(**kwargs)


def test_callback(tmpdir, vcrmode):
    run = run_playbook(tmpdir)
    assert run.rc == 0
    for file in os.listdir(str(tmpdir)):
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
                assert expected_contents, contents
