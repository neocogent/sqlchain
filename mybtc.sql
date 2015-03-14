CREATE TABLE `address` (`id` INTEGER PRIMARY KEY NOT NULL , `addr` BLOB not null) ;
CREATE TABLE `blocks` (`id` INTEGER PRIMARY KEY NOT NULL ,`hash` BLOB NOT NULL ,`hdr` BLOB NOT NULL , "coinbase" BLOB );
CREATE TABLE `outputs` (`id` INTEGER PRIMARY KEY NOT NULL ,`value` INTEGER,`addr_id` INTEGER );
CREATE TABLE `scripts` (`out_id` INTEGER PRIMARY KEY  NOT NULL ,"sig" BLOB DEFAULT (null) ,"pk" BLOB DEFAULT (null) );
CREATE TABLE `trxs` (`id` INTEGER PRIMARY KEY NOT NULL , `hash` BLOB NOT NULL , `inputs` BLOB, `outputs` BLOB, `block_id` INTEGER);

