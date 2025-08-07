"""
This module provides functions for generating statistics for H3 DGGS cells.
"""

import pandas as pd
import h3


def h3stats():
    """
    Generate statistics for H3 DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing H3 DGGS statistics with columns:
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
        num_cells_at_res = h3.get_num_cells(res)
        cell_width = h3.average_hexagon_edge_length(res, unit="m")
        cell_area = h3.average_hexagon_area(res, unit="m^2")
        
        resolutions.append(res)
        num_cells_list.append(num_cells_at_res)
        avg_edge_lengths.append(cell_width)
        avg_areas.append(cell_area)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Resolution': resolutions,
        'Number_of_Cells': num_cells_list,
        'Avg_Edge_Length_m': avg_edge_lengths,
        'Avg_Cell_Area_sq_m': avg_areas
    })
    
    return df


def h3stats_cli():
    """
    Command-line interface for generating H3 DGGS statistics.
    """
    # Get the DataFrame
    df = h3stats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    h3stats_cli()
