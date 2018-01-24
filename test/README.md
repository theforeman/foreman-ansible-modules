Guidedeline to writing tests
===

The tests in this repository run playbooks that can be found in `test/test_playbooks`.
To be run, the name of the corresponding playbook must be listed in `test/test_crud.py`.

The playbooks should be self contained, target the features of a specific module and be able to run against an actual foreman instance.
The structure would usually be something like setup -> run tests -> clean up.

In `test/test_playbooks/tasks`, preconfigured tasks for individual entities / actions can be found.
They can be reused, to create common dependent resources, as well as to manipulate the entities in the actual test.
If the boolean variable `expected_change` is set, such a task fails if the result does not meet this expectation.

The ansible inventory contains two hosts:

- fixtures: This host runs locally without modification it is meant to setup (and teardown) dependent resources, only when (re-)recording.
- tests: This host should run the actual tests. It is used to record the vcr-yaml-files, or to run isolated against those files.

In order to run these tests, the API responses of a running Foreman or Katello server must be recorded.
For this last step, `test/test_playbooks/server_vars.yml` must be configured to point to a running Foreman or Katello server.
Then, `make record_<playbook name>` must be called, and the resulting vcr files (`test_playbook/fixtures/<playbook_name>-*.yml`) must be checked into git.
