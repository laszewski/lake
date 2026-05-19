import csv
import requests
import os
import time
import random

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
    # Rotate User-Agents to avoid fingerprinting
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://apps.nationalmap.gov/epqs/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    
    try:
        response = session.get(base_url, params=params, headers=headers, timeout=10)
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
                # Use correct header names from the CSV
                lat = row.get('Latitude')
                lng = row.get('Longitude')
                
                if lat and lng:
                    coord_key = (lat, lng)
                    if coord_key in usgs_cache:
                        row['USGS'] = usgs_cache[coord_key]
                    else:
                        val = get_usgs_elevation(session, lat, lng)
                        usgs_cache[coord_key] = val
                        row['USGS'] = val
                        # Randomize delay to mimic human behavior (0.5 to 1.5 seconds)
                        time.sleep(random.uniform(0.5, 1.5))
                else:
                    # Log missing coords to console but don't spam tqdm
                    pass

    # Write updated data back to CSV
    with open(temp_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    os.replace(temp_path, csv_path)
    print(f"Successfully updated {csv_path} with USGS elevations.")

if __name__ == "__main__":
    main()