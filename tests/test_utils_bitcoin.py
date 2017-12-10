#!/usr/bin/env python
#
#   sqlchain.utils - unit test module
#

import os, sys
from struct import unpack

try:
    import MySQLdb as db
except ImportError:
    print "Cannot run database tests without MySQLdb module"
    
import pytest   
 
from sqlchain.version import ADDR_ID_FLAGS, P2SH_FLAG, BECH32_FLAG, BECH32_LONG
from sqlchain.util import dotdict, is_address, addr2pkh, mkaddr, addr2id, decodeScriptPK, mkOpCodeStr, decodeVarInt, encodeVarInt
from sqlchain.util import txh2id, insertAddress, findTx

__builtins__['sqc'] = dotdict()  # container for super globals
sqc.cfg = { 'cointype':'bitcoin' }

# memory based test db with same schema
# remains after test run for inspection, cleared at start of each run
# does not survive mysql restart or os reboot
@pytest.fixture(scope="module")
def testdb(request):
    if 'MySQLdb' not in sys.modules:
        print "No test db available"
        return None
    dbuser,dbpwd = request.config.getoption("--dbuser").split(':')
    try:
        sql = db.connect('localhost',dbuser,dbpwd,'')
    except db.OperationalError:
        return None
    cur = sql.cursor()
    cur.execute("set sql_notes=0;")
    cur.execute("show databases like 'unittest';")
    if cur.rowcount > 0:
        print "\nClearing test db"
        cur.execute("drop database unittest;")
    sqlsrc = open('/usr/local/share/sqlchain/docs/sqlchain.sql').read()
    sqlcode = ''
    for k,v in [('{dbeng}','Memory'),('{dbname}','unittest'),('{dbpwd}',dbpwd),('{dbuser}',dbuser)]:
        sqlsrc = sqlsrc.replace(k, v)
    for line in sqlsrc.splitlines():
        if line != '' and line[:2] != '--':
            sqlcode += line
    for stmnt in sqlcode.split(';'):
        if stmnt:
            cur.execute(stmnt)
    return cur

def test_is_address():
    #p2pkh
    assert is_address('1FomKJy8btcmuyKBFXeZmje94ibnQxfDEf')
    assert is_address('1EWpTBe9rE27NT9boqg8Zsc643bCFCEdbh')
    assert is_address('1MBxxUgVF27trqqBMnoz8Rr7QATEoz1u2Y')
    assert not is_address('1MBxxUgVF27trqqCMnoz8Rr7QATEoz1u2Y')
    assert not is_address('1EWpTBe9rE27NT9boqg8Zsc643bCFCEdbc')
    assert not is_address('3EWpTBe9rE27NT9boqg8Zsc643bCFCEdbh')
    #p2sh
    assert is_address('3De5zB9JKmwU4zP85EEazYS3MEDVXSmvvm')
    assert is_address('3MixsgkBB8NBQe5GAxEj4eGx5YPxvbaSk9')
    assert is_address('3HQR7C1Ag53BoaxKDeaA97wTh9bpGuUpgg')
    assert not is_address('3HQR7C1Ag53BoaxKDeaA97wTh7bpGuUpgg')
    assert not is_address('2MixsgkBB8NBQe5GAxEj4eGx5YPxvbaSk9')
    #p2wpkh
    assert is_address('bc1qs5d7gy4l7k7nm5rqzda8qruh7kqzhjdhgn7upf')
    assert is_address('bc1qvee24y274ymfxx0luvl2jsr6mfxmewd22jfvwd')
    assert is_address('bc1qxn8tc5kmuu2sevvjz0xxcz4dm2c42pxd9ea0dt')
    assert is_address('BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4')
    assert is_address('BC1SW50QA3JX3S')
    assert is_address('bc1zw508d6qejxtdg4y5r3zarvaryvg6kdaj')
    assert not is_address('bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5')
    assert not is_address('bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5')
    assert not is_address('BC13W508D6QEJXTDG4Y5R3ZARVARY0C5XW7KN40WF2')
    assert not is_address('cb1zw508d6qejxtdg4y5r3zarvaryvg6kdaj')
    #p2wsh
    assert is_address('bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3')
    assert is_address('bc1ql0y3lcuy6937hauw7ur304dd9fmw4ca7tt4kr99uda7cg7walvystw4gyu')
    assert is_address('bc1qadvzzmf5fzh7546n2ms76vkl0rd65wlg753dq4ds0v30urtpxlasf5lc7a')
    assert is_address('bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx')
    assert not is_address('tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sL5k7')
    assert not is_address('bc10w508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kw5rljs90')
    assert not is_address('bc1rw5uspcuh')

