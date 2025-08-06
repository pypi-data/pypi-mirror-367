"""
Settings Module.

This module provides settings for the DGGS Generator Module.
"""

import platform 

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.enums.model import Model
    isea4t_dggs = Eaggr(Model.ISEA4T)
    isea3h_dggs = Eaggr(Model.ISEA3H)

from pyproj import Geod
geod = Geod(ellps="WGS84")


MAX_CELLS = 10_000_000
CHUNK_SIZE = 100_000

INITIAL_GEOHASHES = [
    "b",
    "c",
    "f",
    "g",
    "u",
    "v",
    "y",
    "z",
    "8",
    "9",
    "d",
    "e",
    "s",
    "t",
    "w",
    "x",
    "0",
    "1",
    "2",
    "3",
    "p",
    "q",
    "r",
    "k",
    "m",
    "n",
    "h",
    "j",
    "4",
    "5",
    "6",
    "7",
]


ISEA4T_BASE_CELLS = [
    "00",
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
]

ISEA3H_BASE_CELLS = [
    "00000,0",
    "01000,0",
    "02000,0",
    "03000,0",
    "04000,0",
    "05000,0",
    "06000,0",
    "07000,0",
    "08000,0",
    "09000,0",
    "10000,0",
    "11000,0",
    "12000,0",
    "13000,0",
    "14000,0",
    "15000,0",
    "16000,0",
    "17000,0",
    "18000,0",
    "19000,0",
]

MGRS_GZD_LON_DICT = {
    "01": 1,
    "02": 2,
}

MGRS_GZD_LAT_DICT = {"C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "H": 6}