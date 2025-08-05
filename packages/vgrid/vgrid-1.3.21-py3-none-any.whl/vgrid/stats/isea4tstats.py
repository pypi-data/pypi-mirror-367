"""
This module provides functions for generating statistics for ISEA4T DGGS cells.
"""
import locale
import argparse
import csv
import platform
from pyproj import Geod
from shapely.wkt import loads
from texttable import Texttable
from vgrid.conversion.latlon2dggs import latlon2isea4t

geod = Geod(ellps="WGS84")

locale.setlocale(locale.LC_ALL, "")

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

    # isea4t_cell = DggsCell(latlon2isea4t(lat, lon, res))
    # isea4t2point = isea4t_dggs.convert_dggs_cell_to_point(isea4t_cell)
    # accuracy = isea4t2point.get_accuracy()

    avg_area = abs(
        geod.geometry_area_perimeter(cell_polygon)[0]
    )  # Area in square meters
    avg_edge_length = (
        abs(geod.geometry_area_perimeter(cell_polygon)[1]) / 3
    )  # Perimeter in meters/ 3
    return num_cells, avg_edge_length, avg_area


def isea4tstats(output_file=None):
    """
    Generate statistics for ISEA4T DGGS cells.
    """
    min_res = 0
    max_res = 39
    t = Texttable()

    # Add header to the table, including the new 'Cell Width' and 'Cell Area' columns
    t.add_row(
        [
            "Resolution",
            "Number of Cells",
            "Avg Edge Length (m)",
            "Avg Cell Area (sq m)",
            # "Accuracy",
        ]
    )

    # Check if an output file is specified (for CSV export)
    if output_file:
        # Open the output CSV file for writing
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Resolution",
                    "Number of Cells",
                    "Avg Edge Length (m)",
                    "Avg Cell Area (sq m)",
                    # "Accuracy",
                ]
            )

            # Iterate through resolutions and write rows to the CSV file
            for res in range(min_res, max_res):
                num_cells, avg_edge_length, avg_area = isea4t_metrics(res)
                writer.writerow([res, num_cells, avg_edge_length, avg_area])
        print(f"OpenEAGGGR ISEA4T stats saved to {output_file}.")
    else:
        for res in range(min_res, max_res + 1):
            num_cells, avg_edge_length, avg_area = isea4t_metrics(res)
            formatted_num_cells = locale.format_string("%d", num_cells, grouping=True)
            formatted_edge_length = locale.format_string(
                "%.5f", avg_edge_length, grouping=True
            )
            formatted_area = locale.format_string("%.5f", avg_area, grouping=True)
            # formatted_accuracy = locale.format_string("%.3f", accuracy, grouping=True)

            t.add_row(
                [
                    res,
                    formatted_num_cells,
                    formatted_edge_length,
                    formatted_area,
                    # formatted_accuracy,
                ]
            )

        # Print the formatted table to the console
        print(t.draw())


def isea4tstats_cli():
    """
    Command-line interface for generating ISEA4T DGGS statistics.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Export or display OpenEAGGR ISEA4T DGGS stats."
    )
    parser.add_argument("-o", "--output", help="Output CSV file name.")
    args = parser.parse_args()

    if platform.system() == "Windows":
        isea4tstats(args.output)


if __name__ == "__main__":
    isea4tstats_cli()