def test_addr2pkh():
    #p2pkh
    assert addr2pkh('127RhwC5vQJN4cJ6UaHc1A9NCSpz1e9B4i') =='0c2f3eb0fa5f65269236658bc361187dfaa964bb'.decode('hex')
    assert addr2pkh('1JS2xvSfG2hD3rnMGd3xxEeYSoBs8r7eKh') =='bf362d4dda191483e789ccf3059d6447cd64bb9c'.decode('hex')
    assert addr2pkh('1DK2kyHNMUx8XoWZm9t2GWqJGzqBNxUYuv') =='870a76dd469ab77084229a61984db634abaafb8b'.decode('hex')
    #p2sh
    assert addr2pkh('34H8pSTwFNEngG5xfadqctdQykcGgRmSgf') =='1c6426545908803de2a4ed61caf805ccc282900f'.decode('hex') #2of2
    assert addr2pkh('3KKXcGTmxvedJr9GrzWayA8GVnS5AXm8tj') =='c161e4848786150e2add1a93f084fa94a7259b97'.decode('hex') #2of3
    assert addr2pkh('38oAwJnDWRTWf1GUg7FJ112bjVRoMjvCmV') =='4df2e66aeb640a642c8476185f63e433ad074220'.decode('hex') #3of4
    #p2wpkh-p2sh
    assert addr2pkh('3F2YodB6PAzbov1rAkYVMNu6KBB1g9AHrG') =='924b50fdfc0e0afab1b1d12acae31c3b4a215154'.decode('hex')
    assert addr2pkh('36LF9sFUJQAzGgxKtrVFDcXqmTF9yyVeow') =='32eaeff4e7e856e74dcf0926724d04324320eb75'.decode('hex')
    assert addr2pkh('35FowTfm9qpeKGX9VQuuSrcgDiBd9SczAi') =='271c19a61825788201434354d2a3a6b03d23e316'.decode('hex')
    assert addr2pkh('3Pux8TuPxZHm7RsBvAP9zjkF3jCcw9K7wL') =='f3c501dd6b3086911f7b9e7eea0dade0de025287'.decode('hex')
    #p2wsh-p2sh - unavailble
    #p2wpkh
    assert addr2pkh('BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4').encode('hex') == '751e76e8199196d454941c45d1b3a323f1433bd6' # bip173
    assert addr2pkh('bc1q5lz8xffjt4azkzm4hled45qpgcu46thhl6j7vm').encode('hex') == 'a7c47325325d7a2b0b75bff2dad00146395d2ef7' # electrum
    assert addr2pkh('bc1qzlc8mvcyww95ycfgf520y7yvu64qhta6uqxada').encode('hex') == '17f07db304738b4261284d14f2788ce6aa0bafba' # electrum
    assert addr2pkh('bc1qtcpsntfzjx7mj6ljqy480sdufnh2nuwqhtsz8g').encode('hex') == '5e0309ad2291bdb96bf2012a77c1bc4ceea9f1c0' # electrum
    assert addr2pkh('bc1q0yrdw9t2pyev94jfeyq9mm4a0smfdswfweht6t').encode('hex') == '7906d7156a0932c2d649c9005deebd7c3696c1c9' # electrum
    #p2wsh
    assert addr2pkh('bc1qm7fcgs9ugg66rw5tg2w7sy0m0afttnnucr59hcmpa87sezd769vsac7pmy') \
                    =='df938440bc4235a1ba8b429de811fb7f52b5ce7cc0e85be361e9fd0c89bed159'.decode('hex') #2of2 electrum
    assert addr2pkh('bc1q5gp20lfuhz2avvqwau6sgwmakrp5r2qv66x56rfr9t30halv4vfs283f6e') \
                    =='a202a7fd3cb895d6300eef35043b7db0c341a80cd68d4d0d232ae2fbf7ecab13'.decode('hex') #2of2 electrum
    assert addr2pkh('bc1qs5vep8zczr6rfskq3euz44zjnv05zmhkp84jhkufufsdy2ygfr7qr8x759') \
                    =='8519909c5810f434c2c08e782ad4529b1f416ef609eb2bdb89e260d2288848fc'.decode('hex') #2of2 electrum
    #bech32, future versions from bip173 spec.
    assert addr2pkh('bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx') \
                    == '751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6'.decode('hex') # witver 0x51
    assert addr2pkh('BC1SW50QA3JX3S') == '751e'.decode('hex') # witver 0x60
    assert addr2pkh('bc1zw508d6qejxtdg4y5r3zarvaryvg6kdaj') =='751e76e8199196d454941c45d1b3a323'.decode('hex') # witver 0x52

