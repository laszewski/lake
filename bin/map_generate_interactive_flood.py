import os
import requests
import numpy as np
import rasterio
import base64
from rasterio.windows import from_bounds
import folium
from folium import plugins
from folium.raster_layers import ImageOverlay
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

from rasterio.warp import calculate_default_transform, reproject, Resampling

def generate_interactive_flood_map(dem_file, water_level_ft):
    """Generates an interactive Folium map showing flood areas for a given water level."""
    output_html = "docs/flood-map-interactive.html"
    
    print(f"Processing DEM for water level: {water_level_ft} ft...")
    
    # Monroe Lake bounds in WGS84 (Updated to match final selection)
    lon_min, lon_max = -86.525843, -86.289218
    lat_min, lat_max = 38.993715, 39.161233
    
    dst_crs = 'EPSG:3857' # Web Mercator (Leaflet/Folium standard)
    
    with rasterio.open(dem_file) as src:
        # Calculate transform and dimensions for the target reprojected window
        from rasterio.warp import transform_bounds, transform as transform_coords
        w, s, e, n = transform_bounds(src.crs, dst_crs, lon_min, lat_min, lon_max, lat_max)
        
        # Define target transform for the output image
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
    
    # Apply exclusion polygon mask (below dam)
    # We calculate the mask directly in the target Web Mercator space to ensure perfect alignment
    cols_dst, rows_dst = np.meshgrid(np.arange(dst_width), np.arange(dst_height))
    # Transform pixel coordinates to Web Mercator meters
    x_dst = dst_transform.a * cols_dst + dst_transform.c
    y_dst = dst_transform.e * rows_dst + dst_transform.f
    
    # Transform Web Mercator meters to Lon/Lat (using the same CRS as the source DEM)
    lons_dst, lats_dst = transform_coords(dst_crs, src.crs, x_dst.flatten(), y_dst.flatten())
    lons_dst = np.array(lons_dst).reshape(dst_height, dst_width)
    lats_dst = np.array(lats_dst).reshape(dst_height, dst_width)
    
    # Create mask in target space
    poly_path = Path(EXCLUSION_POLYGON)
    exclusion_mask = poly_path.contains_points(np.column_stack((lons_dst.flatten(), lats_dst.flatten())))
    exclusion_mask = exclusion_mask.reshape(dst_height, dst_width)
    
    # Create soft mask for anti-aliasing
    transition_width = 0.5 # meters
    alpha = 125 * (1.0 - (reprojected_dem - (water_level_m - transition_width/2)) / transition_width)
    alpha = np.clip(alpha, 0, 125).astype(np.uint8)
    
    # Set nodata AND exclusion areas to transparent
    alpha[is_nodata] = 0
    alpha[exclusion_mask] = 0
    
    # Create RGBA images
    rgba_blue = np.zeros((dst_height, dst_width, 4), dtype=np.uint8)
    rgba_blue[..., 2] = 255   # B
    rgba_blue[..., 3] = alpha 

    rgba_red = np.zeros((dst_height, dst_width, 4), dtype=np.uint8)
    rgba_red[..., 0] = 200    # R
    rgba_red[..., 3] = alpha 
    
    # Embed DEM data for client-side querying
    # Convert float32 array to base64 string for efficient embedding
    dem_bytes = reprojected_dem.tobytes()
    dem_b64 = base64.b64encode(dem_bytes).decode('utf-8')
    
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
        "Stillwater Observation": [39.143109, -86.392968],
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
    buttons_html += '<h4 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">Map Tools</h4>'
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
    
    buttons_html += '<div style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">'
    buttons_html += '<h4 style="margin: 0 0 5px 0; font-size: 14px; color: #333;">Current View</h4>'
    buttons_html += '<div style="font-size: 11px; color: #666; line-height: 1.4;">'
    buttons_html += f'Lat: <span id="view-lat">{lat_min:.6f} to {lat_max:.6f}</span><br>'
    buttons_html += f'Lon: <span id="view-lon">{lon_min:.6f} to {lon_max:.6f}</span>'
    buttons_html += '</div>'
    buttons_html += '</div>'
    
    buttons_html += '<div style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">'
    buttons_html += '<div style="margin-bottom: 5px; font-size: 13px;">'
    buttons_html += '<input type="checkbox" id="query-mode" onchange="updateQueryMode()"> '
    buttons_html += '<label for="query-mode" style="font-weight: bold; font-size: 14px; color: #333;">Point Info</label>'
    buttons_html += '</div>'
    buttons_html += '<div id="point-info" style="font-size: 12px; color: #666; line-height: 1.4;">Click map to query elevation</div>'
    buttons_html += '</div>'
    
    buttons_html += '<h4 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">Quick Zoom</h4>'
    
    for name, coords in locations.items():
        js_call = f"var m = Object.values(window).find(v => v instanceof L.Map); if(m) m.setView([{coords[0]}, {coords[1]}], 17);"
        buttons_html += f'<button onclick="{js_call}" style="display: block; width: 100%; margin: 5px 0; padding: 5px 10px; cursor: pointer; background: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; text-align: left; font-size: 12px;">{name}</button>'
    
    buttons_html += '</div>' # Close panel-content
    buttons_html += '</div>' # Close flood-control-panel
    
    script_html = '<script>'
    
    # Embed the DEM data as a Float32Array
    script_html += f'const demB64 = "{dem_b64}";'
    script_html += 'const demData = new Float32Array(Uint8Array.from(atob(demB64), c => c.charCodeAt(0)).buffer);'
    
    # Function to update query mode status
    script_html += 'function updateQueryMode() {'
    script_html += '  const enabled = document.getElementById("query-mode").checked;'
    script_html += '  const info = document.getElementById("point-info");'
    script_html += '  if (enabled) {'
    script_html += '    info.innerHTML = "Query Mode ON:<br>Click map for elevation";'
    script_html += '  } else {'
    script_html += '    info.innerText = "Click map to query elevation";'
    script_html += '  }'
    script_html += '}'

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

    # Function to update view coordinates on map move
    script_html += 'function updateViewCoords(map) {'
    script_html += '  const bounds = map.getBounds();'
    script_html += '  const sw = bounds.getSouthWest();'
    script_html += '  const ne = bounds.getNorthEast();'
    script_html += '  document.getElementById("view-lat").innerText = sw.lat.toFixed(6) + " to " + ne.lat.toFixed(6);'
    script_html += '  document.getElementById("view-lon").innerText = sw.lng.toFixed(6) + " to " + ne.lng.toFixed(6);'
    script_html += '}'

    # Coordinate transformation and sampling logic
    script_html += 'function getElevationAt(lat, lon) {'
    script_html += '  const R = 6378137;'
    script_html += '  const x = R * lon * Math.PI / 180;'
    script_html += '  const y = R * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI / 180) / 2));'
    script_html += '  const col = Math.floor((x - ' + str(dst_transform.c) + ') / ' + str(dst_transform.a) + ');'
    script_html += '  const row = Math.floor((y - ' + str(dst_transform.f) + ') / ' + str(dst_transform.e) + ');'
    script_html += '  if (col >= 0 && col < ' + str(dst_width) + ' && row >= 0 && row < ' + str(dst_height) + ') {'
    script_html += '    return demData[row * ' + str(dst_width) + ' + col];'
    script_html += '  }'
    script_html += '  return null;'
    script_html += '}'
    
    # Initialize map event listener for coordinates and clicks
    script_html += 'window.onload = function() {'
    script_html += '  const map = Object.values(window).find(v => v instanceof L.Map);'
    script_html += '  if (map) {'
    script_html += '    map.on("moveend", function() { updateViewCoords(map); });'
    script_html += '    updateViewCoords(map);'
    script_html += '    '
    script_html += '    let lastMarker = null;'
    script_html += '    map.on("click", function(e) {'
    script_html += '      if (!document.getElementById("query-mode").checked) return;'
    script_html += '      const lat = e.latlng.lat;'
    script_html += '      const lon = e.latlng.lng;'
    script_html += '      const elev = getElevationAt(lat, lon);'
    script_html += '      const lakeLevel_m = ' + str(water_level_m) + ';'
    script_html += '      const lakeLevel_ft = ' + str(water_level_ft) + ';'
    script_html += '      '
    script_html += '      if (elev === null || isNaN(elev) || elev < -100) {'
    script_html += '        document.getElementById("point-info").innerHTML = `Lat: ${lat.toFixed(5)}<br>Lon: ${lon.toFixed(5)}<br>No elevation data`;'
    script_html += '        if (lastMarker) map.removeLayer(lastMarker);'
    script_html += '        lastMarker = L.circleMarker([lat, lon], {radius: 5, color: "gray", fillOpacity: 0.8}).addTo(map);'
    script_html += '        return;'
    script_html += '      }'
    script_html += '      '
    script_html += '      const elev_ft = elev / 0.3048;'
    script_html += '      const isHigher = elev_ft > lakeLevel_ft;'
    script_html += '      const color = isHigher ? "green" : "blue";'
    script_html += '      const status = isHigher ? "Above Lake" : "Below Lake/Flooded";'
    script_html += '      '
    script_html += '      document.getElementById("point-info").innerHTML = `Lat: ${lat.toFixed(6)}<br>Lon: ${lon.toFixed(6)}<br>Elev: ${elev_ft.toFixed(2)} ft<br>Status: <span style="color:${color}; font-weight:bold;">${status}</span>`;'
    script_html += '      if (lastMarker) map.removeLayer(lastMarker);'
    script_html += '      lastMarker = L.circleMarker([lat, lon], {radius: 6, color: color, weight: 2, fillColor: color, fillOpacity: 0.6}).addTo(map);'
    script_html += '    });'
    script_html += '  }'
    script_html += '};'
    
    # Fetch lake level
    script_html += 'fetch("https://monroe-lake-level.laszewski.workers.dev/level")'
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
    dem_file = get_dem_file()
    current_pool_elevation = get_live_lake_level()
    
    if current_pool_elevation is None:
        print("Falling back to default elevation of 538.0 ft")
        current_pool_elevation = 538.0
        
    generate_interactive_flood_map(dem_file, current_pool_elevation)