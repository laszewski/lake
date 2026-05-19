import json

# Load the elevation data
with open('elevation_data.json', 'r', encoding='utf-8') as f:
    elevation_data = f.read()

template = f"""# Lake Level Flood Map

This interactive map shows the flood status of various locations based on the current live lake level.

<div id="lake-level-info" style="margin-bottom: 20px; padding: 15px; background: #f0f4f8; border-radius: 10px; border: 1px solid #d1d9ff; font-family: sans-serif;">
  <strong>Current Lake Level:</strong> <span id="current-level">Loading...</span> ft
</div>

<div id="map" style="height: 600px; width: 100%; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"></div>

<div style="margin-top: 20px; margin-bottom: 20px; font-family: sans-serif;">
  <strong>Legend:</strong><br>
  <span style="color: blue;">🔵</span> Flooded (Elevation $\le$ Lake Level)<br>
  <span style="color: #d4a017;">🟡</span> Warning (Within 1 foot)<br>
  <span style="color: green;">🟢</span> Safe (Elevation > Lake Level + 1 ft)
</div>

### Location Details

<div style="overflow-x: auto;">
  <table id="flood-table" style="width: 100%; border-collapse: collapse; font-family: sans-serif; margin-top: 10px;">
    <thead>
      <tr style="background-color: #f2f2f2; text-align: left;">
        <th style="padding: 12px; border: 1px solid #ddd;">Location</th>
        <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Elevation (ft)</th>
        <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Status</th>
      </tr>
    </thead>
    <tbody>
      <!-- Data will be inserted here by JS -->
    </tbody>
  </table>
</div>

<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
(async function() {{
  const elevationData = {elevation_data};
  const proxyUrl = 'https://monroe-lake-level.laszewski.workers.dev';
  
  // Initialize Map
  const map = L.map('map').setView([39.05, -86.45], 11);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap contributors'
  }}).addTo(map);

  try {{
    // Fetch Live Lake Level
    const response = await fetch(proxyUrl);
    const data = await response.json();
    const latestValue = data.values[data.values.length - 1][1];
    document.getElementById('current-level').innerText = latestValue;

    const tableBody = document.querySelector('#flood-table tbody');
    
    // Sort data by location for the table
    const sortedData = [...elevationData].sort((a, b) => a.loc.localeCompare(b.loc));

    // Plot Markers and Populate Table
    sortedData.forEach(point => {{
      let color = 'green';
      let status = 'Safe';
      let statusEmoji = '🟢';
      
      if (point.elev <= latestValue) {{
        color = 'blue';
        status = 'Flooded';
        statusEmoji = '🔵';
      }} else if (point.elev <= latestValue + 1) {{
        color = 'orange';
        status = 'Warning';
        statusEmoji = '🟡';
      }}

      // Add Map Marker
      L.circleMarker([point.lat, point.lon], {{
        radius: 8,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
      }}).addTo(map).bindPopup(`<strong>${{point.loc}}</strong><br>Elevation: ${{point.elev}} ft<br>Status: ${{status}}`);

      // Add Table Row
      const row = document.createElement('tr');
      row.innerHTML = `
        <td style="padding: 10px; border: 1px solid #ddd;">${{point.loc}}</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${{point.elev}}</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${{statusEmoji}} ${{status}}</td>
      `;
      tableBody.appendChild(row);
    }});
  }} catch (error) {{
    console.error('Error loading map data:', error);
    document.getElementById('current-level').innerText = 'Error loading data';
  }}
}})();
</script>
"""

with open('docs/lake-level-map.md', 'w', encoding='utf-8') as f:
    f.write(template)

print("Successfully updated docs/lake-level-map.md with table")
