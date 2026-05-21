import csv

lake_level = 547.41
input_file = 'elevation_converted.csv'
output_file = 'lake-level-map.md'

results = []

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        loc = row['Location']
        elev = float(row['Elevation (ft)'])
        
        if elev <= lake_level:
            status = "🔵 Flooded"
        elif elev <= lake_level + 1:
            status = "🟡 Warning"
        else:
            status = "🟢 Not Flooded"
        
        results.append({
            'location': loc,
            'elevation': elev,
            'status': status
        })

results.sort(key=lambda x: x['location'])

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"# Lake Level Flood Map\n\n")
    f.write(f"**Current Lake Level:** {lake_level} ft\n\n")
    f.write(f"This map shows the flood status of various locations based on the current lake level.\n\n")
    f.write(f"**Legend:**\n")
    f.write(fr"- 🔵 **Blue**: Flooded (Elevation $\le$ {lake_level} ft)" + "\n")
    f.write(fr"- 🟡 **Yellow**: Within 1 foot ({lake_level} ft < Elevation $\le$ {lake_level + 1:.2f} ft)" + "\n")
    f.write(fr"- 🟢 **Green**: Not Flooded (Elevation > {lake_level + 1:.2f} ft)" + "\n\n")
    f.write(f"| Location | Elevation (ft) | Status |\n")
    f.write(f"| :--- | :---: | :---: |\n")
    
    for res in results:
        f.write(f"| {res['location']} | {res['elevation']} | {res['status']} |\n")

print(f"Successfully generated {output_file}")
