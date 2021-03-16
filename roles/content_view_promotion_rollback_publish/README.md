theforeman.foreman.content_view_promotion_rollback_publish
=========

A role for automating the staging/promotion of Foreman Content-Views through various Organizations and LifeCycle Environemnts.  Can also be used for publishing new versions as well as rolling back.

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

For example, if the previously mentioned dictionary describes *ALL* of my Foreman environment, but I only want to promote the 'Prod' lifecycle_environment in the content-view 'content-view1' in organization 'org', my dictionary would look like this:
```
organizations:
  org1:
    lifecycle_environments:
      - "Prod"
    content_views:
      - "content-view1"
```
Items not described in the inventory will not be affected (the exception being Library when a new content_view_version needs to be published).

If you only want to use this role for staging new content_view_versions, simply set the variable **publish_only** to **True** (this can be done in vars/main.yml or elsewhere).  This action will only publish a new content_view_version to the content_views described in the dictionary.

If you want to rollback (reverse promote) lifecycle environments simply set the variable **rollback** to **True**.  This action will only roll back lifecycle_environments in the content views described in main dictionary.

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
- name: "Run the content_view_promotion_rollback_publish Role"
  hosts: all
  tasks:
  - name: "Run the content_view_promotion_rollback_publish Role"
    include_role: 
      name: theforeman.foreman.content_view_promotion_rollback_publish 
```
For example:

Promoting Lifecycle Environments (and publishing new Content-View versions if necessary):
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

The role would promote the Dev, QA and Prod Lifecycle Environments up one version level for both content-view1 and content-view2.  If that newest Content-View version does not exist, first we will publish a new version then promote the appropiate Lifecycle Environments.

Rolling back Lifecycle Environments to the previous version:
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
rollback: true
```

The role would take the Dev, QA and Prod Lifecycle Environments to Content-View version N-1.  If, prior to role runtime, the versions were: Prod=10, QA=11, and Dev=12, the result at the end of the run would be: Prod=9, QA=10, and Dev=11.

Only publishing a new Content-View version:
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
publish_only: true
```

The role would publish a new version of Content-Views content-view1 and content-view2 only.

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
publish_only: true
```

The role would publish a new version of all the listed Content-Views, across both organizations.
