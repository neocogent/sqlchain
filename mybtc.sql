DROP DATABASE IF EXISTS bitcoin;
CREATE DATABASE bitcoin;
USE bitcoin;

CREATE TABLE `blocks` (
  `id` int(11) NOT NULL,
  `hash` binary(32) NOT NULL,
  `hdr` varbinary(180) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1

CREATE TABLE `address` (
  `id` decimal(13,0) NOT NULL,
  `addr` binary(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1

CREATE TABLE `trxs` (
  `id` decimal(13,0) NOT NULL,
  `hash` binary(37) NOT NULL,
  `txdata` decimal(13,0) DEFAULT NULL,
  `block_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1

CREATE TABLE `outputs` (
  `id` decimal(15,0) NOT NULL,
  `value` decimal(16,0) DEFAULT NULL,
  `addr_id` decimal(13,0) DEFAULT NULL,
  `tx_id` decimal(13,0) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `addr` (`addr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1
