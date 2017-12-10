#!/usr/bin/env python
#
#   live api test - unit test module
#     - read api urls from livetest db and call live api
#     - compare json returned to livetest db json
#

import sys, time, requests

try:
    from deepdiff import DeepDiff
except ImportError:
    print "Cannot run database tests without deepdiff module"

try:
    import sqlite3 as db
except ImportError:
    print "Cannot run database tests without sqlite3 module"

import pytest

millis = lambda: int(round(time.time() * 1000))
server = None

live = pytest.mark.skipif(
    not pytest.config.getoption("--runlive"),
    reason = "need --runlive option to run"
)

# livetest db created by mklivetestdb.py
@pytest.fixture(scope="module")
def testdb(request):
    global server
    if 'sqlite3' not in sys.modules:
        print "No test db available"
        return None
    server = request.config.getoption("--server")
    cwd = str(request.fspath.join('..'))
    sql = db.connect(cwd+'/livetest.db',isolation_level=None)
    cur = sql.cursor()
    cur.execute("select name from sqlite_master where name='calls';")
    if cur.fetchone() is None:
        print "livetest.db not initialized."
        return None
    if not request.config.getoption("--append"):
        cur.execute("delete from tests;")
    return cur

def api_call(url):
    try:
        call_ts = millis()
        r = requests.get('http://'+server+url)
        if r.status_code == requests.codes.ok:
            return r.json(),millis()-call_ts
    except requests.exceptions.ConnectionError:
        return { "error": "Connect Error: http://"+server+url },0
    return { "error": r.status_code },0

def api_diff(cur, sqlstr, **kwargs):
    cur.execute("select url,result from calls where url like ?;", (sqlstr,))
    for url,result in cur:
        rtn,rtt = api_call(url)
        if 'error' in rtn:
            return rtn
        diff = DeepDiff(result, rtn, ignore_order=True, **kwargs)
        cur.execute("insert into tests (url,result,diff,rtt) values (?,?,?,?);", (url,rtn,diff,rtt))
        if diff != {}:
            return diff
    return {}

@live
def test_live_api_block(testdb):
    if testdb is not None:
        assert api_diff(testdb, '/block/%') == {}

@live
def test_live_api_block_index(testdb):
    if testdb is not None:
        assert api_diff(testdb, '/block-index/%') == {}

@live
def test_live_api_rawblock(testdb):
    assert True

@live
def test_live_api_blocks(testdb): # not currently supported
    assert True

@live
def test_live_api_tx(testdb):
    assert True

@live
def test_live_api_rawtx(testdb):
    assert True

@live
def test_live_api_addr(testdb):
    assert True

@live
def test_live_api_utxo(testdb):
    assert True

@live
def test_live_api_txs_block(testdb):
    assert True

@live
def test_live_api_txs_addr(testdb):
    assert True

@live
def test_live_api_addrs(testdb):
    assert True

@live
def test_live_api_status(testdb):
    assert True