def test_mkaddr():
    #p2pkh
    assert mkaddr('0c2f3eb0fa5f65269236658bc361187dfaa964bb'.decode('hex')) == '127RhwC5vQJN4cJ6UaHc1A9NCSpz1e9B4i'
    assert mkaddr('bf362d4dda191483e789ccf3059d6447cd64bb9c'.decode('hex')) == '1JS2xvSfG2hD3rnMGd3xxEeYSoBs8r7eKh'
    assert mkaddr('870a76dd469ab77084229a61984db634abaafb8b'.decode('hex')) == '1DK2kyHNMUx8XoWZm9t2GWqJGzqBNxUYuv'
    #p2sh
    assert mkaddr('1c6426545908803de2a4ed61caf805ccc282900f'.decode('hex'),p2sh=True) == '34H8pSTwFNEngG5xfadqctdQykcGgRmSgf'
    assert mkaddr('c161e4848786150e2add1a93f084fa94a7259b97'.decode('hex'),p2sh=True) == '3KKXcGTmxvedJr9GrzWayA8GVnS5AXm8tj'
    assert mkaddr('4df2e66aeb640a642c8476185f63e433ad074220'.decode('hex'),p2sh=True) == '38oAwJnDWRTWf1GUg7FJ112bjVRoMjvCmV'
    #p2wpkh-p2sh
    assert mkaddr('924b50fdfc0e0afab1b1d12acae31c3b4a215154'.decode('hex'),p2sh=True) == '3F2YodB6PAzbov1rAkYVMNu6KBB1g9AHrG'
    assert mkaddr('32eaeff4e7e856e74dcf0926724d04324320eb75'.decode('hex'),p2sh=True) == '36LF9sFUJQAzGgxKtrVFDcXqmTF9yyVeow'
    assert mkaddr('271c19a61825788201434354d2a3a6b03d23e316'.decode('hex'),p2sh=True) == '35FowTfm9qpeKGX9VQuuSrcgDiBd9SczAi'
    #p2wsh-p2sh - unavailble
    #p2wpkh
    assert mkaddr('751e76e8199196d454941c45d1b3a323f1433bd6'.decode('hex'),bech32=True) == 'BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4'.lower()
    assert mkaddr('a7c47325325d7a2b0b75bff2dad00146395d2ef7'.decode('hex'),bech32=True) == 'bc1q5lz8xffjt4azkzm4hled45qpgcu46thhl6j7vm'
    assert mkaddr('7906d7156a0932c2d649c9005deebd7c3696c1c9'.decode('hex'),bech32=True) == 'bc1q0yrdw9t2pyev94jfeyq9mm4a0smfdswfweht6t'
    #p2wsh
    assert mkaddr('df938440bc4235a1ba8b429de811fb7f52b5ce7cc0e85be361e9fd0c89bed159'.decode('hex'),bech32=True) \
                == 'bc1qm7fcgs9ugg66rw5tg2w7sy0m0afttnnucr59hcmpa87sezd769vsac7pmy'
    assert mkaddr('a202a7fd3cb895d6300eef35043b7db0c341a80cd68d4d0d232ae2fbf7ecab13'.decode('hex'),bech32=True) \
                == 'bc1q5gp20lfuhz2avvqwau6sgwmakrp5r2qv66x56rfr9t30halv4vfs283f6e'
    assert mkaddr('8519909c5810f434c2c08e782ad4529b1f416ef609eb2bdb89e260d2288848fc'.decode('hex'),bech32=True) \
                == 'bc1qs5vep8zczr6rfskq3euz44zjnv05zmhkp84jhkufufsdy2ygfr7qr8x759'

