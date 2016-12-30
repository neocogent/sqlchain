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

from bitcoinrpc.authproxy import AuthServiceProxy
from struct import pack, unpack, unpack_from
from time import sleep
from hashlib import sha256

from version import *
from util import *

verbose = False
done = threading.Event()

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
   
def BlkDatHandler(cfg, owner_done):
    global done
    done = owner_done
    cur = initdb(cfg)
    blockpath = cfg['blkdat'] + "/blocks/blk%05d.dat"
    while not done.isSet():
        lastpos = findBlocks(cur, blockpath)
        blk,blkhash = getLastBlock(cfg)
        log("Blkdat at %05d:%d > %d" % (lastpos+(blk,)) )
        linkMainChain(cur, blk, blkhash)
        for _ in range(12):
            if not done.isSet():
                sleep(5)
                
def findBlocks(cur, blockpath):
    global verbose
    cur.execute("select max(filenum) from blkdat;") # find any previous state
    row = cur.fetchone()
    filenum = int(row[0]) if row and row[0] else 0
    cur.execute("select max(filepos) from blkdat where filenum=%s;", (filenum,))
    row = cur.fetchone()
    startpos = pos = row[0] if row and row[0] else 0
    lastfound = 0,0
    verbose = ( pos == 0 )
    while not done.isSet():
        try:
            with open(blockpath % filenum, "rb") as fd:
                while True:
                    fd.seek(pos)
                    buf = fd.read(8)
                    if len(buf) < 8:
                        break
                    magic,blksize = unpack('<II', buf)
                    if magic != 0xD9B4BEF9:
                        if pos-startpos > 1e6: # skip large end gaps
                            break
                        pos += 1
                        continue
                    buf = fd.read(80)
                    blkhash = sha256(sha256(buf).digest()).digest()
                    prevhash = buf[4:36]
                    lastfound = filenum,pos
                    if verbose:
                        log("%05d:%d %s %s" % (filenum, pos, blkhash[::-1].encode('hex')[:32], prevhash[::-1].encode('hex')[:32]) )
                    cur.execute("insert ignore into blkdat (id,hash,prevhash,filenum,filepos) values(-1,%s,%s,%s,%s);", (blkhash,prevhash,filenum,pos))
                    pos += blksize
                    startpos = pos
                    
                filenum += 1
                pos = 0
        except IOError:
            #print "Cannot open ", blockpath % filenum
            return lastfound

def linkMainChain(cur, blk, blkhash):
    blkhash = blkhash.decode('hex')[::-1]
    while not done.isSet():
        if verbose:
            log("%d - %s" % (blk, blkhash[::-1].encode('hex')) )
        cur.execute("select id from blkdat where id=%s and hash=%s limit 1;", (blk, blkhash))
        row = cur.fetchone()
        if row:
            break
        cur.execute("update blkdat set id=%s where hash=%s;", (blk, blkhash))
        if cur.rowcount < 1:
            log("Cannot update %d! Rewinding blkdat." % blk)
            cur.execute("select filenum from blkdat where prevhash=%s limit 1;", (blkhash,))
            cur.execute("delete from blkdat where filenum >= %s;", cur.fetchone()) 
            break
        cur.execute("select prevhash from blkdat where id=%s limit 1;", (blk,))
        row = cur.fetchone()
        if row:
            blkhash = row[0]
            blk -= 1
        if blk < 0:
            break
            
def getLastBlock(cfg):
    blk = 0
    while not done.isSet():
        try: # this tries to talk to bitcoind despite it being comatose
            rpc = AuthServiceProxy(cfg['rpc'], timeout=120)
            if blk == 0:
                blkinfo = rpc.getblockchaininfo()
                blk = blkinfo['blocks'] - 60
            blkhash = rpc.getblockhash(blk) # trailing by 60 to avoid reorg problems
            return blk,blkhash
        except Exception, e:
            log( 'Blkdat rpc ' + str(e) + ' trying again' )
            sleep(5) 
    return 0,''

def initdb(cfg):
    sql = db.connect(*cfg['db'].split(':'))
    cur = sql.cursor()
    cur.execute("select count(1) from information_schema.tables where table_name='blkdat';")
    if not cur.fetchone()[0]:
        cur.execute(sqlmk) # create table if not existing
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
        findBlocks(cur, blockpath)
        
        log( "Getting last block from rpc" )
        blk,blkhash = getLastBlock(cfg)
            
        log( "Linking main chain" )
        linkMainChain(cur, blk, blkhash)
        
        if not done.isSet():
            log( "Waiting" )
            sleep(60)
    
    log( "Shutting down." )



    
    


    



    
