### sqlChain - The Blockchain as a SQL Layer

**sqlChain** is a *compact* SQL layer that runs on top of bitcoind. It extends the query options on the blockchain with a priority placed on low storage overhead. It provides multiple API (compatible) interfaces:

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

#### Recent Updates

Added pruning support using "manual pruning", prune=1 in bitcoin.conf. This currently requires a custom build with PR$7871 but it's fairly painless and a better way of dealing with pruning blocks once they've been processed into MySQL. With the current blockchain size of 101 GB I'm hopeful this will cut down total storage to about half, maybe.

Also, now testing sqlchain-init - this script asks setup questions and creates the MySQL DB and config files, system user, boot init scripts. I've given it some basic run through but will be testing soon on a fresh pip install to an EC2 server.

**sqlchain-api** now uses the gevent.websocket module to provide a low overhead, highly concurrent, WSGI based server. In theory, thousands of connections could use either the websocket, or more simply, the long polling *sync* api.

A new **blkdat** module enables syncing directly from block files. Now sqlchain can build sql data even as bitcoind syncs itself, saving a lot of time on low-end systems. This module includes **btcGate** support for "throttling" a pruning node. It can pause/resume bitcoind to ensure data isn't pruned before being sync'd to mysql (still to be fully tested).

Testing and development is under way to run sqlChain (optionally) on top of a **pruning bitcoind node**, providing full querying with much lower storage demands compared to other API stacks. I expect that a full Electrum server can be run in ~28 GB, and sync each block in ~1 second even on low end hardware. The blockchain is currently close to 51GB and the regular Electrum server adds another 20GB - so this is quite a savings for users who want to run on a VPS where SSD space costs money every month. Also, with sqlChain you do not need to trust a utxo download - it is built from bitcoind (even from a pruning node).

sqlChain is still *Alpha level* software under active development (not ready for prime time) - but I'm busy on getting it there. For this reason the IRC peer discovery for public Electrum servers is not yet implemented, and wont be until enough testing has been completed.

#### TODO

- create boot init scripts and better install scripting 
- test pruning full sync on an EC2 instance, from scratch, and write an **install guide**
- open server for demo purposes as public api
- more testing on Electrum server operation
- look further into pruning spent trxs for a wallet api with even lower storage needs



