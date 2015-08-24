#
#  RPC compatible API module
#  
import urlparse, cgi, json, decimal

from bitcoinrpc.authproxy import AuthServiceProxy
from util import *

# encode json btc values as satoshi integer
class btcEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(float(o)*1e8)
        return super(btcEncoder, self).default(o)
        
def do_RPC(env, send_resp):
    get,args,cur = urlparse.parse_qs(env['QUERY_STRING']), env['PATH_INFO'].split('/')[2:], sqc.dbpool.get().cursor()
    send_resp('200 OK', [('Content-Type', 'application/json')])
    if args[0] == "getblockcount":
        return json.dumps(sqc.cfg['block'])
    if args[0] == "getinfo":
        return json.dumps( { 'blocks':sqc.cfg['block'], 'difficulty':bits2diff(gethdr(sqc.cfg['block'], 'bits', sqc.cfg['path'])) } )
    if args[0] == "getdifficulty":
        return json.dumps( bits2diff(gethdr(sqc.cfg['block'], 'bits', sqc.cfg['path'])) )
        
    rpc = AuthServiceProxy(sqc.cfg['rpc'])
    if args[0] == "getblock":
        return json.dumps( rpc.getblock(args[1]), cls=btcEncoder )
    if args[0] == "getblockhash":
        return json.dumps( rpc.getblockhash(int(args[1])) )
    if args[0] == "getrawtransaction":
        return json.dumps( rpc.getrawtransaction(args[1], 1), cls=btcEncoder )
    if args[0] == "gettxout":
        return json.dumps( rpcTxOut(cur, args[1], args[2]) )
    if args[0] == "getmempoolinfo":
        return json.dumps( rpc.getmempoolinfo(), cls=btcEncoder )
    if args[0] == "getrawmempool":
        return json.dumps( rpc.getrawmempool(False), cls=btcEncoder )
    return []

def rpcTxOut(cur, txhash, out):
    return 'blah' # todo find output in fmt below

'''
{
    "bestblock" : "00000000c92356f7030b1deeab54b3b02885711320b4c48523be9daa3e0ace5d",
    "confirmations" : 0,
    "value" : 0.00100000,
    "scriptPubKey" : {
        "asm" : "OP_DUP OP_HASH160 a11418d3c144876258ba02909514d90e71ad8443 OP_EQUALVERIFY OP_CHECKSIG",
        "hex" : "76a914a11418d3c144876258ba02909514d90e71ad844388ac",
        "reqSigs" : 1,
        "type" : "pubkeyhash",
        "addresses" : [
            "mvCfAJSKaoFXoJEvv8ssW7wxaqRPphQuSv"
        ]
    },
    "version" : 1,
    "coinbase" : false
}

'''
