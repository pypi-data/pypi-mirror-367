import os
from io import BytesIO
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.control import GroundControlPoint
from rasterio.warp import Resampling, calculate_default_transform, reproject

TILE_SIZE = 256


def create_tiff(
    tiles_directory: Path,
    layers_bounds: list[tuple[int, int, int, int]],
    zoom: int,
    width: int,
    height: int,
    gcps: list[GroundControlPoint],
) -> BytesIO:
    print("Creating TIFF from tiles...")
    layer_bounds = layers_bounds[zoom]
    width_in_tiles = layer_bounds[2] - layer_bounds[0] + 1
    height_in_tiles = layer_bounds[3] - layer_bounds[1] + 1

    total_width = width_in_tiles * TILE_SIZE
    total_height = height_in_tiles * TILE_SIZE

    # RGBA image
    data = np.zeros((total_height, total_width, 4), dtype=np.uint8)
    data[:, :, 0:3] = 255  # white background
    data[:, :, 3] = 0  # alpha=0 transparent

    for x in range(width_in_tiles):
        for y in range(height_in_tiles):
            tile_filename = f"{tiles_directory}/{zoom}_{x}_{y}.webp"

            if os.path.exists(tile_filename):
                tile_img = Image.open(tile_filename).convert("RGBA")
                tile_array = np.array(tile_img)
                y_offset = y * TILE_SIZE
                x_offset = x * TILE_SIZE
                data[
                    y_offset : y_offset + TILE_SIZE, x_offset : x_offset + TILE_SIZE
                ] = tile_array

    # Crop image to the actual size
    data = data[:height, :width]

    # Write new GeoTIFF to a BytesIO object
    buffer = BytesIO()

    with rasterio.open(
        buffer,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=4,
        dtype="uint8",
        gcps=gcps,
        crs="EPSG:4326",
        compress="deflate",
        tiled=True,
        zlevel=9,
    ) as dst:
        dst.write(data[:, :, 0], 1)  # Red channel
        dst.write(data[:, :, 1], 2)  # Green channel
        dst.write(data[:, :, 2], 3)  # Blue channel
        dst.write(data[:, :, 3], 4)  # Alpha channel

    buffer.seek(0)

    return buffer


def warp_tiff_with_resampling(
    input_buffer: BytesIO,
    dst_crs: str = "EPSG:4326",
    resampling_method: Resampling = Resampling.bilinear,
) -> BytesIO:
    print("Warping TIFF with resampling...")
    with rasterio.open(input_buffer) as src_ds:
        gcps, gcps_crs = src_ds.gcps  # read GCPs + their CRS

        # Ask GDAL for an output grid based on those GCPs
        transform, width, height = calculate_default_transform(
            gcps_crs,
            dst_crs,
            src_ds.width,
            src_ds.height,
            gcps=gcps,  # use GCPs
            MAX_GCP_ORDER=1,  # -order 1
        )

        profile = src_ds.profile
        profile.update(crs=dst_crs, transform=transform, width=width, height=height)

        output_buffer = BytesIO()
        with rasterio.open(output_buffer, "w", **profile) as dst_ds:
            for i in range(1, src_ds.count + 1):
                reproject(
                    rasterio.band(src_ds, i),  # source
                    rasterio.band(dst_ds, i),  # destination
                    gcps=gcps,
                    src_crs=gcps_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=resampling_method,
                    MAX_GCP_ORDER=1,  # first-order polynomial
                )
    output_buffer.seek(0)

    return output_buffer
