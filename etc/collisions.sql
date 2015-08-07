# Count number of trxs collisions:

select count(*) from trxs where  strcmp(reverse(unhex(hex(id*8))), left(hash,5)) > 0;

# Count number of address collisions:

select  count(*) from address where  cast(conv(hex(reverse(unhex(substr(sha2(addr,0),1,10)))),16,10)*2 as unsigned) != id;

# Make addr_id in SQL

select id,hex(addr),cast(conv(hex(reverse(unhex(substr(sha2(addr,0),1,10)))),16,10)*2 as unsigned) as nid from address limit 20;
