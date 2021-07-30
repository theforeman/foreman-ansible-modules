theforeman.foreman.content_view_promote
=========

A role for automating the promotion of Foreman Content-Views through various LifeCycle Environemnts.

Requirements
------------

This role requires the theforeman.foreman module collection.

Role Variables
--------------

This role requires most of the common foreman variable more noteably:

`foreman_organization`: The Organization that the Content-View belongs to.

`foreman_username`: A foreman user that has access rights to publish new Content-View versions in the aforementioned Organization. 

`foreman_password`: The password for the user. foreman_server_url: The URL used to access foreman.

As well as two additional variables:

`foreman_content_view`: The name of the Content-View which should have Lifecycle Environments promoted.

`foreman_lifecycle_envrionments`: A list of Lifecycle Environments that should be promtoed.

Dependencies
------------

You need a Foreman user with admin access to the Organization, Lifecycle_Environment, and Content_View you wish to interact with.

By default, the role will require a valid SSL certificate installed on your Foreman server that the ansible client can trace trust to.  To disable that update the 'FOREMAN_VALIDATE_CERTS' variable in defaults/main.yml.

For example, to disable certificate checking you would update the variable as such:
```
FOREMAN_VALIDATE_CERTS: false
```

Example Playbook
----------------

The role can be instantiated quite simply, all of the decision making is handled by the variables previously set:

```
---
- name: "Run the content_view_promotion Role"
  hosts: all
  tasks:
  - name: "Run the content_view_promotion Role"
    include_role: 
      name: theforeman.foreman.content_view_promotion
```


Notes
----------------

Not all Lifecycle Environments in a Content-View must be promoted.  If you only want to promote a subset (or single), LifeCycle Environment, you just need to update the `foreman_lifecycle_envrionments` variable with the Lifecycle Environments you wish to be affected.  This may be helpful in an environment where you only want to promote one environment at a time to help minimize potential risk.

When there isn't a new version of the Content-View to promote to, a new version of the Content-View will be published automatically.  Be aware that publishing new versions on a large Content-View can take a long time- you may need to adjust your Ansible job timeouts accordingly.
