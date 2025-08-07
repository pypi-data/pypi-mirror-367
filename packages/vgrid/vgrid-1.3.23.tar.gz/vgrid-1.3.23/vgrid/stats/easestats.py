"""
This module provides functions for generating statistics for EASE-DGGS cells.
"""
import pandas as pd
from vgrid.dggs.easedggs.constants import levels_specs


def easestats():
    """
    Generate statistics for EASE-DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing EASE-DGGS statistics with columns:
            - Resolution: Resolution level (0-6)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 6
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        if res in levels_specs:
            num_cells_at_res = (
                levels_specs[res]["n_row"] * levels_specs[res]["n_col"]
            )
            cell_width = levels_specs[res]["x_length"]
            cell_area = (
                levels_specs[res]["x_length"] * levels_specs[res]["y_length"]
            )
            
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


def easestats_cli():
    """
    Command-line interface for generating EASE-DGGS statistics.
    """
    # Get the DataFrame
    df = easestats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    easestats_cli()
