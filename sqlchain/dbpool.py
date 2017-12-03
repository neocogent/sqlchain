"""
The MIT License

Copyright (C) 2012 Gordon Chan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
#  Extended from gevent.db by neocogent
#  Original: https://github.com/gordonc/gevent-db/blob/master/db.py
#
#  Modified for use with MySQLdb
#  - allowing it to take a connection list arg as well as string
#  - adding a cursor __iter__ to allow iteration like MySQLdb supports.
#  - adding __enter__ and __exit_ to support using "with" context manager
#  - adding executemany on cursor
#  - original license copied into file to avoid confusion
#
import gevent.socket
from gevent import queue

# avoid socket monkey patching
import imp
fp, pathname, description = imp.find_module('socket')
try:
    socket_ = imp.load_module('socket_', fp, pathname, description)
finally:
    if fp:
        fp.close()

import threading
import logging

KEEPALIVE_PERIOD = 1800

class DBPool():
    def __init__(self,connectionstring,poolsize,modulename='pyodbc'):
        self.conns = [DBConnection_(socket_.socketpair()) for x in xrange(poolsize)]
        self.threads = [threading.Thread(target=self.worker, args=(self.conns[x],)) for x in xrange(poolsize)]
        self.queue = queue.Queue(poolsize)
        for i in xrange(poolsize):
            self.threads[i].daemon = True
            self.threads[i].start()
            self.conns[i].connect(connectionstring,modulename)
            self.queue.put(self.conns[i])
        if KEEPALIVE_PERIOD > 0:
            self.monitor = gevent.spawn(self.keepalive)

    def keepalive(self):
        while True:
            for n in range(len(self.conns)):
                self.get().cursor().execute("select 1;")
            gevent.sleep(KEEPALIVE_PERIOD)

    def worker(self,conn):
        while True:
            conn.pipe[1].recv(1)
            try:
                function = conn.state.function
                args = conn.state.args
                conn.state.ret = function(*args)
                conn.state.status = 0
            except Exception as inst:
                conn.state.error = inst
                conn.state.status = -1
            finally:
                conn.pipe[1].send('\0')

    def get(self, commit=True):
        c = self.queue.get()
        if callable(c.conn.autocommit):
            c.conn.autocommit(commit)
        else:
            c.conn.autocommit = commit
        return DBConnection(self,c)

class DBConnection_():
    class State():
        pass

    def __init__(self,pipe):
        self.pipe = pipe
        self.state = self.State()

    def connect(self,connectionstring,modulename):
        self.conn = self.apply(__import__(modulename).connect,*(connectionstring,) if isinstance(connectionstring, basestring) else connectionstring)

    def __del__():
        self.conn.close()

    def apply(self,function,*args):
        logging.info(args)

        self.state.function = function
        self.state.args = args
        gevent.socket.wait_write(self.pipe[0].fileno())
        self.pipe[0].send('\0')
        gevent.socket.wait_read(self.pipe[0].fileno())
        self.pipe[0].recv(1)
        if self.state.status != 0:
            raise self.state.error
        return self.state.ret

class DBConnection():
    def __init__(self,pool,conn_):
        self.pool = pool
        self.conn_ = conn_

    def apply(self,function,*args):
        return self.conn_.apply(function,*args)

    def __del__(self):
        self.pool.queue.put(self.conn_)

    def cursor(self):
        return DBCursor(self,self.conn_.apply(self.conn_.conn.cursor))

class DBCursor():
    def __init__(self,conn,cursor):
        self.conn = conn
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, type, value, traceback):
        pass

    def __iter__(self,*args):
        return self.conn.apply(self.cursor.__iter__,*args)

    def execute(self,*args):
        return self.conn.apply(self.cursor.execute,*args)

    def executemany(self,*args):
        return self.conn.apply(self.cursor.executemany,*args)

    def fetchone(self,*args):
        return self.conn.apply(self.cursor.fetchone,*args)

    def fetchall(self,*args):
        return self.conn.apply(self.cursor.fetchall,*args)

    def fetchmany(self,*args):
        return self.conn.apply(self.cursor.fetchmany,*args)

    @property
    def description(self):
        return self.cursor.description

import unittest
import time

class TestDBPool(unittest.TestCase):
    def percentile(self,timings,percent):
        idx = int((len(timings)-1) * percent)
        return timings[idx]

    def test_benchmark(self):
        requests = 1000
        concurrency = 10
        sql = 'SELECT 1'

        timings = []
        def timer(pool,sql):
            conn = pool.get()
            t0 = time.time()
            cursor = conn.cursor()
            cursor.execute(sql)
            timings.append(time.time()-t0)

        pool = DBPool(':memory:',concurrency,'sqlite3')

        greenlets = []
        for i in xrange(requests):
            greenlets.append(gevent.spawn(timer,pool,sql))

        for g in greenlets:
            g.join()

        print '66%% %f' % self.percentile(timings,0.66)
        print '90%% %f' % self.percentile(timings,0.90)
        print '99%% %f' % self.percentile(timings,0.99)
        print '99.9%% %f' % self.percentile(timings,0.999)
        print '100%% %f' % self.percentile(timings,1.00)

if __name__ == '__main__':
    unittest.main()
