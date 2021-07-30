theforeman.foreman.content_view_rollback
=========

A role for automating the rollback of Content-Views.

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

`foreman_lifecycle_environments`: A list of Lifecycle Environments that should be promtoed.



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
- name: "Run the content_view_rollback Role"
  hosts: all
  tasks:
  - name: "Run the content_view_rollback Role"
    include_role: 
      name: theforeman.foreman.content_view_rollback
```
For example:

Rolling back Lifecycle Environments inside their respective Content-Views to the previous version:
```
foreman_organization: "Org1"
foreman_content_view: "content-view1"
foreman_lifecycle_environments:
  - "Dev"
  - "QA"
  - "Prod"

```

The role would take the Dev, QA and Prod Lifecycle Environments to Content-View version N-1.  If, prior to role runtime, the versions were: Prod=10, QA=11, and Dev=12, the result at the end of the run would be: Prod=9, QA=10, and Dev=11.  If that Content-View version does not exist it will select the next lowest Content-View version.  If there are none lower, it will exit with a message saying such.