def test_addr2id():
    assert addr2id('127RhwC5vQJN4cJ6UaHc1A9NCSpz1e9B4i') & ADDR_ID_FLAGS == 0
    assert addr2id('34H8pSTwFNEngG5xfadqctdQykcGgRmSgf') & ADDR_ID_FLAGS == P2SH_FLAG
    assert addr2id('3Pux8TuPxZHm7RsBvAP9zjkF3jCcw9K7wL') & ADDR_ID_FLAGS == P2SH_FLAG
    assert addr2id('BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4') & ADDR_ID_FLAGS == BECH32_FLAG
    assert addr2id('bc1q0yrdw9t2pyev94jfeyq9mm4a0smfdswfweht6t') & ADDR_ID_FLAGS == BECH32_FLAG
    assert addr2id('bc1qm7fcgs9ugg66rw5tg2w7sy0m0afttnnucr59hcmpa87sezd769vsac7pmy') & ADDR_ID_FLAGS == BECH32_LONG
    assert addr2id('bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx') & ADDR_ID_FLAGS == BECH32_LONG

    assert addr2id('127RhwC5vQJN4cJ6UaHc1A9NCSpz1e9B4i', rtnPKH=True) == (369302191541,'0c2f3eb0fa5f65269236658bc361187dfaa964bb'.decode('hex'))
    assert addr2id('34H8pSTwFNEngG5xfadqctdQykcGgRmSgf', rtnPKH=True) == (1260639692375,'1c6426545908803de2a4ed61caf805ccc282900f'.decode('hex'))
    assert addr2id('3Pux8TuPxZHm7RsBvAP9zjkF3jCcw9K7wL', rtnPKH=True) == (1905635504253,'f3c501dd6b3086911f7b9e7eea0dade0de025287'.decode('hex'))
    assert addr2id('BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4', rtnPKH=True) \
                == (2239906766591,'751e76e8199196d454941c45d1b3a323f1433bd6'.decode('hex'))
    assert addr2id('bc1q0yrdw9t2pyev94jfeyq9mm4a0smfdswfweht6t', rtnPKH=True) \
                == (2322962910768,'7906d7156a0932c2d649c9005deebd7c3696c1c9'.decode('hex'))
    assert addr2id('bc1qm7fcgs9ugg66rw5tg2w7sy0m0afttnnucr59hcmpa87sezd769vsac7pmy', rtnPKH=True) \
                == (3310624892327,'df938440bc4235a1ba8b429de811fb7f52b5ce7cc0e85be361e9fd0c89bed159'.decode('hex'))
    assert addr2id('bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx', rtnPKH=True) \
                == (4041402476188,'751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6'.decode('hex'))

data = [
     ['76a9140c2f3eb0fa5f65269236658bc361187dfaa964bb88ac','p2pkh','','127RhwC5vQJN4cJ6UaHc1A9NCSpz1e9B4i',
        'OP_DUP OP_HASH160 0c2f3eb0fa5f65269236658bc361187dfaa964bb OP_EQUALVERIFY OP_CHECKSIG'], # p2pkh

     ['a9141c6426545908803de2a4ed61caf805ccc282900f87','p2sh','','34H8pSTwFNEngG5xfadqctdQykcGgRmSgf',
        'OP_HASH160 1c6426545908803de2a4ed61caf805ccc282900f OP_EQUAL'], # p2sh

     ['210298d26fa24aca4b1fdf7bc0d73bf875c3e10b198fb47de414cff39c7229dbacc6AC','p2pk',
        '210298d26fa24aca4b1fdf7bc0d73bf875c3e10b198fb47de414cff39c7229dbacc6AC','1G7AYiSCXMKyVeSVcPUe8PqgfygiqxZyeX',
        '0298d26fa24aca4b1fdf7bc0d73bf875c3e10b198fb47de414cff39c7229dbacc6 OP_CHECKSIG'], # p2pk compressed

     ['4104E9A095A6A5790BC82FEADE07EE6FC77B05BC4DE7F3790C36D2ECC886D9EC0AC0E44402759C51ED0D3BA2F53E749B30A6D1772F0DAE1E3F465E8C8828DF899FE2AC','p2pk',
        '4104E9A095A6A5790BC82FEADE07EE6FC77B05BC4DE7F3790C36D2ECC886D9EC0AC0E44402759C51ED0D3BA2F53E749B30A6D1772F0DAE1E3F465E8C8828DF899FE2AC',
        '1JGTdegLcK8N9mqwhXmGjeUgbQNugii3rm', # p2pk uncompressed
        '04e9a095a6a5790bc82feade07ee6fc77b05bc4de7f3790c36d2ecc886d9ec0ac0e44402759c51ed0d3ba2f53e749b30a6d1772f0dae1e3f465e8c8828df899fe2 OP_CHECKSIG'],

     ['a914924b50fdfc0e0afab1b1d12acae31c3b4a21515487','p2sh','','3F2YodB6PAzbov1rAkYVMNu6KBB1g9AHrG',
        'OP_HASH160 924b50fdfc0e0afab1b1d12acae31c3b4a215154 OP_EQUAL'], # p2sh(p2wpkh)

     ['0014a7c47325325d7a2b0b75bff2dad00146395d2ef7','p2wpkh','','bc1q5lz8xffjt4azkzm4hled45qpgcu46thhl6j7vm',
        'OP_0 a7c47325325d7a2b0b75bff2dad00146395d2ef7'], # p2wpkh

     ['0020a202a7fd3cb895d6300eef35043b7db0c341a80cd68d4d0d232ae2fbf7ecab13','p2wsh','',
        'bc1q5gp20lfuhz2avvqwau6sgwmakrp5r2qv66x56rfr9t30halv4vfs283f6e',
        'OP_0 a202a7fd3cb895d6300eef35043b7db0c341a80cd68d4d0d232ae2fbf7ecab13'], # p2wsh

     ['5128751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6','other',
        '5128751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6', # future bech32, witver 0x51

        'bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx',
        'OP_1 751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6'],
     ['6002751e','other','6002751e','BC1SW50QA3JX3S','OP_16 751e'] # future bech32, witver 0x60
]

