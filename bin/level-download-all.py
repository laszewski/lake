import requests
import csv
import time
from datetime import datetime, timedelta

def download_lake_levels():
    base_url = "https://water.usace.army.mil/cda/reporting/providers/lrl/timeseries"
    sensor_name = "Monroe.Elev.Inst.0.0.lrldlb-rev"
    output_file = "level-all.csv"
    
    # Start from now and go backwards
    end_date = datetime.utcnow()
    start_year = 1900 # Reasonable floor for data
    
    all_data = []
    year = end_date.year
    
    print(f"Starting download for sensor: {sensor_name}")
    print(f"Saving to: {output_file}")
    
    while year >= start_year:
        # Define the window for the current year
        begin = datetime(year, 1, 1, 0, 0, 0).isoformat() + "Z"
        end = datetime(year, 12, 31, 23, 59, 59).isoformat() + "Z"
        
        # Adjust end date for the current year
        if year == end_date.year:
            end = end_date.isoformat() + "Z"
            
        print(f"Fetching data for {year}...", end=" ", flush=True)
        
        params = {
            "name": sensor_name,
            "begin": begin,
            "end": end
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # The USACE API returns data in a 'values' list: [[timestamp, value], ...]
            if "values" in data and data["values"]:
                year_data = data["values"]
                all_data.extend(year_data)
                print(f"Done ({len(year_data)} records)")
            else:
                print("No data found.")
                # If we hit a year with no data, we might have reached the start of the record
                # But we'll continue a bit further just in case of gaps
                if year < 2000: # Stop if we are far back and find nothing
                    break
        except Exception as e:
            print(f"Error: {e}")
            break
            
        year -= 1
        time.sleep(0.5) # Be respectful to the API

    if not all_data:
        print("No data was downloaded.")
        return

    # Save to CSV
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "level_ft"])
            writer.writerows(all_data)
        print(f"\nSuccessfully saved {len(all_data)} records to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    download_lake_levels()