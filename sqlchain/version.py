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
    'bitcoin': [ '1',  0,   '3',  5,   'bc',  0xD9B4BEF9, 500 ],
    'testnet': [ 'mn', 111, '2',  196, 'tb',  0x0709110B, 8000 ],
    'litecoin':[ 'L',  48,  '3M', 50,  'ltc', 0xDBB6C0FB, 500 ]
}

def coincfg(IDX):
    return coin_cfg[sqc.cfg['cointype']][IDX]

# addr id flags
ADDR_ID_FLAGS = 0x70000000000
P2SH_FLAG = 0x10000000000
BECH32_FLAG = 0x20000000000
BECH32_LONG = 0x30000000000

# global version related definitions
# cannot change these without first updating existing table schema and data
# these are set to reasonable values for now - to increase, alter trxs.block_id or outputs.id column widths
# and update data eg. update trxs set block_id=block_id/OLD_MAX*NEW_MAX + block_id%OLD_MAX
MAX_TX_BLK = 20000  # allows 9,999,999 blocks with decimal(11)
MAX_IO_TX = 16384    # allows 37 bit out_id value, (5 byte hash >> 3)*16384 in decimal(16), 7 bytes in blobs
BLOB_SPLIT_SIZE = int(5e9) # size limit for split blobs, approx. as may extend past if tx on boundary
S3_BLK_SIZE = 4096 # s3 block size for caching
