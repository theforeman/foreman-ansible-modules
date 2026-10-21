# -*- coding: utf-8 -*-
# (c) 2026 Jakub Duchek
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def get_host_power_state(module, host_name):
    """Return the normalized power state of a host."""
    if 'power_status' not in module.foremanapi.resource('hosts').actions:
        params = {'id': host_name, 'power_action': 'status'}
        power_state = module.resource_action('hosts', 'power', params=params, ignore_check_mode=True)
        return 'on' if power_state['power'] == 'running' else 'off'

    params = {'id': host_name}
    power_state = module.resource_action('hosts', 'power_status', params=params, ignore_check_mode=True)
    return power_state['state']
