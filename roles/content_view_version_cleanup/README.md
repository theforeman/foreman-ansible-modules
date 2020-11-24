theforeman.foreman.content_view_version_cleanup
===============================================

Clean up unused Content View Versions.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

### Required

- `content_view_version_cleanup_keep`: How many unused versions to keep.

### Optional

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
