theforeman.foreman.manifest
===========================

Upload Subscription Manifest

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

The main data structure for this role is the list of `foreman_manifest`. Each `manifest` requires the following field:

- `path`: Path to subscription Manifest file on Ansible target host. When using `download`, it is first downloaded to this location from the Red Hat Customer Portal before being uploaded to the Foreman server.

Additionally the following parameters can be used.

- `organization`: The where the manifest should be uploaded.
- `download`: Whether to first download the Manifest from the Red Hat Customer Portal. Defaults to `False`.
- `uuid`: UUID of the Manifest to download, corresponding to a [Subscription Allocation](https://access.redhat.com/management/subscription_allocations) defined on your Red Hat account. Required when `download` is `True`.
- `username`: Your username for the Red Hat Customer Portal. Required when `download` is `true`.
- `password`: Your password for the Red Hat Customer Portal. Required when `download` is `true`.
- `state`: Define if manifest is present or absent.

Define Manifest with multiple variables
---------------------------------------

- `foreman_manifest_path`
- `foreman_manifest_download`
- `foreman_rhsm_username`
- `foreman_rhsm_password`
- `foreman_manifest_uuid`

Example Playbooks
-----------------

Use a Subscription Manifest which has already been downloaded on localhost at `~/manifest.zip`:

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.manifest
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_manifest:
          - path: "~/manifest.zip"
```

Download the Subscription Manifest from the Red Hat Customer Portal to localhost before uploading to Foreman server:

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.manifest
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_manifest:
          - path: "~/manifest.zip"
            download: true
            rhsm_username: "happycustomer"
            rhsm_password: "$ecur3p4$$w0rd"
            uuid: "01234567-89ab-cdef-0123-456789abcdef"
```

Download the Subscription Manifest from the Red Hat Customer Portal, via a proxy, to localhost before uploading to Foreman server:

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.manifest
      environment:
        https_proxy: "http://proxy.example.com:3128"
        no_proxy: "foreman.example.com"
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_manifest:
          - path: "~/manifest.zip"
          - organization: "Explicit Organization"
          - download: true
          - rhsm_username: "happycustomer"
          - rhsm_password: "$ecur3p4$$w0rd"
          - uuid: "01234567-89ab-cdef-0123-456789abcdef"
```
