:source: foreman_search_facts.py

:orphan:

.. _foreman_search_facts_module:


foreman_search_facts - Gather facts about Foreman resources
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Gather facts about Foreman resources



Requirements
~~~~~~~~~~~~
The below requirements are needed on the host that executes this module.

- nailgun


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
                    <b>resource</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Resource to search</div>
                                                    <div>Set to an invalid choice like <code>foo</code> see all available options.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>search</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Search query to use</div>
                                                    <div>If None, all resources are returned</div>
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

    
    - name: "Read a Setting"
      foreman_search_facts:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        resource: Setting
        search: name = http_proxy
      register: result
    - debug:
        var: result.response[0].value

    - name: "Read all Registries"
      foreman_search_facts:
        username: "admin"
        password: "changeme"
        server_url: "https://foreman.example.com"
        resource: Registry
      register: result
    - debug:
        var: item.name
      with_items: result.response




Return Values
-------------
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
                    <tr>
                                <td colspan="1">
                    <b>resources</b>
                    <br/><div style="font-size: small; color: red">list</div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Search results from Foreman</div>
                                        <br/>
                                    </td>
            </tr>
                        </table>
    <br/><br/>


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
    If you notice any issues in this documentation you can `edit this document <https://github.com/theforeman/foreman-ansible-modules/edit/master/modules/foreman_search_facts.py?description=%3C!---%20Your%20description%20here%20--%3E%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
