#!/usr/bin/env python
#
#  Scan blockchain blk*.dat files and build index table.
#  With the index, blocks can be read directly for processing.
#
#  If you have a fully sync'd blockchain then this isn't useful as bitcoind 
#  responds fast enough for sqlchaind with rpc calls. This is useful if you
#  want to sync sqlchain while bitcoind is still syncing (to save time on 
#  slow systems) and bitcoind is basically unresponsive via rpc.
#
#  Can run standalone to build blkdat table, or be called by sqlchaind
#  with less verbose logging info. 
#
#  Trails the main chain tip by 60 blocks to avoid reorg problems 
#
import os, sys, signal, getopt, socket, threading
import MySQLdb as db

from struct import pack, unpack, unpack_from
from time import sleep
from hashlib import sha256

from version import *
from util import *

done = threading.Event()
todo = {}
lastpos = (0,0)

cfg = { 'path':'.bitcoin', 'db':'', 'rpc':'' }      

sqlmk='''
CREATE TABLE `blkdat` (
  `id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `prevhash` binary(32) NOT NULL,
  `filenum` int(11) NOT NULL,
  `filepos` int(11) NOT NULL,
  UNIQUE KEY `filenum` (`filenum`,`filepos`),
  KEY `id` (`id`),
  KEY `hash` (`hash`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;'''
  
def BlkDatHandler(cfg, verbose = False):
    global done
    if sqc and 'done' in sqc:
        done = sqc.done
    cur = initdb(cfg)
    blockpath = cfg['blkdat'] + "/blocks/blk%05d.dat"
    while not done.isSet():
        blkhash = findBlocks(cur, blockpath, verbose)
        if blkhash:
            blk,blkhash = getBlk(blkhash)
            if blk:
                log("Blkdat %d - %s" % (blk,blkhash[::-1].encode('hex')) )
                linkMainChain(cfg, cur, blk, blkhash, verbose)
                
def findBlocks(cur, blockpath, verbose):
    global lastpos
    filenum,pos = lastpos
    startpos = pos
    blkhash = None
    if filenum > 0:
        while not os.path.exists(blockpath % (filenum+2,)): # we trail by 2 blks file otherwise not reliable
            for _ in range(12):
                sleep(5)
                if done.isSet():
                    return None
            cur.execute("select 1;") # keepalive during long waits
    try:
        with open(blockpath % filenum, "rb") as fd:
            while not done.isSet():
                fd.seek(pos)
                buf = fd.read(8)
                if len(buf) < 8:
                    break
                magic,blksize = unpack('<II', buf)
                if magic != ( 0xD9B4BEF9 if not sqc.testnet else 0x0709110B ): 
                    if pos-startpos > 1e6: # skip large end gaps
                        break
                    pos += 1
                    continue
                buf = fd.read(80)
                blkhash = sha256(sha256(buf).digest()).digest()
                prevhash = buf[4:36]
                if verbose:
                    log("%05d:%d %s %s" % (filenum, pos, blkhash[::-1].encode('hex')[:32], prevhash[::-1].encode('hex')[:32]) )
                cur.execute("insert ignore into blkdat (id,hash,prevhash,filenum,filepos) values(-1,%s,%s,%s,%s);", (blkhash,prevhash,filenum,pos))
                pos += blksize
                startpos = pos
            lastpos = filenum+1,0
            return blkhash
    except IOError:
        print "No file:", blockpath % filenum
        lastpos = filenum,pos
        sqc.done.set()
        return None

def linkMainChain(cfg, cur, blk, blkhash, verbose):
    global todo
    todo[blk] = blkhash
    if verbose:
        print "TODO", [ (blk,todo[blk][::-1].encode('hex')) for blk in todo ]
    tmp = {}
    for blk in todo:
        blkhash = todo[blk]
        while not done.isSet():
            if verbose:
                log("%d - %s" % (blk, blkhash[::-1].encode('hex')) )
            cur.execute("select id from blkdat where id=%s and hash=%s limit 1;", (blk, blkhash))
            row = cur.fetchone()
            if row:
                break
            cur.execute("update blkdat set id=%s where hash=%s;", (blk, blkhash))
            if cur.rowcount < 1:
                log("Blkdat hash miss for %d, requeued" % blk)
                tmp[blk] = blkhash
                break
            cur.execute("select prevhash from blkdat where id=%s limit 1;", (blk,))
            row = cur.fetchone()
            if row:
                blkhash = row[0]
                blk -= 1
            if blk < 0:
                break
    todo = tmp
            
