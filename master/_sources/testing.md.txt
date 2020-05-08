# Testing Foreman Ansible Modules

## Overview

Foreman Ansible Modules are tested in different ways:
1. Unit tests
2. Integration tests
3. Ansible Sanity

### Unit tests

We currently only have unit tests for the `foreman_spec` to `argument_spec` translation helpers (see `tests/test_foreman_spec_helper.py`).
All other code is tested by the integration tests.

### Integration tests

Every module is tested using a playbook (`see tests/test_playbooks`) against all supported Ansible versions plus the current `devel` branch of Ansible.
Additionally, the modules which support check mode are tested with the latest Ansible release in check mode.

### Ansible Sanity

Ansible provides [Sanity Tests](https://docs.ansible.com/ansible/latest/dev_guide/testing/sanity/index.html) that ensure the modules are using the current best practices in terms of development and documentantion.
We run these tests with the `devel` branch of Ansible to ensure conformability with the latest guidelines.

## Running tests

### Preparation

All tests require you to have run `make test-setup`. This will install all test dependencies and prepare a configuration file (`tests/test_playbooks/vars/server.yml`).

The configuration file will need updates if you want to run tests against a live Foreman instance (see below).

### Unit tests

To run the unit tests, execute:

```console
$ make test-other
```

### Integration tests

To run all integration tests, execute:

```console
$ make test
```

To run a specific test or a set of tests, execute:

```console
$ make test_global_parameter  # single test
$ make test TEST="-k 'organzation or global_parameter'"  # select tests by expression (see `pytest -h`)
```

By default, tests are run with prerecorded server responses using [VCRpy](https://vcrpy.readthedocs.io/).
When tests or modules are changed, those responses might not match anymore and you'll have to re-record the interaction.

To be able to re-record, you need a running instance of Foreman, probably with Katello (use [forklift](https://github.com/theforeman/forklift) if unsure).
You also need to update `tests/test_playbooks/vars/server.yml` with the URL and credentials of said instance.

To re-record, execute:

```console
$ make record_global_parameter
```

### Ansible Sanity

To run the Ansible Sanity tests, execute:

```console
$ make sanity
```

## Writing tests

The tests in this repository run playbooks that can be found in `tests/test_playbooks`.
To be run, the name of the corresponding playbook must be listed in `tests/test_crud.py`.

The playbooks should be self contained, target the features of a specific module and be able to run against an actual foreman instance.
The structure would usually be something like setup -> run tests -> clean up.

In `tests/test_playbooks/tasks`, preconfigured tasks for individual entities / actions can be found.
They can be reused, to create common dependent resources, as well as to manipulate the entities in the actual test.
If the boolean variable `expected_change` is set, such a task fails if the result does not meet this expectation.

The ansible inventory contains two hosts:

- localhost: This host runs locally without modification it is meant to setup (and teardown) dependent resources, only when (re-)recording.
  It can also be useful to run ad hoc commands or small playbooks during development.
- tests: This host should run the actual tests. It is used to record the vcr-yaml-files, or to run isolated against those files.

In order to run these tests, the API responses of a running Foreman or Katello server must be recorded.
For this last step, `tests/test_playbooks/vars/server.yml` must be configured to point to a running Foreman or Katello server.
Then, `make record_<playbook name>` must be called, and the resulting vcr files (`test_playbook/fixtures/<playbook_name>-*.yml`) must be checked into git.

### Recording/storing apidoc.json for tests

The tests depend on a valid `apidoc.json` being available during execution.
The easiest way to do so is to provide a `<module>.json` in the `tests/fixtures/apidoc` folder.
Most modules can just use a symlink to either `foreman.json` or `katello.json`, depending on whether they need a plain Foreman or Foreman+Katello to function properly.
If you need a setup with different plugins enabled, just get `https://foreman.example.com/apidoc/v2.json` from your install and place it in `tests/fixtures/apidoc`.
