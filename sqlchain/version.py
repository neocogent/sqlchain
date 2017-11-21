# like a version, touched for the very first time

version = '0.2.5'

# definitions for coin types / chains supported
# selected by sqc.cfg['cointype']

ADDR_CHAR = 0
ADDR_PREFIX = 1
P2SH_CHAR = 2
P2SH_PREFIX = 3
BECH_HRP = 4
BLKDAT_MAGIC = 5
BLKDAT_NEAR_SYNC = 6

coin_cfg = { 
    'bitcoin': [ '1', 0, '3', 5, 'bc', 0xD9B4BEF9, 500 ],
    'testnet': [ 'mn', 111, '2', 196, 'tb', 0x0709110B, 8000 ],
    'litecoin': [ 'L', 48, '3M', 50, 'ltc', 0xDBB6C0FB, 500 ]
}

def coincfg(IDX):
    return coin_cfg[sqc.cfg['cointype']][IDX]

# addr id flags
P2SH_FLAG = 0x10000000000
BECH32_FLAG = 0x20000000000
BECH32_LONG = 0x30000000000
