"""
This module provides functions for generating statistics for S2 DGGS cells.
"""
import math
import pandas as pd


def s2_metrics(res):
    earth_surface_area_km2 = 510_065_621.724  # 510.1 million square kilometers
    num_cells = 6 * (4**res)
    avg_area = (earth_surface_area_km2 / num_cells) * (10**6)
    avg_edge_length = math.sqrt(avg_area)
    return num_cells, avg_edge_length, avg_area


def s2stats():
    """
    Generate statistics for S2 DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing S2 DGGS statistics with columns:
            - Resolution: Resolution level (0-30)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 30
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_length, avg_area = s2_metrics(res)
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


def s2stats_cli():
    """
    Command-line interface for generating S2 DGGS statistics.
    """
    # Get the DataFrame
    df = s2stats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    s2stats_cli()
