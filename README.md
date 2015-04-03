## sqlCoin - Project to convert Bitcoin blockchain to SQl data

See my [blog series](http://www.neocogent.com) describing work here. At this point this is just a first stab - a python script for converting and first pass on db schema.

Status: stalled waiting on new SSD drive.

This code tests out multipass idea to reduce insertion complexity and improve speed. Turns out the real work is in the outputs table and it's linkages to addresses and transactions. That's the slow part.

Some current numbers as of around block 249,500:

63 million transactions

179 million outputs

62 million addresses

More to follow.




