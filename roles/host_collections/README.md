theforeman.foreman.host_collections
===================================

This role creates and manages Host collections

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

- `foreman_host_collections`: List of host collections to manage that are each represented as a dictionary. See module documentation for a list of available options for each host collection.
  A variety of examples are demonstrated in the data structure below:

```yaml
foreman_host_collections:
  - name: collection_a
    description: "host collection a"
    organization: ACME
  - name: collection_b
    description: "host collection b"
    organization: ACME
```

Example Playbooks
-----------------

This example creates several host collections.

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.host_collections
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_host_collections:
          - name: collection_a
            description: "host collection a"
            organization: ACME
          - name: collection_b
            description: "host collection b"
            organization: ACME
```
