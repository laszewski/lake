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
    const pathname = url.pathname.replace(/\/$/, ""); // Remove trailing slash for easier matching
    
    let targetUrl;
    
    // Handle weather requests
    if (pathname === "/weather") {
      targetUrl = "https://wttr.in/Bloomington,Indiana?format=j1";
    } else if (pathname === "/level" || pathname === "") {
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
      return new Response("Not Found", { 
        status: 404,
        headers: { "Access-Control-Allow-Origin": "*" }
      });
    }

    try {
      // 2. Check the Cloudflare Cache first
      const cache = caches.default;
      let response = await cache.match(request);

      if (!response) {
        // Cache miss: Fetch from target
        const fetchOptions = {
          headers: { "Accept": "application/json" }
        };
        
        response = await fetch(targetUrl, fetchOptions);
        
        // Create a new response to modify headers and store it in cache
        // Clone it so we don't consume the body yet
        const freshResponse = response.clone();
        
        // Create a response to be cached
        const responseToCache = new Response(freshResponse.body, freshResponse);
        
        // Set cache duration: 6 hours for USACE, 15 mins for weather
        const cacheMaxAge = (pathname === "/weather") ? 900 : 21600;
        responseToCache.headers.set('Cache-Control', `public, max-age=${cacheMaxAge}`);
        
        // Store in cache
        ctx.waitUntil(cache.put(request, responseToCache));
      }

      // 3. Return response with CORS headers
      const finalResponse = new Response(response.body, response);
      finalResponse.headers.set('Access-Control-Allow-Origin', '*');
      finalResponse.headers.set('Access-Control-Allow-Methods', 'GET, HEAD, POST, OPTIONS');
      finalResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type');
      
      // Force application/json for weather
      if (pathname === "/weather") {
        finalResponse.headers.set('Content-Type', 'application/json; charset=utf-8');
      }
      
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