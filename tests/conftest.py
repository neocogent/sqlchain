import pytest

def pytest_addoption(parser):
    parser.addoption("--runlive", action="store_true", help="run live tests")
    parser.addoption("--server", action="store", default="localhost:8085", help="set api-server: host:port")

@pytest.fixture
def server(request):
    return request.config.getoption("--server")
