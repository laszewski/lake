# Live Lake Level

To ensure you are seeing the most accurate and up-to-date information, we provide a direct link to the official U.S. Army Corps of Engineers (USACE) monitoring station.

<div style="max-width: 600px; margin: 20px auto; font-family: sans-serif;">
  <div id="lake-level-card" style="text-align: center; padding: 30px; background: #f8faff; border: 1px solid #d1d9ff; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="margin-top: 0; color: #3f51b5; font-size: 1.2em; text-transform: uppercase; letter-spacing: 1px;">Current Lake Level</h3>
    
    <div style="margin-bottom: 10px;">
      <span style="font-size: 0.9em; color: #666; text-transform: uppercase; font-weight: 600;">Above Normal: </span>
      <div id="lake-level-relative" style="font-size: 4em; font-weight: 800; color: #3f51b5; margin: 10px 0; line-height: 1;">Loading...</div>
    </div>
    <div style="margin-bottom: 20px;">
      <span style="font-size: 0.9em; color: #666; text-transform: uppercase; font-weight: 600;">Absolute Level: </span>
      <span id="lake-level-value" style="font-size: 1.5em; font-weight: 700; color: #1a237e;">Loading...</span>
    </div>
    <div id="lake-level-time" style="font-size: 0.85em; color: #777; margin-bottom: 25px;">Fetching latest data...</div>
    
    <div style="border-top: 1px solid #e0e5ff; padding-top: 20px;">
      <p style="font-size: 0.95em; color: #555; margin-bottom: 15px;">
        For detailed trends, forecasts, and official monitoring, visit the USACE station.
      </p>
      <a href="https://water.usace.army.mil/overview/lrl/locations/monroe" 
         target="_blank" 
         style="display: inline-block; padding: 12px 24px; background-color: #3f51b5; color: white; text-decoration: none; font-weight: 600; border-radius: 10px; font-size: 1em; transition: background-color 0.2s; box-shadow: 0 2px 4px rgba(63, 81, 181, 0.3);">
        View Official USACE Data &rarr;
      </a>
    </div>
  </div>

<script>
(function() {
  async function updateLakeLevel() {
    const valueEl = document.getElementById('lake-level-value');
    const timeEl = document.getElementById('lake-level-time');
    
    try {
      const now = new Date();
      const yesterday = new Date(now.getTime() - (24 * 60 * 60 * 1000));
      
      const begin = yesterday.toISOString();
      const end = now.toISOString();
      const sensor = "Monroe.Elev.Inst.0.0.lrldlb-rev";
      const targetUrl = `https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries?name=${sensor}&begin=${begin}&end=${end}`;
      // Using corsproxy.io which returns the raw response instead of wrapping it in a JSON object
      const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(targetUrl)}`;
      
      const response = await fetch(proxyUrl);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      
      if (data.values && data.values.length > 0) {
        const latest = data.values[data.values.length - 1];
        // Assuming values is an array of [timestamp, value] or similar
        // Based on typical USACE JSON, it's often an array of objects or arrays
        const val = Array.isArray(latest) ? latest[1] : latest.value;
        const time = Array.isArray(latest) ? latest[0] : latest.time;
        
        const relativeVal = (val - 538.00).toFixed(2);
        document.getElementById('lake-level-relative').innerText = `${relativeVal} ft`;
        valueEl.innerText = `${val} ${data.unit || 'ft'}`;
        
        if (time) {
          const date = new Date(time);
          timeEl.innerText = `Last updated: ${date.toLocaleString()}`;
        } else {
          timeEl.innerText = `Last updated: ${new Date().toLocaleString()}`;
        }
      } else {
        valueEl.innerText = "N/A";
        timeEl.innerText = "No recent data available from USACE";
      }
    } catch (error) {
      console.error('Error fetching lake level:', error);
      valueEl.innerText = "Error";
      timeEl.innerText = `Error: ${error.message}`;
    }
  }

  // Run on load
  updateLakeLevel();
})();
</script>
</div>

***

### Why a separate window?
The U.S. Army Corps of Engineers website employs strict security protocols (X-Frame-Options) that prevent their data from being embedded directly into other websites. This is a security measure to protect their infrastructure and ensure data integrity.

**What to look for on the USACE page:**
- **Current Stage:** The most recent water level reading.
- **Trend Graph:** A visual representation of whether the lake is rising or falling.
- **Forecasts:** Predicted levels for the coming days.