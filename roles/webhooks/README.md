theforeman.foreman.webhooks
===================================

This role creates and manages webhooks

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

- `foreman_webhooks`: List of webhooks to manage that are each represented as a dictionary. See module documentation for a list of available options for each host collection.
  A variety of examples are demonstrated in the data structure below:

```yaml
foreman_webooks:
  - name: Example webhook
    event: host_created.event.foreman
    target_url: https://example.org/api/
    http_method: POST
    verify_ssl: true
    enabled: true
    webhook_username: my_webhook_user
    webhook_password: my_vaul_encrypted_webhook_user_password
```

Example Playbooks
-----------------

This example creates a webhook

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.webhooks
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_webhooks:
          - name: Example webhook
            event: host_created.event.foreman
            target_url: https://example.org/api/
            http_method: POST
            verify_ssl: true
            enabled: true
            webhook_username: my_webhook_user
            webhook_password: my_vaul_encrypted_webhook_user_password
```
