export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight requests
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    const url = new URL(request.url);
    
    let targetUrl;
    
    // Handle weather requests
    if (url.pathname === "/weather") {
      targetUrl = "https://wttr.in/Bloomington,Indiana?format=j1";
    } else if (url.pathname === "/level" || url.pathname === "/") {
      // Handle USACE lake level requests
      const baseTargetUrl = "https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries";
      const queryString = url.search;
      
      if (queryString) {
        targetUrl = `${baseTargetUrl}${queryString}`;
      } else {
        // Default to the last 24 hours for the primary sensor
        const now = new Date();
        const yesterday = new Date(now.getTime() - (24 * 60 * 60 * 1000));
        targetUrl = `${baseTargetUrl}?name=Monroe.Elev.Inst.0.0.lrldlb-rev&begin=${yesterday.toISOString()}&end=${now.toISOString()}`;
      }
    } else {
      return new Response("Not Found", { status: 404 });
    }

    try {
      // 2. Check the Cloudflare Cache first
      const cache = caches.default;
      let response = await cache.match(request);

      if (!response) {
        // Cache miss: Fetch from target
        const fetchOptions = {};
        if (url.pathname === "/weather") {
          fetchOptions.headers = { "Accept": "application/json" };
        }
        
        response = await fetch(targetUrl, fetchOptions);
        
        // Create a new response to modify headers and store it in cache
        response = new Response(response.body, response);
        
        // Set cache duration: 6 hours for USACE, 15 mins for weather
        const cacheMaxAge = (url.pathname === "/weather") ? 900 : 21600;
        response.headers.set('Cache-Control', `public, max-age=${cacheMaxAge}`);
        
        // Store the response in cache in the background
        ctx.waitUntil(cache.put(request, response.clone()));
      }

      // 3. Add CORS headers to the response (whether cached or fresh)
      const finalResponse = new Response(response.body, response);
      finalResponse.headers.set('Access-Control-Allow-Origin', '*');
      finalResponse.headers.set('Access-Control-Allow-Methods', 'GET, HEAD, POST, OPTIONS');
      finalResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type');
      
      return finalResponse;
    } catch (e) {
      return new Response('Error fetching data: ' + e.message, { 
        status: 500,
        headers: { 
          'Content-Type': 'text/plain',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  },
};