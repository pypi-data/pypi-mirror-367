"""
This module provides functions for generating statistics for MGRS DGGS cells.
"""
import pandas as pd


def mgrs_metrics(res):
    """
    Calculate metrics for MGRS DGGS cells.
    """
    latitude_degrees = 8  # The latitude span of each GZD cell in degrees
    longitude_degrees = 6  # The longitude span of each GZD cell in degrees
    km_per_degree = 111  # Approximate kilometers per degree of latitude/longitude
    gzd_cells = 1200  # Total number of GZD cells

    # Convert degrees to kilometers
    latitude_span = latitude_degrees * km_per_degree
    longitude_span = longitude_degrees * km_per_degree

    # Map resolution levels to corresponding cell sizes (in kilometers)
    res_to_cell_size = {
        0: 100,  # 100 km x 100 km
        1: 10,  # 10 km x 10 km
        2: 1,  # 1 km x 1 km
        3: 0.1,  # 0.1 km x 0.1 km
        4: 0.01,  # 0.01 km x 0.01 km
        5: 0.001,  # 0.001 km x 0.001 km
    }

    cell_size = res_to_cell_size[res]
    # Calculate number of cells in latitude and longitude for the chosen cell size
    cells_latitude = latitude_span / cell_size
    cells_longitude = longitude_span / cell_size

    # Total number of cells for each GZD cell
    cells_per_gzd_cell = cells_latitude * cells_longitude

    # Total number of cells for all GZD cells
    num_cells = cells_per_gzd_cell * gzd_cells
    avg_edge_length = cell_size * (10**3)
    avg_area = avg_edge_length**2

    return num_cells, avg_edge_length, avg_area


def mgrsstats():
    """
    Generate statistics for MGRS DGGS cells.
    
    Returns:
        pandas.DataFrame: DataFrame containing MGRS DGGS statistics with columns:
            - Resolution: Resolution level (0-5)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_m: Average edge length in meters
            - Avg_Cell_Area_sq_m: Average cell area in square meters
    """
    min_res = 0
    max_res = 5
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lengths = []
    avg_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_length, avg_area = mgrs_metrics(res)
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


def mgrsstats_cli():
    """
    Command-line interface for generating MGRS DGGS statistics.
    """
    print("Resolution 0: 100 x 100 km")
    print("Resolution 1: 10 x 10 km")
    print("2 <= Resolution <= 5 = Finer subdivisions (1 x 1 km, 0.1 x 0.11 km, etc.)")

    # Get the DataFrame
    df = mgrsstats()
    
    # Display the DataFrame
    print(df.to_string(index=False))


if __name__ == "__main__":
    mgrsstats_cli()
