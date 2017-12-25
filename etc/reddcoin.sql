-- reddcoin sql def changes:
-- * increase output value amounts to 1 digits because the first few blocks
-- actually have values that require it, and larger colum takes same byte count (8)
-- * increase block_id to allow more than 5,000,000 blocks
-- reddcoin already up to 2,000,000 with ~1 minute blocks

CREATE USER IF NOT EXISTS '{dbuser}'@'localhost';
ALTER USER '{dbuser}'@'localhost' IDENTIFIED BY '{dbpwd}';
GRANT ALL PRIVILEGES ON {dbname}.* TO '{dbuser}'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS {dbname};
USE {dbname};

CREATE TABLE IF NOT EXISTS `blocks` (
  `id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `coinbase` varbinary(100) NOT NULL,
  `chainwork` binary(32) NOT NULL,
  `blksize` int(11) NOT NULL,  
  PRIMARY KEY (`id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `address` (
  `id` decimal(13) NOT NULL,
  `addr` binary(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `bech32` (
  `id` decimal(13) NOT NULL,
  `addr` binary(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `trxs` (
  `id` decimal(13) NOT NULL,
  `hash` binary(32) NOT NULL,
  `ins` tinyint unsigned NOT NULL,
  `outs` tinyint unsigned NOT NULL,
  `txsize` smallint unsigned NOT NULL,
  `txdata` decimal(13) DEFAULT NULL,
  `block_id` decimal(13) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `block` (`block_id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `outputs` (
  `id` decimal(16) NOT NULL,
  `value` decimal(18) DEFAULT NULL,
  `addr_id` decimal(13) DEFAULT NULL,
  `tx_id` decimal(13) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `addr` (`addr_id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `mempool` (
  `id` decimal(13) NOT NULL,
  `sync_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sync` (`sync_id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `orphans` (
  `sync_id` int(11) NOT NULL,
  `block_id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `hdr` binary(80) NOT NULL,
  `coinbase` varbinary(100) NOT NULL,  
  KEY (`sync_id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `blkdat` (
  `id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `prevhash` binary(32) NOT NULL,
  `filenum` int(11) NOT NULL,
  `filepos` int(11) NOT NULL,
  UNIQUE KEY `filenum` (`filenum`,`filepos`),
  KEY `id` (`id`),
  KEY `hash` (`hash`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `info` (
  `class` varbinary(12) NOT NULL,
  `key` varbinary(32) NOT NULL,
  `value` varchar(64) DEFAULT NULL,
  PRIMARY KEY `class` (`class`,`key`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

--dummy row so API will properly return null outputs
INSERT IGNORE INTO `address` (`id`, `addr`) VALUES (0,'');
