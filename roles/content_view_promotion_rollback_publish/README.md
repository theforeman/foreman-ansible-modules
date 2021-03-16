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
Items not described in the inventory will not be affected (the exception being Library when a new content_view_version needs to be published.

If you only want to use this role for staging new content_view_versions, simply set the variable **publish_only** to **True** (this can be done in vars/main.yml or elsewhere).  This action will only publish a new content_view_version to the content_views described in the dictionary.

If you want to rollback (reverse promote) lifecycle environments simply set the variable **rollback** to **True** (this can be done in vars/main.yml or elsewhere).  This action will only roll back lifecycle_environments in the content views described in main dictionary.


Foreman information is accessed by way setting the vars below:
```
foreman_user: admin
foreman_password: changeme
foreman_server_url: "https://myforemanserver.myorg.com"
```
This is in the vars/main.yml for illistrative purposes only!  Please use a vault (or custom credential-type if using Tower).  STORING PASSWORDS IN PLAINTEXT IS BAD, MMM-KAY?


Dependencies
------------

You need a Foreman user with admin access to the Organizations, Lifecycle_Environments, and Content_Views you wish to interact with.

By default, the role will require a valid SSL certificate installed on your Foreman server that the ansible client can trace trust to.  To disable that update the 'FOREMAN_VALIDATE_CERTS variable in defaults/main.yml.'


Example Playbook
----------------

The role can be instantiated quite simply, all of the decision making is handled by the variables set:

```
---
- name: "Run the content_view_promotion_rollback_publish Role"
  hosts: all
  tasks:
  - name: "Run the content_view_promotion_rollback_publish Role"
    include_role: 
      name: theforeman.foreman.content_view_promotion_rollback_publish 
```
