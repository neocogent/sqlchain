### sqlChain - The Blockchain as a SQL Layer

**sqlChain** is a *compact* SQL layer that runs on top of bitcoind (and some altcoins). It extends the query options on the blockchain with a priority placed on low storage overhead. It provides multiple API (compatible) interfaces:

- Insight API (plus some extensions, like /api/closure)
- Blockchain.info API (including websocket)
- RPC via POST, GET urls
- Web Interface (demo of integrating with API backend; only hints at what you can do)
- Electrum Server (old, still untested, needs TLC)

**sqlChain** currently consists of three daemon programs.

- **sqlchaind**             - monitors bitcoind and updates a mysql database
- **sqlchain-api**          - provides multiple API interfaces over the mysql database
- **sqlchain-electrum**     - runs a private electrum server over the sqlchain-api layer

#### Recent Updates (v0.2.5)

Database sync code updated for SQL transactional engines. Tested with MariaDB using the [TokuDB](https://en.wikipedia.org/wiki/TokuDB) engine. This engine has many advanced features but the main ones of interest here is storage size reduction and fractal indexing (instead of Btree) more suited to high entropy keys (tx,address ids). In my tests TokuDB was not much faster initially but didn't drop in speed as DB size grows. It's a bit early to fully recommend but initially it looks like a nice option. I'll update the install guide with TokuDB steps (soonish).

Added **bech32** address support (p2wpkh and p2sh). This requires a database upgrade and **sqlchain-upgrade-db** has been provided for this. sqlchaind will detect and stop on old version databases. The upgrade takes quite some time and if you cannot wait then revert your version (< 0.2.5). The upgrade re-encodes how address ids are stored and expands tx/block and outputs/tx limits to better deal with segwit increases. Finally, the part which takes the longest (but can be killed/restarted) is retro-fixing any past bech32 tx outputs that were ignored. If you have the space you may be better off syncing a new db and then quick-switching it in rather than taking a live db down to do the upgrade. It's also probably safer in case of an upgrade bug.

Now supports multiple blockchains and testnet variants. Currently Litecoin and Reddcoin have been added as test cases (each with a demo page) and I hope to add a few more before long. Each coin requires it's own daemon process but sqlchain-init has been upgraded to take advantage of systemd "instances" so that several can coexist. This means the systemctl commands are now like `systemctl start sqlchain@bitcoin`, and similarly for other coins. There is only one sqlchain@.service and it creates variant instances for each coin described by it's cfg. Upstart (Ubuntu 14.04) support has been removed - it probably works fine but the setup process now only automates Ubuntu 16.04 (systemd) and newer platforms.

#### Supported Features (with more tested history)

- testnet and segwit - decodes and stores witness data but not much of an segwit api yet
- pruning - since block data is parsing into mysql you can remove old blocks and save ~50% disk space with no loss in api 
- no-sig option - can drop signature and witness data to further reduce disk space for uses not requiring historic proofs
- external blobs - most signature, witness and script data is offloaded to blobs exteral to mysql, giving finer control (losing indexibility)
- split blobs, s3 ready -  blobs are split in 5GB chunks, allows mapping older tx data to cheaper offline storage like Amazon s3
- blkdat mode - direct reading of bitcoind block files allows much faster initial sync as sqlchain can read while bitcoind is syncing
- blkbtc - utility to block on/off node network traffic to allow more cpu for sqlchain to catch up
- sqlchain-init - utility to ask questions and generate optimal config files for easy setup

sqlchain is still *Alpha level* software under sporadic active development (not ready for prime time). 

sqlchain-electrum has not receivedd much love over the last 2 years but I do plan to get it caught up and functioning again.

#### Try It Out

You can try it on Testnet and it doesn't take much time or resources. Even a 1vCPU (1.5 cents/hour) [Vultr](http://www.vultr.com/?ref=7087266) instance can run it quite well. You can snapshot the instance and only run as needed. On this VPS Testnet sync'd in 45 minutes and used ~ 12 GB. It takes ~1.5 days to sync mysql data to block 1156000. The first block with segwit txs seems to be 834624.

#### TODO

- extend to support more altcoins
- improve the included demo pages
- more testing on Electrum server and testnet operation  
- look further into pruning spent outputs (most of blob.dat) for a wallet api with even lower storage needs
- add segwit specific API data 




