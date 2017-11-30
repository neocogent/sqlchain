#
#   Override Block and Tx decoding for Reddcoin (Proof of Stake)
#
#   Changes as per reddcoin source core.h
#
#   CTransaction - if version > POW_TX_VERSION then unsigned int nTime follows nLockTime
#   CBlock - if version > POW_BLOCK_VERSION then BlockSig string follows tx array
#   Transactions can be CoinStake, then Block gets marked as PoSV
#

import hashlib

from struct import unpack, unpack_from
from sqlchain.util import decodeVarInt, decodeScriptPK

POW_BLOCK_VERSION = 2
POW_TX_VERSION = 1

# raw data decoding stuff
def decodeBlock(data):
    hdr = ['version','previousblockhash','merkleroot', 'time', 'bits', 'nonce']
    hv = unpack_from('<I32s32s3I', data)
    block = dict(zip(hdr,hv))
    block['hdr'] = data[:80]
    block['hash'] = hashlib.sha256(hashlib.sha256(block['hdr']).digest()).digest()
    block['bits'] = '%08x' % block['bits']
    txcnt,off = decodeVarInt(data[80:89])
    off += 80
    block['tx'] = []
    while txcnt > 0:
        tx = decodeTx(data[off:])
        block['tx'].append(tx)
        off += tx['size']
        txcnt -= 1
    if block['version'] > POW_BLOCK_VERSION:
        block['blocksig'] = ''
    block['height'] = 0
    block['coinbase'] = block['tx'][0]['vin'][0]['coinbase']
    block['coinstake'] = txcnt > 1 and 'coinstake' in block['tx'][0] # mark as posv when first tx is CoinStake
    if block['version'] > 1 and block['height'] >= 227836 and block['coinbase'][0] == '\x03':
        block['height'] = unpack('<I', block['coinbase'][1:4]+'\0')[0]
    return block

def decodeTx(data): # pylint:disable=too-many-locals
    vers, = unpack_from('<I', data)
    tx = { 'version': vers, 'vin':[], 'vout':[] }
    off = 4
    vicnt,ioff = decodeVarInt(data[off:off+9])
    off += ioff
    while vicnt > 0:
        txid,vout = unpack_from('<32sI', data, off)
        sigsz,soff = decodeVarInt(data[off+36:off+36+9])
        off += soff+36
        seq, = unpack_from('<I', data, off+sigsz)
        if txid == '\0'*32 and vout == 0xffffffff:
            tx['vin'].append({'coinbase':data[off:off+sigsz], 'sequence':seq })
        else:
            tx['vin'].append({'txid':txid, 'vout':vout, 'scriptSig':data[off:off+sigsz], 'sequence':seq })
        off += sigsz+4
        vicnt -= 1
    vocnt,voff = decodeVarInt(data[off:off+9])
    off += voff
    n = 0
    while n < vocnt:
        value, = unpack_from('<Q', data, off)
        pksz,soff = decodeVarInt(data[off+8:off+8+9])
        off += 8+soff
        tx['vout'].append({'value':value, 'n':n, 'scriptPubKey':decodeScriptPK( data[off:off+pksz] ) })
        off += pksz
        n += 1
    if vocnt > 1 and vicnt > 0 and emptyTXO(tx['vout'][0]) and not 'coinbase' in tx['vin'][0]: # mark as coinstake
        tx['coinstake'] = True
    tx['locktime'], = unpack_from('<I', data, off)
    if vers > POW_TX_VERSION:
        tx['time'], = unpack_from('<I', data, off)
        off += 4
    tx['size'] = off+4
    tx['txid'] = hashlib.sha256(hashlib.sha256(data[:tx['size']]).digest()).digest()
    return tx

def emptyTXO(txo):
    return txo['value'] == 0 and txo['scriptPubKey']['type'] == 'other' and txo['scriptPubKey']['data'] == ''
