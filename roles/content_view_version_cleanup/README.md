theforeman.foreman.content_view_version_cleanup
===============================================

Clean up unused Content View Versions.

Requirements
------------

- `jmespath` Python library

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

- `content_view_version_cleanup_keep`: How many versions to keep uncleaned (default: 5).
- `content_view_version_cleanup_search`: Limit the cleaned content views using a search string (example: `name ~ SOE`).

Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.content_view_version_cleanup
      vars:
        server_url: https://foreman.example.com
        username: "admin"
        password: "changeme"
        organization: "Default Organization"
        content_view_version_cleanup_keep: 10
```