def test_decodeScriptPK():
    for row in data:
        r = decodeScriptPK(row[0].decode('hex'))
        assert r['type'] == row[1]
        assert r['data'].encode('hex').lower() == row[2].lower()
        if 'addr' in r:
            assert r['addr'] == row[3]

def test_mkOpCodeStr():
    for row in data:
        assert mkOpCodeStr(row[0].decode('hex'), sepPUSH=' ') == row[4]

def test_VarInt():
    values = [  (1, [ 0,1,2,55,192,192,234,252]),
                (3, [ 253, 255,256,257,4000,16500,47654,2**16-1]),
                (5, [2**16,2**16+1,2**16+2,2*2**16,2**24,2**32-1]),
                (9, [2**32,2**32+1,2**32+2,2**40+234,2**42,2**44+2**24-5,2**48 ]) ]
    for (L,grp) in values:
        for N in grp:
            assert decodeVarInt(encodeVarInt(N)) == ( N,L )

def test_insertAddress(testdb, monkeypatch):
    if testdb is None:
        pytest.skip("requires test db to run")
    addrs = [ '1FomKJy8btcmuyKBFXeZmje94ibnQxfDEf','1EWpTBe9rE27NT9boqg8Zsc643bCFCEdbh','1MBxxUgVF27trqqBMnoz8Rr7QATEoz1u2Y',
              '1EWpTBe9rE27NT9b1qg8Zsc643bCFCEdbh','3EWpTBe9rE27NT9boqg8Zsc643bCFCEdbh','3De5zB9JKmwU4zP85EEazYS3MEDVXSmvvm',
              '3MixsgkBB8NBQe5GAxEj4eGx5YPxvbaSk9','3HQR7C1Ag53BoaxKDeaA97wTh9bpGuUpgg','2MixsgkBB8NBQe5GAxEj4eGx5YPxvbaSk9',
              'bc1q5lz8xffjt4azkzm4hled45qpgcu46thhl6j7vm','bc1q0yrdw9t2pyev94jfeyq9mm4a0smfdswfweht6t',
              '1EWpTBe9rE27NT9boqg8Zsc643bCFCEdbh', # duplicate, should not add row
              'bc1q5gp20lfuhz2avvqwau6sgwmakrp5r2qv66x56rfr9t30halv4vfs283f6e' ] # bech32 table, should not add row
             
    def fake_id(addr, cur=None, rtnPKH=False): # forces collisions by always returning same id
        x = monkeypatch._setattr[0][2](addr, cur, rtnPKH)
        return ((x[0]&ADDR_ID_FLAGS)|123456,x[1]) if isinstance(x, tuple) else (x&ADDR_ID_FLAGS)|123456 # keep flags
    monkeypatch.setattr("sqlchain.util.addr2id", fake_id)
    
    for addr in addrs:
        insertAddress(testdb, addr)
    testdb.execute("select count(1) from address where id !=0;")
    assert testdb.fetchone()[0] == 11 # 13 minus 2 addresses not inserted 

def test_findTx(testdb):
    if testdb is None:
        pytest.skip("requires test db to run")
    trxs = []
    tx1 = bytearray(os.urandom(32))
    for x in range(16):
        tx1[-1] = chr((int(tx1[-1])+x)&0xFF) # use sequential tx hashes to test collisions
        tid,new = findTx(testdb, tx1, True)
        testdb.execute("insert ignore into trxs (id,hash,ins,outs,txsize) values (%s,%s,0,0,0);", (tid,tx1))
        trxs.append(tid)
    assert len(set(trxs)) == len(trxs) # all ids should be unique
    
    for x in range(1000):
        tx1 = os.urandom(32)
        assert txh2id(tx1) == unpack('<q', tx1[:5]+'\0'*3)[0] >> 3 # test 1000 randoms hashes match, just for heck of it
