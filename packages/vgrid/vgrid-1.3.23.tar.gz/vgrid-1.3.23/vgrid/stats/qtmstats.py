"""
This module provides functions for generating statistics for QTM DGGS cells.
"""
import math
import pandas as pd


def qtm_metrics(res):
    """
    Calculate metrics for QTM DGGS cells.
    """
    earth_surface_area_km2 = 510_065_621.724  # 510.1 million square kilometers
    num_cells = 8 * 4 ** (res - 1)
    avg_area = (earth_surface_area_km2 / num_cells) * (10**6)
    avg_edge_length = math.sqrt(avg_area)
    return num_cells, avg_edge_length, avg_area


def qtmstats():
    """
    Generate statistics for QTM DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing QTM DGGS statistics with columns:
            - Resolution: Resolution level (1-24)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 1
    max_res = 24
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_length, avg_area = qtm_metrics(res)
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


def qtmstats_cli():
    """
    Command-line interface for generating QTM DGGS statistics.
    """
    # Get the DataFrame
    df = qtmstats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    qtmstats_cli()
