#
# Common sqlchain support utils
#
import os, sys, pwd, time, json, threading, re, urllib2, hashlib

from datetime import datetime
from struct import pack, unpack, unpack_from
from binascii import unhexlify
from glob import glob
from importlib import import_module
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from backports.functools_lru_cache import lru_cache # pylint:disable=relative-import
from sqlchain.version import coincfg, ADDR_PREFIX, P2SH_PREFIX, P2SH_CHAR, BECH_HRP, BECH32_FLAG, BECH32_LONG, P2SH_FLAG
from sqlchain.version import S3_BLK_SIZE, BLOB_SPLIT_SIZE, BLK_REWARD, HALF_BLKS

tidylog = threading.Lock()

b58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

class dotdict(dict):
    """dot.notation for more concise globals access on dict"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

# address support stuff
def is_address(addr):
    if addr[:2].lower() == coincfg(BECH_HRP):
        return bech32decode(addr) != None
    try:
        n = 0
        for c in addr:
            n = n * 58 + b58.index(c)
        btc = ('%%0%dx' % (25 << 1) % n).decode('hex')[-25:]
        return btc[-4:] == hashlib.sha256(hashlib.sha256(btc[:-4]).digest()).digest()[:4]
    except Exception: # pylint:disable=broad-except
        return False

def mkpkh(pk):
    rmd = hashlib.new('ripemd160')
    rmd.update(hashlib.sha256(pk).digest())
    return rmd.digest()

def addr2pkh(addr):
    if addr[:2].lower() == coincfg(BECH_HRP):
        pkh = bech32decode(addr)
        return str(pkh[2:]) if pkh else None
    long_value = 0L
    for (i, c) in enumerate(addr[::-1]):
        long_value += b58.find(c) * (58**i)
    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result
    nPad = 0
    for c in addr:
        if c == b58[0]:
            nPad += 1
        else:
            break
    result = chr(0)*nPad + result
    return result[1:-4]

def mkaddr(pkh, aid=None, p2sh=False, bech32=False):
    if pkh == '\0'*20 and aid==0:
        return '' # pkh==0 id==0, special case for null address when op_return or non-std script
    if bech32 or (aid and (aid & BECH32_FLAG != 0)):
        return bech32encode(coincfg(BECH_HRP), pkh)
    pad = ''
    an = chr(coincfg(ADDR_PREFIX) if (aid is None and not p2sh) or (aid is not None and (aid & P2SH_FLAG != P2SH_FLAG)) else coincfg(P2SH_PREFIX)) + str(pkh)
    for c in an:
        if c == '\0':
            pad += '1'
        else:
            break
    num = long((an + hashlib.sha256(hashlib.sha256(an).digest()).digest()[0:4]).encode('hex'), 16)
    out = ''
    while num >= 58:
        num,m = divmod(num, 58)
        out = b58[m] + out
    return pad + b58[num] + out

def is_BL32(addr_id):
    return addr_id and (addr_id & BECH32_LONG) == BECH32_LONG

def addr2id(addr, cur=None, rtnPKH=False):
    pkh = addr2pkh(addr)
    if not pkh:
        return None,'' if rtnPKH else None
    addr_id, = unpack('<q', hashlib.sha256(pkh).digest()[:5]+'\0'*3)
    if addr[:2].lower() == coincfg(BECH_HRP): # bech32 has bit 42 set, >20 byte, encode as odd id and stored in bech32 table
        addr_id |= BECH32_FLAG
        if len(pkh) > 20:
            addr_id |= P2SH_FLAG
    elif addr[0] in coincfg(P2SH_CHAR): # encode P2SH flag
        addr_id |= P2SH_FLAG
    if cur:
        tbl = 'bech32' if is_BL32(addr_id) else 'address'
        cur.execute("select id from {0} where id>=%s and id<%s+32 and addr=%s limit 1;".format(tbl), (addr_id,addr_id,pkh))
        row = cur.fetchone()
        return row[0] if row else None
    return (addr_id,pkh) if rtnPKH else addr_id

# script support stuff
def mkSPK(pkh, addr_id):
    if addr_id & BECH32_FLAG: # bech32 id have witness spk
        return ('\x16','\x00\x14%s'%pkh) if (addr_id & P2SH_FLAG != P2SH_FLAG) else ('\x22','\x00\x20%s'%pkh)
    return ('\x19','\x76\xa9\x14%s\x88\xac'%pkh) if (addr_id & P2SH_FLAG != P2SH_FLAG) else ('\x17','\xa9\x14%s\x87'%pkh)

def decodeScriptPK(data):
    result = { 'type':'other', 'data':data } # other, non-std
    if len(data) > 1:
        if len(data) == 25 and data[:3] == '\x76\xa9\x14' and data[23:25] == '\x88\xac': # P2PKH
            result = { 'type':'p2pkh', 'data':'', 'addr':mkaddr(data[3:23]) }
        elif len(data) == 23 and data[:2] == '\xa9\x14' and data[22] == '\x87': # P2SH
            result = { 'type':'p2sh', 'data':'', 'addr':mkaddr(data[2:22],p2sh=True)}
        elif len(data) == 67 and data[0] == '\x41' and data[66] == '\xac': # P2PK
            result = { 'type':'p2pk', 'data':data, 'addr':mkaddr(mkpkh(data[1:66])) }
        elif len(data) >= 35 and data[0] == '\x21' and data[34] == '\xac': # P2PK (compressed key)
            result = { 'type':'p2pk', 'data':data, 'addr':mkaddr(mkpkh(data[1:34])) }
        elif len(data) == 22 and data[:2] == '\x00\x14': # P2WPKH
            result = { 'type':'p2wpkh', 'data':'', 'addr':mkaddr(data[2:22],bech32=True) }
        elif len(data) == 34 and data[:2] == '\x00\x20': # P2WSH
            result = { 'type':'p2wsh', 'data':'', 'addr':mkaddr(data[2:34],bech32=True) }
        elif len(data) >= 38 and data[:6] == '\x6a\x24\xaa\x21\xa9\xed': # witness commitment
            result = { 'type':'witness', 'hash':data[6:38], 'data':data[38:] }
        elif len(data) <= 41 and data[0] == '\x6a': # OP_RETURN
            result = { 'type':'null', 'data':data }
    return result

OpCodes = { '\x4F':'OP_1NEGATE', '\x61':'OP_NOP', '\x63':'OP_IF', '\x64':'OP_NOTIF', '\x67':'OP_ELSE', '\x68':'OP_ENDIF',
            '\x69':'OP_VERIFY', '\x6A':'OP_RETURN', '\x6B':'OP_TOALTSTACK', '\x6C':'OP_FROMALTSTACK', '\x6D':'OP_2DROP', '\x6E':'OP_2DUP',
            '\x6F':'OP_3DUP', '\x70':'OP_2OVER', '\x71':'OP_2ROT', '\x72':'OP_2SWAP','\x73':'OP_IFDUP', '\x74':'OP_DEPTH', '\x75':'OP_DROP',
            '\x76':'OP_DUP', '\x77':'OP_NIP', '\x78':'OP_OVER', '\x79':'OP_PICK', '\x7A':'OP_ROLL', '\x7B':'OP_ROT', '\x7C':'OP_SWAP',
            '\x7D':'OP_TUCK',  '\x7E':'OP_CAT', '\x7F':'OP_SUBSTR', '\x80':'OP_LEFT', '\x81':'OP_RIGHT', '\x82':'OP_SIZE', '\x83':'OP_INVERT',
            '\x84':'OP_AND', '\x85':'OP_OR', '\x86':'OP_XOR', '\x87':'OP_EQUAL', '\x88':'OP_EQUALVERIFY', '\x8B':'OP_1ADD', '\x8C':'OP_1SUB',
            '\x8D':'OP_2MUL', '\x8E':'OP_2DIV', '\x8F':'OP_NEGATE', '\x90':'OP_ABS', '\x91':'OP_NOT', '\x92':'OP_0NOTEQUAL', '\x93':'OP_ADD',
            '\x94':'OP_SUB', '\x95':'OP_MUL', '\x96':'OP_DIV', '\x97':'OP_MOD', '\x98':'OP_LSHIFT', '\x99':'OP_RSHIFT', '\x9A':'OP_BOOLAND',
            '\x9B':'OP_BOOLOR', '\x9C':'OP_NUMEQUAL', '\x9D':'OP_NUMEQUALVERIFY', '\x9E':'OP_NUMNOTEQUAL', '\x9F':'OP_LESSTHAN',
            '\xA0':'OP_GREATERTHAN', '\xA1':'OP_LESSTHANOREQUAL', '\xA2':'OP_GREATERTHANOREQUAL', '\xA3':'OP_MIN', '\xA4':'OP_MAX',
            '\xA5':'OP_WITHIN', '\xA6':'OP_RIPEMD160', '\xA7':'OP_SHA1', '\xA8':'OP_SHA256', '\xA9':'OP_HASH160', '\xAA':'OP_HASH256',
            '\xAB':'OP_CODESEPARATOR ', '\xAC':'OP_CHECKSIG', '\xAD':'OP_CHECKSIGVERIFY', '\xAE':'OP_CHECKMULTISIG', '\xAF':'OP_CHECKMULTISIGVERIFY',
            '\xFD':'OP_PUBKEYHASH', '\xFE':'OP_PUBKEY', '\xFF':'OP_INVALIDOPCODE', '\x50':'OP_RESERVED', '\x62':'OP_VER', '\x65':'OP_VERIF',
            '\x66':'OP_VERNOTIF', '\x89':'OP_RESERVED1', '\x8A':'OP_RESERVED2', '\xB1':'OP_CHECKLOCKTIMEVERIFY', '\xB2':'OP_CHECKSEQUENCEVERIFY' }

def mkOpCodeStr(data, sepOP=' ', sepPUSH='\n'):
    ops,pos = '',0
    while pos < len(data):
        if data[pos] == '\x00':
            ops += 'OP_0'+sepOP
        elif data[pos] <= '\x4C':
            sz, = unpack('<B', data[pos])
            ops += data[pos+1:pos+1+sz].encode('hex')+sepPUSH
            pos += sz
        elif data[pos] == '\x4C':
            sz, = unpack('<B', data[pos+1:])
            ops += data[pos+2:pos+2+sz].encode('hex')+sepPUSH
            pos += sz
        elif data[pos] == '\x4D':
            sz, = unpack('<H', data[pos+1:])
            ops += data[pos+2:pos+2+sz].encode('hex')+sepPUSH
            pos += sz
        elif data[pos] == '\x4E':
            sz, = unpack('<I', data[pos+1:])
            ops += data[pos+2:pos+2+sz].encode('hex')+sepPUSH
            pos += sz
        elif data[pos] >= '\x50' and data[pos] <= '\x60':
            ops += 'OP_'+str(int(ord(data[pos]))-0x50)+sepOP
        elif data[pos] >= '\xB3' and data[pos] <= '\xB9':
            ops += 'OP_NOP'+str(int(ord(data[pos])-0xB2)+1)+sepOP
        else:
            ops += OpCodes[data[pos]]+sepOP
        pos += 1
    return ops[:-1]

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
    block['size'] = off
    block['height'] = 0
    block['coinbase'] = block['tx'][0]['vin'][0]['coinbase']
    if block['version'] > 1 and block['height'] >= 227836 and block['coinbase'][0] == '\x03':
        block['height'] = unpack('<I', block['coinbase'][1:4]+'\0')[0]
    return block

def decodeTx(data): # pylint:disable=too-many-locals
    vers, = unpack_from('<I', data)
    tx = { 'version': vers, 'vin':[], 'vout':[] }
    tx['segwit'] = ( data[4:6] == '\0\1' )
    off = 6 if tx['segwit'] else 4
    vicnt,ioff = decodeVarInt(data[off:off+9])
    off += ioff
    wcnt = vicnt
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
    if tx['segwit']:
        woff = off
        while wcnt > 0:
            scnt,soff = decodeVarInt(data[off:off+9])
            off += soff
            while scnt > 0:
                icnt,ioff = decodeVarInt(data[off:off+9])
                off += icnt+ioff
                scnt -= 1
            wcnt -= 1
        tx['witness'] = data[woff:off]
        tx['txid'] = hashlib.sha256(hashlib.sha256(data[:4]+data[6:woff]+data[off:off+4]).digest()).digest()
    tx['locktime'], = unpack_from('<I', data, off)
    tx['size'] = off+4
    tx['wtxid' if tx['segwit'] else 'txid'] = hashlib.sha256(hashlib.sha256(data[:tx['size']]).digest()).digest()
    return tx

# bech32 support stuff
BECH_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32polymod(values):
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def bech32checksum(hrp, data):
    values = [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp] + data
    polymod = bech32polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def base2cvt(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def bech32verify(hrp, data):
    return bech32polymod([ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp] + data) == 1

def bech32encode(hrp, witprog, witver=0):
    data = [witver] + base2cvt(bytearray(witprog), 8, 5)
    combined = data + bech32checksum(hrp, data)
    return hrp + '1' + ''.join([BECH_CHARSET[d] for d in combined])

def bech32decode(addr):
    if (any(ord(x) < 33 or ord(x) > 126 for x in addr)) or (addr.lower() != addr and addr.upper() != addr):
        return None
    addr = addr.lower()
    pos = addr.rfind('1')
    if pos < 1 or pos + 7 > len(addr) or len(addr) > 90:
        return None
    data = [BECH_CHARSET.find(x) for x in addr[pos+1:]]
    keyhash = base2cvt(data[1:-6], 5, 8, False)
    witver = data[0]+0x50 if data[0] > 0 else 0
    if len(keyhash) < 2 or len(keyhash) > 40 or witver > 96 or (witver==0 and not len(keyhash) in [20,32]):
        return None
    return bytearray([witver,len(keyhash)] + keyhash) if bech32verify(addr[:pos], data) else None

# sqlchain ids support stuff
def txh2id(txh):
    return unpack('<q', txh[:5]+'\0'*3)[0] >> 3

addr_lock = threading.Lock()

def insertAddress(cur, addr):
    addr_id,pkh = addr2id(addr, rtnPKH=True)
    if not addr_id:
        return 0
    tbl = 'bech32' if is_BL32(addr_id) else 'address'
    #start_id = addr_id
    with addr_lock:
        while True:
            cur.execute("select addr from {0} where id=%s".format(tbl), (addr_id,))
            row = cur.fetchone()
            if row is None:
                cur.execute("insert into {0} (id,addr) values(%s,%s)".format(tbl), (addr_id,pkh))
                return addr_id
            elif str(row[0]) == str(pkh):
                return addr_id
            addr_id += 1

def findTx(cur, txhash, mkNew=False, warn=32):
    tx_id = txh2id(txhash)
    warn_id = tx_id+warn
    while True:
        cur.execute("select hash from trxs where id=%s", (tx_id,))
        row = cur.fetchone()
        if row is None:
            if mkNew:
                return (tx_id,False)
            return None
        if str(row[0]) == str(txhash):
            return (tx_id,True) if mkNew else tx_id
        if tx_id > warn_id:
            logts("*** TxId collisions excessive %d => %s ***" % (tx_id,txhash))
            #return (None,False) if mkNew else None
        tx_id += 1

# work and difficulty
def coin_reward(height):
    return float(int(coincfg(BLK_REWARD)) >> int(height // coincfg(HALF_BLKS)))/float(1e8)
def bits2diff(bits):
    return float(0x00ffff * 2**(8*(0x1d - 3))) / float((bits&0xFFFFFF) * 2**(8*((bits>>24) - 3)))
def blockwork(bits):
    bits = int(bits,16)
    return 2**256/((bits&0xFFFFFF) * 2**(8*((bits>>24) - 3))+1)
def int2bin32(val):
    return unhexlify('%064x' % val)

# blob and header file support stuff
def puthdr(blk, cfg, hdr):
    with open(cfg['path']+'/hdrs.dat', 'r+b') as f:
        f.seek(blk*80)
        f.write(hdr)
        f.flush()

def gethdr(blk, cfg, var=None):
    with open(cfg['path']+'/hdrs.dat', 'rb') as f:
        f.seek(blk*80)
        data = f.read(80)
    hdr = dict(zip(['version','previousblockhash','merkleroot', 'time', 'bits', 'nonce'], unpack_from('<I32s32s3I', data)))
    return hdr if var is None else hdr[var] if var != 'raw' else data

def getChunk(chunk, cfg):
    with open(cfg['path']+'/hdrs.dat', 'rb') as f:
        f.seek(chunk*80*2016)
        return f.read(80*2016)

def getBlobHdr(pos, cfg):
    buf = readBlob(int(pos), 13, cfg)
    bits = [ (1,'B',0), (1,'B',0), (2,'H',0), (4,'I',1), (4,'I',0) ]  # ins,outs,tx size,version,locktime
    out,mask = [1],0x80
    for sz,typ,default in bits:
        if ord(buf[0])&mask:
            out.append(unpack('<'+typ, buf[out[0]:out[0]+sz])[0])
            out[0] += sz
        else:
            out.append(default)
        mask >>= 1
    out.append( ord(buf[0])&0x04 == 0 )  # stdSeq
    out.append( ord(buf[0])&0x02 != 0 )  # nosigs
    out.append( ord(buf[0])&0x01 != 0 )  # segwit
    return out # out[0] is hdr size

def getBlobData(txdata, ins, outs=0, txsize=0):
    data = { 'hdr':getBlobHdr(txdata, sqc.cfg), 'ins':[], 'outs':[] }
    if ins >= 0xC0:
        ins = ((ins&0x3F)<<8) + data['hdr'][1]
    if outs >= 0xC0:
        outs = ((outs&0x3F)<<8) + data['hdr'][2]
    if txsize >= 0xFF00:
        txsize = ((txsize&0xFF)<<16) + data['hdr'][3]
    data['size'] = txsize
    vpos = int(txdata) + data['hdr'][0]
    buf = readBlob(vpos, ins*7, sqc.cfg)
    vpos += ins*7
    for n in range(ins):
        data['ins'].append({ 'outid': unpack('<Q', buf[n*7:n*7+7]+'\0')[0] })
    if not data['hdr'][7]: # no-sigs flag
        for n in range(ins):
            vsz,off = decodeVarInt(readBlob(vpos, 9, sqc.cfg))
            sigbuf = readBlob(vpos, off+vsz+(0 if data['hdr'][6] else 4), sqc.cfg)
            data['ins'][n]['sigs'] = sigbuf[off:off+vsz]
            data['ins'][n]['seq'] = '\xFF'*4 if data['hdr'][6] else sigbuf[off+vsz:]
            vpos += off+vsz+(0 if data['hdr'][6] else 4)
    elif not data['hdr'][6]: # non-std seq flag
        buf = readBlob(vpos, ins*4, sqc.cfg)
        for n in range(ins):
            data['ins'][n]['seq'] = buf[n*4:n*4+4]
        vpos += ins*4
    else:
        for n in range(ins):
            data['ins'][n]['seq'] = '\xFF'*4
    for n in range(outs):
        vsz,off = decodeVarInt(readBlob(vpos, 9, sqc.cfg))
        pkbuf = readBlob(vpos+off, vsz, sqc.cfg)
        data['outs'].append(pkbuf)
        vpos += off+vsz
    return data

def mkBlobHdr(tx, ins, outs, nosigs):
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
    if not tx['stdSeq']:
        flags |= 0x04
    if nosigs:
        flags |= 0x02
    if 'segwit' in tx and tx['segwit']:
        flags |= 0x01
    # max hdr = 13 bytes but most will be only 1 flag byte
    return ins,outs,sz,pack('<B', flags) + hdr

blob_lock = threading.Lock()

def insertBlob(data, cfg):
    if len(data) == 0:
        return 0
    fn = '/blobs.dat'
    pos,off = (0,2)
    with blob_lock:
        if not os.path.exists(cfg['path']+fn): # support split blobs
            try:
                fn = '/blobs.%d.dat' % (insertBlob.nextpos//BLOB_SPLIT_SIZE,)
            except AttributeError:
                n = 0
                for f in glob(cfg['path']+'/blobs.*[0-9].dat'): # should happen only once as init
                    n = max(n, int(re.findall(r'\d+', f)[0]))
                pos = os.path.getsize(cfg['path']+'/blobs.%d.dat' % n) if os.path.exists(cfg['path']+'/blobs.%d.dat' % n) else 0
                insertBlob.nextpos =  n*BLOB_SPLIT_SIZE + pos
                fn = '/blobs.%d.dat' % (insertBlob.nextpos//BLOB_SPLIT_SIZE,) # advances file number when pos > split size
            pos,off = (insertBlob.nextpos % BLOB_SPLIT_SIZE, 0)
            rtnpos = insertBlob.nextpos
            insertBlob.nextpos += len(data)
        with open(cfg['path']+fn, 'r+b' if os.path.exists(cfg['path']+fn) else 'wb') as blob:
            blob.seek(pos,off)
            newpos = blob.tell()
            blob.write(data)
        return rtnpos if 'rtnpos' in locals() else newpos


def readBlob(pos, sz, cfg):
    if sz == 0:
        return ''
    fn = '/blobs.dat'
    if not os.path.exists(cfg['path']+fn): # support split blobs
        fn = '/blobs.%d.dat' % (pos//BLOB_SPLIT_SIZE)
        pos = pos % BLOB_SPLIT_SIZE
    if not os.path.exists(cfg['path']+fn): # file missing, try s3 if available
        if 's3' in cfg:
            return s3get(cfg['s3']+fn, pos, sz)
        return '\0'*sz  # data missing, return zeros as null data (not ideal)
    with open(cfg['path']+fn, 'rb') as blob:
        blob.seek(pos)
        return blob.read(sz)

def s3get(blob, pos, sz):
    data = ''
    for blk in range(pos // S3_BLK_SIZE, (pos+sz) // S3_BLK_SIZE + 1):
        data += s3blk(blob, blk)
    return data[ pos % S3_BLK_SIZE : pos % S3_BLK_SIZE + sz ]

@lru_cache(maxsize=512)
def s3blk(blob, blk):
    log( "S3 REQ: %s %d" % (blob,blk) )
    req = urllib2.Request(blob)
    req.add_header('Range', 'bytes=%d-%d' % (blk*S3_BLK_SIZE,(blk+1)*S3_BLK_SIZE-1))
    resp = urllib2.urlopen(req)
    return resp.read(S3_BLK_SIZE)

def getBlobsSize(cfg):
    sz = 0
    for f in glob(cfg['path']+'/blobs*.dat'):
        sz += os.stat(f).st_size
    return sz

# cfg file handling stuff
def loadcfg(cfg):
    cfgpath = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1][0] != '-' else os.path.basename(sys.argv[0])+'.cfg'
    try:
        with open(cfgpath) as json_file:
            cfg.update(json.load(json_file))
    except IOError:
        logts('No cfg file.')
    finally:
        cfg['debug'] = False

def savecfg(cfg):
    cfgpath = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1][0] != '-' else os.path.basename(sys.argv[0])+'.cfg'
    try:
        with open(cfgpath, 'w') as json_file:
            json.dump(cfg, json_file, indent=2)
    except IOError:
        logts('Cannot save cfg file')

def logts(msg):
    tidylog.acquire()
    print datetime.now().strftime('%d-%m-%Y %H:%M:%S'), msg
    sys.stdout.flush()
    tidylog.release()

def log(msg):
    tidylog.acquire()
    print msg
    sys.stdout.flush()
    tidylog.release()

def drop2user(cfg, chown=False):
    if ('user' in cfg) and (cfg['user'] != '') and (os.getuid() == 0):
        pw = pwd.getpwnam(cfg['user'])
        if chown:
            logfile = cfg['log'] if 'log' in cfg else sys.argv[0]+'.log'
            pidfile = cfg['pid'] if 'pid' in cfg else sys.argv[0]+'.pid'
            if os.path.exists(logfile):
                os.chown(logfile, pw.pw_uid, pw.pw_gid)
            if os.path.exists(pidfile):
                os.chown(pidfile, pw.pw_uid, pw.pw_gid)
        os.setgroups([])
        os.setgid(pw.pw_gid)
        os.setuid(pw.pw_uid)
        os.umask(0022)
        log('Dropped to user %s' % cfg['user'])

def getssl(cfg):
    if not ('ssl' in cfg) or (cfg['ssl'] == ''):
        return {}

    logts("Loading SSL certificate chain.")
    if sys.version_info < (2,7,9):
        log("*** Warning: Upgrade to Python 2.7.9 for better SSL security! ***")
        cert = { 'certfile':cfg['ssl'] }                                                        # ssl = key+cert in one file, or cert only
        cert.update({ 'keyfile':cfg['key'] } if ('key' in cfg) and (cfg['key'] != '') else {})  # with key in 2nd file
        return cert

    from gevent.ssl import SSLContext, PROTOCOL_SSLv23 # pylint:disable=no-name-in-module
    context = SSLContext(PROTOCOL_SSLv23)
    context.load_cert_chain(cfg['ssl'], cfg['key'] if ('key' in cfg) and (cfg['key'] != '') else None)
    return { 'ssl_context': context }

rpc_lock = threading.Lock()

class rpcPool(object): # pylint:disable=too-few-public-methods
    def __init__(self, cfg, timeout=30):
        self.url = cfg['rpc']
        self.timeout = timeout
        self.name = None

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError
        rpc_lock.acquire()
        self.name = name
        return self

    def __call__(self, *args):
        name = self.name
        start = time.time()
        wait = 3
        rpc_lock.release()
        rpc_obj = AuthServiceProxy(self.url, None, self.timeout, None)
        while True:
            try:
                result = rpc_obj.__getattr__(name)(*args)
                break
            except JSONRPCException as e:
                if e.code == -5:
                    return None
            except Exception as e: # pylint:disable=broad-except
                log( 'RPC Error ' + str(e) + ' (retrying in %d seconds)' % wait )
                print "===>", name, args
                rpc_obj = AuthServiceProxy(self.url, None, self.timeout, None) # maybe broken, make new connection
                if time.time()-start > 300:  # max wait time
                    return None
                wait = min(wait*2,60)
                time.sleep(wait) # slow down, in case gone away
        return result

def sqlchain_overlay(pattern):
    if not pattern[-3:].lower() =='.py':
        pattern += '.py'
    ovrlist = glob(os.path.dirname(os.path.abspath(__file__))+'/overlay/'+pattern)
    for ovr in ovrlist:
        try:
            modname,_ = os.path.splitext(os.path.split(ovr)[1])
            module = import_module('sqlchain.overlay.'+modname)
            log("Overlay module loaded: %s" % modname)
        except ImportError:
            log("Cannot load overlay: %s" % modname)
            return
        globals().update(
            {n: getattr(module, n) for n in module.__all__} if hasattr(module, '__all__')
            else
            {k: v for (k, v) in module.__dict__.items() if not k.startswith('_') })
