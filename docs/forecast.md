# Kayak Photo Weather Forecast for Lake Monroe

Plan your trip with the 3-day weather forecast for the Bloomington, IN area.

<div style="max-width: 800px; margin: 20px auto; font-family: sans-serif;">
  <div id="forecast-card" style="padding: 30px; background: #f8faff; border: 1px solid #d1d9ff; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="margin-top: 0; color: #3f51b5; font-size: 1.2em; text-transform: uppercase; letter-spacing: 1px; text-align: center;">Today's Hourly Breakdown</h3>
    <div style="overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 10px; overflow: hidden;">
        <thead>
          <tr style="background-color: #5c6bc0; color: white; text-align: left;">
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 80px;">Time</th>
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 80px;">Temp</th>
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff;">Condition</th>
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 120px; white-space: nowrap;">Wind</th>
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 80px;">Precip</th>
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 80px; text-align: center;">Photo</th>
            <th style="padding: 10px 15px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 150px;">Events</th>
          </tr>
        </thead>
        <tbody id="hourly-body">
          <tr>
            <td colspan="7" style="padding: 20px; text-align: center; color: #666;">Loading hourly data...</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h3 style="margin-top: 30px; color: #3f51b5; font-size: 1.2em; text-transform: uppercase; letter-spacing: 1px; text-align: center;">3-Day Forecast</h3>
    <div style="overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 10px; overflow: hidden; table-layout: auto;">
        <thead>
          <tr style="background-color: #3f51b5; color: white; text-align: left;">
            <th style="padding: 10px 8px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 1%; white-space: nowrap;">Date</th>
            <th style="padding: 10px 8px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 1%; white-space: nowrap;">Temp</th>
            <th style="padding: 10px 8px; font-weight: 600; border-bottom: 2px solid #d1d9ff;">Condition</th>
            <th style="padding: 10px 8px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 1%; white-space: nowrap;">Wind</th>
            <th style="padding: 10px 8px; font-weight: 600; border-bottom: 2px solid #d1d9ff; text-align: center; width: 1%; white-space: nowrap;">Photo</th>
            <th style="padding: 10px 8px; font-weight: 600; border-bottom: 2px solid #d1d9ff; width: 1%; white-space: nowrap;">Precip</th>
          </tr>
        </thead>
        <tbody id="forecast-body">
          <tr>
            <td colspan="5" style="padding: 20px; text-align: center; color: #666;">Loading forecast data...</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div style="border-top: 1px solid #e0e5ff; padding-top: 20px; margin-top: 20px; text-align: center;">
      <p style="font-size: 0.95em; color: #555; margin-bottom: 15px;">
        Data provided by wttr.in for Bloomington, IN.
      </p>
      <a href="https://wttr.in/Bloomington,Indiana" 
         target="_blank" 
         style="display: inline-block; padding: 12px 24px; background-color: #3f51b5; color: white; text-decoration: none; font-weight: 600; border-radius: 10px; font-size: 1em; transition: background-color 0.2s; box-shadow: 0 2px 4px rgba(63, 81, 181, 0.3);">
         View Full Forecast &rarr;
      </a>
    </div>
  </div>
</div>

