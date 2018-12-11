:source: foreman_operating_system.py

:orphan:

.. _foreman_operating_system_module:


foreman_operating_system - Manage Foreman Operating Systems
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.4

.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Manage Foreman Operating System Entities
- Uses https://github.com/SatelliteQE/nailgun



Requirements
~~~~~~~~~~~~
The below requirements are needed on the host that executes this module.

- nailgun >= 0.29.0
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
                    <b>architectures</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>architectures, the operating system can be installed on</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>description</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Description of the Operating System</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>family</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>distribution family of the Operating System</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>major</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>major version of the Operating System</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>media</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>list of installation media</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>minor</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>minor version of the Operating System</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>name</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Name of the Operating System</div>
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
                    <b>password_hash</b>
                                                                            </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li>MD5</li>
                                                                                                                                                                                                <li>SHA256</li>
                                                                                                                                                                                                <li>SHA512</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>hashing algorithm for passwd</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>provisioning_templates</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>list of provisioning templates</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>ptables</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>list of partitioning tables</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>release_name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Release name of the operating system (recommended for debian)</div>
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
                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>present_with_defaults</li>
                                                                                                                                                                                                <li>absent</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>State of the Operating System</div>
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
                        </table>
    <br/>



Examples
--------

.. code-block:: yaml+jinja

    
    - name: "Create an Operating System"
      foreman_operating_system:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        name: "TheAnswer"
        value: "42"
        state: present

    - name: "Ensure existence of an Operating System (provide default values)"
      foreman_operating_system:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        name: "TheAnswer"
        value: "43"
        state: present_with_defaults

    - name: "Delete an Operating System"
      foreman_operating_system:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        name: "TheAnswer"
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

- Matthias M Dellweg (@mdellweg) ATIX AG
- Bernhard Hopfenmüller (@Fobhep) ATIX AG


.. hint::
    If you notice any issues in this documentation you can `edit this document <https://github.com/theforeman/foreman-ansible-modules/edit/master/modules/foreman_operating_system.py?description=%3C!---%20Your%20description%20here%20--%3E%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
