theforeman.foreman.content_view_publish
=========

A role for automating the publishing new versions of a Foreman Content-View.

Requirements
------------

This role requires the theforeman.foreman module collection.

Role Variables
--------------

This role requires most of the common foreman variable more noteably:


`foreman_organization`: The Organization that the Content-View belongs to.
`foreman_username`: A foreman user that has access rights to publish new Content-View versions in the aforementioned Organization.
`foreman_password`: The password for the user.
`foreman_server_url`: The URL used to access foreman.

as well as one additional variable:

`foreman_content_view`: The name of the Content-View in which a new version should be published.


Dependencies
------------

You need a Foreman user with admin access to the Organization and Content_Views you wish to interact with.

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
- name: "Run the content_view_publish Role"
  hosts: all
  tasks:
  - name: "Run the content_view_publish Role"
    include_role: 
      name: theforeman.foreman.content_view_publish 
```

