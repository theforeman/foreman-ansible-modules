theforeman.foreman.content_view_rollback
=========

A role for automating the rollback of Content-Views.

Requirements
------------

This role requires the theforeman.foreman module collection.

Role Variables
--------------

The primary dictionary is the organizations dictionary, which is formatted as such:
```
organizations:
  org1:
    lifecycle_environments:
      - "Dev"
      - "QA"
      - "Prod"
    content_views:
      - "content-view1"
      - "content-view2"
  org2:
    lifecycle_environments:
      - "Dev2"
      - "QA2"
      - "Prod2"
    content_views:
      - "content-view3"
      - "content-view4"
```

This can run against multiple organizations/lifecycle_environments/content-views or selected subsets.

For example, if the previously mentioned dictionary describes *ALL* of my Foreman environment, but I only want to rollback the 'Prod' lifecycle_environment in the content-view 'content-view1' in organization 'org', my dictionary would look like this:
```
organizations:
  org1:
    lifecycle_environments:
      - "Prod"
    content_views:
      - "content-view1"
```
Items not described in the inventory will not be affected.

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
organizations:
  org1:
    lifecycle_environments:
      - "Dev"
      - "QA"
      - "Prod"
    content_views:
      - "content-view1"
      - "content-view2"
```

The role would take the Dev, QA and Prod Lifecycle Environments to Content-View version N-1.  If, prior to role runtime, the versions were: Prod=10, QA=11, and Dev=12, the result at the end of the run would be: Prod=9, QA=10, and Dev=11.  If that Content-View version does not exist it will select the next lowest Content-View version.  If there are none lower, it will exit with a message saying such.

To perform actions across multiple Organizations:
```
organizations:
  org1:
    lifecycle_environments:
      - "Dev"
      - "QA"
      - "Prod"
    content_views:
      - "content-view1"
      - "content-view2"
  org2:
    lifecycle_environments:
      - "LCE1"
      - "LCE2"
    content_views:
      - "org2_content-view"
```
