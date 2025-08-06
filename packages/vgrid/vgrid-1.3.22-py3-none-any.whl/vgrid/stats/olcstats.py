"""
This module provides functions for generating statistics for OLC DGGS cells.
"""
import math
import pandas as pd


def olc_metrics(res):
    """
    Calculate metrics for OLC DGGS cells.
    """
    earth_surface_area_km2 = 510_065_621.724  # 510.1 million square kilometers
    num_cells = 20 ** res
    avg_area = (earth_surface_area_km2 / num_cells) * (10**6)
    avg_edge_length = math.sqrt(avg_area)
    return num_cells, avg_edge_length, avg_area


def olcstats():
    """
    Generate statistics for OLC DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing OLC DGGS statistics with columns:
            - Resolution: Resolution level (0-15)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 15
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_length, avg_area = olc_metrics(res)
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


def olcstats_cli():
    """
    Command-line interface for generating OLC DGGS statistics.
    """
    # Get the DataFrame
    df = olcstats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    olcstats_cli()
