import pytest


def pytest_addoption(parser):
    parser.addoption("--record", action="store_true",
                     help="record new server-responses")


@pytest.fixture
def record(request):
    return request.config.getoption('record')
