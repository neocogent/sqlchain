### sqlchain - Project to convert Bitcoin blockchain to SQL data

See my [blog series](http://www.neocogent.com) describing work here. At this point this is just a first stab - a python script for converting and first pass on db schema.

Update: Resuming work. July 29, 2015 

Have new SSD and built db up to block 353259 but then realized some deficiencies in db schema so reworked and currently rebuilding db. This time I'm keeping track of time and will post details of conversion in a new blog post.

In case anyone watching is confused I've changed the name to "sqlchain". I think this is more suitable as otherwise it seems like another alt coin. If you have cloned the repo you should probably update the origin or upstream url in .git/config even though it will redirect properly (according to github docs).

I've reworked some of the code and have pushed the update (sql db build still in progress). I've altered where script blob data is stored and created a tx_id "back link" in outputs so that it's easy to build tx data sets. This reduces data size while also easing the queries needed to support an api.

The initial beginnings of initially Insight compatible but eventually perhaps will also support blockchain.info.

Warning: work in progress so treat as ALPHA software.

- sqlchain api server, bitpay compatible, initial code added, currently has /block-index and /block (with some missing values)




