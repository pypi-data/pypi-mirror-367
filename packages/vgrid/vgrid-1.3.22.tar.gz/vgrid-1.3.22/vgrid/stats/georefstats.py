"""
This module provides functions for generating statistics for GEOREF DGGS cells.
"""
import math
import pandas as pd


def georef_metrics(res):
    """
    Calculate metrics for GEOREF DGGS cells.
    """
    earth_surface_area_km2 = 510_065_621.724  # 510.1 million square kilometers
    
    # GEOREF grid has 3600 (60x60) cells at base level
    # Each subdivision adds 10x10 = 100 cells per parent cell
    if res == 0:
        num_cells = 3600  # 60x60 base grid
    else:
        num_cells = 3600 * (100 ** res)
    
    avg_area = (earth_surface_area_km2 / num_cells) * (10**6)
    avg_edge_length = math.sqrt(avg_area)
    return num_cells, avg_edge_length, avg_area


def georefstats():
    """
    Generate statistics for GEOREF DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing GEOREF DGGS statistics with columns:
            - Resolution: Resolution level (0-10)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 10
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_length, avg_area = georef_metrics(res)
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


def georefstats_cli():
    """
    Command-line interface for generating GEOREF DGGS statistics.
    """
    # Get the DataFrame
    df = georefstats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    georefstats_cli()
