Create a basic Activation Key that uses Library LCE, Default Organization View, and performs auto-attach from the set of all available Subscriptions (i.e. auto-attach=true and no Subscriptions are assigned to the Activation Key).

.. code-block:: yaml+jinja

    - hosts: localhost
      roles:
        - role: theforeman.foreman.activation_keys
          vars:
            foreman_server_url: https://foreman.example.com
            foreman_username: "admin"
            foreman_password: "changeme"
            foreman_organization: "Default Organization"
            foreman_activation_keys:
              - name: "Basic Activation Key"
                description: "Registers hosts in Library/Default Organization View and tries to attach the best fitting subscription(s) from all available in the organization"

Define two Activation Keys. The first registers hosts in the "ACME" organization and attaches the Subscription for the custom product "ACME_App". The second assigns the "Test" LCE and "RHEL7_Base" Content View, and auto-attaches the best fitting subscription(s) from all which are available in the ACME Organization:

.. code-block:: yaml+jinja

    - hosts: localhost
      roles:
        - role: theforeman.foreman.activation_keys
          vars:
            foreman_server_url: https://foreman.example.com
            foreman_username: "admin"
            foreman_password: "changeme"
            foreman_organization: "ACME"
            foreman_activation_keys:
              - name: "ACME_App_Key"
                auto_attach: false
                subscriptions:
                  - name: "ACME_App"
              - name: "ACME_RHEL7_Base_Test"
                lifecycle_environment: "Test"
                content_view: "RHEL7_Base"

Following the second example, a Host which is registered using ``subscription-manager register --activationkey ACME_App_Key,ACME_RHEL7_Base_Test`` will get the ACME_App subscription, Test LCE, RHEL7_Base Content View, and auto-attach any additional necessary subscriptions from ACME Organization to cover the Base OS and any other products which require an entitlement certificate.
