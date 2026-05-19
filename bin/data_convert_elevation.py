import csv
import re

input_file = 'elevation.csv'
output_file = 'elevation_converted.csv'

data = []
current_location = None

elevation_pattern = re.compile(r'Estimated Elevation\s*:\s*([\d.]+)\s*m\s*or\s*([\d.]+)\s*feet')
location_pattern = re.compile(r'Location\s*\(latitude,longitude\):\s*([\d.-]+),([\d.-]+)')

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    line = lines[i].strip()
    if i + 1 < len(lines) and lines[i+1].strip().startswith('='):
        current_location = line
        continue
    elev_match = elevation_pattern.search(line)
    if elev_match and current_location:
        elev_m = elev_match.group(1)
        elev_ft = elev_match.group(2)
        for j in range(i + 1, min(i + 5, len(lines))):
            loc_match = location_pattern.search(lines[j])
            if loc_match:
                lat = loc_match.group(1)
                lon = loc_match.group(2)
                data.append([current_location, lat, lon, elev_m, elev_ft])
                break

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Location', 'Latitude', 'Longitude', 'Elevation (m)', 'Elevation (ft)'])
    writer.writerows(data)
