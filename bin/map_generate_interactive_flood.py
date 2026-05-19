import os
import requests
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import folium
from folium import plugins
from folium.raster_layers import ImageOverlay

def download_usgs_dem():
    """Downloads the USGS DEM tile for the Monroe Lake area."""
    url = "https://s3.amazonaws.com/usgs-dem-tiles/13_n40w087.tif"
    output_file = "docs/data/USGS_13_n40w087.tif"
    
    if os.path.exists(output_file):
        print(f"Using existing DEM file: {output_file}")
        return output_file

    print(f"Downloading DEM tile from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"DEM tile saved to {output_file}")
        return output_file
    else:
        raise Exception(f"Failed to download DEM: {response.status_code}")

def generate_interactive_flood_map(dem_file, water_level_ft):
    """Generates an interactive Folium map showing flood areas for a given water level."""
    output_html = "docs/flood-map-interactive.html"
    
    print(f"Processing DEM for water level: {water_level_ft} ft...")
    
    with rasterio.open(dem_file) as src:
        # Reproject to EPSG:4326 (WGS84) for Folium
        dst_crs = 'EPSG:4326'
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        
        # Create an empty array for the reprojected data
        reprojected_dem = np.zeros((height, width), dtype=np.float32)
        
        reproject(
            source=rasterio.band(src, 1),
            destination=reprojected_dem,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.bilinear
        )
        
        # Calculate bounds for Folium [ [min_lat, min_lon], [max_lat, max_lon] ]
        # transform[2] is left (min_lon), transform[5] is top (max_lat)
        # transform[0] is pixel width, transform[4] is pixel height (negative)
        min_lon = transform[2]
        max_lon = transform[2] + transform[0] * width
        max_lat = transform[5]
        min_lat = transform[5] + transform[4] * height
        folium_bounds = [[min_lat, min_lon], [max_lat, max_lon]]

    # Convert water level from feet to meters for comparison with DEM
    water_level_m = water_level_ft * 0.3048
    
    # Create a binary mask: 1 where elevation <= water_level, 0 otherwise
    # We use a semi-transparent blue for the flood area
    mask = (reprojected_dem <= water_level_m).astype(np.uint8)
    
    # Create RGBA image: [R, G, B, A]
    # Lighter Blue: (0, 100, 200), Alpha: 125 if flooded, 0 if not
    rgba_data = np.zeros((height, width, 4), dtype=np.uint8)
    rgba_data[..., 0] = 0     # R
    rgba_data[..., 1] = 100   # G
    rgba_data[..., 2] = 200   # B
    rgba_data[..., 3] = mask * 125 # Alpha
    
    # Initialize Folium Map
    m = folium.Map(location=[39.06, -86.45], zoom_start=13, tiles=None)
    
    # Add OpenStreetMap base layer
    folium.TileLayer('openstreetmap', name="OpenStreetMap").add_to(m)
    
    # Add high-contrast Satellite base layer option
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite View",
        overlay=False,
        control=True,
    ).add_to(m)
    
    # Add the flood overlay
    ImageOverlay(
        image=rgba_data,
        bounds=folium_bounds,
        name=f"Flood Layer ({water_level_ft} ft)",
        opacity=0.8,
        interactive=False,
        cross_origin=False,
    ).add_to(m)
    
    folium.LayerControl(position="topright").add_to(m)
    plugins.Fullscreen(position="topleft", title="Expand", title_cancel="Exit").add_to(m)
    
    # Custom Zoom Control Panel
    locations = {
        "Cartop": [39.09829, -86.46397],
        "Cutright": [39.06877, -86.40666],
        "Fairfax": [39.02275, -86.48169],
        "Osprey Trail": [39.01638, -86.48529],
        "Paynetown": [39.08104, -86.43379],
        "Pinegrove": [39.10910, -86.38909],
        "North Fork": [39.11133, -86.39926],
        "Salt Creek": [39.13144, -86.39161],
    }
    
    buttons_html = '<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); font-family: Arial, sans-serif;">'
    buttons_html += '<h4 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">Quick Zoom</h4>'
    
    for name, coords in locations.items():
        js_call = f"var m = Object.values(window).find(v => v instanceof L.Map); if(m) m.setView([{coords[0]}, {coords[1]}], 17);"
        buttons_html += f'<button onclick="{js_call}" style="display: block; width: 100%; margin: 5px 0; padding: 5px 10px; cursor: pointer; background: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; text-align: left; font-size: 12px;">{name}</button>'
    
    buttons_html += '</div>'
    
    m.get_root().html.add_child(folium.Element(buttons_html))
    
    m.save(output_html)
    print(f"\nSuccess! Interactive map file generated: {output_html}")

if __name__ == "__main__":
    dem_file = download_usgs_dem()
    current_pool_elevation = 547.41
    generate_interactive_flood_map(dem_file, current_pool_elevation)