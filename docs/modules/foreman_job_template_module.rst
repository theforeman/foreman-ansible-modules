:source: foreman_job_template.py

:orphan:

.. _foreman_job_template_module:


foreman_job_template - Manage Job Templates in Foreman
++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Manage Foreman Remote Execution Job Templates
- Uses https://github.com/SatelliteQE/nailgun
- Uses ansible_nailgun_cement in /module_utils



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
            <th colspan="2">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
                        <th width="100%">Comments</th>
        </tr>
                    <tr>
                                                                <td colspan="2">
                    <b>audit_comment</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Content of the audit comment field</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>description_format</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>description of the job template. Template inputs can be referenced.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>file_name</b>
                    <br/><div style="font-size: small; color: red">path</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The path of a template file, that shall be imported.
    Either this or layout is required as a source for
    the Job Template &quot;content&quot;.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>job_category</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The category the template should be assigend to</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>locations</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The locations the template should be assigend to</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>locked</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                                                                    <ul><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Determines whether the template shall be locked</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The name a template should be assigned with in Foreman.
    name must be provided.
    Possible sources are, ordererd by preference:
    The &quot;name&quot; parameter, config header (inline or in a file),
    basename of a file.
    The special name &quot;*&quot; (only possible as parameter) is used
    to perform bulk actions (modify, delete) on all existing Job Templates.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>organizations</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The organizations the template shall be assigned to</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>password</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Password for user accessing Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>provider_type</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>SSH</b>&nbsp;&larr;</div></li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Determines via which provider the template shall be executed</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>server_url</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>URL of Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>snippet</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                                                                    <ul><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Determines whether the template shall be a snippet</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>state</b>
                                                                            </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>present_with_defaults</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>The state the template should be in.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>template</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The content of the Job Template, either this or file_name
    is required as a source for the Job Template &quot;content&quot;.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <b>template_inputs</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>The template inputs used in the Job Template</div>
                                                                                </td>
            </tr>
                                                            <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>fact_name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>description of the Template Input</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>description of the Template Input</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>input_type</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li>user</li>
                                                                                                                                                                                                <li>fact</li>
                                                                                                                                                                                                <li>variable</li>
                                                                                                                                                                                                <li>puppet_parameter</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>input type</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>description</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>description of the Template Input</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>required</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                        <ul><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Is the input required</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>puppet_parameter_name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Puppet parameter name, used when input type is puppet_parameter</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>variable_name</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Variable name, used when input type is variable</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>options</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>selecTemplate values for user inputs. Must be an array of any type.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>advanced</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                                                                    <ul><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                                                        <div>Template Input is advanced</div>
                                                                                </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <b>puppet_parameter_class</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Puppet class name, used when input type is puppet_parameter</div>
                                                                                </td>
            </tr>
                    
                                                <tr>
                                                                <td colspan="2">
                    <b>username</b>
                                        <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                                                        <div>Username on Foreman server</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
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

    

    - name: "Create a Job Template inline"
      foreman_job_template:
          username: "admin"
          password: "changeme"
          server_url: "https://foreman.example.com"
          name: A New Job Template
          state: present
          template: |
            <%#
                name: A Job Template
            %>
            rm -rf <%= input("toDelete") %>
          template_inputs:
            - name: toDelete
              input_type: user
          locations:
          - Gallifrey
          organizations:
          - TARDIS INC

    - name: "Create a Job Template from a file"
      foreman_job_template:
          username: "admin"
          password: "changeme"
          server_url: "https://foreman.example.com"
          name: a new job template
          file_name: timeywimey_template.erb
          template_inputs:
            - name: a new template input
              input_type: user
          state: present
          locations:
          - Gallifrey
          organizations:
          - TARDIS INC

    - name: "remove a job template's template inputs"
      foreman_job_template:
          username: "admin"
          password: "changeme"
          server_url: "https://foreman.example.com"
          name: a new job template
          template_inputs: []
          state: present
          locations:
          - Gallifrey
          organizations:
          - TARDIS INC

    - name: "Delete a Job Template"
      foreman_job_template:
          username: "admin"
          password: "changeme"
          server_url: "https://foreman.example.com"
          name: timeywimey
          state: absent

    - name: "Create a Job Template from a file and modify with parameter(s)"
      foreman_job_template:
          username: "admin"
          password: "changeme"
          server_url: "https://foreman.example.com"
          file_name: timeywimey_template.erb
          name: Wibbly Wobbly Template
          state: present
          locations:
          - Gallifrey
          organizations:
          - TARDIS INC

    # Providing a name in this case wouldn't be very sensible.
    # Alternatively make use of with_filetree to parse recursively with filter.
    - name: Parsing a directory of Job templates
      foreman_job_template:
          username: "admin"
          password: "changeme"
          server_url: "https://foreman.example.com"
          file_name: "{{ item }}"
          state: present
          locations:
          - SKARO
          organizations:
          - DALEK INC
          with_fileglob:
           - "./arsenal_templates/*.erb"

    # If the templates are stored locally and the ansible module is executed on a remote host
    - name: Ensure latest version of all your Job Templates
      foreman_job_template:
        server_url: "https://foreman.example.com"
        username:  "admin"
        password:  "changeme"
        state: present
        layout: '{{ lookup("file", item.src) }}'
      with_filetree: '{{ /path/to/Job/Templates/templates" }}'
      when: item.state == 'file'


    # with name set to "*" bulk actions can be performed
    - name: "Delete *ALL* Job Templates"
      local_action:
          module: foreman_job_template
          username: "admin"
          password: "admin"
          server_url: "https://foreman.example.com"
          name: "*"
          state: absent

    - name: "Assign all Job Templates to the same organization(s)"
      local_action:
          module: foreman_job_template
          username: "admin"
          password: "admin"
          server_url: "https://foreman.example.com"
          name: "*"
          state: present
          organizations:
          - DALEK INC
          - sky.net
          - Doc Brown's garage






Status
------



This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.



Maintenance
-----------

This module is flagged as **community** which means that it is maintained by the Ansible Community. See :ref:`Module Maintenance & Support <modules_support>` for more info.

For a list of other modules that are also maintained by the Ansible Community, see :ref:`here <community_supported>`.





Author
~~~~~~

- Manuel Bonk (@manuelbonk) ATIX AG
- Matthias Dellweg (@mdellweg) ATIX AG


.. hint::
    If you notice any issues in this documentation you can `edit this document <https://github.com/theforeman/foreman-ansible-modules/edit/master/modules/foreman_job_template.py?description=%3C!---%20Your%20description%20here%20--%3E%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
