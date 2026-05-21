import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.windows import from_bounds
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from scipy.ndimage import gaussian_filter  # Standard for cleaner contour rendering
from matplotlib.path import Path

def get_dem_file():
    """Returns the path to the processed lake elevation file."""
    return "docs/data/lake.tif"

# Exclusion polygon for area below Monroe Dam (Lon, Lat)
EXCLUSION_POLYGON = [
    (-86.510084, 39.0094025),
    (-86.5128471, 39.0066343),
    (-86.5150358, 39.0068011),
    (-86.5199281, 39.0112363),
    (-86.5330173, 39.0109695),
    (-86.5327598, 38.9894912),
    (-86.4917327, 38.9900249),
    (-86.4918186, 39.001832),
    (-86.497698, 39.0026991),
    (-86.5030244, 39.0090356),
    (-86.5046981, 39.0107363),
    (-86.5090111, 39.0110531),
    (-86.5098158, 39.009961),
    (-86.510084, 39.0094025)
]

def generate_flood_map(dem_path, water_level_ft):
    """
    Clips the DEM to Monroe Lake bounds, scales units, and overlays
    a anti-aliased flood layer.
    """
    # Adjusted bounding box tightly framing Monroe Lake (Updated to match final selection)
    lon_min, lon_max = -86.525843, -86.289218
    lat_min, lat_max = 38.993715, 39.161233
    
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

    # Apply exclusion polygon mask (below dam)
    # Calculate coordinates for the clipped window
    rows, cols = np.indices(dem_data.shape)
    # Use the window's offset to get absolute pixel coordinates in the source DEM
    abs_rows = rows + window.row_off
    abs_cols = cols + window.col_off
    
    # Convert pixel coordinates to Lon/Lat using the transform matrix
    # Correct Affine transformation:
    # x = a*col + b*row + c
    # y = d*col + e*row + f
    t = src.transform
    lons = t.a * abs_cols + t.b * abs_rows + t.c
    lats = t.d * abs_cols + t.e * abs_rows + t.f
    
    # Create the path and check points
    poly_path = Path(EXCLUSION_POLYGON)
    mask_flat = poly_path.contains_points(np.column_stack((lons.flatten(), lats.flatten())))
    exclusion_mask = mask_flat.reshape(dem_data.shape)
    
    # Smooth edges slightly to combat pixelation along shallow fingers
    smoothed_mask = gaussian_filter(raw_mask, sigma=0.8)
    
    # Exclude the polygon area from flooding
    # We do this AFTER smoothing to ensure absolute transparency in the exclusion zone
    smoothed_mask[exclusion_mask] = 0
    
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

    # Add bounding box coordinates to the bottom of the map
    bounds_text = f"View Area: Lat {lat_min:.6f} to {lat_max:.6f}, Lon {lon_min:.6f} to {lon_max:.6f}"
    plt.figtext(0.5, 0.02, bounds_text, ha="center", fontsize=10, color="gray", style='italic')
    
    output_plot = f"monroe_flood_stage_{int(water_level_ft)}.png"
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"Map successfully saved to disk: {output_plot}")
    plt.show()

if __name__ == "__main__":
    # 1. Use the processed lake elevation file
    dem_file = get_dem_file()
    
    # 2. Run simulation using target water level 
    current_pool_elevation = 546.75 
    generate_flood_map(dem_file, current_pool_elevation)