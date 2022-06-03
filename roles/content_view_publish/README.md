theforeman.foreman.content_view_publish
=======================================

Publish a list of Content Views.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

### Required

- `foreman_content_views`: List of content views to publish

### Optional

- `foreman_lifecycle_environments`: List of lifecycle environments to promote new versions to.

Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.content_view
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_content_views:
          - RHEL 7 View
          - RHEL 8 View
        foreman_lifecycle_environments:
          - Testing
          - Development
```
