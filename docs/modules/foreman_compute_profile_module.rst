:source: foreman_compute_profile.py

:orphan:

.. _foreman_compute_profile_module:


foreman_compute_profile - Manage Foreman Compute Profiles using Foreman API
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.0

.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Create and delete Foreman Compute Profiles using Foreman API



Requirements
~~~~~~~~~~~~
The below requirements are needed on the host that executes this module.

- nailgun >= 0.28.0
- python >= 2.6
- ansible >= 2.3


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
                    <b>name</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>compute profile name</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>password</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>foreman user password</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>server_url</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>foreman url</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>state</b>
                                                                            </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>absent</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>compute profile presence</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>updated_name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>new compute profile name</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>username</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>foreman username</div>
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
                                                                        <div>verify ssl connection when communicating with foreman</div>
                                                                                </td>
            </tr>
                        </table>
    <br/>



Examples
--------

.. code-block:: yaml+jinja

    
    - name: compute profile
      foreman_compute_profile:
        name: example_compute_profile
        server_url: foreman.example.com
        username: admin
        password: secret
        verify_ssl: false
        state: present





Status
------



This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.



Maintenance
-----------

This module is flagged as **community** which means that it is maintained by the Ansible Community. See :ref:`Module Maintenance & Support <modules_support>` for more info.

For a list of other modules that are also maintained by the Ansible Community, see :ref:`here <community_supported>`.





Author
~~~~~~

- Philipp Joos (@philippj)


.. hint::
    If you notice any issues in this documentation you can `edit this document <https://github.com/theforeman/foreman-ansible-modules/edit/master/modules/foreman_compute_profile.py?description=%3C!---%20Your%20description%20here%20--%3E%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
