#!/usr/bin/env python
#
#   sqlchain.utils - unit test module
#

from sqlchain.util import dotdict, is_address, addr2pkh

__builtins__['sqc'] = dotdict()  # container for super globals

sqc.cfg = { 'cointype':'bitcoin' }

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
    #p2wpkh
    assert addr2pkh('BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4') == '751e76e8199196d454941c45d1b3a323f1433bd6'.decode('hex')
    #bech32
    assert addr2pkh('bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx') \
                     == '751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6'.decode('hex') # witver 0x51
    assert addr2pkh('BC1SW50QA3JX3S') == '751e'.decode('hex') # witver 0x60
    assert addr2pkh('bc1zw508d6qejxtdg4y5r3zarvaryvg6kdaj') =='751e76e8199196d454941c45d1b3a323'.decode('hex') # witver 0x52
    
