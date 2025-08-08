import os
from typing import List, Optional, Dict, Any, Union
from tqdm import tqdm
import xarray as xr
import rioxarray as rxr
import geopandas as gpd
from shapely.geometry import mapping, Point
from pystac_client import Client
import planetary_computer as pc
from rasterio.enums import Resampling

def download(
    start_date: str,
    end_date: str,
    location: Union[List[float], Dict[str, Any], str],
    bands: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    show_progress: bool = True,
    merge_bands: bool = False,
    merged_filename: Optional[str] = None,
    overwrite: bool = False,
    cell_size: Optional[float] = None,
    max_items: int = 10,
    collection: str = "sentinel-2-l2a"
) -> List[Dict[str, Any]]:
    '''
    Download Sentinel-2 data from Planetary Computer using search parameters.

    Args:
        start_date (str): Start date (e.g., "2023-06-01").
        end_date (str): End date (e.g., "2023-06-30").
        location (list, dict, or str): [lon, lat], GeoJSON geometry, or path to shapefile.
        bands (list, optional): List of bands to download (e.g., ["B02", "B03"]).
        output_dir (str, optional): Where to save output files.
        show_progress (bool): Show download progress.
        merge_bands (bool): Merge into single file.
        merged_filename (str, optional): Filename for merged file.
        overwrite (bool): Overwrite existing files.
        cell_size (float, optional): Target resolution.
        max_items (int): How many items to fetch.
        collection (str): STAC collection name.

    Returns:
        List of result dicts, one per STAC item.
    '''

    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)

    if isinstance(location, list):
        geometry = mapping(Point(location[0], location[1]))
    elif isinstance(location, dict):
        geometry = location
    elif isinstance(location, str) and location.endswith(".shp"):
        gdf = gpd.read_file(location)
        geometry = mapping(gdf.unary_union)
    else:
        raise ValueError("Location must be [lon, lat], GeoJSON geometry, or shapefile path")

    search = catalog.search(
        collections=[collection],
        intersects=geometry,
        datetime=f"{start_date}/{end_date}",
        max_items=max_items,
    )

    items = list(search.get_items())
    if not items:
        raise ValueError("No Sentinel-2 items found for the given location and time range.")

    all_results = []

    for item in items:
        item_id = item.id
        available_assets = list(item.assets.keys())
        cloud_cover = item.properties.get("eo:cloud_cover", "N/A")

        if bands is None:
            bands_to_download = [asset for asset in available_assets if asset.startswith("B")]
        else:
            missing_bands = [band for band in bands if band not in available_assets]
            if missing_bands:
                print(f"Skipping {item_id}: Missing bands {missing_bands}")
                continue
            bands_to_download = bands

        item_output_dir = os.path.join(output_dir, item_id) if output_dir else None
        if item_output_dir and not os.path.exists(item_output_dir):
            os.makedirs(item_output_dir)

        result = {
            "item_id": item_id,
            "cloud_cover": cloud_cover
        }
        band_data_arrays = []
        resampled_arrays = []
        band_names = []
        progress_iter = tqdm(bands_to_download, desc=f"{item_id}") if show_progress else bands_to_download

        for band in progress_iter:
            band_url = item.assets[band].href
            file_path = os.path.join(item_output_dir, f"{item.id}_{band}.tif") if item_output_dir else None

            if file_path and os.path.exists(file_path) and not overwrite:
                if show_progress:
                    progress_iter.write(f"{file_path} exists, skipping.")
                if merge_bands:
                    band_data = rxr.open_rasterio(file_path)
                    band_data_arrays.append((band, band_data))
                    band_names.append(band)
                result[band] = file_path
                continue

            if show_progress:
                progress_iter.set_description(f"{item_id}: {band}")

            band_data = rxr.open_rasterio(band_url)
            if merge_bands:
                band_data_arrays.append((band, band_data))
                band_names.append(band)

            # if item_output_dir:
            #     band_data.rio.to_raster(file_path)
            #     result[band] = file_path
            if item_output_dir:
                band_data.rio.to_raster(
                    file_path,
                    tags={
                        "CLOUD_COVER": str(cloud_cover)
                    }
                )
                result[band] = file_path
            
            else:
                result[band] = band_data

        if merge_bands and item_output_dir:
            merged_path = os.path.join(item_output_dir, merged_filename or f"{item.id}_merged.tif")
            if os.path.exists(merged_path) and not overwrite:
                if show_progress:
                    print(f"Merged file {merged_path} exists, skipping.")
                result["merged"] = merged_path
            else:
                if cell_size is None and band_data_arrays:
                    cell_size = abs(band_data_arrays[0][1].rio.transform()[0])
                elif cell_size is None:
                    cell_size = 10

                for band_name, data_array in band_data_arrays:
                    current_res = abs(data_array.rio.transform()[0])
                    if abs(current_res - cell_size) > 0.01:
                        resampling_method = Resampling.bilinear if current_res < cell_size else Resampling.nearest
                        resampled = data_array.rio.reproject(
                            data_array.rio.crs,
                            resolution=(cell_size, cell_size),
                            resampling=resampling_method,
                        )
                        resampled_arrays.append(resampled)
                    else:
                        resampled_arrays.append(data_array)

                merged_data = xr.concat(resampled_arrays, dim="band")
                merged_data.attrs["description"] = f"Merged bands: {', '.join(band_names)}"
                merged_data.rio.to_raster(merged_path, tags={"BAND_NAMES": ",".join(band_names), "CLOUD_COVER": str(cloud_cover)}, descriptions=band_names)
                result["merged"] = merged_path
                if show_progress:
                    print(f"Merged file written: {merged_path}")

        all_results.append(result)

    return all_results


import rioxarray as rxr
import rasterio

def show_meta(file_path: str) -> None:
    """
    Print metadata of a raster file, including cloud cover if available.

    Args:
        file_path (str): Path to the downloaded image (.tif)
    """
    data = rxr.open_rasterio(file_path)

    # Use rasterio to get TIFF tags
    with rasterio.open(file_path) as src:
        tags = src.tags()

    cloud_cover = tags.get("CLOUD_COVER")

    print(f"📄 File: {file_path}")
    if cloud_cover is not None:
        print(f"☁️ Cloud cover: {cloud_cover}%")
    print(f"📐 Dimensions: {data.rio.width} x {data.rio.height}")
    print(f"📊 Number of bands: {data.rio.count}")
    print(f"🗺️ CRS: {data.rio.crs}")
    print(f"📏 Resolution: {data.rio.resolution()}")
    print(f"📌 Bounds: {data.rio.bounds()}")
    print(f"🧾 Metadata: {data.attrs}")


