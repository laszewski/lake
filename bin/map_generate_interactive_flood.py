import os
import requests
import numpy as np
import rasterio
from rasterio.windows import from_bounds
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

from rasterio.warp import calculate_default_transform, reproject, Resampling

def generate_interactive_flood_map(dem_file, water_level_ft):
    """Generates an interactive Folium map showing flood areas for a given water level."""
    output_html = "docs/flood-map-interactive.html"
    
    print(f"Processing DEM for water level: {water_level_ft} ft...")
    
    # Monroe Lake bounds in WGS84
    lon_min, lon_max = -86.55, -86.30
    lat_min, lat_max = 38.98, 39.12
    
    dst_crs = 'EPSG:3857' # Web Mercator (Leaflet/Folium standard)
    
    with rasterio.open(dem_file) as src:
        # Calculate transform and dimensions for the target reprojected window
        # We want to reproject into a window defined by our WGS84 bounds
        from rasterio.warp import transform_bounds
        w, s, e, n = transform_bounds(src.crs, dst_crs, lon_min, lat_min, lon_max, lat_max)
        
        # Define target transform for the output image
        # We'll use a fixed resolution (e.g., 10m)
        res = 10 # meters
        dst_width = int((e - w) / res)
        dst_height = int((n - s) / res)
        dst_transform = rasterio.transform.from_bounds(w, s, e, n, dst_width, dst_height)
        
        reprojected_dem = np.zeros((dst_height, dst_width), dtype=np.float32)
        
        reproject(
            source=rasterio.band(src, 1),
            destination=reprojected_dem,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.bilinear,
            src_nodata=src.nodata
        )
        
        folium_bounds = [[lat_min, lon_min], [lat_max, lon_max]]

    # Convert water level from feet to meters for comparison with DEM
    water_level_m = water_level_ft * 0.3048
    
    # Handle nodata and determine alpha
    # Use 0 for dry/nodata, and 125 for flooded
    is_nodata = (reprojected_dem == src.nodata) | np.isnan(reprojected_dem)
    is_flooded = reprojected_dem <= water_level_m
    
    # Create soft mask for anti-aliasing
    transition_width = 0.5 # meters
    alpha = 125 * (1.0 - (reprojected_dem - (water_level_m - transition_width/2)) / transition_width)
    alpha = np.clip(alpha, 0, 125).astype(np.uint8)
    
    # Set nodata areas to transparent
    alpha[is_nodata] = 0
    
    # Create RGBA images
    rgba_blue = np.zeros((dst_height, dst_width, 4), dtype=np.uint8)
    rgba_blue[..., 2] = 255   # B
    rgba_blue[..., 3] = alpha 

    rgba_red = np.zeros((dst_height, dst_width, 4), dtype=np.uint8)
    rgba_red[..., 0] = 200    # R
    rgba_red[..., 3] = alpha 
    
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
    
    # Add the flood overlays
    # We add Blue first, then Red. JS will target them by index.
    ImageOverlay(
        image=rgba_blue,
        bounds=folium_bounds,
        name="Flood Layer Blue",
        opacity=0.8,
        interactive=False,
        cross_origin=False,
    ).add_to(m)

    ImageOverlay(
        image=rgba_red,
        bounds=folium_bounds,
        name="Flood Layer Red",
        opacity=0, # Hidden by default
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
    
    buttons_html = '<div id="flood-control-panel" style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); font-family: Arial, sans-serif; min-width: 200px;">'
    
    # Panel Header with Toggle
    buttons_html += '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px;">'
    buttons_html += '<strong style="font-size: 14px; color: #333;">Flood Controls</strong>'
    buttons_html += '<button onclick="togglePanel()" id="panel-toggle-btn" style="cursor: pointer; background: #eee; border: 1px solid #ccc; border-radius: 4px; font-size: 10px; padding: 2px 5px;">Minimize</button>'
    buttons_html += '</div>'
    
    # Content Wrapper
    buttons_html += '<div id="panel-content">'
    
    # Flood Layer Controls
    buttons_html += '<div style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">'
    buttons_html += '<h4 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">Flood Layer</h4>'
    buttons_html += '<div style="margin-bottom: 10px; font-size: 13px;">'
    buttons_html += '<input type="checkbox" id="flood-visible" checked onchange="updateFloodLayer()"> '
    buttons_html += '<label for="flood-visible">Show Flood Area</label>'
    buttons_html += '</div>'
    buttons_html += '<div style="font-size: 13px; display: flex; gap: 10px;">'
    buttons_html += '<label><input type="radio" name="flood-color" value="blue" checked onchange="updateFloodLayer()"> Blue</label>'
    buttons_html += '<label><input type="radio" name="flood-color" value="red" onchange="updateFloodLayer()"> Red</label>'
    buttons_html += '</div>'
    buttons_html += '</div>'
    
    buttons_html += '<div style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">'
    buttons_html += '<h4 style="margin: 0 0 5px 0; font-size: 14px; color: #333;">Lake Level</h4>'
    buttons_html += '<div id="lake-level-value" style="font-size: 18px; font-weight: bold; color: #007bff;">Loading...</div>'
    buttons_html += '<div style="margin-top: 10px; font-size: 12px; color: #666;">Above Normal:</div>'
    buttons_html += '<div id="lake-level-relative" style="font-size: 18px; font-weight: bold; color: #007bff;">Loading...</div>'
    buttons_html += '</div>'
    buttons_html += '<h4 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">Quick Zoom</h4>'
    
    for name, coords in locations.items():
        js_call = f"var m = Object.values(window).find(v => v instanceof L.Map); if(m) m.setView([{coords[0]}, {coords[1]}], 17);"
        buttons_html += f'<button onclick="{js_call}" style="display: block; width: 100%; margin: 5px 0; padding: 5px 10px; cursor: pointer; background: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; text-align: left; font-size: 12px;">{name}</button>'
    
    buttons_html += '</div>' # Close panel-content
    buttons_html += '</div>' # Close flood-control-panel
    
    script_html = '<script>'
    # Function to toggle panel visibility
    script_html += 'function togglePanel() {'
    script_html += '  const content = document.getElementById("panel-content");'
    script_html += '  const btn = document.getElementById("panel-toggle-btn");'
    script_html += '  if (content.style.display === "none") {'
    script_html += '    content.style.display = "block";'
    script_html += '    btn.innerText = "Minimize";'
    script_html += '  } else {'
    script_html += '    content.style.display = "none";'
    script_html += '    btn.innerText = "Expand";'
    script_html += '  }'
    script_html += '}'
    # Function to toggle flood layers
    script_html += 'function updateFloodLayer() {'
    script_html += '  const visible = document.getElementById("flood-visible").checked;'
    script_html += '  const color = document.querySelector(\'input[name="flood-color"]:checked\').value;'
    script_html += '  const layers = document.querySelectorAll(".leaflet-image-layer");'
    script_html += '  if (layers.length >= 2) {'
    script_html += '    layers[0].style.opacity = (visible && color === "blue") ? "0.8" : "0";'
    script_html += '    layers[1].style.opacity = (visible && color === "red") ? "0.8" : "0";'
    script_html += '  }'
    script_html += '}'
    
    # Fetch lake level
    script_html += 'fetch("https://monroe-lake-level.laszewski.workers.dev")'
    script_html += '.then(response => response.json())'
    script_html += '.then(data => { const latest = data.values[data.values.length - 1][1]; document.getElementById("lake-level-value").innerText = latest + " ft"; const relative = (latest - 538.00).toFixed(2); document.getElementById("lake-level-relative").innerText = relative + " ft"; })'
    script_html += '.catch(err => { document.getElementById("lake-level-value").innerText = "Error"; });'
    script_html += '</script>'
    
    m.get_root().html.add_child(folium.Element(buttons_html))
    m.get_root().html.add_child(folium.Element(script_html))
    
    m.save(output_html)
    print(f"\nSuccess! Interactive map file generated: {output_html}")

def get_live_lake_level():
    """Fetches the latest lake level from the API."""
    url = "https://monroe-lake-level.laszewski.workers.dev"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        latest_value = data["values"][-1][1]
        print(f"Fetched live lake level: {latest_value} ft")
        return float(latest_value)
    except Exception as e:
        print(f"Error fetching live lake level: {e}")
        return None

if __name__ == "__main__":
    dem_file = download_usgs_dem()
    current_pool_elevation = get_live_lake_level()
    
    if current_pool_elevation is None:
        print("Falling back to default elevation of 538.0 ft")
        current_pool_elevation = 538.0
        
    generate_interactive_flood_map(dem_file, current_pool_elevation)