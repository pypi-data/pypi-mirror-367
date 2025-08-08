"""Pure Load No GVAL"""

import time
import subprocess
import os
import gc

import memray
import rioxarray as rxr


def run_normal_load(cand_file, bench_file, cache=True):
    """
    Loads without context wrappers and deletes objects
    """

    ds = rxr.open_rasterio(cand_file, cache=cache)
    ds2 = rxr.open_rasterio(bench_file, cache=cache)

    # Pure load
    ds.load()
    ds2.load()


def run_normal_load_gc(cand_file, bench_file, cache=True):
    """
    Loads without context wrappers and deletes objects
    """

    ds = rxr.open_rasterio('c_uint8.tif', cache=cache)
    ds2 = rxr.open_rasterio('b_uint8.tif', cache=cache)

    # Pure load
    ds.load()
    ds2.load()

    gc.collect()


def run_normal_load_gc(cand_file, bench_file, cache=True):
    """
    Loads without context wrappers and garbage collects
    """

    ds = rxr.open_rasterio(cand_file, cache=cache)
    ds2 = rxr.open_rasterio(bench_file, cache=cache)

    # Pure load
    ds.load()
    ds2.load()

    gc.collect()


def run_normal_load_delete(cand_file, bench_file, cache=True):
    """
    Loads without context wrappers and deletes objects
    """

    ds = rxr.open_rasterio(cand_file, cache=cache)
    ds2 = rxr.open_rasterio(bench_file, cache=cache)

    # Pure load
    ds.load()
    ds2.load()

    del ds, ds2


def run_normal_load_delete_gc(cand_file, bench_file, cache=True):
    """
    Loads without context wrappers, deletes objects, and garbage collects
    """

    ds = rxr.open_rasterio(cand_file, cache=cache)
    ds2 = rxr.open_rasterio(bench_file, cache=cache)

    # Pure load
    ds.load()
    ds2.load()

    del ds, ds2
    gc.collect()


def run_context_load(cand_file, bench_file, cache=True):
    """
    Loads with context wrappers
    """

    with (rxr.open_rasterio(cand_file, cache=cache) as ds,
          rxr.open_rasterio(bench_file, cache=cache) as ds2):

        # Pure load
        ds.load()
        ds2.load()


def run_context_load_gc(cand_file, bench_file, cache=True):
    """
    Loads with context wrappers and garbage collects
    """

    with (rxr.open_rasterio(cand_file, cache=cache) as ds,
          rxr.open_rasterio(bench_file, cache=cache) as ds2):

        # Pure load
        ds.load()
        ds2.load()

    gc.collect()


def run_context_load_delete(cand_file, bench_file, cache=True):
    """
    Loads with context wrappers and deletes objects
    """

    with (rxr.open_rasterio(cand_file, cache=cache) as ds,
          rxr.open_rasterio(bench_file, cache=cache) as ds2):

        # Pure load
        ds.load()
        ds2.load()

    del ds, ds2


def run_context_load_delete_gc(cand_file, bench_file, cache=True):
    """
    Loads with context wrappers, deletes objects, and garbage collects
    """

    with (rxr.open_rasterio(cand_file, cache=cache) as ds,
          rxr.open_rasterio(bench_file, cache=cache) as ds2):

        # Pure load
        ds.load()
        ds2.load()

    del ds, ds2
    gc.collect()


if __name__ == "__main__":

    # ---------------------- If user wants to use command line ----------------------------
    # import argparse
    #
    # # Parse arguments
    # parser = argparse.ArgumentParser(description="Flamegraph baby")
    #
    # parser.add_argument(
    #     "-o", "--file_name", help="Name of output file", required=True
    # )
    #
    # args = vars(parser.parse_args())
    # file_name = args['file_name']

    file_name = 'one81.bin'

    if os.path.exists(file_name):
        os.remove(file_name)

    with memray.Tracker(file_name):
        for x in range(5):
            run_context_load_delete_gc()

        time.sleep(2)

    subprocess.call(['memray', 'flamegraph', file_name, '--temporal'])

