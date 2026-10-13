theforeman.foreman.smart_proxies_sync
======================================

Sync content on Smart Proxies.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

### Required

- `foreman_smart_proxies_sync`: List of Smart Proxies to sync content on. Each entry is a dictionary with the following keys:

| Key | Required | Description |
|-----|----------|-------------|
| `name` | yes | Name of the Smart Proxy |
| `organization` | no | Organization (defaults to `foreman_organization`) |
| `lifecycle_environment` | no | Limit sync to this Lifecycle Environment |
| `content_view` | no | Limit sync to this Content View |
| `product` | no | Product the repository belongs to (required when `repository` is set) |
| `repository` | no | Limit sync to this Repository |
| `skip_metadata_check` | no | Skip metadata check on each repository |

### Optional

- `foreman_smart_proxies_sync_wait`: Whether to wait for the sync tasks to complete. Defaults to `true`.

Example Playbook
----------------

### Sync all content on multiple Smart Proxies

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.smart_proxies_sync
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_smart_proxies_sync:
          - name: capsule1.example.com
          - name: capsule2.example.com
```

### Sync a specific lifecycle environment

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.smart_proxies_sync
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_smart_proxies_sync:
          - name: capsule.example.com
            lifecycle_environment: Production
```

### Sync a specific repository

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.smart_proxies_sync
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_smart_proxies_sync:
          - name: capsule.example.com
            product: "Red Hat Enterprise Linux for x86_64"
            repository: "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
```
