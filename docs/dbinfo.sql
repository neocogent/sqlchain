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
-- SELECT t1.id-1 FROM blkdat t1 LEFT OUTER JOIN blkdat t2 ON t2.id=t1.id-1 WHERE t2.id IS NULL AND t1.id > 0 ORDER BY t1.id;
