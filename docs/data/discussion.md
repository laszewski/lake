# Elevation Data Acquisition and Processing Summary

## Objective
Acquire and process USGS Digital Elevation Model (DEM) tiles to create a custom, seamless elevation map (`lake.tif`) covering specific areas of interest in Monroe and Brown counties, Indiana.

## Data Sources
Data was retrieved from the USGS public S3 bucket (`s3://prd-tnm/StagedProducts/Elevation/13/TIFF/current/`).

**Tiles Required for Final Output:**
- `USGS_13_n40w087.tif` (Original Center)
- `USGS_13_n39w087.tif` (South Extension)

*Note: Northern (`n41w087`) and Western (`w088`) tiles were originally evaluated but excluded from the final pipeline as the target coordinates fell entirely within the `w087` blocks.*

## Technical Stack
- **OS:** macOS
- **Environment:** Python 3.14.4 (via `pyenv`)
- **CLI Tools:**
  - `awscli` (via Homebrew): For data download.
  - `gdal` / `gdalwarp` (via Homebrew): For merging and cropping GeoTIFFs.
- **Python Libraries:**
  - `leafmap`, `folium`: For interactive visualization.
  - `xarray`, `rioxarray`, `localtileserver`: For raster processing.
  - `whitebox`, `whiteboxgui`: For terrain analysis.

## Processing Workflow
1. **Download:** Fetched required 1/3 arc-second DEM tiles from the public S3 bucket using the AWS CLI:
   ```bash
   aws s3 cp s3://prd-tnm/StagedProducts/Elevation/13/TIFF/current/n40w087/USGS_13_n40w087.tif . --no-sign-request
   aws s3 cp s3://prd-tnm/StagedProducts/Elevation/13/TIFF/current/n39w087/USGS_13_n39w087.tif . --no-sign-request
   ```
2. **Merge & Crop:** Used `gdalwarp` to stitch multiple tiles and clip them directly to the boundary envelope.
3. **Refinement:** Iteratively adjusted the bounding box to include three specific target zones around Monroe and Brown counties while aggressively trimming away the long northern tail to optimize file size.
4. **Visualization:** Created an interactive HTML map using `leafmap.foliumap` to overlay the raster and verify coverage boundaries with a red vector box.

## Final Coordinate Selection
The final `lake.tif` file was cropped to the following geographic bounding box:
- **Bottom-Left (Min Lon, Min Lat):** `-86.525843, 38.993715`
- **Top-Right (Max Lon, Max Lat):** `-86.289218, 39.161233`

**Final GDAL Command used for cropping:**
```bash
gdalwarp \
  -te -86.525843 38.993715 -86.289218 39.161233 \
  USGS_13_n40w087.tif USGS_13_n39w087.tif \
  lake.tif
```
