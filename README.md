### sqlChain - The Blockchain as a SQL Layer

**sqlChain** is a *compact* SQL layer that runs on top of bitcoind. It extends the query options on the blockchain with a priority placed on low storage overhead. It provides multiple API (mostly compatible) interfaces:

- Insight API (plus some extensions, like /api/closure)
- Blockchain.info API (including websocket)
- RPC via POST, GET urls
- Web Interface (using bootstrap, integrated with API backend, primarily a demo)
- Electrum Server

(at this time a demo server is being tested locally, but later will be hosted publicly)

**sqlChain** currently consists of three daemon programs.

- **sqlchaind**             - monitors bitcoind and updates a mysql database
- **sqlchain-api**          - provides multiple API interfaces over the mysql database
- **sqlchain-electrum**     - runs an electrum server over the sqlchain-api layer

**sqlchain-api** now uses the gevent.websocket module to provide a low overhead, highly concurrent, WSGI based server. In theory, thousands of connections could use either the websocket, or more simply, the long polling *sync* api.

A new **blkdat** module enables syncing directly from block files. Now sqlchain can build sql data even as bitcoind syncs itself, saving a lot of time on low-end systems. This module includes **btcGate** support for "throttling" a pruning node. It can pause/resume bitcoind to ensure data isn't pruned before being sync'd to mysql (still to be fully tested).

Testing and development is under way to run sqlChain (optionally) on top of a **pruning bitcoind node**, providing full querying with much lower storage demands compared to other API stacks. I expect that a full Electrum server can be run in ~28 GB, and sync each block in ~1 second even on low end hardware. The blockchain is currently close to 51GB and the regular Electrum server adds another 20GB - so this is quite a savings for users who want to run on a VPS where SSD space costs money every month. Also, with sqlChain you do not need to trust a utxo download - it is built from bitcoind (even from a pruning node).

sqlChain is still "Alpha" level software under active development (not ready for prime time) - but I'm busy on getting it there. For this reason the IRC peer discovery for public Electrum servers is not yet implemented, and wont be until enough testing has been completed.





