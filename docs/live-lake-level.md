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
      <div style="font-size: 0.8em; color: #888; margin-top: 15px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Other years to today's level (+ is other year was higher):</div>
      <div id="lake-level-history" style="font-size: 0.9em; color: #777; margin-top: 5px; font-weight: 500;">Loading history...</div>
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
  const NORMAL_LEVEL = 538.00;

   async function updateLakeLevel() {
     const valueEl = document.getElementById('lake-level-value');
     const timeEl = document.getElementById('lake-level-time');
     const historyEl = document.getElementById('lake-level-history');
     
     try {
        const proxyUrl = `https://monroe-lake-level.laszewski.workers.dev`;
        const sensorName = encodeURIComponent("Monroe.Elev.Inst.0.0.lrldlb-rev");
        
        // 1. Fetch Current Level
        const response = await fetch(proxyUrl);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        
        let val = null;
        if (data.values && data.values.length > 0) {
          const latest = data.values[data.values.length - 1];
          val = Array.isArray(latest) ? latest[1] : latest.value;
          const time = Array.isArray(latest) ? latest[0] : latest.time;
          
          const relativeVal = (val - NORMAL_LEVEL).toFixed(2);
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

        // 2. Fetch Historical Data for the same day for the past 3 years
        const now = new Date();
        const currentYear = now.getFullYear();
        const month = now.getMonth();
        const day = now.getDate();
        
        let historyText = "";
        const yearsToFetch = [currentYear - 1, currentYear - 2, currentYear - 3];
        
        if (val === null) {
          historyEl.innerText = "Cannot calculate history without current level";
        } else {
          for (const year of yearsToFetch) {
            const begin = new Date(year, month, day, 0, 0, 0).toISOString();
            const end = new Date(year, month, day, 23, 59, 59).toISOString();
            
            try {
              const histResponse = await fetch(`${proxyUrl}?name=${sensorName}&begin=${begin}&end=${end}`);
              if (histResponse.ok) {
                const histData = await histResponse.json();
                if (histData.values && histData.values.length > 0) {
                  const histLatest = histData.values[histData.values.length - 1];
                  const histVal = Array.isArray(histLatest) ? histLatest[1] : histLatest.value;
                  
                  // Calculate difference relative to today's value (val)
                  const diff = (histVal - val).toFixed(2);
                  const sign = diff >= 0 ? '+' : '';
                  historyText += `${year}: ${sign}${diff} ${data.unit || 'ft'} | `;
                } else {
                  historyText += `${year}: N/A | `;
                }
              } else {
                console.error(`Error fetching ${year}: ${histResponse.status} ${histResponse.statusText}`);
                historyText += `${year}: Error | `;
              }
            } catch (e) {
              console.error(`Exception fetching ${year}:`, e);
              historyText += `${year}: Error | `;
            }
          }
          historyEl.innerText = historyText ? historyText.slice(0, -3) : "No historical data available";
        }

     } catch (error) {
       console.error('Error fetching lake level:', error);
       valueEl.innerText = "Error";
       timeEl.innerText = `Error: ${error.message}`;
       historyEl.innerText = "Error loading history";
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