"""
Generator module for vgrid.

This module provides functions to generate discrete global grid systems (DGGS)
for various coordinate systems and geographic areas.
"""

import platform

# Main grid generation functions
from .h3grid import h3grid, h3_grid as h3_generate_grid, h3_grid_within_bbox as h3_generate_grid_within_bbox, h3_grid_resample as h3_generate_grid_resample
from .s2grid import s2grid, s2_grid as s2_generate_grid, s2_grid_resample as s2_generate_grid_resample
from .a5grid import a5grid, a5_grid as a5_generate_grid    
from .rhealpixgrid import rhealpixgrid, rhealpix_grid as rhealpix_generate_grid, rhealpix_grid_within_bbox as rhealpix_generate_grid_within_bbox, rhealpix_grid_resample as rhealpix_generate_grid_resample
# if platform.system() == "Windows":
#     from .isea4tgrid import generate_grid as isea4t_generate_grid, generate_grid_within_bbox as isea4t_generate_grid_within_bbox, generate_grid_resample as isea4t_generate_grid_resample
#     from .isea3hgrid import generate_grid as isea3h_generate_grid, generate_grid_within_bbox as isea3h_generate_grid_within_bbox

from .easegrid import easegrid, ease_grid as ease_generate_grid, ease_grid_within_bbox as ease_generate_grid_within_bbox
from .qtmgrid import qtmgrid, qtm_grid as qtm_generate_grid, qtm_grid_within_bbox as qtm_generate_grid_within_bbox
from .olcgrid import olcgrid, olc_grid as olc_generate_grid, olc_grid_within_bbox as olc_generate_grid_within_bbox
from .geohashgrid import geohashgrid, geohash_grid as geohash_generate_grid, geohash_grid_within_bbox as geohash_generate_grid_within_bbox
from .georefgrid import georefgrid, georef_grid as georef_generate_grid
from .mgrsgrid import mgrsgrid, mgrs_grid as mgrs_generate_grid
from .tilecodegrid import tilecodegrid, tilecode_grid as tilecode_generate_grid
from .quadkeygrid import quadkeygrid, quadkey_grid as quadkey_generate_grid
from .maidenheadgrid import maidenheadgrid, maidenhead_grid as maidenhead_generate_grid, maidenhead_grid_within_bbox as maidenhead_generate_grid_within_bbox
from .garsgrid import garsgrid, gars_grid as gars_generate_grid, gars_grid_within_bbox as gars_generate_grid_within_bbox
from .settings import (
    MAX_CELLS, CHUNK_SIZE, ISEA4T_BASE_CELLS, ISEA3H_BASE_CELLS,
    MGRS_GZD_LON_DICT, MGRS_GZD_LAT_DICT
)
from vgrid.utils.constants import (
    ISEA4T_RES_ACCURACY_DICT, ISEA3H_RES_ACCURACY_DICT, ISEA3H_ACCURACY_RES_DICT
)

__all__ = [
    # Main grid functions
    'h3grid', 's2grid', 'a5grid', 'rhealpixgrid', 'isea4tgrid', 'isea3hgrid',
    'easegrid', 'qtmgrid', 'olcgrid', 'geohashgrid', 'georefgrid', 'mgrsgrid',
    'tilecodegrid', 'quadkeygrid', 'maidenheadgrid', 'garsgrid',
    # Grid generation with specific parameters
    'h3_generate_grid', 'h3_generate_grid_within_bbox', 'h3_generate_grid_resample',
    's2_generate_grid', 's2_generate_grid_resample', 
    'a5_generate_grid', 
    'rhealpix_generate_grid', 'rhealpix_generate_grid_within_bbox', 'rhealpix_generate_grid_resample',
    # 'isea4t_generate_grid', 'isea4t_generate_grid_within_bbox', 'isea4t_generate_grid_resample',
    # 'isea3h_generate_grid', 'isea3h_generate_grid_within_bbox', 
    'ease_generate_grid', 'ease_generate_grid_within_bbox',
    'qtm_generate_grid', 'qtm_generate_grid_within_bbox',
    'olc_generate_grid', 'olc_generate_grid_within_bbox', 
    'geohash_generate_grid', 'geohash_generate_grid_within_bbox',
    'georef_generate_grid',  
    'mgrs_generate_grid',  
    'tilecode_generate_grid',
    'quadkey_generate_grid', 
    'maidenhead_generate_grid', 'maidenhead_generate_grid_within_bbox',
    'gars_generate_grid', 'gars_generate_grid_within_bbox',   
]
__all__ += [
    'MAX_CELLS', 'CHUNK_SIZE', 'ISEA4T_BASE_CELLS', 'ISEA3H_BASE_CELLS',
    'ISEA4T_RES_ACCURACY_DICT', 'ISEA3H_RES_ACCURACY_DICT', 'ISEA3H_ACCURACY_RES_DICT',
    'MGRS_GZD_LON_DICT', 'MGRS_GZD_LAT_DICT'
]
