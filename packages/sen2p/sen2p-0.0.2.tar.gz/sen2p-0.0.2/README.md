# Sentinel Downloader

This Python library allows you to download Sentinel-2 data from Microsoft Planetary Computer.

## Installation

```bash
pip install sen2p
```

## Usage

### Using a Point Location [lon, lat]
```python
from sen2p import download

location = [172.1, -43.5]

results = download(
    start_date="2023-06-01",
    end_date="2023-06-10",
    location=location,
    bands=["B02", "B03", "B04"],
    output_dir="test_outputs",
    merge_bands=True,
    max_items=3  # download up to 3 images
)

for r in results:
    print("Downloaded:", r)
```

### Using a Polygon Shapefile
```python
from sen2p import download

# Path to your shapefile
shapefile_path = "Site.shp"  # Update with your actual shapefile path

# Call the function
results = download(
    start_date="2023-06-01",
    end_date="2023-06-30",
    location=shapefile_path,
    bands=["B02", "B03", "B04"],
    output_dir="test_output",
    merge_bands=True,
    max_items=5  # Download up to 5 matching images
)
```