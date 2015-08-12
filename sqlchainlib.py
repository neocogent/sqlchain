#!/usr/bin/env python
#
# common support utils for sqlchain 
#
import os, sys, hashlib, json

from struct import pack, unpack, unpack_from
from datetime import datetime
from hashlib import sha256

# cannot change these without first updating existing table schema and data
# these are set to reasonable values for now - to increase, alter trxs.block_id or outputs.id column widths
# and update data eg. update trxs set block_id=block_id/OLD_MAX*NEW_MAX + block_id%OLD_MAX
MAX_TX_BLK = 10000  # allows 9,999,999 blocks with decimal(11)
MAX_IO_TX = 4096    # allows 37 bit out_id value, (5 byte hash >> 3)*4096 in decimal(16), 7 bytes in blobs

b58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# address support stuff
def is_address(addr):
    try:
        n = 0
        for c in addr:
            n = n * 58 + b58.index(c)
        btc = ('%%0%dx' % (25 << 1) % n).decode('hex')[-25:]
        return btc[-4:] == sha256(sha256(btc[:-4]).digest()).digest()[:4]
    except Exception:
        return False
        
def mkpkh(pk):
    rmd = hashlib.new('ripemd160')
    rmd.update(sha256(pk).digest())
    return rmd.digest()

def addr2pkh(v):
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += b58.find(c) * (58**i)
    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result
    nPad = 0
    for c in v:
        if c == b58[0]: nPad += 1
        else: break
    result = chr(0)*nPad + result
    return result[1:-4]
    
def mkaddr(pkh, aid=0):
    pad = ''
    an = chr(0 if aid%2==0 else 5) + str(pkh)
    for c in an:
        if c == '\0': pad += '1'
        else: break
    num = long((an + sha256(sha256(an).digest()).digest()[0:4]).encode('hex'), 16)
    out = ''
    while num >= 58:
        num,m = divmod(num, 58)
        out = b58[m] + out
    return pad + b58[num] + out 

def addr2id(addr, cur=None, rtnPKH=False):
    pkh = addr2pkh(addr)
    addr_id, = unpack('<q', sha256(pkh).digest()[:5]+'\0'*3) 
    addr_id *= 2
    if addr[0] == '3': # encode P2SH as odd id, P2PKH as even id
        addr_id += 1
    if cur:
        cur.execute("select id from address where id>=%s and id<%s+32 and addr=%s limit 1;", (addr_id,addr_id,pkh))
        row = cur.fetchone()
        return row[0] if row else None
    return addr_id,pkh if rtnPKH else addr_id

# script support stuff
def mkSPK(addr, addr_id):
    return ('\x19','\x76\xa9\x14%s\x88\xac'%addr) if addr_id % 2 == 0 else ('\x17','\xa9\x14%s\x87'%addr)
    
def decodeScriptPK(data):
    if len(data) > 1:
        if data[:3] == '\x76\xa9\x14' and data[23:25] == '\x88\xac': # P2PKH
            return { 'type':'p2pkh', 'data':'', 'addr':mkaddr(data[3:23]) };
        if data[:2] == '\xa9\x14' and data[22] == '\x87': # P2SH
            return { 'type':'p2sh', 'data':'', 'addr':mkaddr(data[2:22],5)};
        if data[0] == '\x41' and data[66] == '\xac': # P2PK
            return { 'type':'p2pk', 'data':data, 'addr':mkaddr(mkpkh(data[1:66])) };
        if data[0] == '\x21' and data[34] == '\xac': # P2PK (compressed key)
            return { 'type':'p2pk', 'data':data, 'addr':mkaddr(mkpkh(data[1:66])) };
        if len(data) <= 41 and data[0] == '\x6a': # NULL
            return { 'type':'null', 'data':data };
    return { 'type':'other', 'data':data } # other, non-std

def decodeVarInt(v):
    if v[0] <= '\xfc':
        return unpack('<B', v[0])[0],1
    if v[0] == '\xfd':
        return unpack('<H', v[1:3])[0],3
    if v[0] == '\xfe':
        return unpack('<I', v[1:5])[0],5
    return unpack('<Q', v[1:9])[0],9
    
def encodeVarInt(v):
    if v <= 252:
        return pack('<B', v)
    if v < 2**16:
        return '\xfd' + pack('<H', v)
    if v < 2**32:
        return '\xfe' + pack('<I', v)
    return '\xff' + pack('<Q', v)

# sqlchain ids support stuff
def txh2id(txh):
    return ( unpack('<q', txh[:5]+'\0'*3)[0] >> 3 )

