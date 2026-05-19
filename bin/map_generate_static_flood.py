import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.windows import from_bounds
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from scipy.ndimage import gaussian_filter  # Standard for cleaner contour rendering

def download_usgs_dem(lon_bounds, lat_bounds, output_filename="USGS_13_n40w087.tif"):
    """
    Downloads the corrected 1/3 arc-second (~10m) DEM tile from the updated 
    USGS 3DEP public S3 path.
    """
    # Updated direct path pattern inside the prd-tnm bucket
    s3_key = "StagedProducts/Elevation/13/TIFF/current/n40w087/USGS_13_n40w087.tif"
    bucket_name = "prd-tnm"
    
    if not os.path.exists(output_filename):
        print(f"Downloading corrected DEM tile from USGS S3:\n-> s3://{bucket_name}/{s3_key}")
        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        s3.download_file(bucket_name, s3_key, output_filename)
        print("Download complete.")
    return output_filename

def generate_flood_map(dem_path, water_level_ft):
    """
    Clips the DEM to Monroe Lake bounds, scales units, and overlays
    a anti-aliased flood layer.
    """
    # Adjusted bounding box tightly framing Monroe Lake
    lon_min, lon_max = -86.55, -86.30
    lat_min, lat_max = 38.98, 39.12
    
    # Target conversion: DEM values are metric (NAVD88)
    water_level_m = water_level_ft * 0.3048
    
    with rasterio.open(dem_path) as src:
        window = from_bounds(lon_min, lat_min, lon_max, lat_max, src.transform)
        dem_data = src.read(1, window=window)
        
        # Guard against arbitrary NODATA sentinel values
        dem_data = np.where(dem_data == src.nodata, np.nan, dem_data)
        
    extent = [lon_min, lon_max, lat_min, lat_max]
    
    # Generate binary mask: 1 where submerged, 0 elsewhere
    raw_mask = (dem_data <= water_level_m).astype(float)
    
    # Smooth edges slightly to combat pixelation along shallow fingers
    smoothed_mask = gaussian_filter(raw_mask, sigma=0.8)
    
    # Convert back to a display mask where land is completely transparent (NaN)
    flood_visual = np.where(smoothed_mask > 0.1, smoothed_mask, np.nan)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Base terrain layer
    terrain_plot = ax.imshow(dem_data, extent=extent, cmap='terrain', origin='upper')
    fig.colorbar(terrain_plot, ax=ax, label='Terrain Elevation (Meters above MSL)')
    
    # Flood map overlay using transparent blue
    ax.imshow(flood_visual, extent=extent, cmap='Blues_r', alpha=0.55, origin='upper', vmin=0, vmax=1.2)
    
    ax.set_title(f"Monroe Lake Inundation Profile\nSimulated Stage: {water_level_ft} ft (NGVD29)", fontsize=13)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle=':', alpha=0.6)
    
    output_plot = f"monroe_flood_stage_{int(water_level_ft)}.png"
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"Map successfully saved to disk: {output_plot}")
    plt.show()

if __name__ == "__main__":
    # 1. Pull down data via corrected s3 path mapping
    dem_file = download_usgs_dem(
        lon_bounds=(-86.55, -86.30), 
        lat_bounds=(38.98, 39.12)
    )
    
    # 2. Run simulation using target water level 
    current_pool_elevation = 546.75 
    generate_flood_map(dem_file, current_pool_elevation)