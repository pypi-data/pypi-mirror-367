"""
This module provides functions for generating statistics for ISEA4T DGGS cells.
"""
import platform
import pandas as pd
from pyproj import Geod
from shapely.wkt import loads
from vgrid.conversion.latlon2dggs import latlon2isea4t

geod = Geod(ellps="WGS84")

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    isea4t_dggs = Eaggr(Model.ISEA4T)

from vgrid.utils.geometry import isea4t_cell_to_polygon

def isea4t_metrics(res):
    """
    Calculate metrics for ISEA4T DGGS cells.
    """
    num_cells = 20 * (4**res)
    lat, lon = 10.775275567242561, 106.70679737574993
    eaggr_cell = DggsCell(latlon2isea4t(lat, lon, res))
    cell_polygon = isea4t_cell_to_polygon(eaggr_cell)

    avg_area = abs(
        geod.geometry_area_perimeter(cell_polygon)[0]
    )  # Area in square meters
    avg_edge_length = (
        abs(geod.geometry_area_perimeter(cell_polygon)[1]) / 3
    )  # Perimeter in meters/ 3
    return num_cells, avg_edge_length, avg_area


def isea4tstats():
    """
    Generate statistics for ISEA4T DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing ISEA4T DGGS statistics with columns:
            - Resolution: Resolution level (0-39)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 39
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res):
        num_cells, avg_edge_length, avg_area = isea4t_metrics(res)
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lengths.append(avg_edge_length)
        avg_areas.append(avg_area)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Resolution': resolutions,
        'Number_of_Cells': num_cells_list,
        'Avg_Edge_Length_m': avg_edge_lengths,
        'Avg_Cell_Area_sq_m': avg_areas
    })
    
    return df


def isea4tstats_cli():
    """
    Command-line interface for generating ISEA4T DGGS statistics.
    """
    if platform.system() == "Windows":
        # Get the DataFrame
        df = isea4tstats()
        
        # Display the DataFrame
        print(df.to_string(index=False))


if __name__ == "__main__":
    isea4tstats_cli()
