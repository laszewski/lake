import csv
import requests
import os

def get_usgs_elevation(session, lat, lng):
    """
    Fetches elevation for a single coordinate from the USGS Point Query Service.
    """
    base_url = "https://epqs.nationalmap.gov/v1/3dep/json"
    params = {
        'x': lng,
        'y': lat,
        'units': 'Feet'  # Requesting Feet directly to match project units
    }
    
    try:
        response = session.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('elevation')
    except Exception as e:
        print(f"Error fetching USGS data for {lat}, {lng}: {e}")
        return None

def main():
    csv_path = 'docs/data/elevation.csv'
    temp_path = 'docs/data/elevation_temp.csv'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    with open(csv_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        if 'USGS' not in fieldnames:
            fieldnames.append('USGS')
        
        rows = list(reader)

    # Cache to avoid duplicate requests for the same coordinates
    usgs_cache = {}
    
    with requests.Session() as session:
        for row in rows:
            # Only fetch if USGS is empty or missing
            if not row.get('USGS'):
                lat = row.get('lat')
                lng = row.get('lon')
                
                if lat and lng:
                    coord_key = (lat, lng)
                    if coord_key in usgs_cache:
                        row['USGS'] = usgs_cache[coord_key]
                    else:
                        print(f"Fetching USGS elevation for {row.get('loc')} ({lat}, {lng})...")
                        val = get_usgs_elevation(session, lat, lng)
                        usgs_cache[coord_key] = val
                        row['USGS'] = val
                else:
                    print(f"Missing coordinates for {row.get('loc')}, skipping USGS fetch.")

    # Write updated data back to CSV
    with open(temp_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    os.replace(temp_path, csv_path)
    print(f"Successfully updated {csv_path} with USGS elevations.")

if __name__ == "__main__":
    main()