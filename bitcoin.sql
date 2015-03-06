CREATE TABLE `address` (`id` INTEGER PRIMARY KEY NOT NULL , `addr` BLOB not null) ;
CREATE TABLE `blocks` (`id` INTEGER PRIMARY KEY NOT NULL ,`hash` BLOB NOT NULL ,`time` INTEGER NOT NULL  );
CREATE TABLE `outputs` (`id` INTEGER PRIMARY KEY NOT NULL ,`value` INTEGER,`addr_id` INTEGER );
CREATE TABLE `scripts` (`out_id` INTEGER PRIMARY KEY  NOT NULL ,`script_in` BLOB,`script_out` BLOB);
CREATE TABLE `trxs` (`id` INTEGER PRIMARY KEY NOT NULL , `hash` BLOB NOT NULL , `inputs` BLOB, `outputs` BLOB, `block_id` INTEGER);
CREATE TABLE `hdrs` (`id` INTEGER PRIMARY KEY NOT NULL , `vers` INTEGER, `prevhash` BLOB, `merkle` BLOB, `nbits` INTEGER, `nonce` INTEGER);
