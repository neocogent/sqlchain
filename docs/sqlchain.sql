-- create new database after install
-- need to do these as mysql root user

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
  `block_id` decimal(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `block` (`block_id`)
) ENGINE={dbeng} DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `outputs` (
  `id` decimal(16) NOT NULL,
  `value` decimal(16) DEFAULT NULL,
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

CREATE TABLE `blkdat` (
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
