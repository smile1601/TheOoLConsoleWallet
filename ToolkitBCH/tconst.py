"""
Created on 15 ���. 2021 �.

@author: Alex Nenashev
©TheOoL, Inc
"""

from decouple import config
import os
import sys

"""
рабочая директория
"""

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + '/'
WORK_DIR = ROOT_DIR + config('WORK_DIR', default='theool/')
BLOCK_DIR = ROOT_DIR + config('BLOCK_DIR', default='theool/bchbase/')
POOL_DIR = ROOT_DIR + config('POOL_DIR', default='theool/bchpool/')
INDEX_DIR = ROOT_DIR + config('INDEX_DIR', default='theool/bchindexes/')
DATA_DIR = ROOT_DIR + config('DATA_DIR', default='theool/bchlocaldata/')
WALLETS_DIR = ROOT_DIR + config('WALLETS_DIR', default='theool/wallets/')

SEEDS_F = ROOT_DIR + config('SEEDS_F', default='theool/seeds.dat')
PEERS_F = ROOT_DIR + config('PEERS_F', default='theool/peers.dat')
LOCAL_TRN_F = ROOT_DIR + config('LOCALTRN_F', default='theool/localTransactions.dat')

is_windows = sys.platform.startswith('win')
if is_windows:
    ROOT_DIR = ROOT_DIR.replace('/', '\\')
    WORK_DIR = WORK_DIR.replace('/', '\\')
    BLOCK_DIR = BLOCK_DIR.replace('/', '\\')
    POOL_DIR = BLOCK_DIR.replace('/', '\\')
    INDEX_DIR = INDEX_DIR.replace('/', '\\')
    DATA_DIR = DATA_DIR.replace('/', '\\')
    WALLETS_DIR = WALLETS_DIR.replace('/', '\\')
    SEEDS_F = SEEDS_F.replace('/', '\\')
    PEERS_F = PEERS_F.replace('/', '\\')
    LOCAL_TRN_F = LOCAL_TRN_F.replace('/', '\\')


SEEDS_LIST = config('SEEDS_LIST', default=["62.77.154.93"])
MAX_PEERS = config('MAX_PEERS', default=20, cast=int)
PORT = config('PORT', default=58877, cast=int)
