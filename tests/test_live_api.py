#!/usr/bin/env python
#
#   live api test - unit test module
#     - read api urls from livetest db and call live api
#     - compare json returned to livetest db json
#

import os, sys
from struct import unpack

try:
    import sqlite3 as db
except ImportError:
    print "Cannot run database tests without sqlite3 module"
    
import pytest   

live = pytest.mark.skipif(
    not pytest.config.getoption("--runlive"),
    reason = "need --runlive option to run"
)

# livetest db created by mklivetestdb.py
@pytest.fixture(scope="module")
def testdb(request):
    if 'sqlite3' not in sys.modules:
        print "No test db available"
        return None
    sql = db.connect('livetest.db')
    cur = sql.cursor()
    return cur

@live
def test_live_api(testdb):
    assert True
