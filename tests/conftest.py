import pytest


TEST_PLAYBOOKS = [
    'activation_key',
    'architecture',
    'auth_source_ldap',
    'bookmark',
    'compute_attribute',
    'compute_profile',
    'compute_resource',
    'content_credential',
    'content_view',
    'content_view_filter',
    'content_view_version',
    'domain',
    'environment',
    'external_usergroup',
    'config_group',
    'filters',
    'global_parameter',
    'host',
    'host_power',
    'hostgroup',
    'image',
    'inventory_plugin',
    'katello_hostgroup',
    'luna_hostgroup',
    'host_collection',
    'installation_medium',
    'job_template',
    'katello_manifest',
    'katello_sync',
    'lifecycle_environment',
    'location',
    'model',
    'operatingsystem',
    'organization',
    'os_default_template',
    'product',
    'provisioning_template',
    'ptable',
    'realm',
    'redhat_manifest',
    'repository',
    'repository_set',
    'role',
    'scc_account',
    'scc_product',
    'scap_content',
    'scap_tailoring_file',
    'search_facts',
    'setting',
    'smart_class_parameter',
    'snapshot',
    'subnet',
    'sync_plan',
    'upload',
    'user',
    'usergroup',
]


def pytest_addoption(parser):
    parser.addoption("--record", action="store_true",
                     help="record new server-responses")


@pytest.fixture
def record(request):
    return request.config.getoption('record')
