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

Database sync code updated for SQL transactional engines. Tested with MariaDB using the [RocksDB](https://en.wikipedia.org/wiki/MyRocks) engine. This engine has some nice features but the main ones of interest here are storage size reduction and indexing (instead of Btree) more suited to high entropy keys (tx,address ids). In my tests RocksDB was not much faster initially but didn't drop in speed so much as DB size grows. It's a bit early to fully recommend but initially it looks like a nice option. I'll update the install guide with RocksDB steps (soonish).

Added **bech32** address support (p2wpkh and p2sh). This requires a database upgrade and along with other changes the best option is to re-sync the blockchain. sqlchain will stop if it detects an old db and if re-sync is not possible then reverting to pre v0.2.5 is best.

Now supports multiple blockchains and testnet variants. Currently Litecoin, Dogecoin and Reddcoin have been added as test cases (with demo pages) and I hope to add a few more before long. Each coin requires it's own daemon process but sqlchain-config (sqlchain-init replacement) now takes advantage of systemd "instances" so that several can coexist. This means the systemctl commands are now like `systemctl start sqlchain@bitcoin`, and similarly for other coins. There is only one sqlchain@.service and it creates variant instances for each coin described by it's cfg. Upstart (Ubuntu 14.04) support has been removed - it probably works fine but the setup process now only automates Ubuntu 16.04 (systemd) and newer platforms.

As part of new altcoin support there is now an "overlay" feature where custom modules can be loaded based on cointype or for extending an api. SQL schema can be overridden likewise based on cointype or db name. If you have a custom schema you can have it initialized by sqlchain-config simply by using a matching custom db name. Both these options allow customizing and extending code while easing the burden of merging updates.

New unit tests have been added, see the README in the tests directory. Many bugs fixed and api behaviour improved as a result.

#### Supported Features (with more tested history)

- testnet and segwit - decodes and stores witness data but not much of an segwit api yet
- pruning - since block data is parsing into mysql you can remove old blocks and save ~50% disk space with no loss in api 
- no-sig option - can drop signature and witness data to further reduce disk space for uses not requiring proofs and raw tx data
- external blobs - most signature, witness and script data is offloaded to blobs exteral to mysql, giving finer control (losing indexibility)
- split blobs, s3 ready -  blobs are split in 5GB chunks, allows mapping older tx data to cheaper offline storage like Amazon s3
- blkdat mode - direct reading of bitcoind block files allows much faster initial sync as sqlchain can read while bitcoind is syncing
- blkbtc - utility to block on/off node network traffic to allow more cpu for sqlchain to catch up, or limit disk used by syncing
- sqlchain-config - dialog based utility to ease setup and generate optimal config files 

sqlchain is still *Alpha level* software under sporadic active development (not ready for prime time). 

sqlchain-electrum has not received much love over the last 2 years but I do plan to get it caught up and functioning again.

#### Try It Out

You can try it on Testnet and it doesn't take much time or resources. Even a 1vCPU (1.5 cents/hour) [Vultr](http://www.vultr.com/?ref=7087266) instance can run it quite well. You can snapshot the instance and only run as needed. On this VPS Testnet sync'd in 45 minutes and used ~ 12 GB. It takes ~1.5 days to sync mysql data to block 1156000. The first block with segwit txs seems to be 834624.

#### TODO

- improve the included demo pages
- fix up and do more testing on Electrum server  
- look further into pruning spent outputs (most of blob.dat) for a wallet api with even lower storage needs
- add segwit specific API data 




