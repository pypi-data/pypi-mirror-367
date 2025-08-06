# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Benchmark geodesic distance calculation methods.

This file was initially generated with the Windsurf Editor, to test the
GPT-4.1 model (free, with limited time).
"""

import time

import numpy as np
from pyproj import Geod
from rich import box
from rich.console import Console
from rich.table import Table

from pyfuppes.geo import geodesic_dist, haversine_dist


def geodesic_dist_pyproj(lat: np.ndarray, lon: np.ndarray, ellipsoid="WGS84") -> np.ndarray:
    """
    Calculate geodesic distance in km along lat/lon coordinates.
    Uses pyproj.Geod for vectorized computation.

    Returns
        array of step-wise distance for each pair of lat/lon coordinates
    """
    assert lat.shape[0] == lon.shape[0], "lat/lon must be of same length."

    geod = Geod(ellps=ellipsoid)
    # Compute distances between consecutive points
    lons1, lats1 = lon[:-1], lat[:-1]
    lons2, lats2 = lon[1:], lat[1:]
    # inv returns fwd_az, back_az, dist in meters
    _, _, dist = geod.inv(lons1, lats1, lons2, lats2)
    result = np.zeros(lat.shape, dtype=float)
    result[1:] = dist / 1000.0  # Convert meters to km

    return result


def benchmark_geo_distance(size=10000, seed=42, N=100):
    np.random.seed(seed)
    # Generate random coordinates within plausible ranges
    lat = np.random.uniform(-90, 90, size)
    lon = np.random.uniform(-180, 180, size)

    results = []

    # Haversine benchmark (average over N runs)
    hav_times = []
    hav_total = 0.0
    for _ in range(N):
        t0 = time.perf_counter()
        dist_hav = haversine_dist(lat, lon)
        t1 = time.perf_counter()
        hav_times.append(t1 - t0)
        hav_total += dist_hav
    results.append({
        "method": "haversine_dist",
        "avg_time": np.mean(hav_times),
        "total_dist": hav_total / N,
    })

    # Geodesic benchmark (average over N runs)
    geo_times = []
    geo_total = 0.0
    for _ in range(N):
        t0 = time.perf_counter()
        dist_geo = geodesic_dist(lat, lon)
        total_geo = np.sum(dist_geo)
        t1 = time.perf_counter()
        geo_times.append(t1 - t0)
        geo_total += total_geo
    results.append({
        "method": "geodesic_dist",
        "avg_time": np.mean(geo_times),
        "total_dist": geo_total / N,
    })

    # Geodesic (pyproj) benchmark (average over N runs)
    pyproj_times = []
    pyproj_total = 0.0
    for _ in range(N):
        t0 = time.perf_counter()
        dist_pyproj = geodesic_dist_pyproj(lat, lon)
        total_pyproj = np.sum(dist_pyproj)
        t1 = time.perf_counter()
        pyproj_times.append(t1 - t0)
        pyproj_total += total_pyproj
    results.append({
        "method": "geodesic_dist_pyproj",
        "avg_time": np.mean(pyproj_times),
        "total_dist": pyproj_total / N,
    })

    results.sort(key=lambda x: x["avg_time"])

    console = Console()
    table = Table(title=f"Geo Distance Benchmark ({size} points, {N} runs)", box=box.SIMPLE_HEAVY)
    table.add_column("Method", style="bold")
    table.add_column("Avg Time (s)", justify="right")
    table.add_column("Total Distance (km)", justify="right")
    fastest_time = results[0]["avg_time"]
    slowest_time = results[-1]["avg_time"]

    for res in results:
        style = (
            "green"
            if res["avg_time"] == fastest_time
            else ("red" if res["avg_time"] == slowest_time else "")
        )
        table.add_row(
            res["method"], f"{res['avg_time']:.6f}", f"{res['total_dist']:.3f}", style=style
        )

    console.print(table)


if __name__ == "__main__":
    benchmark_geo_distance(size=10000, N=10)
