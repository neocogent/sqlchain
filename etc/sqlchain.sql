DROP DATABASE IF EXISTS bitcoin;
CREATE DATABASE bitcoin;
USE bitcoin;

CREATE TABLE `blocks` (
  `id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `hdr` varbinary(180) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `address` (
  `id` decimal(13) NOT NULL,
  `addr` binary(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `trxs` (
  `id` decimal(13) NOT NULL,
  `hash` binary(37) NOT NULL,
  `txdata` decimal(13,0) DEFAULT NULL,
  `block_id` int(11) DEFAULT NULL,
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

