# like a version, touched for the very first time

version = '0.2.5'

# definitions for coin types / chains supported
# selected by sqc.cfg['cointype']

ADDR_CHAR = 0
ADDR_PREFIX = 1
P2SH_CHAR = 2
P2SH_PREFIX = 3
BECH_HRP = 4
RPC_PORT = 5
BLKDAT_MAGIC = 6
BLKDAT_NEAR_SYNC = 7

coin_cfg = { 
    'bitcoin': [ 0, '1', 111, '3', 'bc', 8332, 0xD9B4BEF9, 500 ],
    'testnet': [ 5, 'mn', 196, '2', 'tb', 18332, 0x0709110B, 8000 ]
}

def coincfg(IDX):
    return coin_cfg[sqc.cfg['cointype']][IDX]

# addr id flags
P2SH_FLAG = 0x10000000000
BECH32_FLAG = 0x20000000000
BECH32_LONG = 0x20000000001
