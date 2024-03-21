theforeman.foreman.your_new_role
================================

This section should contain a basic explanation of what the role does and why the user might use it.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

Role specific variables should be documented as below:

`foreman_variable_name`: Documentation of variable behavior and default if any. Ideally, keep it brief but do not assume that the user is an expert in the corresponding Katello/Foreman feature.

Example Playbooks
-----------------

Include a basic example playbook here, and explain what the playbook does when it is run.

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.your_new_role
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "ACME"
        foreman_variable_name: "some_value"
```

It is appreciated if you can include a few more examples here, along with an explanation of how each behaves. Many users will go straight to the examples, so having a few examples showing key differences in how the role can be used will be very helpful.
