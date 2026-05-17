# Lake Level Service API Examples

This directory contains the implementation for the Lake Level monitoring service. Below are examples of how to query the USACE API for the Monroe Lake elevation data.

## API Details
- **Sensor ID:** `Monroe.Elev.Inst.0.0.lrldlb-rev`
- **Base URL:** `https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries`
- **Required Parameters:** 
  - `name`: The sensor ID.
  - `begin`: Start date in ISO 8601 format (e.g., `2026-01-01T00:00:00Z`).
  - `end`: End date in ISO 8601 format.

---

## 1. cURL Example
Use this for quick testing in your terminal.

```bash
curl -s "https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries?name=Monroe.Elev.Inst.0.0.lrldlb-rev&begin=2026-01-01T00%3A00%3A00Z&end=2026-12-31T23%3A59%3A59Z"
```

## 2. JavaScript Example (Fetch API)
Use this for frontend applications. Note that if calling directly from a browser, you may encounter CORS restrictions and might need a proxy.

```javascript
async function getLakeLevel() {
  const sensor = "Monroe.Elev.Inst.0.0.lrldlb-rev";
  const begin = "2026-01-01T00:00:00Z";
  const end = new Date().toISOString();
  const url = `https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries?name=${sensor}&begin=${begin}&end=${end}`;

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    
    const latest = data.values[data.values.length - 1];
    const value = Array.isArray(latest) ? latest[1] : latest.value;
    console.log(`Current Lake Level: ${value} ${data.unit}`);
  } catch (error) {
    console.error("Could not fetch lake level:", error);
  }
}

getLakeLevel();
```

## 3. Python Example (Requests)
Use this for backend services or data analysis scripts.

```python
import requests
from datetime import datetime, timedelta

def get_lake_level():
    sensor = "Monroe.Elev.Inst.0.0.lrldlb-rev"
    # Fetch data from the last 24 hours
    end = datetime.utcnow()
    begin = end - timedelta(days=1)
    
    params = {
        "name": sensor,
        "begin": begin.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "end": end.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    url = "https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries"
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("values"):
            latest = data["values"][-1]
            value = latest[1] if isinstance(latest, list) else latest.get("value")
            unit = data.get("unit", "ft")
            print(f"Current Lake Level: {value} {unit}")
        else:
            print("No data found.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    get_lake_level()