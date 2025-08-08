from sentinel_downloader import download_pc_stac_item

def test_function_runs():
    item_url = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2A_35UNU_20230827_0_L2A"
    result = download_pc_stac_item(item_url, bands=["B02"], output_dir="output_test", show_progress=False)
    assert "B02" in result
