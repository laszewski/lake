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
        <span id="weather-wind" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">UV Index</span>
        <span id="weather-uv" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Condition</span>
        <span id="weather-cond" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
      </div>
      <div style="padding: 15px; background: white; border-radius: 15px; border: 1px solid #e0e5ff;">
        <span style="font-size: 0.8em; color: #666; text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 5px;">Cloud Cover</span>
        <span id="weather-clouds" style="font-size: 1.4em; font-weight: 700; color: #1a237e;">Loading...</span>
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

    try {
      const targetUrl = `https://wttr.in/Bloomington,Indiana?format=j1`;
      const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(targetUrl)}`;
      
      const response = await fetch(proxyUrl);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      const current = data.current_condition[0];
      const weather = data.weather[0];

      tempEl.innerText = `${current.temp_F}°F`;
      rangeEl.innerText = `High: ${weather.maxtempF}°F &bull; Low: ${weather.mintempF}°F`;
      humEl.innerText = `${current.humidity}%`;
      windEl.innerText = `${current.windspeedMiles} mph ${current.winddir16Point}`;
      uvEl.innerText = `${weather.uvIndex} ${weather.uvIndex >= 6 ? '(High)' : ''}`;
      condEl.innerText = current.weatherDesc[0].value;
      cloudEl.innerText = `${current.cloudcover}%`;

    } catch (error) {
      console.error('Error fetching weather:', error);
      const elements = [tempEl, rangeEl, humEl, windEl, uvEl, condEl, cloudEl];
      elements.forEach(el => { if(el) el.innerText = 'Error'; });
    }
  }

  // Run once on load
  updateWeather();
})();
</script>

***

**Note:** Weather conditions can change rapidly near the lake. Always check the latest forecast before heading out.