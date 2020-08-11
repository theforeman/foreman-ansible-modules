================================
theforeman.foreman Release Notes
================================

.. contents:: Topics

This changelog describes changes after version 0.8.1.

v1.0.1
======

Release Summary
---------------

Documentation fixes to reflect the correct module names.


v1.0.0
======

Release Summary
---------------

This is the first stable release of the ``theforeman.foreman`` collection.


Breaking Changes / Porting Guide
--------------------------------

- All modules were renamed to drop the ``foreman_`` and ``katello_`` prefixes.
  Additionally to the prefix removal, the following modules were further ranamed:

  * katello_upload to content_upload
  * katello_sync to repository_sync
  * katello_manifest to subscription_manifest
  * foreman_search_facts to resource_info
  * foreman_ptable to partition_table
  * foreman_model to hardware_model
  * foreman_environment to puppet_environment
