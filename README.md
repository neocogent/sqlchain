### sqlchain - The Blockchain as a SQL Layer

**sqlChain** is a *compact* SQL layer that runs on top of bitcoind. It extends the query options on the blockchain with a priority placed on low storage overhead. A demonstration server provides multiple API (mostly compatible) interfaces (all under development):

- Insight API
- Blockchain.info API
- RPC via POST, GET urls
- Web Interface (using bootstrap, integrated with API backend)
- Electrum Server
- WebSocket Feed (soon)

(at this time the demo server is being tested locally, but later will be hosted on a public server)

**sqChain** currently consists of three daemon programs.

- sqlchaind             - monitors bitcoind and updates a mysql database
- sqlchain-api          - provides multiple http API interfaces over the mysql database
- sqlchain-electrum     - runs an electrum server over the sqlchain API layer

sqlchain-electrum is using gevent to provide fast, low overhead connections. sqlchain-api currently uses the Python HTTPServer module but will be migrated to an gevent based WSGI server soon.

Testing and development is under way to run sqlChain (optionally) on top of a pruning bitcoind node, providing full querying with much lower storage demands compared to other API stacks.

sqlChain is still "Alpha" level software under active development (not ready for prime time) - but I'm busy on getting it there.



