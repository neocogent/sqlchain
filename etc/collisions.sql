# Count number of trxs collisions:

select count(*) from trxs where  strcmp(reverse(unhex(hex(id*8))), left(hash,5)) > 0;

# Count number of address collisions:

select  count(*) from address where  cast(conv(hex(reverse(unhex(substr(sha2(addr,0),1,10)))),16,10)*2 as unsigned) != id;

# Make addr_id in SQL

select id,hex(addr),cast(conv(hex(reverse(unhex(substr(sha2(addr,0),1,10)))),16,10)*2 as unsigned) as nid from address limit 20;


# Find missing rows (gaps) in sequence.

SELECT t1.id-1 FROM blkdat t1 LEFT OUTER JOIN blkdat t2 ON t2.id=t1.id-1 WHERE t2.id IS NULL AND t1.id > 0 ORDER BY t1.id;