def insertAddress(cur, addr):
    addr_id,pkh = addr2id(addr, rtnPKH=True)
    start_id = addr_id
    while True:
        cur.execute("select addr from address where id=%s", (addr_id,))
        row = cur.fetchone()
        if row == None:
            cur.execute("insert into address (id,addr) values(%s,%s)", (addr_id, pkh))
            #if addr_id != start_id:
            #    print '!', # collision
            return addr_id
        elif str(row[0]) == str(pkh):
            return addr_id
        addr_id += 2
            
def findTx(cur, txhash, mkNew=False, limit=32):
    tx_id = txh2id(txhash)
    limit_id = tx_id+limit
    start_id = tx_id
    while True:
        cur.execute("select hash from trxs where id=%s", (tx_id,))
        row = cur.fetchone()
        if row == None:
            if mkNew:
                #if tx_id != start_id:
                #    print '#', # collision
                return tx_id
            return None
        if str(row[0][:32]) == txhash:
            return tx_id
        if tx_id > limit_id:
            return None
        tx_id += 1

# blob and header file support stuff 
def puthdr(blk, hdr):
    with open('/var/data/hdrs.dat', 'r+b') as f:
        f.seek(blk*80)
        f.write(hdr)
        f.flush()
        
def gethdr(blk, var=None):
    with open('/var/data/hdrs.dat', 'rb') as f:
        f.seek(blk*80)
        data = f.read(80)
    hdr = dict(zip(['version','previousblockhash','merkleroot', 'time', 'bits', 'nonce'], unpack_from('<I32s32s3I', data)))
    return hdr if var == None else hdr[var] if var != 'raw' else data

def bits2diff(bits):
    return (0x00ffff * 2**(8*(0x1d - 3)) / float((bits&0xFFFFFF) * 2**(8*((bits>>24) - 3))))
    
def getBlobHdr(pos):
    buf = readBlob(int(pos), 13)
    bits = [ (1,'B',0), (1,'B',0), (2,'H',0), (4,'I',1), (4,'I',0) ]  # ins,outs,size,version,locktime
    out,mask = [1],0x80 
    for sz,typ,default in bits:
        v, = unpack('<'+typ, buf[out[0]:out[0]+sz])
        out.append(v if ord(buf[0])&mask else default)
        if ord(buf[0])&mask:
            out[0] += sz
        mask >>= 1
    out.append( ord(buf[0])&mask == 0 )  # stdSeq
    return out # out[0] is hdr size

def mkBlobHdr(ins, outs, tx, stdSeq):
    flags,hdr = 0,''
    sz = tx['size']
    if ins >= 0xC0:
        flags |= 0x80
        hdr += pack('<B', ins & 0xFF)
        ins = 0xC0|(ins>>8)
    if outs >= 0xC0:
        flags |= 0x40
        hdr += pack('<B', outs & 0xFF)
        outs = 0xC0|(outs>>8)
    if sz >= 0xFF00:
        flags |= 0x20
        hdr += pack('<H', sz & 0xFFFF)
        sz = 0xFF00|(sz>>16)
    if tx['version'] != 1:
        flags |= 0x10
        hdr += pack('<I', tx['version'])
    if tx['locktime'] != 0:
        flags |= 0x08
        hdr += pack('<I', tx['locktime'])
    if not stdSeq:
        flags |= 0x04  
    # future use: 0x02 = sigs pruned, 0x01 = pks pruned
    # max hdr = 13 bytes but most will be only 1 flag byte
    return ins,outs,sz,pack('<B', flags) + hdr
    
def insertBlob(data):
    if len(data) == 0:
        return 0
    with open('/var/data/blobs.dat', 'r+b') as blob:
        blob.seek(0,2)
        pos = blob.tell()
        blob.write(data)
    return pos

def readBlob(pos, sz):
    if sz != 0:
        with open('/var/data/blobs.dat', 'rb') as blob:
            blob.seek(pos)
            return blob.read(sz)
    return ''
        
# cfg file handling stuff
def loadcfg(cfg):
    try:
        with open(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1][0] != '-' else sys.argv[0]+'.cfg') as json_file:
            cfg.update(json.load(json_file))
    except IOError:
        logts('No cfg file.')
    finally:
        cfg['debug'] = False

def savecfg(cfg):
    try:
        with open(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1][0] != '-' else sys.argv[0]+'.cfg', 'w') as json_file:
            json.dump(cfg, json_file, indent=2)
    except IOError:
        logts('Cannot save cfg file')

def logts(msg):
    print datetime.now().strftime('%d-%m-%Y %H:%M:%S'), msg
    sys.stdout.flush() 
    

