# Count number of trxs collisions:

select count(*) from trxs where  strcmp(reverse(unhex(hex(id*16))), left(hash,5)) > 0;

# Count number of address collisions:

select  count(*) from address where  strcmp(reverse(unhex(hex(id/2))), left(addr,5)) > 0;
