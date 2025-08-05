"""
This module provides functions for generating statistics for QTM DGGS cells.
"""
import locale
import argparse
import csv
import math
from texttable import Texttable

locale.setlocale(locale.LC_ALL, "")


def qtm_metrics(res):
    """
    Calculate metrics for QTM DGGS cells.
    """
    earth_surface_area_km2 = 510_065_621.724  # 510.1 million square kilometers
    num_cells = 8 * 4 ** (res - 1)
    avg_area = (earth_surface_area_km2 / num_cells) * (10**6)
    avg_edge_length = math.sqrt(avg_area)
    return num_cells, avg_edge_length, avg_area


def qtmstats(output_file=None):
    """
    Generate statistics for QTM DGGS cells.
    """
    min_res = 1
    max_res = 24
    # Create a Texttable object for displaying in the terminal
    t = Texttable()

    # Add header to the table, including the new 'Cell Width' and 'Cell Area' columns
    t.add_row(
        ["Resolution", "Number of Cells", "Avg Edge Length (m)", "Avg Cell Area (sq m)"]
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
                ]
            )
            for res in range(min_res, max_res + 1):
                num_cells, avg_edge_length, avg_area = qtm_metrics(res)
                writer.writerow([res, num_cells, avg_edge_length, avg_area])
    else:
        for res in range(min_res, max_res + 1):
            num_cells, avg_edge_length, avg_area = qtm_metrics(res)
            formatted_num_cells = locale.format_string("%d", num_cells, grouping=True)
            formatted_length = locale.format_string(
                "%.3f", avg_edge_length, grouping=True
            )
            formatted_area = locale.format_string("%.3f", avg_area, grouping=True)

            t.add_row([res, formatted_num_cells, formatted_length, formatted_area])

        print(t.draw())


def qtmstats_cli():
    """
    Command-line interface for generating QTM DGGS statistics.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Export or display QTM stats.")
    parser.add_argument("-o", "--output", help="Output CSV file name.")
    args = parser.parse_args()

    # Call the function with the provided output file (if any)
    qtmstats(args.output)


if __name__ == "__main__":
    qtmstats_cli()
