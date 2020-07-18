import pytest

def pytest_addoption(parser):
    parser.addoption("--runlive", action="store_true", help="run live tests")
    parser.addoption("--nosigs", action="store_true", help="is nosigs db")
    parser.addoption("--dbuser", action="store", default="root:root", help="db user:pwd for mysql tests")
    parser.addoption("--coin", action="store", default="btc", help="set coin type, default btc")
    parser.addoption("--server", action="store", default="localhost:8085/api", help="set api-server: host:port/api-path")
    parser.addoption("--append", action="store_true", help="don't clear previous live test results")

def pytest_configure(config):
    config.addinivalue_line("markers", "live: mark test to run live")
    config.addinivalue_line("markers", "nosigs: mark is nosigs db")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runlive"):
        live = pytest.mark.skipif(not config.getoption("--runlive"), reason = "need --runlive option to run")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(live)
    if config.getoption("--nosigs"):
        nosigs = pytest.mark.skipif(config.getoption("--nosigs"), reason = "cannot test with nosigs db")
        for item in items:
            if "nosigs" in item.keywords:
                item.add_marker(nosigs)
