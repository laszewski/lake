# Lake Level CORS Proxy (Cloudflare Worker)

This directory contains a Cloudflare Worker implementation that acts as a dedicated, cached CORS proxy for the USACE Lake Level API. It allows frontend applications (like GitHub Pages) to fetch live lake level data without encountering CORS errors.

## 🚀 Setup Instructions

### 1. Deploy to Cloudflare
1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Workers & Pages** $\rightarrow$ **Create application** $\rightarrow$ **Create Worker**.
3. Name your worker (e.g., `lake-level-proxy`) and click **Deploy**.
4. Click **Edit Code**, delete the existing content, and paste the contents of `worker.js` from this folder.
5. Click **Save and Deploy**.

### 2. Your API Endpoint
Once deployed, your endpoint will look like this:
`https://lake-level-proxy.<your-subdomain>.workers.dev/`

---

## 📖 API Documentation

The proxy forwards requests to the USACE API. You can either call the proxy without parameters to get the default Lake Monroe data, or provide specific parameters.

### Request Details
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `name` | String | No | `Monroe.Elev.Inst.0.0.lrldlb-rev` | The USACE sensor ID. |
| `begin` | String | No | `2026-01-01T00:00:00Z` | Start date in ISO 8601 format. |
| `end` | String | No | `2026-12-31T23:59:59Z` | End date in ISO 8601 format. |

### Response Format
The proxy returns a JSON object from USACE:
- `unit`: The unit of measurement (e.g., "ft").
- `values`: An array of `[timestamp, value]` pairs.

### Caching Policy
- **Cache Duration**: 6 Hours (21,600 seconds).
- **Behavior**: The worker checks the Cloudflare Edge Cache. If the data is older than 6 hours, it fetches fresh data from USACE and updates the cache.

---

## 💻 Usage Examples

Replace `YOUR_WORKER_URL` with your actual Cloudflare Worker URL (e.g., `https://lake-level-proxy.abc.workers.dev`).

### 1. cURL
Quickly test the endpoint from your terminal:
```bash
curl -s "https://YOUR_WORKER_URL/"
```

### 2. JavaScript (Fetch API)
Ideal for integration into a website.
```javascript
async function fetchLakeLevel() {
  const workerUrl = "https://YOUR_WORKER_URL/";
  
  try {
    const response = await fetch(workerUrl);
    const data = await response.json();
    
    // Get the most recent value from the array
    const latest = data.values[data.values.length - 1];
    console.log(`Current Level: ${latest[1]} ${data.unit}`);
  } catch (error) {
    console.error("Error fetching lake level:", error);
  }
}

fetchLakeLevel();
```

### 3. Python (Requests)
Ideal for backend scripts or data analysis.
```python
import requests

def get_lake_level():
    worker_url = "https://YOUR_WORKER_URL/"
    
    try:
        response = requests.get(worker_url)
        response.raise_for_status()
        data = response.json()
        
        latest_value = data["values"][-1][1]
        unit = data.get("unit", "ft")
        print(f"Current Lake Level: {latest_value} {unit}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_lake_level()