<script>
(function() {
  async function updateForecast() {
    const forecastBody = document.getElementById('forecast-body');
    const hourlyBody = document.getElementById('hourly-body');

    const timeToMins = (t) => {
      if (!t) return null;
      const match = t.match(/(\d+):?(\d+)?\s*(AM|PM)?/i);
      if (!match) return null;
      let hrs = parseInt(match[1]);
      const mins = match[2] ? parseInt(match[2]) : 0;
      const amp = match[3];
      if (amp && amp.toUpperCase() === 'PM' && hrs < 12) hrs += 12;
      if (amp && amp.toUpperCase() === 'AM' && hrs === 12) hrs = 0;
      return hrs * 60 + mins;
    };

    try {
      const proxyUrl = `https://monroe-lake-level.laszewski.workers.dev/weather`;
      
      const response = await fetch(proxyUrl);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      if (!data || !data.weather || !Array.isArray(data.weather)) {
        throw new Error("Invalid weather data format received");
      }
      const weatherForecast = data.weather;
      
      forecastBody.innerHTML = '';

      weatherForecast.forEach(day => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #e0e5ff';
        
        const date = day.date || 'N/A';
        const condition = (day.hourly && day.hourly[0] && day.hourly[0].weatherDesc && day.hourly[0].weatherDesc[0]) 
                          ? day.hourly[0].weatherDesc[0].value : 'N/A';
        const high = day.maxtempF || 'N/A';
        const low = day.mintempF || 'N/A';
        const precip = (day.hourly && day.hourly[0]) ? day.hourly[0].precipMM : '0';

        // Calculate Wind Range
        const windSpeeds = (day.hourly || []).map(h => parseFloat(h.windspeedMiles || 0));
        const minWind = Math.min(...windSpeeds);
        const maxWind = Math.max(...windSpeeds);

        // Calculate Photo Suitability for Daylight Hours
        const astro = (day.astronomy && day.astronomy[0]) ? day.astronomy[0] : {};
        const sunriseMins = timeToMins(astro.sunrise);
        const sunsetMins = timeToMins(astro.sunset);
        
        const daylightHours = day.hourly.filter(h => {
          const tVal = parseInt(h.time);
          const mins = tVal <= 23 ? tVal * 60 : (Math.floor(tVal/100)*60 + (tVal%100));
          return sunriseMins !== null && sunsetMins !== null && mins >= sunriseMins && mins < sunsetMins;
        });

        let photoCircles = '';
        if (daylightHours.length > 0) {
          // Pick 3 representative hours: start, middle, end of daylight
          const indices = [0, Math.floor(daylightHours.length / 2), daylightHours.length - 1];
          const uniqueIndices = [...new Set(indices)];
          
          photoCircles = `<div style="display: flex; justify-content: center; gap: 4px;">`;
          uniqueIndices.forEach(idx => {
            const h = daylightHours[idx];
            const ws = parseFloat(h.windspeedMiles);
            let color = '#f44336';
            if (ws <= 5) color = '#4caf50';
            else if (ws <= 10) color = '#ffeb3b';
            else if (ws <= 15) color = '#ff9800';
            photoCircles += `<div style="width: 10px; height: 10px; border-radius: 50%; background-color: ${color}; border: 1px solid rgba(0,0,0,0.1);"></div>`;
          });
          photoCircles += `</div>`;
        } else {
          photoCircles = '<span style="color: #ccc; font-size: 0.8em;">N/A</span>';
        }

        row.innerHTML = `
          <td style="padding: 10px 8px; color: #333; font-weight: 600; white-space: nowrap;">${date}</td>
          <td style="padding: 10px 8px; color: #333; font-weight: 700; white-space: nowrap;">${low} - ${high}°F</td>
          <td style="padding: 10px 8px; color: #555;">${condition}</td>
          <td style="padding: 10px 8px; color: #555; white-space: nowrap;">${minWind}–${maxWind} mph</td>
          <td style="padding: 10px 8px; text-align: center; white-space: nowrap;">${photoCircles}</td>
          <td style="padding: 10px 8px; color: #555; white-space: nowrap;">${precip} mm</td>
        `;
        forecastBody.appendChild(row);
      });

      // Populate Hourly Data for Today
      const todayHourly = weatherForecast[0].hourly;
      const astronomy = (weatherForecast[0].astronomy && weatherForecast[0].astronomy[0]) ? weatherForecast[0].astronomy[0] : {};
      const sunriseStr = astronomy.sunrise || '';
      const sunsetStr = astronomy.sunset || '';


      const sunriseMins = timeToMins(sunriseStr);
      const sunsetMins = timeToMins(sunsetStr);
      
      // Create a unified timeline of events
      const timeline = [];
      
      // Add hourly blocks
      todayHourly.forEach(hour => {
        const timeVal = parseInt(hour.time);
        let mins;
        
        if (timeVal <= 23) {
          // Format is just the hour (0-23)
          mins = timeVal * 60;
        } else {
          // Format is HHmm (e.g., 300 for 3:00, 1500 for 15:00)
          const hrs = Math.floor(timeVal / 100);
          const m = timeVal % 100;
          mins = hrs * 60 + m;
        }
        timeline.push({ mins, type: 'hourly', data: hour });
      });
      
      // Add sunrise event
      if (sunriseMins !== null) {
        timeline.push({ mins: sunriseMins, type: 'sunrise', timeStr: sunriseStr });
      }
      
      // Add sunset event
      if (sunsetMins !== null) {
        timeline.push({ mins: sunsetMins, type: 'sunset', timeStr: sunsetStr });
      }
      
      // Sort timeline by minutes since midnight
      timeline.sort((a, b) => a.mins - b.mins);
      
      hourlyBody.innerHTML = '';
      timeline.forEach(item => {
        const hRow = document.createElement('tr');
        hRow.style.borderBottom = '1px solid #e0e5ff';
        
        let bgColor = 'white';
        let rowContent = '';

        if (item.type === 'sunrise') {
          bgColor = '#fff9c4'; // Yellow
          rowContent = `
            <td style="padding: 10px 15px; color: #333; font-weight: 600;">${item.timeStr}</td>
            <td colspan="4" style="border: none; background: transparent;"></td>
            <td style="padding: 10px 15px; color: #3f51b5; font-weight: 600; font-size: 0.9em;">🌅 Sunrise</td>
            <td style="border: none; background: transparent;"></td>
          `;
        } else if (item.type === 'sunset') {
          bgColor = '#f5f5f5'; // Grey
          rowContent = `
            <td style="padding: 10px 15px; color: #333; font-weight: 600;">${item.timeStr}</td>
            <td colspan="4" style="border: none; background: transparent;"></td>
            <td style="padding: 10px 15px; color: #3f51b5; font-weight: 600; font-size: 0.9em;">🌇 Sunset</td>
            <td style="border: none; background: transparent;"></td>
          `;
        } else {
          // Hourly row
          if (sunriseMins !== null && item.mins < sunriseMins) {
            bgColor = '#f5f5f5'; // Grey before sunrise
          } else if (sunsetMins !== null && item.mins >= sunsetMins) {
            bgColor = '#f5f5f5'; // Grey after sunset
          }
          
          const hour = item.data;
          
          // Convert the raw time (e.g., "300" or "3") to a readable format (e.g., "3:00 AM")
          const timeVal = parseInt(hour.time);
          let displayTime = hour.time;
          if (timeVal <= 23) {
            displayTime = `${timeVal}:00 ${timeVal >= 12 ? 'PM' : 'AM'}`;
            if (timeVal === 0) displayTime = '12:00 AM';
            if (timeVal === 12) displayTime = '12:00 PM';
            if (timeVal > 12) {
              const h12 = timeVal - 12;
              displayTime = `${h12}:00 PM`;
            }
          } else {
            const hrs = Math.floor(timeVal / 100);
            const m = timeVal % 100;
            const amp = hrs >= 12 ? 'PM' : 'AM';
            let h12 = hrs % 12;
            if (h12 === 0) h12 = 12;
            displayTime = `${h12}:${m.toString().padStart(2, '0')} ${amp}`;
          }

          const windSpeed = parseFloat(hour.windspeedMiles);
          let photoColor = '#ccc';
          
          // Check if it's before sunrise or after sunset
          if (sunriseMins !== null && item.mins < sunriseMins) {
            photoColor = '#555'; // Dark gray for night/dawn
          } else if (sunsetMins !== null && item.mins >= sunsetMins) {
            photoColor = '#555'; // Dark gray for night/dusk
          } else {
            // Daylight wind suitability
            if (windSpeed <= 5) photoColor = '#4caf50'; // Green
            else if (windSpeed <= 10) photoColor = '#ffeb3b'; // Yellow
            else if (windSpeed <= 15) photoColor = '#ff9800'; // Orange
            else photoColor = '#f44336'; // Red
          }

          rowContent = `
            <td style="padding: 10px 15px; color: #333; font-weight: 600;">${displayTime}</td>
            <td style="padding: 10px 15px; color: #333;">${hour.tempF}°F</td>
            <td style="padding: 10px 15px; color: #555;">${hour.weatherDesc[0].value}</td>
            <td style="padding: 10px 15px; color: #555; white-space: nowrap;">
              <div style="display: flex; align-items: center; gap: 6px;">
                <div style="position: relative; width: 16px; height: 16px;">
                  <div style="position: absolute; width: 0; height: 0; border-left: 3px solid transparent; border-right: 3px solid transparent; border-bottom: 10px solid #3f51b5; left: 5px; top: 3px; transform: rotate(${hour.winddirDegree || 0}deg);"></div>
                </div>
                <span>${hour.windspeedMiles} mph ${hour.winddir16Point}</span>
              </div>
            </td>
            <td style="padding: 10px 15px; color: #555;">${hour.precipMM} mm</td>
            <td style="padding: 10px 15px; text-align: center;">
              <div style="width: 14px; height: 14px; border-radius: 50%; background-color: ${photoColor}; margin: 0 auto; border: 1px solid rgba(0,0,0,0.1);"></div>
            </td>
            <td style="padding: 10px 15px; color: #3f51b5; font-weight: 600; font-size: 0.9em;"></td>
          `;
        }

        hRow.style.backgroundColor = bgColor;
        hRow.innerHTML = rowContent;
        hourlyBody.appendChild(hRow);
      });

    } catch (error) {
      console.error('Error fetching forecast:', error);
      forecastBody.innerHTML = `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #d32f2f;">Error loading forecast data. Please try again later.</td></tr>`;
      hourlyBody.innerHTML = `<tr><td colspan="7" style="padding: 20px; text-align: center; color: #d32f2f;">Error loading hourly data.</td></tr>`;
    }
  }

  updateForecast();
})();
</script>

