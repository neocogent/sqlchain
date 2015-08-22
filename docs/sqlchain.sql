-- create new database during install

-- disabled for safety
-- DROP DATABASE IF EXISTS bitcoin;

CREATE DATABASE bitcoin;
USE bitcoin;

CREATE TABLE `blocks` (
  `id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `coinbase` varbinary(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `address` (
  `id` decimal(13) NOT NULL,
  `addr` binary(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `trxs` (
  `id` decimal(13) NOT NULL,
  `hash` binary(32) NOT NULL,
  `ins` tinyint unsigned NOT NULL,
  `outs` tinyint unsigned NOT NULL,
  `txsize` smallint unsigned NOT NULL,
  `txdata` decimal(13,0) DEFAULT NULL,
  `block_id` decimal(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `block` (`block_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `outputs` (
  `id` decimal(16) NOT NULL,
  `value` decimal(16) DEFAULT NULL,
  `addr_id` decimal(13) DEFAULT NULL,
  `tx_id` decimal(13) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `addr` (`addr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `mempool` (
  `id` decimal(13) NOT NULL,
  `sync_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sync` (`sync_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `orphans` (
  `sync_id` int(11) NOT NULL,
  `block_id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `hdr` binary(80) NOT NULL,
  `coinbase` varbinary(100) NOT NULL,  
  KEY (`sync_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `info` (
  `class` varchar(12) NOT NULL,
  `key` varchar(32) NOT NULL,
  `value` varchar(64) DEFAULT NULL,
  PRIMARY KEY `class` (`class`,`key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

