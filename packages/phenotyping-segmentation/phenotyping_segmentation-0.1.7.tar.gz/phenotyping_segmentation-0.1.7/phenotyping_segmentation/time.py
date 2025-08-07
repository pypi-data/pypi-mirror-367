import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cProfile
from phenotyping_segmentation.pipeline import pipeline_cylinder

# from tests.fixtures.data import input_dir, output_dir
import pstats
import csv


input_dir = (
    "tests/data"  # Ensure this is set for profiling, or use the fixture in actual tests
)
output_dir = "tests/data/output"  # Ensure this is set for profiling, or use the fixture in actual tests


def run_pipeline(input_dir, output_dir):
    pipeline_cylinder(input_dir, output_dir)


cProfile.run("run_pipeline(input_dir, output_dir)", "profile_output_traits_v0427")
# check the visualization of the profile in the terminal
# snakeviz profile_output_traits_v0427
stats = pstats.Stats("profile_output_traits_v0427")
stats.sort_stats("cumulative").print_stats(10)  # Show top 10 functions


# Read and save in a formatted text file
with open("profile_output_traits_v0427.csv", "w") as f:
    stats = pstats.Stats("profile_output", stream=f)
    stats.sort_stats("cumulative").print_stats()


# with open("profile_output.csv", "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow(
#         [
#             "Function",
#             "Total Calls",
#             "Primitive Calls",
#             "Total Time",
#             "Per Call",
#             "Cumulative Time",
#             "Per Call (Cumulative)",
#             "File:Line(Function)",
#         ]
#     )

#     for func, stat in stats.stats.items():
#         filename, line, function = func
#         total_calls = stat[0]
#         primitive_calls = stat[1]
#         total_time = stat[2]
#         per_call = stat[2] / total_calls if total_calls else 0
#         cumulative_time = stat[3]
#         per_call_cumulative = stat[3] / total_calls if total_calls else 0

#         writer.writerow(
#             [
#                 f"{filename}:{line}({function})",
#                 total_calls,
#                 primitive_calls,
#                 total_time,
#                 per_call,
#                 cumulative_time,
#                 per_call_cumulative,
#             ]
#         )
