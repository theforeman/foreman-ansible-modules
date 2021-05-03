theforeman.foreman.content_view_publish
=========

A role for automating the publishing new versions of a Foreman Content-View.

Requirements
------------

This role requires the theforeman.foreman module collection.

Role Variables
--------------

The primary dictionary is the organizations dictionary, which is formatted as such:
```
organizations:
  org1:
    content_views:
      - "content-view1"
      - "content-view2"
  org2:
    content_views:
      - "content-view3"
      - "content-view4"
```

This can run against multiple organizations/content-views or selected subsets.

For example, if the previously mentioned dictionary describes *ALL* of my Foreman environment, but I only want to promote the 'Prod' lifecycle_environment in the content-view 'content-view1' in organization 'org', my dictionary would look like this:
```
organizations:
  org1:
    content_views:
      - "content-view1"
```
Items not described in the inventory will not be affected (the exception being Library when a new content_view_version needs to be published).


Dependencies
------------

You need a Foreman user with admin access to the Organizations, Lifecycle_Environments, and Content_Views you wish to interact with.

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
For example:

Publishing a new Content-View version for 'content-view1' and 'content-view2' in org1.
```
organizations:
  org1:
    content_views:
      - "content-view1"
      - "content-view2"
```

Publishing a new Content-View version for 'content-view1' and 'content-view2' in org1 and 'content-view3' in org2
```
organizations:
  org1:
    content_views:
      - "content-view1"
      - "content-view2"
  org2:
    content_views:
      - "content-view3"
```
