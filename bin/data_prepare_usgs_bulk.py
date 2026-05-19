import csv
import os

def main():
    """
    This script prepares a coordinate file for the USGS Bulk Point Query Service.
    URL: https://apps.nationalmap.gov/bulkpqs/
    
    The Bulk PQS service allows uploading a file with coordinates to get elevations in bulk,
    which bypasses the rate limits and 403 errors encountered with the single-point API.
    """
    input_csv = 'docs/data/elevation.csv'
    output_file = 'usgs_bulk_upload.txt'
    
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return

    try:
        with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # The Bulk PQS expects Longitude, Latitude
            coords = []
            for row in reader:
                lat = row.get('Latitude')
                lng = row.get('Longitude')
                if lat and lng:
                    # Format: Longitude, Latitude
                    coords.append(f"{lng},{lat}")
            
            if not coords:
                print("No valid coordinates found in the CSV.")
                return

            with open(output_file, mode='w', encoding='utf-8') as outfile:
                outfile.write("\n".join(coords))
        
        print(f"Successfully created {output_file} with {len(coords)} coordinates.")
        print("\nNext Steps:")
        print(f"1. Go to https://apps.nationalmap.gov/bulkpqs/")
        print(f"2. Upload the generated file: {output_file}")
        print("3. Select 'Feet' as the units.")
        print("4. Download the resulting file and manually update the USGS column in elevation.csv.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()