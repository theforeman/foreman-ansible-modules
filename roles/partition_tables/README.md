theforeman.foreman.partition_tables
===================================

This role creates and manages Partition Tables.

Role Variables
--------------

This role supports the [Common Role Variables](https://github.com/theforeman/foreman-ansible-modules/blob/develop/README.md#common-role-variables).

The main data structure for this role is the list of `foreman_partition_tables`. Each `partition_table` requires the following fields:

- `name`: The name of the partition table.

The following fields are optional and will be omitted by default:

- `layout`: The content of the partition table. Mutually exclusive with `file_name`.
- `file_name`: Path to a file on the controller containing the partition table content. Mutually exclusive with `layout`.
- `os_family`: The OS family the partition table shall be assigned with.
- `locked`: Determines whether the partition table shall be locked for editing.
- `locations`: List of locations the partition table should be assigned to.
- `organizations`: List of organizations the partition table should be assigned to.
- `updated_name`: New name of the partition table. When this parameter is set, the module will not be idempotent.

Example Playbook
----------------

Create a partition table `Kickstart GPT` using the file `files/kickstart_gpt.erb`:

```yaml
- hosts: localhost
  roles:
    - role: theforeman.foreman.partition_tables
      vars:
        foreman_server_url: https://foreman.example.com
        foreman_username: "admin"
        foreman_password: "changeme"
        foreman_partition_tables:
          - name: Kickstart GPT
            os_family: Redhat
            layout: "{{ lookup('file', 'kickstart_gpt.erb') }}"
            locations:
              - "Uppsala"
            organizations:
              - "ACME"
```