def getBlk(blkhash):
    blk = sqc.rpc.getblock(blkhash[::-1].encode('hex'))
    blkhash = sqc.rpc.getblockhash(blk['height']-120) # offset to avoid reorg, order problems
    return ( blk['height']-120,blkhash.decode('hex')[::-1] )

def initdb(cfg):
    global todo,lastpos
    sql = db.connect(*cfg['db'].split(':'))
    cur = sql.cursor()
    cur.execute("select count(1) from information_schema.tables where table_name='blkdat';")
    if not cur.fetchone()[0]:
        cur.execute(sqlmk) # create table if not existing
    
    #queries separated for ubuntu 16 compatibility.
    cur.execute("select max(filenum) from blkdat;") # find any previous position
    maxFileNum = cur.fetchone()[0]
    cur.execute("select max(filepos) from blkdat where filenum=%s;", (maxFileNum,) )
    maxFilePos = cur.fetchone()[0]
    row = (maxFileNum, maxFilePos)

    if row != (None,None):
        lastpos = row
        cur.execute("""select (select min(t3.id)-1 from blkdat t3 where t3.id > t1.id) as blk,
                          (select prevhash from blkdat t4 where t4.id=blk+1) as blkhash from blkdat t1 where not exists 
                          (select t2.id from blkdat t2 where t2.id = t1.id + 1) having blk is not null;""") # scan for id gaps, set todo
        for (blk,blkhash) in cur:
            todo[blk] = blkhash    
    return cur

def options(cfg):
    try:                                
        opts,args = getopt.getopt(sys.argv[1:], "hvp:d:r:", 
            ["help", "version", "path=", "db=", "rpc=", "defaults" ])
    except getopt.GetoptError:
        usage()
    for opt,arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-v", "--version"):
            sys.exit(sys.argv[0]+': '+version)
        elif opt in ("-p", "--path"):
            cfg['path'] = arg
        elif opt in ("-d", "--db"):
            cfg['db'] = arg
        elif opt in ("-r", "--rpc"):
            cfg['rpc'] = arg
        elif opt in ("--defaults"):
            savecfg(cfg)
            sys.exit("%s updated" % (sys.argv[0]+'.cfg'))
    
def usage():
    print """Usage: {0} [options...][cfg file]\nCommand options are:\n-h,--help\tShow this help info\n-v,--version\tShow version info
--defaults\tUpdate cfg and exit\nDefault cfg file is {0}.cfg
\nThese options get saved in cfg file as defaults.
-p,--path\tSet path to bitcoin directory
-d,--db  \tSet mysql db connection, "host:user:pwd:dbname"
-r,--rpc\tSet rpc connection, "http://user:pwd@host:port" """.format(sys.argv[0])
    sys.exit(2) 
    
def sigterm_handler(_signo, _stack_frame):
    global done
    done.set()
    
if __name__ == '__main__':
    
    loadcfg(cfg)
    options(cfg)
    
    sqc = dotdict()
    sqc.rpc = rpcPool(cfg)
    
    if cfg['db'] == '':
        print "No db connection provided."
        usage()
    if cfg['rpc'] == '':
        print "No rpc connection provided."
        usage()
    
    verbose = True
    signal.signal(signal.SIGINT, sigterm_handler)
    
    if not os.path.isdir(cfg['path']):
        log("Bad path to bitcoin directory: %s\n" % cfg['path'])
        usage()
    log( 'Using: '+cfg['path'] )
    blockpath = cfg['path'] + "/blocks/blk%05d.dat"
        
    cur = initdb(cfg)
  
    while not done.isSet():
        log( "Finding new blocks" )
        findBlocks(cur, blockpath, verbose)
        
        log( "Getting last block from rpc" )
        blk,blkhash = getLastBlock(cfg)
            
        log( "Linking main chain" )
        linkMainChain(cur, blk, blkhash, verbose)
        
        if not done.isSet():
            log( "Waiting" )
            sleep(60)
    
    log( "Shutting down." )



    
    


    



    
