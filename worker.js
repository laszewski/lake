export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // 1. Define the target USACE API base URL
    const baseTargetUrl = "https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries";
    
    // Use the query parameters from the incoming request (e.g., ?name=...&begin=...&end=...)
    const queryString = url.search;
    const targetUrl = queryString ? `${baseTargetUrl}${queryString}` : `${baseTargetUrl}?name=Monroe.Elev.Inst.0.0.lrldlb-rev&begin=2026-01-01T00:00:00Z&end=2026-12-31T23:59:59Z`;

    try {
      // 2. Check the Cloudflare Cache first
      const cache = caches.default;
      let response = await cache.match(request);

      if (!response) {
        // Cache miss: Fetch from USACE
        response = await fetch(targetUrl);
        
        // We must create a new response to modify headers and store it in cache
        // We set Cache-Control to 6 hours (21600 seconds) to match USACE update frequency
        response = new Response(response.body, response);
        response.headers.set('Cache-Control', 'public, max-age=21600');
        
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
        headers: { 'Content-Type': 'text/plain' }
      });
    }
  },
};