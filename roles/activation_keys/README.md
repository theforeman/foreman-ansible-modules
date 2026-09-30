theforeman.foreman.activation_keys
==================================

This role creates and manages Activation Keys.

Since Katello 4.12, Simple Content Access (SCA) is the only content access mode. With SCA, hosts get access to the content of their Content View and Lifecycle Environment without attaching subscriptions, so auto-attach and the `subscriptions` field are not used.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

The main data structure for this role is the list of `foreman_activation_keys`. Each `activation_key` requires the following fields:

- `name`: The name of the activation key.

The following fields are required for an activation key but have defaults which make them optional for this role:

- `organization`: Organization to create the activation key for. Defaults to `foreman_organization` variable.

The following fields are optional in the sense that the server will use default values when they are omitted:

- `unlimited_hosts`: Allow an unlimited number of hosts to register with the activation key when true. When false, the `max_hosts` parameter which sets a numerical limit on the number of hosts that can be registered becomes required. server defaults to true.

The following fields are optional and will be omitted by default:

- `lifecycle_environment`: Lifecycle Environment to assign to hosts registered with this activation key.
- `content_view`: Content View to assign to hosts registered with this activation key.
- `content_view_environments`: Content View Environments to assign to hosts registerd with this activation key.
- `description`: Description of the activation key. Helpful for other users to find which activation key to use.
- `host_collections`: List of Host Collections to associate with the activation key.
- `subscriptions`: List of Subscriptions to associate with the activation key. Each Subscription is required to have one of `name`, `pool_id`, or `upstream_pool_id`. Of these, only the `pool_id` is guaranteed to be unique. `upstream_pool_id` only exists for subscriptions imported from a 3rd party organization (e.g. on a Red Hat Subscription Manifest). When uniqueness is not an issue, `name` or `upstream_pool_id` can be easier to work with since the `pool_id` does not get determined until the subscription is imported or created and therefore may not yet be determined when you are writing playbooks. Not supported in SCA mode.
- `content_overrides`: List of Content Overrides for the activation key. Each Content Override is required to have a `label` which refers to a repository and `override` which refers to one of the states enabled, disabled, or default.
For Red Hat products the `label` is the repository label, e.g. `rhel-7-server-rpms`.
For custom products it's in the format `<organization_label>_<product_label>_<repository_label>`, e.g. `ExampleOrg_ExampleCustomProduct_ExampleRepository`.
- `release_version`: Release Version to set when registering hosts with the activation key.
- `service_level`: Service Level to set when registering hosts with the activation key. Premium, Standard, or Self-Support. This will limit Subscriptions available to hosts to those matching this service level.
- `purpose_usage`: System Purpose Usage to set when registering hosts with the activation key. Production, Development/Test, Disaster Recovery. When left unset this will not set System Purpose Usage on registering hosts. This should only be used when it is supported by the OS of registering hosts (RHEL 8 only at the time of writing).
- `purpose_role`: System Purpose Role to set when registering hosts with the activation key. Red Hat Enterprise Linux Server, Red Hat Enterprise Linux Workstation, Red Hat Enterprise Linux Compute Node. When left unset this will not set System Purpose Role on registering hosts. This should only be used when it is supported by the OS of registering hosts (RHEL 8 only at the time of writing).
- `purpose_addons`: List of System Purpose Addons (ELS, EUS) to set on registering hosts. This should only be used when it is supported by the OS of registering hosts (RHEL 8 only at the time of writing).

A helpful behavior to keep in mind when creating activation keys is that a host can register with multiple activation keys, which are applied in the order that they are listed. Host attributes like Lifecycle Environment, Content View, etc will be overwritten by later activation keys so that the last activation key listed wins.

Example Playbooks
-----------------

Create a basic Activation Key that uses Library LCE and Default Organization View.

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.activation_keys
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "Default Organization"
        foreman_activation_keys:
          - name: "Basic Activation Key"
            description: "Registers hosts in Library/Default Organization View"
```

Define two Activation Keys. The first registers hosts in the "ACME" organization and enables the repository of the custom product "ACME_App". The second assigns the "Test" LCE and "RHEL7_Base" Content View. Additionally the organization of the second Activation Key is explicitly specified as "Base_Test".

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.activation_keys
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "ACME"
        foreman_activation_keys:
          - name: "ACME_App_Key"
            content_overrides:
              - label: ACME_ACME_App_ACME_App_Repository
                override: enabled
          - name: "ACME_RHEL7_Base_Test"
            lifecycle_environment: "Test"
            content_view: "RHEL7_Base"
            organization: "Base_Test"
            content_overrides:
              - label: rhel-7-server-rpms
                override: enabled
              - label: ExampleOrganization_ExampleCustomProduct_ExampleRepository
                override: enabled
```

Following the second example, a Host which is registered using `subscription-manager register --activationkey ACME_App_Key,ACME_RHEL7_Base_Test` will get the ACME_App repository enabled, the Test LCE and the RHEL7_Base Content View.

To delete multiple activation_keys
```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.activation_keys
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_organization: "ACME"
        foreman_activation_keys:
          - name: "ACME_App_Key"
            state: absent
          - name: "ACME_OS_Key"
            state: absent
