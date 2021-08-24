================================
theforeman.foreman Release Notes
================================

.. contents:: Topics

This changelog describes changes after version 0.8.1.

v2.2.0
======

Minor Changes
-------------

- repository - add support for filtering repositories by OS version based on API feature apidoc/v2/repositories/create.html

Bugfixes
--------

- host, hostgroup - don't accidentally duplicate ``kt_activation_keys`` param (https://github.com/theforeman/foreman-ansible-modules/issues/1268)

v2.1.2
======

Bugfixes
--------

- activation_key - submit organization_id when querying subs, required for Katello 4.1
- content_view_version_cleanup - sort content view versions before deleting (https://github.com/RedHatSatellite/satellite-ansible-collection/issues/30, https://bugzilla.redhat.com/show_bug.cgi?id=1980274)
- content_view_version_cleanup role - properly clean up when users set keep=0 (https://bugzilla.redhat.com/show_bug.cgi?id=1974314)
- host, compute_profile - when resolving cluster and other values in vm_attrs, compare them as strings (https://github.com/theforeman/foreman-ansible-modules/issues/1245)
- subscription_info - mark ``organization`` parameter as required, to match Katello

v2.1.1
======

Bugfixes
--------

- external_usergroup - always lookup the ID of the usergroup, instead of passing the name to the API (https://bugzilla.redhat.com/show_bug.cgi?id=1967649)
- host, hostgroup - don't override already set parameters when passing an activation key only (and vice versa) (https://bugzilla.redhat.com/show_bug.cgi?id=1967904)

v2.1.0
======

Minor Changes
-------------

- Add a domain_info module
- Add a hostgroups role (https://github.com/theforeman/foreman-ansible-modules/issues/1116)
- Add a role `content_rhel` to perform basic setup for registering and syncing RHEL content hosts
- Add content credentials role
- callback plugin - collect facts during the run, merge them correctly and upload them once at the end
- compute_resource - add ``cloud`` param for the AzureRm provider, to select which Azure cloud to use
- compute_resource - add ``sub_id`` parameter for handling the Azure Subscription ID instead of the ``user`` parameter
- host - Add ``Redfish`` to list of possible BMC providers of an interface
- host, compute_profile - look up the correct id for storage pods and domains given as part of ``volumes_attributes`` (https://bugzilla.redhat.com/show_bug.cgi?id=1885234)
- hostgroup - add a ``ansible_roles`` parameter (https://github.com/theforeman/foreman-ansible-modules/issues/1123)
- new ``content_views`` role to manage content views (https://github.com/theforeman/foreman-ansible-modules/issues/1111)
- new ``organizations`` role to manage organizations (https://github.com/theforeman/foreman-ansible-modules/issues/1109)
- subnet - add ``bmc_proxy`` parameter to configure BMC proxies for subnets

Bugfixes
--------

- host - pass the right image id to the compute resource when creating a host (https://github.com/theforeman/foreman-ansible-modules/issues/1160, https://bugzilla.redhat.com/show_bug.cgi?id=1911670)

New Modules
-----------

- theforeman.foreman.content_view_info - Fetch information about Content Views
- theforeman.foreman.content_view_version_info - Fetch information about Content Views
- theforeman.foreman.domain_info - Fetch information about Domains
- theforeman.foreman.host_errata_info - Fetch information about Host Errata
- theforeman.foreman.repository_set_info - Fetch information about Red Hat Repositories
- theforeman.foreman.setting_info - Fetch information about Settings
- theforeman.foreman.subnet_info - Fetch information about Subnets
- theforeman.foreman.subscription_info - Fetch information about Subscriptions

v2.0.1
======

Bugfixes
--------

- host - don't filter ``false`` values for ``interfaces_attributes`` (https://github.com/theforeman/foreman-ansible-modules/issues/1148)
- host_info, repository_info - correctly fetch all entities when neither ``name`` nor ``search`` is set
- host_info, repository_info - enforce mutual exclusivity of ``name`` and ``search``

v2.0.0
======

Minor Changes
-------------

- Add a role `activation_keys` to manage activation keys
- Add a role `lifecycle_environments` to manage lifecycle environments
- Add a role `repositories` to manage products, repositories, and repository_sets
- Add a role `sync_plans` to manage sync plans
- activation_key - add support for selecting subscriptions by ``upstream_pool_id``
- compute_resource - add ``set_console_password``, ``keyboard_layout`` and ``public_key`` parameters (https://github.com/theforeman/foreman-ansible-modules/issues/1052)
- host - clarify that ``owner`` refers to a users login, not their full name (https://github.com/theforeman/foreman-ansible-modules/issues/1045)
- host - look up the correct network id for a network given as part of ``interfaces_attributes`` (https://github.com/theforeman/foreman-ansible-modules/issues/1104)
- host, hostgroup - add ``activation_keys`` parameter to ease configuring activation keys for deploments

Breaking Changes / Porting Guide
--------------------------------

- All role variables are now prefixed with ``foreman_`` to avoid clashes with similarly named variables from roles outside this collection.

Bugfixes
--------

- content_view_version - make the ``version`` parameter not fail when the version was entered without a minor part (https://github.com/theforeman/foreman-ansible-modules/issues/1087)
- host - allow moving hosts between Organizations and Locations (https://bugzilla.redhat.com/show_bug.cgi?id=1901716)
- host - fix subnet/domain assignment when multiple interfaces are defined (https://github.com/theforeman/foreman-ansible-modules/issues/1095)
- host, hostgroup - select kickstart_repository based on lifecycle_environment and content_view if those are set (https://github.com/theforeman/foreman-ansible-modules/issues/1090, https://bugzilla.redhat.com/1915872)
- resource_info - correctly show the exact resource when passing ``id`` in ``params``

New Modules
-----------

- theforeman.foreman.host_info - Fetch information about Hosts
- theforeman.foreman.puppetclasses_import - Import Puppet Classes from a Proxy
- theforeman.foreman.repository_info - Fetch information about Repositories

v1.5.0
======

Minor Changes
-------------

- content_upload - use ``to_native`` to decode RPM headers if needed (RPM 4.15+ returns strings)
- content_view_version - provide examples how to obtain detailed information about content view versions (https://bugzilla.redhat.com/show_bug.cgi?id=1868145)
- content_view_version_cleanup - new role for cleaning up unused content view versions (https://github.com/theforeman/foreman-ansible-modules/issues/497)
- host - allow management of interfaces (https://github.com/theforeman/foreman-ansible-modules/issues/757)
- inventory plugin - add support for the Report API present in Foreman 1.24 and later
- inventory plugin - allow to compose the ``inventory_hostname`` (https://github.com/theforeman/foreman-ansible-modules/issues/1070)
- manifest - new role for easier handling of subscription manifest workflows
- subnet - add new ``externalipam_group`` parameter
- update vendored ``apypie`` to 0.3.2

Bugfixes
--------

- content_upload - Fix upload of files bigger than 2MB in Pulp3-based setups (https://github.com/theforeman/foreman-ansible-modules/issues/1043)
- job_invocation - properly submit ``ssh``, ``recurrence``, ``scheduling`` and ``concurrency_control`` to the server
- repository - don't emit a false warning about ``organization_id`` not being supported by the server (https://github.com/theforeman/foreman-ansible-modules/issues/1055)
- repository_set, repository - clarify documentation which module should be used for Red Hat Repositories (https://github.com/theforeman/foreman-ansible-modules/issues/1059)

v1.4.0
======

Minor Changes
-------------

- global_parameter - allow to set hidden flag (https://github.com/theforeman/foreman-ansible-modules/issues/1024)
- job_template - stricter validation of ``template_inputs`` sub-options
- redhat_manifest - allow configuring content access mode (https://github.com/theforeman/foreman-ansible-modules/issues/820)
- subnet - verify the server has the ``remote_execution`` plugin when specifying ``remote_execution_proxies``
- the ``apypie`` library is vendored inside the collection, so users only have to install ``requests`` manually now.

Bugfixes
--------

- Don't try to update an entity, if only parameters that aren't supported by the server are detected as changed. (https://github.com/theforeman/foreman-ansible-modules/issues/975)
- allow to pass an empty string when refering to entities, thus unsetting the value (https://github.com/theforeman/foreman-ansible-modules/issues/969)
- compute_profile - don't fail when trying to update compute attributes of a profile (https://github.com/theforeman/foreman-ansible-modules/issues/997)
- host, hostgroup - support ``None`` as the ``pxe_loader`` (https://github.com/theforeman/foreman-ansible-modules/issues/971)
- job_template - don't fail when trying to update template_inputs
- os_default_template - document possible template kind choices (https://bugzilla.redhat.com/show_bug.cgi?id=1889952)
- smart_class_parameters - don't fail when trying to update override_values

New Modules
-----------

- theforeman.foreman.job_invocation - Invoke Remote Execution Jobs
- theforeman.foreman.smart_proxy - Manage Smart Proxies

v1.3.0
======

Minor Changes
-------------

- external_usergroup - rename the ``auth_source_ldap`` parameter to ``auth_source`` (``auth_source_ldap`` is still supported via an alias)
- server URL and credentials can now also be specified using environment variables (https://github.com/theforeman/foreman-ansible-modules/issues/837)
- subnet - add support for external IPAM (https://github.com/theforeman/foreman-ansible-modules/issues/966)

Bugfixes
--------

- content_view - remove CVs from lifecycle environments before deleting them (https://bugzilla.redhat.com/show_bug.cgi?id=1875314)
- external_usergroup - support non-LDAP external groups (https://github.com/theforeman/foreman-ansible-modules/issues/956)
- host - properly scope image lookups by the compute resource (https://bugzilla.redhat.com/show_bug.cgi?id=1878693)
- inventory plugin - include empty parent groups in the inventory (https://github.com/theforeman/foreman-ansible-modules/issues/919)

New Modules
-----------

- theforeman.foreman.status_info - Get status info

v1.2.0
======

Minor Changes
-------------

- compute_resource - added ``caching_enabled`` option for VMware compute resources
- domain, host, hostgroup, operatingsystem, subnet - manage parameters in a single API call (https://bugzilla.redhat.com/show_bug.cgi?id=1855008)
- host - add ``compute_attributes`` parameter to module (https://bugzilla.redhat.com/show_bug.cgi?id=1871815)
- provisioning_template - update list of possible template kinds (https://bugzilla.redhat.com/show_bug.cgi?id=1871978)
- repository - update supported parameters (https://github.com/theforeman/foreman-ansible-modules/issues/935)

Bugfixes
--------

- image - fix quoting of search values (https://github.com/theforeman/foreman-ansible-modules/issues/927)

v1.1.0
======

Minor Changes
-------------

- activation_key - add ``description`` parameter (https://github.com/theforeman/foreman-ansible-modules/issues/915)
- callback plugin - add reporter to report logs sent to Foreman (https://github.com/theforeman/foreman-ansible-modules/issues/836)
- document return values of modules (https://github.com/theforeman/foreman-ansible-modules/pull/901)
- inventory plugin - allow to control batch size when pulling hosts from Foreman (https://github.com/theforeman/foreman-ansible-modules/pull/865)
- subnet - Require mask/cidr only on ipv4 (https://github.com/theforeman/foreman-ansible-modules/issues/878)

Bugfixes
--------

- inventory plugin - fix want_params handling (https://github.com/theforeman/foreman-ansible-modules/issues/847)

New Modules
-----------

- theforeman.foreman.http_proxy - Manage HTTP Proxies

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

New Modules
-----------

- theforeman.foreman.activation_key - Manage Activation Keys
- theforeman.foreman.architecture - Manage Architectures
- theforeman.foreman.auth_source_ldap - Manage LDAP Authentication Sources
- theforeman.foreman.bookmark - Manage Bookmarks
- theforeman.foreman.compute_attribute - Manage Compute Attributes
- theforeman.foreman.compute_profile - Manage Compute Profiles
- theforeman.foreman.compute_resource - Manage Compute Resources
- theforeman.foreman.config_group - Manage (Puppet) Config Groups
- theforeman.foreman.content_credential - Manage Content Credentials
- theforeman.foreman.content_upload - Upload content to a repository
- theforeman.foreman.content_view - Manage Content Views
- theforeman.foreman.content_view_filter - Manage Content View Filters
- theforeman.foreman.content_view_version - Manage Content View Versions
- theforeman.foreman.domain - Manage Domains
- theforeman.foreman.external_usergroup - Manage External User Groups
- theforeman.foreman.global_parameter - Manage Global Parameters
- theforeman.foreman.hardware_model - Manage Hardware Models
- theforeman.foreman.host - Manage Hosts
- theforeman.foreman.host_collection - Manage Host Collections
- theforeman.foreman.host_power - Manage Power State of Hosts
- theforeman.foreman.hostgroup - Manage Hostgroups
- theforeman.foreman.image - Manage Images
- theforeman.foreman.installation_medium - Manage Installation Media
- theforeman.foreman.job_template - Manage Job Templates
- theforeman.foreman.lifecycle_environment - Manage Lifecycle Environments
- theforeman.foreman.location - Manage Locations
- theforeman.foreman.operatingsystem - Manage Operating Systems
- theforeman.foreman.organization - Manage Organizations
- theforeman.foreman.os_default_template - Manage Default Template Associations To Operating Systems
- theforeman.foreman.partition_table - Manage Partition Table Templates
- theforeman.foreman.product - Manage Products
- theforeman.foreman.provisioning_template - Manage Provisioning Templates
- theforeman.foreman.puppet_environment - Manage Puppet Environments
- theforeman.foreman.realm - Manage Realms
- theforeman.foreman.redhat_manifest - Interact with a Red Hat Satellite Subscription Manifest
- theforeman.foreman.repository - Manage Repositories
- theforeman.foreman.repository_set - Enable/disable Repositories in Repository Sets
- theforeman.foreman.repository_sync - Sync a Repository or Product
- theforeman.foreman.resource_info - Gather information about resources
- theforeman.foreman.role - Manage Roles
- theforeman.foreman.scap_content - Manage SCAP content
- theforeman.foreman.scap_tailoring_file - Manage SCAP Tailoring Files
- theforeman.foreman.scc_account - Manage SUSE Customer Center Accounts
- theforeman.foreman.scc_product - Subscribe SUSE Customer Center Account Products
- theforeman.foreman.setting - Manage Settings
- theforeman.foreman.smart_class_parameter - Manage Smart Class Parameters
- theforeman.foreman.snapshot - Manage Snapshots
- theforeman.foreman.subnet - Manage Subnets
- theforeman.foreman.subscription_manifest - Manage Subscription Manifests
- theforeman.foreman.sync_plan - Manage Sync Plans
- theforeman.foreman.templates_import - Sync Templates from a repository
- theforeman.foreman.user - Manage Users
- theforeman.foreman.usergroup - Manage User Groups
