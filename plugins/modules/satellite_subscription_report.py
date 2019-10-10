#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}


DOCUMENTATION = """
---
module: satellite_subscription_report
short_description: Red Hat Satellite subcription (license) reporting module
description:
  - This module reports the subscription usage in a Red Hat Satellite server.
  - It will generate a CSV file with an overview of the subscription totals or the subscriptions assigned to hosts.
version_added: "2.9"
author:
  - "Luc Stroobant (@stroobl)"
options:
  hostname:
    description:
      - Red Hat Satelite server (6.x) hostname.
    required: yes
  url_username:
    description:
      - Satellite server user.
    required: yes
    aliases: [username]
  url_password:
    description:
      - Satellite server password.
    required: yes
    aliases: [password]
  org_id:
    description:
      - Satellite organization ID to work on.
    required: yes
  state:
    description:
      - overview = subscriptions consumed and available.
      - host_assigned = asigned subscriptions per host.
    choices: [overview, host_assigned]
    default: overview
  content_hosts:
    description:
      - Content host(s) to search for when executing host_assigned.
      - Can be a single host or hostname search query accepted by the satellite.
  subscription:
    description:
      - Subscription name or search patern to report for.
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: yes
  dest:
    description:
        - CSV report file path.
"""

EXAMPLES = """
- name: report on subscription usage
  satellite_subscription:
    hostname: satellite.domain.local
    state: overview
    user: admin
    password: adminpass
    org_id: 1
    dest: subscription_overview.csv

- name: report on subscriptions per host
  satellite_subscription:
    hostname: satellite.domain.local
    state: host_assigned
    user: admin
    password: adminpass
    org_id: 1
    dest: host_assigned.csv
"""

RETURN = """
status:
  description: The result of the requested action
  returned: success
  type: str
  sample: Subscription assigned
errors:
  description: Errors when trying to execute action
  returned: success
  type: str
  sample: Authentication failed
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import url_argument_spec, fetch_url
from ansible.module_utils.satellite import request, host_list


def host_assigned_csv(host_list, dest):
    """Create host assign CSV file"""

    csv = open(dest, "w")
    csv.write(
        "Name;Model name;Sockets;Cores per Socket;Memory (KB);Virtual Host;Virtual Guests;Total guests;Subscriptions\n"
    )
    for hid in host_list.values():
        csv.write("{name};{model_name};{sockets};{cores_per_socket};{memory_kb};".format(**hid))
        if "virtual_host" in hid:
            csv.write("{0};".format(hid["virtual_host"]["name"]))
        else:
            csv.write(";")
        if "virtual_guests" in hid:
            hid["total_guests"] = len(hid["virtual_guests"])
            csv.write(", ".join([guest["name"] for guest in hid["virtual_guests"]]))
            csv.write(";")
        else:
            hid["total_guests"] = 0
            csv.write(";")
        csv.write("{total_guests};".format(**hid))
        if "subscriptions" in hid:
            rh_subscriptions = []
            for sub in hid.get("subscriptions", []):
                # exclude non Red Hat subscriptions (custom products)
                if sub["account_number"] is not None and sub["product_id"]:
                    rh_subscriptions.append("{name} ({quantity_consumed} consumed {type})".format(**sub))
            csv.write(", ".join(rh_subscriptions))
        csv.write(";\n")
    csv.close()
    return


def host_assigned(module, sat_url, hosts):
    """"Get assigned subscriptions for hosts"""

    # Process hosts and create hosts_list with assigned subscriptions
    host_list = {}
    for host in hosts:
        if host["id"]:
            host_list.setdefault(host["id"], {})["name"] = host["name"]
            # request detailed info for host
            url = "{0}/api/hosts/{1}".format(sat_url, host["id"])
            host_info = request(module, url, False)
            # Initialize system info vars
            host_list[host["id"]]["sockets"] = -1
            host_list[host["id"]]["cores_per_socket"] = -1
            host_list[host["id"]]["memory_kb"] = -1
            # and set them if we have facts defined:
            if "facts" in host_info:
                host_list[host["id"]]["sockets"] = host_info["facts"]["cpu::cpu_socket(s)"]
                host_list[host["id"]]["cores_per_socket"] = host_info["facts"]["cpu::core(s)_per_socket"]
                host_list[host["id"]]["memory_kb"] = host_info["facts"]["memory::memtotal"]
            if "model_name" in host_info:
                host_list[host["id"]]["model_name"] = host["model_name"]
            # if this is a subscribed host:
            if "subscription_global_status" in host_info:
                # assign already available subscription info
                if "subscription_facet_attributes" in host_info:
                    if host_info["subscription_facet_attributes"]["virtual_host"]:
                        host_list[host["id"]]["virtual_host"] = {}
                        host_list[host["id"]]["virtual_host"] = host_info["subscription_facet_attributes"][
                            "virtual_host"
                        ]
                    if "virtual_guests" in host_info["subscription_facet_attributes"]:
                        host_list[host["id"]]["virtual_guests"] = {}
                        host_list[host["id"]]["virtual_guests"] = host_info["subscription_facet_attributes"][
                            "virtual_guests"
                        ]
                        host_list[host["id"]]["total_guests"] = len(
                            host_info["subscription_facet_attributes"]["virtual_guests"]
                        )
                    else:
                        host_list[host["id"]]["total_guests"] = 0
                # and finally, request the attached subscriptions for this host
                url = "{0}/api/hosts/{1}/subscriptions".format(sat_url, host["id"])
                subs = request(module, url, True)
                host_list[host["id"]]["subscriptions"] = {}
                host_list[host["id"]]["subscriptions"] = subs
            else:
                # unsubscribed host, pass
                pass

    return host_list