***

### 📷 Kayak Photography Wind Guide

For doing photos in a kayak, acceptable wind speeds are under **5 to 10 mph (4 to 9 knots)**. Winds above this create choppy water and push your kayak around, turning your boat into an unstable platform that makes holding a camera steady and avoiding blurry photos almost impossible.

**Wind Range Suitability:**
- <span style="color: #4caf50; font-weight: bold;">0–5 mph: Blissful.</span> The water is often glassy, offering perfect conditions for sharp wildlife shots, macro photography, and stunning reflections.
- <span style="color: #fbc02d; font-weight: bold;">5–10 mph: Manageable.</span> Light chop; increase shutter speed (e.g., 1/1000s) and rely on image stabilization.
- <span style="color: #ff9800; font-weight: bold;">10–15 mph: Challenging.</span> Waves increase and kayak blows off course. Not recommended for casual photography.
- <span style="color: #f44336; font-weight: bold;">15+ mph: Unsafe.</span> Choppy conditions and whitecaps make operating a camera a major risk.

**Pro Tips for Kayak Photography:**
- **Go early**: Wind speeds are typically lowest in the early morning. Paddle out against the wind so the breeze pushes you home when you are tired.
- **Seek shelter**: Narrow rivers, sheltered coves, and areas with dense tree lines block the wind and smooth out the water.
- **Prioritize safety**: Review marine and weather forecasts using the National Weather Service to ensure conditions match your experience.

**Note:** Forecasts are estimates. Please check the full forecast for detailed hourly updates.
