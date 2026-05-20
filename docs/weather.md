# Weather for Lake Monroe

To help you plan your visit, we provide the current weather conditions for the Lake Monroe area.

<div style="max-width: 600px; margin: 20px auto; font-family: sans-serif;">
  <div id="weather-card" style="text-align: center; padding: 30px; background: #f8faff; border: 1px solid #d1d9ff; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="margin-top: 0; color: #3f51b5; font-size: 1.2em; text-transform: uppercase; letter-spacing: 1px;">Current Weather</h3>
    
    <div style="margin-bottom: 20px;">
      <span style="font-size: 0.9em; color: #666; text-transform: uppercase; font-weight: 600;">Temperature</span>
      <div id="weather-temp" style="font-size: 3em; font-weight: 800; color: #3f51b5; margin: 10px 0; line-height: 1;">Loading...</div>
      <div id="weather-range" style="font-size: 1em; color: #555;">Fetching range...</div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 15px; margin-bottom: 25px; text-align: center;">
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Humidity</span>
        <span id="weather-humidity" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Wind</span>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px;">
          <div style="position: relative; width: 40px; height: 40px; margin-bottom: 5px;">
            <div id="weather-wind-arrow" style="position: absolute; width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-bottom: 20px solid #3f51b5; left: 14px; top: 5px; transition: transform 0.5s ease;"></div>
          </div>
          <div id="weather-wind" style="font-size: 1.1em; font-weight: 700; color: #1a237e; line-height: 1.2;">Loading...</div>
        </div>
      </div>
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">UV Index</span>
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
          <div id="weather-uv-dot" style="width: 24px; height: 24px; border-radius: 50%; background: #ccc;"></div>
          <span id="weather-uv" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
        </div>
      </div>
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Condition</span>
        <span id="weather-cond" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
       <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
         <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Cloud Cover</span>
         <span id="weather-clouds" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
       </div>
       <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
         <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Feels Like</span>
         <span id="weather-feels" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
       </div>
       <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
         <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Visibility</span>
         <span id="weather-vis" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
       </div>
       <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
         <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Pressure</span>
         <span id="weather-press" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
       </div>
       <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
         <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Dew Point</span>
         <span id="weather-dew" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
       </div>
       <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
         <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Precip</span>
         <span id="weather-precip" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
       </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 25px; text-align: center;">
      <div style="padding: 15px; background: #f0f4ff; border-radius: 15px; border: 1px solid #d1d9ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Sunrise &bull; Sunset</span>
        <div id="weather-sun-range" style="font-size: 1.1em; font-weight: 700; color: #1a237e; line-height: 1.4;">Loading...</div>
      </div>
      <div style="padding: 15px; background: #f0f4ff; border-radius: 15px; border: 1px solid #d1d9ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Moon Phase</span>
        <span id="weather-moon" style="font-size: 1.1em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
      <div style="padding: 15px; background: #f0f4ff; border-radius: 15px; border: 1px solid #d1d9ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Bloomington Time (EST)</span>
        <span id="weather-time" style="font-size: 1.1em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
    </div>

    <div style="border-top: 1px solid #e0e5ff; padding-top: 20px;">
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
  async function updateWeather() {
    const tempEl = document.getElementById('weather-temp');
    const rangeEl = document.getElementById('weather-range');
    const humEl = document.getElementById('weather-humidity');
    const windEl = document.getElementById('weather-wind');
    const uvEl = document.getElementById('weather-uv');
    const condEl = document.getElementById('weather-cond');
    const cloudEl = document.getElementById('weather-clouds');
    const feelsEl = document.getElementById('weather-feels');
    const visEl = document.getElementById('weather-vis');
    const pressEl = document.getElementById('weather-press');
    const uvDotEl = document.getElementById('weather-uv-dot');
    const windArrowEl = document.getElementById('weather-wind-arrow');
    const dewEl = document.getElementById('weather-dew');
    const precipEl = document.getElementById('weather-precip');
    const sunRangeEl = document.getElementById('weather-sun-range');
    const moonEl = document.getElementById('weather-moon');
    const timeEl = document.getElementById('weather-time');

    try {
      const proxyUrl = `https://monroe-lake-level.laszewski.workers.dev/weather`;
      
      const response = await fetch(proxyUrl);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      
      if (!data || !data.current_condition || !data.weather) {
        throw new Error("Invalid weather data format received");
      }

      const current = data.current_condition[0] || {};
      const weather = data.weather[0] || {};
      const astronomy = (weather.astronomy && weather.astronomy[0]) ? weather.astronomy[0] : {};
      const hourly = (weather.hourly && weather.hourly[0]) ? weather.hourly[0] : {};

      tempEl.innerText = current.temp_F ? `${current.temp_F}°F` : 'N/A';
      rangeEl.innerText = `High: ${weather.maxtempF || 'N/A'}°F • Low: ${weather.mintempF || 'N/A'}°F`;
      humEl.innerText = current.humidity ? `${current.humidity}%` : 'N/A';
      
      const dirAbbr = current.winddir16Point || '';
      const windDeg = current.winddirDegree || 0;
      
      if (windArrowEl) windArrowEl.style.transform = `rotate(${windDeg}deg)`;
      windEl.innerHTML = `${current.windspeedMiles || 'N/A'} mph<br>${dirAbbr}`;
      
      const uv = parseInt(current.uvIndex);
      let uvColor = '#ccc';
      let uvLabel = '';
      
      if (!isNaN(uv)) {
        if (uv <= 2) { uvColor = '#32cd32'; uvLabel = ''; } // Green
        else if (uv <= 5) { uvColor = '#ffff00'; uvLabel = ''; } // Yellow
        else if (uv <= 7) { uvColor = '#ffa500'; uvLabel = ' (High)'; } // Orange
        else if (uv <= 10) { uvColor = '#ff0000'; uvLabel = ' (Very High)'; } // Red
        else { uvColor = '#800080'; uvLabel = ' (Extreme)'; } // Purple
      }
      
      if (uvDotEl) uvDotEl.style.backgroundColor = uvColor;
      uvEl.innerText = (current.uvIndex !== undefined) ? `${current.uvIndex}${uvLabel}` : 'N/A';
      condEl.innerText = (current.weatherDesc && current.weatherDesc[0]) ? current.weatherDesc[0].value : 'N/A';
      cloudEl.innerText = current.cloudcover ? `${current.cloudcover}%` : 'N/A';
      feelsEl.innerText = current.FeelsLikeF ? `${current.FeelsLikeF}°F` : 'N/A';
      visEl.innerText = current.visibility ? `${current.visibility} mi` : 'N/A';
      pressEl.innerText = current.pressure ? `${current.pressure} mb` : 'N/A';
      dewEl.innerText = hourly.DewPointF ? `${hourly.DewPointF}°F` : 'N/A';
      precipEl.innerText = current.precipMM ? `${current.precipMM} mm` : 'N/A';
      sunRangeEl.innerHTML = `${astronomy.sunrise || 'N/A'}<br>${astronomy.sunset || 'N/A'}`;
      moonEl.innerText = astronomy.moon_phase || 'N/A';
       
       // Get actual current time in Bloomington (Eastern Time)
       const bloomingtonTime = new Intl.DateTimeFormat('en-US', {
         timeZone: 'America/New_York',
         hour: 'numeric',
         minute: 'numeric',
         hour12: true
       }).format(new Date());
       
       timeEl.innerText = bloomingtonTime;

    } catch (error) {
      console.error('Error fetching weather:', error);
      const elements = [tempEl, rangeEl, humEl, windEl, uvEl, condEl, cloudEl, feelsEl, visEl, pressEl, dewEl, precipEl, sunRangeEl, moonEl, timeEl];
      elements.forEach(el => { if(el) el.innerText = 'Error'; });
      if(uvDotEl) uvDotEl.style.backgroundColor = '#ccc';
      if(windArrowEl) windArrowEl.style.transform = 'rotate(0deg)';
    }
  }

  // Run once on load
  updateWeather();
})();
</script>

***

**Note:** Weather conditions can change rapidly near the lake. Always check the latest forecast before heading out.