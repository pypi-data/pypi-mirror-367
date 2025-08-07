"""
This module provides functions for generating statistics for A5 DGGS cells.
"""
import math
import pandas as pd
from a5.core.cell_info import get_num_cells, cell_area

def a5_metrics(res):
    num_cells = get_num_cells(res)
    avg_area = cell_area(res)
    k = math.sqrt(5*(5+2*math.sqrt(5)))
    avg_edge_length = round(math.sqrt(4*avg_area/k), 3)
    return num_cells, avg_edge_length, avg_area

def a5stats():
    """
    Generate statistics for A5 DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing A5 DGGS statistics with columns:
            - Resolution: Resolution level (0-29)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 29
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_length, avg_area = a5_metrics(res)
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lengths.append(avg_edge_length)
        avg_areas.append(avg_area)
    
    # Create DataFrame without index
    df = pd.DataFrame({
        'Resolution': resolutions,
        'Number_of_Cells': num_cells_list,
        'Avg_Edge_Length_m': avg_edge_lengths,
        'Avg_Cell_Area_sq_m': avg_areas
    }, index=None)
    
    return df


def a5stats_cli():
    """
    Command-line interface for generating A5 DGGS statistics.
    """
    # Get the DataFrame
    df = a5stats()    
    # Display the DataFrame
    print(df)


if __name__ == "__main__":
    a5stats_cli()
