#!/usr/bin/env python
#
#   democvt - sqlchain demo web page translator
#
#   This script reads a demo web page, matches api values and replaces them for target altcoins.
#   It's called by the sqlchain-init script to prepare main.html for altcoins. It can also be used
#   as a command line utility for testing.
#
import os, sys

demos = {
    'bitcoin': {
        'text':['Bitcoin SQL Blockchain Explorer'],
        'height':['123432','167324'],
        'blockhash':['0000000000001271efd5d9f7e539909160a181b2c0a2b8c164d6f8159e5c7dd9'],
        'addr':['1JK6pUCAXfnvcbXEpdVSxhVZ8W6kxQ4VEH','1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR','1CmTtsKEqPxZsW3YjGYXbPSY89xrzkhy94',
                '17pfg6L3hT1ZPBASPt7DCQZfy9jWeMGq1W','1M8s2S5bgAzSSzVTeL7zruvMPLvzSkEAuv'],
        'txid':['23bb66ef300714042085d0ed2d05100531e80d5239020545887df059c0178b56',
                '2acba2c6916cdfdbf3584dfdd32534af5031ab076029ff275167fa5181dee0a8'] },

    'testnet': {
        'text':['Bitcoin Testnet SQL Blockchain Explorer'],
        'height':['303303','167324'],
        'blockhash':['000000000000291b489ae609b2f303af605ed5b7b4e2ad786958a3ef65ab6160'],
        'addr':['muPawjrif323ikE2oJM3FbPxvTjGP1zNin','n4CLirZ5vrWxtNvEDDwkddN8g88TQk99WJ','mzvpbN1K77mmU9SHftKBEitmybGFb3CPq7',
                '2N3ccQQtsvEo6VDfzcJqcKGgQQCszym9CTp','2N9c1JWFnAy7XZdhxq9ZNZgfE6jW53sv1fF'],
        'txid':['1851c0248739bb3a71ae6d207748b35b9005d5cc31e2dc255c54a7278edc4c35',
                '1851c0248739bb3a71ae6d207748b35b9005d5cc31e2dc255c54a7278edc4c35'] },

    'litecoin': {
        'text':['Litecoin SQL Blockchain Explorer'],    
        'height':['123432','167327'],
        'blockhash':['7fe250115bee18519dc0025bf9470c5d95838bce835b1796f5fd5e6371bd8328'],
        'addr':['LLv6ZfQzTeyiiSNALTpQmhK88Ty1XyYiWs','LLv6ZfQzTeyiiSNALTpQmhK88Ty1XyYiWs','LWfgd9WVdZk9xioJUCPgjQp2iJgbaekPTf',
                'LbbmyDf1MzdaHFf4Z4ks4Hq7SSJ3Tmftyp','LKL7EX5kv8DLvozG1RbqKE6pWEvSbfDbY1'],
        'txid':['83b249009ce5ca0a79d887f606386bb0953c58b9c45c7986200f4a6681aba65f',
                '799ed5d7fe40dc3af3199f785ad191e3c3059b2e3ccc65ef86dde011597ff595'] },

    'reddcoin': {
        'text':['Reddcoin SQL Blockchain Explorer'],    
        'height':['123433','167324'],
        'blockhash':['554b176777f87f8b127be12dd467fe0484aa003254a617ad2200e7c4cc0a42b9'],
        'addr':['Ru4EobrFWYapv6MehxhF7eZBfRKFjAWqqf','RgQ8kpboZvAXAWcRUByfu5n3ZBHf6ZEkQ','Rk3asChtuHfnQfMibyNZxn6FELK3412uEK',
                'RjA6kSne8LPjJe68YX8bnPj2UiGqMZwryd','Rsu6jg9TvE84vxgVD1DMThKFX9rtupdrSf'],
        'txid':['b9c6fc72eaa058851992d7e6ac73b57168e558c4bb270ed3c45f3b026a751d7e',
                'dcd1567e56ae0b059d171cce848435569f9b755830228bde152c94dc37bbc18f'] },
                
    'dogecoin': {
        'text':['Dogecoin SQL Blockchain Explorer'],    
        'height':['303303','167327'],
        'blockhash':['935cfc6d4cb8488ea57aef1d554c04e33ba42f064df9846464512aa31d74c52c'],
        'addr':['D9dA2K4oqd8YiQ9t8VczCpJGhmKRwznHWr','DMJk1faLQL6bhGJsFgz36BBmcyALCegjKA','DSrtdtVgYxGShc57mZ63s85Me6r7LmDmPn',
                'DM7hNeVygTiuZbDBaoeDhu4ZRbQKJ3U9Vx','DJ6rJ9E7bDmQgP591reRjkgoKDnEfJWDSw'],
        'txid':['c08cb98e668c717f097b047d77dcb48408e34ea59b9c684bdc3816ea589119c5',
                'd34b2a454851d902aafdc7e2ef9de347c4fc84531e66f8a9b7b664682a87113f'] }
}


def democvt(src, dest, cointype):
    if not os.path.exists(src) or not cointype in demos:
        return False
    html = open(src).read()
    for k in demos[cointype].keys():
        for n,s in enumerate(demos[cointype][k]):
            html = html.replace(demos['bitcoin'][k][n], s)
    with open(dest, 'w') as f:
        f.write(html)
    return True

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print "Usage: %s <srcfile> <destfile> <cointype>" % sys.argv[0]
        sys.exit(0)

    democvt(sys.argv[1], sys.argv[2], sys.argv[3])
