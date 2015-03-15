CREATE TABLE `address` (`id` DECIMAL(13) PRIMARY KEY NOT NULL , `addr` BLOB not null) ;
CREATE TABLE `blocks` (`id` INTEGER PRIMARY KEY NOT NULL ,`hash` BLOB NOT NULL ,`hdr` BLOB NOT NULL , `coinbase` BLOB );
CREATE TABLE `outputs` (`id` DECIMAL(15) PRIMARY KEY NOT NULL ,`value` DECIMAL(16),`addr_id` DECIMAL(13) );
CREATE TABLE `scripts` (`out_id` DECIMAL(15) PRIMARY KEY  NOT NULL ,`sig` BLOB DEFAULT null ,`pk` BLOB DEFAULT null );
CREATE TABLE `trxs` (`id` DECIMAL(13) PRIMARY KEY NOT NULL , `hash` BLOB NOT NULL , `inputs` BLOB, `block_id` INTEGER);

