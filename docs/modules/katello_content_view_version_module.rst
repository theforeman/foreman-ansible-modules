:source: katello_content_view_version.py

:orphan:

.. _katello_content_view_version_module:


katello_content_view_version - Create, remove or interact with a Katello Content View Version
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Publish, Promote or Remove a Katello Content View Version



Requirements
~~~~~~~~~~~~
The below requirements are needed on the host that executes this module.

- nailgun
- python >= 2.6


Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
                        <th width="100%">Comments</th>
        </tr>
                    <tr>
                                                                <td colspan="1">
                    <b>content_view</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Name of the content view</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>current_lifecycle_environment</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The lifecycle environment that is already associated with the content view version</div>
                                                    <div>Helpful for promoting a content view version</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>force_promote</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                                                                    <ul><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Force content view promotion and bypass lifecycle environment restriction</div>
                                                                                        <div style="font-size: small; color: darkgreen"><br/>aliases: force</div>
                                    </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>force_yum_metadata_regeneration</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Force metadata regeneration when performing Publish and Promote tasks</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>lifecycle_environments</b>
                                                                            </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">Library</div>
                                    </td>
                                                                <td>
                                                                        <div>The lifecycle environments the Content View Version should be in.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>organization</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Organization that the content view is in</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>password</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Password for user accessing Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>server_url</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>URL of Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>state</b>
                                                                            </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Content View Version state</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>synchronous</b>
                                                                            </td>
                                <td>
                                                                                                                                                                                                                <b>Default:</b><br/><div style="color: blue">yes</div>
                                    </td>
                                                                <td>
                                                                        <div>Wait for the Publish or Promote task to complete if True. Immediately return if False.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>username</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Username on Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>verify_ssl</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                                                                    <ul><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Verify SSL of the Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>version</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The content view version number (i.e. 1.0)</div>
                                                                                </td>
            </tr>
                        </table>
    <br/>


Notes
-----

.. note::
    - You cannot use this to remove a Contnet View Version from a Lifecycle environment, you should promote another version first.
    - For idempotency you must specify either ``version`` or ``current_lifecycle_environment``.


Examples
--------

.. code-block:: yaml+jinja

    
    - name: "Ensure content view version 2.0 is in Test & Pre Prod"
      katello_content_view_version:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        content_view: "CV 1"
        organization: "Default Organization"
        version: 2.0
        lifecycle_environments:
          - Test
          - Pre Prod

    - name: "Ensure content view version in Test is also in Pre Prod"
      katello_content_view_version:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        content_view: "CV 1"
        organization: "Default Organization"
        current_lifecycle_environment: Test
        lifecycle_environments:
          - Pre Prod

    - name: "Publish a content view, not idempotent"
      katello_content_view_version:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        content_view: "CV 1"
        organization: "Default Organization"

    - name: "Publish a content view and promote that version to Library & Dev, not idempotent"
      katello_content_view_version:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        content_view: "CV 1"
        organization: "Default Organization"
        lifecycle_environments:
          - Library
          - Dev

    - name: "Ensure content view version 1.0 doesn't exist"
      katello_content_view_version:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        content_view: "Web Servers"
        organization: "Default Organization"
        version: 1.0
        state: absent





Status
------



This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.



Maintenance
-----------

This module is flagged as **community** which means that it is maintained by the Ansible Community. See :ref:`Module Maintenance & Support <modules_support>` for more info.

For a list of other modules that are also maintained by the Ansible Community, see :ref:`here <community_supported>`.





Author
~~~~~~

- Sean O'Keeffe (@sean797)


.. hint::
    If you notice any issues in this documentation you can `edit this document <https://github.com/theforeman/foreman-ansible-modules/edit/master/modules/katello_content_view_version.py?description=%3C!---%20Your%20description%20here%20--%3E%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
