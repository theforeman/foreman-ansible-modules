# Foreman Ansible Modules - Role Developer Documentation

Roles are an active area of development for this collection and community member contributions are highly encouraged! This file contains documentation for those who want to contribute Ansible Roles to the Collection. For general role development documentation, particularly if you are new to role development, see the [Ansible Galaxy Documentation](https://galaxy.ansible.com/docs/contributing/creating_role.html) on role development first.

## Documentation

Documentation is important. Each role needs to be well documented so that users can figure out how to use it. We provide a standard [Template](https://github.com/theforeman/foreman-ansible-modules/tree/develop/docs/development/ROLE_README_TEMPLATE.md) for the role documentation, which you can copy from `docs/development/ROLE_README_TEMPLATE.md` to `roles/${name_of_role}/README.md` before editing.

If your role supports any variable, then that variable needs to be documented with an explanation of how it affects the role behavior, what is the default value if any, and when is the variable required.

When writing documentation, it helps to put yourself in the shoes of an user who is new to this software and not make too many assumptions about what they should already know. In this regard, it is expected to include several example playbooks along with an explanation of how each is expected to behave.

Please have a look at existing role `README.me` files in the collection to get an idea of how this should look. Of course, if you see any room for improvement in the existing role documentation, please open a PR for it!

## Testing

Testing Roles is also important. Writing quality tests ensures that future changes to the role, or to the underlying modules, do not break functionality in unintended ways. Before getting started it is helpful to first read the developer documentation on [Testing](https://theforeman.github.io/foreman-ansible-modules/develop/testing.html#) for this collection.

Every role needs to have an integration test in the form of a playbook `tests/test_playbooks/${name_of_role}_role.yml`. You can look at the test playbook for an existing role in the collection to see an example of what this looks like.

CI does not test against a live instance; rather you are expected to record test fixtures from your own live instance and include them with the role. You can use [Forklift](https://github.com/theforeman/forklift) to quickly get up and running with a live virtual instance for testing. In some cases you may want to use a test instance with greater hardware resources available, if the role performs certain hardware intensive actions such as syncing large repositories.

You will need to configure your development environment to point to your live test instance by editing the file `tests/test_playbooks/vars/server.yml` (first copy it from the example `tests/test_playbooks/vars/server.yml.example` if necessary).

It is recommended to record the test fixtures against an uncofigured instance, so that the recorded fixtures will capture truly creating all necessary resources. You can ensure that your test instance is in this state before recording the fixtures by running `$ foreman-installer --reset-data`. This will drop and re-seed all databases and clear all synced content - do NOT run this on your production instance as you will lose ALL data!

Recording and running the tests requires an API doc fixture `tests/fixtures/apidoc/${name_of_role}_role.json`. This should typically just be a soft link to `katello.json` in the same directory. This fixture should be included with your pull request.

Finally, to record the fixtures, use `make record_${name_of_role}_role`. This will run your test playbook against your test instance, and record all API requests and responses. When it is finished running, add and commit the fixtures at `tests/test_playbooks/fixtures/${name_of_role}_role-*.yml`.

## Changelogs

Don't forget to add a changelog fragment about your role! This is simple to do, just have a look at any previous example such as [this one](https://github.com/theforeman/foreman-ansible-modules/blob/2045c5edef5792d3235eb5c2b234ef08e3fa96b3/changelogs/fragments/1097-content-rhel-role.yml) to see how it should look.
