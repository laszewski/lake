# Lake Level Flood Map

<div style="margin-bottom: 20px; padding: 15px; background: #fff3cd; border-left: 5px solid #ffc107; color: #856404; border-radius: 4px; font-family: sans-serif; font-size: 0.9em; line-height: 1.5;">
  <strong>⚠️ WARNING:</strong> This data is for informational purposes only and <strong>must not be used for navigation</strong> in any form (including cars, boats, or walking) as it is highly inaccurate in nature. The values displayed are based on interpolated elevations and may not be accurate.
</div>

This interactive map shows the flood status of various locations based on the current live lake level.

<div id="lake-level-info" style="margin-bottom: 20px; padding: 15px; background: #f0f4f8; border-radius: 10px; border: 1px solid #d1d9ff; font-family: sans-serif;">
  <strong>Current Lake Level:</strong> <span id="current-level">Loading...</span> ft
</div>

<div id="layer-buttons" style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 10px; font-family: sans-serif; align-items: center;">
  <strong style="font-size: 14px;">Map Style:</strong>
  <!-- Buttons will be inserted here by JS -->
</div>

<div id="area-buttons" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px; font-family: sans-serif;">
  <!-- Buttons will be inserted here by JS -->
</div>

<div id="map" style="height: 600px; width: 100%; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"></div>

<div style="margin-top: 20px; margin-bottom: 20px; font-family: sans-serif;">
  <strong>Legend:</strong><br>
  <span style="color: blue;">🔵</span> Flooded (Elevation $\le$ Lake Level)<br>
  <span style="color: #d4a017;">🟡</span> Warning (Within 1 foot)<br>
  <span style="color: green;">🟢</span> Not Flooded (Elevation > Lake Level + 1 ft)
</div>

### Location Details

<div style="overflow-x: auto;">
  <table id="flood-table" style="width: 100%; border-collapse: collapse; font-family: sans-serif; margin-top: 10px;">
    <thead>
      <tr style="background-color: #f2f2f2; text-align: left;">
        <th style="padding: 12px; border: 1px solid #ddd;">Location</th>
        <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Latitude</th>
        <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Longitude</th>
        <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Elevation (ft)</th>
        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Status</th>
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
(async function() {
  const elevationJsonUrl = '/data/elevation.json';
  const proxyUrl = 'https://monroe-lake-level.laszewski.workers.dev';
  
  // Map Layer Definitions
  const layers = {
    'Standard': {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attr: '© OpenStreetMap contributors'
    },
    'Satellite': {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attr: 'Tiles © Esri &copy; OpenStreetMap contributors'
    },
    'Topological': {
      url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      attr: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
      maxZoom: 17
    }
  };

  // Initialize Map
  const map = L.map('map').setView([39.05, -86.45], 11);
  let currentLayer = L.tileLayer(layers['Standard'].url, {
    attribution: layers['Standard'].attr
  }).addTo(map);

    // 1. Fetch Live Lake Level (Independent)
    try {
      const levelResponse = await fetch(proxyUrl);
      if (!levelResponse.ok) throw new Error(`HTTP ${levelResponse.status}`);
      const levelData = await levelResponse.json();
      const latestValue = levelData.values[levelData.values.length - 1][1];
      document.getElementById('current-level').innerText = latestValue;

      // 2. Fetch Elevation Data (Independent)
      try {
        const elevResponse = await fetch(elevationJsonUrl);
        if (!elevResponse.ok) throw new Error(`HTTP ${elevResponse.status}`);
        const elevationData = await elevResponse.json();

        const tableBody = document.querySelector('#flood-table tbody');
        const buttonContainer = document.getElementById('area-buttons');
        const layerContainer = document.getElementById('layer-buttons');

        // Create Layer Buttons
        Object.keys(layers).forEach(layerName => {
          const btn = document.createElement('button');
          btn.innerText = layerName;
          btn.style.padding = '5px 12px';
          btn.style.borderRadius = '15px';
          btn.style.border = '1px solid #ccc';
          btn.style.backgroundColor = layerName === 'Standard' ? '#e0e0e0' : '#fff';
          btn.style.cursor = 'pointer';
          btn.style.fontSize = '13px';
          btn.style.transition = 'all 0.2s';
          
          btn.onclick = () => {
            layerContainer.querySelectorAll('button').forEach(b => b.style.backgroundColor = '#fff');
            btn.style.backgroundColor = '#e0e0e0';
            map.removeLayer(currentLayer);
            const layerOptions = { attribution: layers[layerName].attr };
            if (layers[layerName].maxZoom) layerOptions.maxZoom = layers[layerName].maxZoom;
            currentLayer = L.tileLayer(layers[layerName].url, layerOptions).addTo(map);
          };
          layerContainer.appendChild(btn);
        });
        
        const sortedData = [...elevationData].sort((a, b) => a.loc.localeCompare(b.loc));

        const uniqueAreas = [...new Set(elevationData.map(p => p.loc))].sort();
        uniqueAreas.forEach(area => {
          const btn = document.createElement('button');
          btn.innerText = area;
          btn.style.padding = '8px 16px';
          btn.style.borderRadius = '20px';
          btn.style.border = '1px solid #ccc';
          btn.style.backgroundColor = '#fff';
          btn.style.cursor = 'pointer';
          btn.style.fontSize = '14px';
          btn.style.transition = 'all 0.2s';
          btn.onmouseover = () => btn.style.backgroundColor = '#f0f0f0';
          btn.onmouseout = () => btn.style.backgroundColor = '#fff';
          btn.onclick = () => {
            const areaPoints = elevationData.filter(p => p.loc === area);
            const bounds = L.latLngBounds(areaPoints.map(p => [p.lat, p.lon]));
            map.fitBounds(bounds, { padding: [50, 50] });
          };
          buttonContainer.appendChild(btn);
        });

        sortedData.forEach(point => {
          let color = 'green';
          let status = 'Not Flooded';
          let statusEmoji = '🟢';
          if (point.elev <= latestValue) {
            color = 'blue'; status = 'Flooded'; statusEmoji = '🔵';
          } else if (point.elev <= latestValue + 1) {
            color = 'orange'; status = 'Warning'; statusEmoji = '🟡';
          }
          L.circleMarker([point.lat, point.lon], {
            radius: 8, fillColor: color, color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.8
          }).addTo(map).bindPopup(`<strong>${point.loc}</strong><br>Elevation: ${point.elev} ft<br>Status: ${status}`);

          const row = document.createElement('tr');
          row.innerHTML = `
            <td style="padding: 10px; border: 1px solid #ddd;">${point.loc}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${point.lat}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${point.lon}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${point.elev}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: left;">${statusEmoji} ${status}</td>
          `;
          tableBody.appendChild(row);
        });
      } catch (elevError) {
        console.error('Error loading elevation data:', elevError);
        // We don't overwrite the lake level here, just log the error
      }
    } catch (levelError) {
      console.error('Error loading lake level:', levelError);
      document.getElementById('current-level').innerText = 'Error loading data';
    }
})();
</script>
