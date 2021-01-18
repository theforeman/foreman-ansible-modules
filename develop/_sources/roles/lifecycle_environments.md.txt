theforeman.foreman.lifecycle_environments
=========================================

This role creates and manages Lifecycle Environments.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

The main data structure for this role is the list of `lifecycle_environments`. Each `lifecycle_environment` requires the following fields:

- `name`: The name of the lifecycle environment.
- `prior`: The name of the previous lifecycle environment to attach to in sequence. For the first lifecycle environment in a new path, set the prior lifecycle environment to Library. The order of definition matters, ensure that the environments are listed in the order the path would exist.

The following fields are optional and will be omitted by default:

- `description`: Description of the lifecycle environment
- `label`: A permanent label for identifying the lifecycle environment to tools such as subscription-manager. This is created by the server if omitted. It can't be changed after the lifecycle environment has been created.

Example Playbooks
-----------------

Create a lifecycle environment path with three environments: Library -> Dev -> Test -> Prod

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.lifecycle_environments
      vars:
        server_url: https://foreman.example.com
        username: "admin"
        password: "changeme"
        organization: "Default Organization"
        lifecycle_environments:
          - name: "Dev"
            prior: "Library"
          - name: "Test"
            prior: "Dev"
          - name: "Prod"
            prior: "Dev"
```

Create two lifecycle environment paths: Library -> Dev -> Test -> Prod and Library -> QA -> Stage -> Prod

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.lifecycle_environments
      vars:
        server_url: https://foreman.example.com
        username: "admin"
        password: "changeme"
        organization: "Default Organization"
        lifecycle_environments:
          - name: "Dev"
            prior: "Library"
          - name: "Test"
            prior: "Dev"
          - name: "Prod"
            prior: "Dev"
          - name: "QA"
            prior: "Library"
          - name: "Stage"
            prior: "QA"
          - name: "Prod"
            prior: "Stage"
```
