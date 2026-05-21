import leafmap.foliumap as leafmap
import folium

# 1. Initialize map and center it slightly further west to balance the new boundary
m = leafmap.Map(center=[39.08, -86.41], zoom=12)

# 2. Add your newly updated terrain raster
m.add_raster('lake.tif', cmap='terrain', layer_name="Lake Elevation Data")

# 3. Create the updated folium rectangle using your new lower-left anchor
red_box = folium.Rectangle(
    bounds=[[38.993715, -86.525843], [39.161233, -86.289218]],
    color="red",
    weight=4,
    fill=False
)

# 4. Attach vector object and save layout
m.add_child(red_box)
m.to_html('map.html')
print("✅ Localized map regenerated with new lower-left coordinate!")
