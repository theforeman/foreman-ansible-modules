theforeman.foreman.manifest
===========================

Upload Subscription Manifest

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

- `manifest_path`: Path to subscription Manifest file on Ansible target host. When using `manifest_download`, it is first downloaded to this location from the Red Hat Customer Portal before being uploaded to the Foreman server.
- `manifest_download`: Whether to first download the Manifest from the Red Hat Customer Portal. Defaults to `False`.
- `manifest_uuid`: UUID of the Manifest to download, corresponding to a [Subscription Allocation](https://access.redhat.com/management/subscription_allocations) defined on your Red Hat account. Required when `manifest_download` is `True`.
- `rhsm_username`: Your username for the Red Hat Customer Portal. Required when `manifest_download` is `True`.
- `rhsm_password`: Your password for the Red Hat Customer Portal. Required when `manifest_download` is `True`.

Example Playbooks
-----------------

Use a Subscription Manifest which has already been downloaded on localhost at `~/manifest.zip`:

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.manifest
      vars:
        server_url: https://foreman.example.com
        username: "admin"
        password: "changeme"
        organization: "Default Organization"
        manifest_path: "~/manifest.zip"
```

Download the Subscription Manifest from the Red Hat Customer Portal to localhost before uploading to Foreman server:

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.manifest
      vars:
        server_url: https://foreman.example.com
        username: "admin"
        password: "changeme"
        organization: "Default Organization"
        manifest_path: "~/manifest.zip"
        manifest_download: True
        rhsm_username: "happycustomer"
        rhsm_password: "$ecur3p4$$w0rd"
        manifest_uuid: "01234567-89ab-cdef-0123-456789abcdef"
```
