### sqlChain - The Blockchain as a SQL Layer

**sqlChain** is a *compact* SQL layer that runs on top of bitcoind. It extends the query options on the blockchain with a priority placed on low storage overhead. It provides multiple API (compatible) interfaces:

- Insight API (plus some extensions, like /api/closure)
- Blockchain.info API (including websocket)
- RPC via POST, GET urls
- Web Interface (using bootstrap, integrated with API backend, primarily a demo)
- Electrum Server

**sqlChain** currently consists of three daemon programs.

- **sqlchaind**             - monitors bitcoind and updates a mysql database
- **sqlchain-api**          - provides multiple API interfaces over the mysql database
- **sqlchain-electrum**     - runs a private electrum server over the sqlchain-api layer

#### Recent Updates

Added **bech32** address support (p2wpkh and p2sh). This requires a database upgrade and **sqlchain-upgrade-db** has been provided for this. sqlchaind will detect and stop on old version databases. The upgrade takes quite some time and if you cannot wait then revert your version (< 0.2.5). The upgrade re-encodes how address ids are stored and expands tx/block and outputs/tx limits to better deal with segwit increases. Finally, the part which takes the longest (but can be killed/restarted) is retro-fixing any past bech32 tx outputs that were ignored.

Added support for multiple blockchains and generalized testnet to be handled in this context. Currently Litecoin has been added but not tested in actual use; hopefully will get that done soon and then see about adding more altcoins. Each coin requires it's own daemon process but the sqlchain-init has been upgraded to allow multiple installs to coexist.

Testnet and first partial SegWit support added. Still testing but should be ignored except on testnet where segwit txs exist. Currently decodes and stores witness data but the API doesn't yet return segwit status or witness data. That will come.

Pruning mode now supported with bitcoind >= 0.14.1 with manual pruning mode. This allows deleting block files as they are processed by sqlchain and cuts down on total disk usage by about 50%. Most of the "witness" data is stored in the sqlchain blob file(s). 

Split blobs are now supported by default allowing more flexible locations - you can put recent blobs on SSD and older ones on slower disks or even Amazon S3. You can move a blob and replace with a symlink (but probably should only do that when sqlchain stopped).

Direct block file mode allows processing blocks even when bitcoind is syncing. This would otherwise be difficult due to how syncing impedes RPC call usage. 

The **blkbtc** utility blocks bitcoin network traffic. This allows sqlchain to catch up while pruning block files thereby cutting down on transient storage needs (and sqlchain can also use more cpu resources).

Improved sync speed with another thread to handle output inserts/updates. These can happen "out of band" with the blocks/txs as long as in order. My testing on a "hybrid" 2 Core (8GB, SSD) server showed about double the tx/s conversion rate. 

Added sqlchain-init and installation guide (INSTALL.md) to help users get up and running. I've tested some more on Amazon EC2 and now also on a regular VPS account, and on a few [Vultr](http://www.vultr.com/?ref=7087266) instances. So it's starting to get some workout and more bugs fixed.  

sqlChain is still *Alpha level* software under sporadic active development (not ready for prime time). For this reason the IRC peer discovery for public Electrum servers is not yet implemented, and wont be until enough testing has been completed.

#### Try It Out

You can try it on Testnet and it doesn't take much time or resources. Even a 1vCPU (1.5 cents/hour) [Vultr](http://www.vultr.com/?ref=7087266) instance can run it quite well. You can snapshot the instance and only run as needed. On this VPS Testnet sync'd in 45 minutes and used ~ 12 GB. It takes ~1.5 days to sync mysql data to block 1156000. The first block with segwit txs seems to be 834624.

#### TODO

- more testing on Electrum server and testnet operation  
- look further into pruning spent outputs (most of blob.dat) for a wallet api with even lower storage needs
- add segwit specific API data



