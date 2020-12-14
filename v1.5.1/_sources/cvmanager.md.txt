# Migrating from `cvmanager` to Foreman Ansible Modules

[cvmanager](https://github.com/RedHatSatellite/katello-cvmanager) is a tool to automate Content View management workflows. It hasn't been updated in a long time and users are encouraged to migrate to Ansible and the Foreman Ansible Modules.

This document documents how the various workflows can be translated into Ansible playbooks.

Please note that `cvmanager` configuration refers to Content Views by their labels, while Ansible uses the names of the Content Views for that.

## Cleanup of old Content Views

To ease cleanup of old Content Views, we ship the `content_view_version_cleanup` role which will identify unused Content View Versions and remove them, much like `cvmanager` did:

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

## Automated Updates

When `cvmanager` was initially written, Composite Content Views did not support setting individual components to `latest` and thus this feature was implemented inside `cvmanager`.
As Composite Content Views gained `latest` support since then, the "Automated Updates" feature of `cvmanager` is not really needed anymore and users are encouraged to configure their Composite Content Views accordingly.

If, for example, the old `cvmanager` configuration contained the following entries:

```yaml
:ccv:
  ccv-RHEL7-automated:
    cv-RHEL7: 23.0
    cv-tools: latest
```

You can achieve the same using the `content_view` module:

```yaml
- name: "Create ccv-RHEL7-automated Composite Content View"
  theforeman.foreman.content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    name: "ccv-RHEL7-automated"
    composite: true
    components:
      - content_view: cv-RHEL7
        content_view_version: 23.0
      - content_view: cv-tools
        latest: true
```

Configurations that also used the `:cv` entry, which resulted in *all* Composite Content Views that contained entries from `:cv` being updated,
will need to be migrated to a more declarative approach as seen above.

Using the `latest` feature in Composite Content Views with multiple componets set to `latest: true` will result in automatic publishes whenever one of the components is updated.
This might be not desired if the components are updated in bulk, thus generating multiple publishes.
To avoid that, you still can use individual versions instead of `latest: true` by looking up the latest version using the `resource_info` module:

```yaml
- name: "Get info about cv-tools Content View"
  theforeman.foreman.resource_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    resource: content_views
    search: 'name="cv-tools"'
  register: cv_tools

- name: "Create/Update ccv-RHEL7-automated Composite Content View"
  theforeman.foreman.content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    name: "ccv-RHEL7-automated"
    composite: true
    components:
      - content_view: cv-RHEL7
        content_view_version: 23.0
      - content_view: cv-tools
        content_view_version: "{{ cv_tools.resources[0].latest_version }}"
  register: ccv_rhel

- name: "Publish ccv-RHEL7-automated Composite Content View"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "ccv-RHEL7-automated"
  when:
    - ccv_rhel.changed
```

## Automated Publishes

Since the inception of `cvmanager`, Composite Content Views gained the "Auto Publish" feature, which means that Composite Content Views will automatically be published whenever a component (that is configured as `latest`) is published.

To configure this using Ansible, add `auto_publish: true` to the `content_view` module invocation:

```yaml
- name: "Create ccv-RHEL7-automated Composite Content View"
  theforeman.foreman.content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    name: "ccv-RHEL7-automated"
    composite: true
    auto_publish: true
    components:
      - content_view: cv-RHEL7
        content_view_version: 23.0
      - content_view: cv-tools
        latest: true
```

`cvmanager` also supports automating publishing for regular Content Views, by inspecting the history of the included Repositories to decide whether a publish is necessary or not.
As the underlying logic is too fragile, there is no equivalent for doing conditional publish using Ansible. Non-conditional publishes can be done using the `content_view_version` module:

```yaml
- name: "Publish cv-tools Content View, not idempotent"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "cv-tools"
```

## Automated Promotes

To not have clients attached to "Library", `cvmanager` has an "Automated Promotes" feature which essentially ensures that a given (Composite) Content View has the same version in "Library" and another user-selected Lifecycle Environment.

The same can be achieved using the `content_view_version` module:

```yaml
- name: "Ensure ccv-RHEL7-automated is the same version in Library and Dev"
  theforeman.foreman.content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "ccv-RHEL7-automated"
    current_lifecycle_environment: Library
    lifecycle_environments:
      - Dev
```