def subscription_report(subs):
    """Process the data from the webservice call"""

    sub_report = {}
    for sub in subs:
        # exclude non Red Hat subscriptions (custom products)
        if sub["account_number"] is not None and sub["product_id"]:
            # Don't report stacked subscriptions
            if sub["type"] not in ["STACK_DERIVED"]:
                product_id = sub_report.setdefault(
                    sub["product_id"], dict(name=sub["name"], available=0, consumed=0, quantity=0)
                )
                product_id["available"] += sub["available"]
                product_id["consumed"] += sub["consumed"]
                product_id["quantity"] += sub["quantity"]

    return sub_report


def subscription_report_csv(sub_report, dest):
    """Create a CSV with the subscription report"""

    with open(dest, "w") as csv:
        csv.write("Name;Available;Consumed;Quantity\n")
        for key in sub_report.values():
            csv.write("{name};{available};{consumed};{quantity}\n".format(**key))
    return


def main():

    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            url_username=dict(type='str', required=True, aliases=['username']),
            url_password=dict(type='str', required=True, no_log=True, aliases=['password']),
            org_id=dict(type='int', required=True),
            state=dict(type='str', default="overview", choices=["overview", "host_assigned"]),
            content_hosts=dict(type='str'),
            subscription=dict(type='str'),
            dest=dict(type='str', required=True),
            validate_certs=dict(type='bool', default=True),
        ),
        supports_check_mode=False,
    )

    # Force basic auth for satellite api calls
    module.params["force_basic_auth"] = True

    hostname = module.params["hostname"]
    state = module.params["state"]
    org = module.params["org_id"]
    content_hosts = module.params["content_hosts"]
    dest = module.params["dest"]
    subscription = module.params["subscription"]

    errors, result = None, None
    changed = False
    sat_url = "https://{0}".format(hostname)

    if state == "overview":
        params = {}
        if subscription:
            params["search"] = subscription
        url = "{0}/katello/api/organizations/{1}/subscriptions".format(sat_url, org)
        subs = request(module, url, True, params)
        sub_report = subscription_report(subs)
        subscription_report_csv(sub_report, dest)

    elif state == "host_assigned":
        hosts = host_list(module, sat_url, org, content_hosts)
        hosts_assigned = host_assigned(module, sat_url, hosts)
        host_assigned_csv(hosts_assigned, dest)

    module.exit_json(changed=changed, status=result, error=errors)


if __name__ == "__main__":
    main()
