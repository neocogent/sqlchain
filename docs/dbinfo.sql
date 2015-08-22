-- dbinfo sample queries 
-- these are used /api/status/db to generate periodic dbinfo values (off by default, see sqlchain-api --dbinfo option)
-- they can be slow and lock up other more important queries so if really needed on a busy server are best done on a replication slave

-- Count number of multi-sig (3-) addresses 
select count(*) from address where id%2=1;

-- Count number of address id collisions (not real collisions because code bumps id but this indicates how well ids map)
select count(*) from address where  cast(conv(hex(reverse(unhex(substr(sha2(addr,0),1,10)))),16,10) as unsigned) != floor(id/2);

-- Count number of tx id collisions (note, as above)
select count(*) from trxs where  strcmp(reverse(unhex(hex(id*8))), left(hash,5)) > 0;

-- Count number of non-std tx outputs (because they don't have an address)
select count(*) from outputs where addr_id=0;

-- Count number of unspent outputs (tx_id is the tx where each output is spent, so null means not spent)
select count(*) from outputs where tx_id is null;

-- Find missing blocks (gaps) in blkdat sequence.
-- select t1.id-1 from blkdat t1 left outer join blkdat t2 on t2.id=t1.id-1 where t2.id is null and t1.id > 0 order by t1.id;

-- Find txs not in mempool but remaining unconfirmed in trxs table - usually rejects or double spend attempts
-- select id,hex(reverse(hash)) from trxs where block_id=-1 and id not in (select id from mempool);
