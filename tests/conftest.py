import pytest
def pytest_addoption(parser):
    parser.addoption("--runlive", action="store_true",
        help="run live tests")

