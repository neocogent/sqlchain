import pytest

def pytest_addoption(parser):
    parser.addoption("--runlive", action="store_true", help="run live tests")
    parser.addoption("--server", action="store", default="localhost:8085/api", help="set api-server: host:port/api-path")
    parser.addoption("--append", action="store_true", help="don't clear previous test results")

