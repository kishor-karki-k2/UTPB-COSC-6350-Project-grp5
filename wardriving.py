import pandas as pd
import os

# Setting up the file directory
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(current_directory, 'wifi_data.csv')  # Replace with your CSV file name

# Google Maps API Key
API_KEY = 'AIzaSyB_5G4UpMqDbacBCm2bTrfse69KftYheuw'

# Load data from CSV
data = pd.read_csv(csv_file)

# Check if required columns are present
required_columns = ['CurrentLatitude', 'CurrentLongitude', 'Encryption']
for column in required_columns:
    if column not in data.columns:
        raise ValueError(f"CSV file must contain '{column}' column")

# Extract valid rows where latitude and longitude are not null
valid_data = data[['CurrentLatitude', 'CurrentLongitude', 'Encryption']].dropna()

# Grouping data based on Encryption type
grouped_data = {
    "Open": valid_data[valid_data['Encryption'].str.lower() == 'none'][['CurrentLatitude', 'CurrentLongitude']].values.tolist(),
    "WEP": valid_data[valid_data['Encryption'].str.lower() == 'wep'][['CurrentLatitude', 'CurrentLongitude']].values.tolist(),
    "WPA": valid_data[valid_data['Encryption'].str.lower() == 'wpa'][['CurrentLatitude', 'CurrentLongitude']].values.tolist(),
    "WPA2": valid_data[valid_data['Encryption'].str.lower() == 'wpa2'][['CurrentLatitude', 'CurrentLongitude']].values.tolist(),
    "Unknown": valid_data[valid_data['Encryption'].str.lower() == 'unknown'][['CurrentLatitude', 'CurrentLongitude']].values.tolist()
}

# Compute map center
all_locations = [loc for locations in grouped_data.values() for loc in locations]
if len(all_locations) > 0:
    avg_lat = sum([loc[0] for loc in all_locations]) / len(all_locations)
    avg_lng = sum([loc[1] for loc in all_locations]) / len(all_locations)
else:
    raise ValueError("No valid latitude and longitude data found in the CSV file")

# Colors for each group
colors = {"Open": "red", "WEP": "blue", "WPA": "purple", "WPA2": "green", "Unknown": "orange"}

# HTML Template
html_file = os.path.join(current_directory, 'map.html')
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Map with ALL Menu</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        #map {{
            height: 90vh;
            width: 100%;
        }}
        #menu {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: white;
            padding: 10px;
            border-bottom: 1px solid #ddd;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        #menu button {{
            margin: 0 5px;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            background-color: #007BFF;
            color: white;
            cursor: pointer;
        }}
        #menu button:hover {{
            background-color: #0056b3;
        }}
        #counter {{
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
    </style>
</head>
<body>
    <div id="menu"></div>
    <div id="counter">Showing: 0 markers</div>
    <div id="map"></div>
    <script>
        let map;
        const markerGroups = {{}};
        const groupCounts = {{}};  // To store counts for each group

        function updateMarkerCount(groupName) {{
            let count = 0;
            if (groupName === "ALL") {{
                for (const group in markerGroups) {{
                    count += markerGroups[group].length;
                }}
            }} else if (markerGroups[groupName]) {{
                count = markerGroups[groupName].length;
            }}
            document.getElementById('counter').textContent = "Showing: " + count + " markers";
        }}

        function showOnlyMarkers(groupName) {{
            // Hide all markers
            for (const group in markerGroups) {{
                markerGroups[group].forEach(marker => marker.setMap(null));
            }}
            // Show selected group markers
            if (groupName === "ALL") {{
                for (const group in markerGroups) {{
                    markerGroups[group].forEach(marker => marker.setMap(map));
                }}
            }} else if (markerGroups[groupName]) {{
                markerGroups[groupName].forEach(marker => marker.setMap(map));
            }}
            updateMarkerCount(groupName); // Update the counter
        }}

        function initMap() {{
            // Initialize map
            map = new google.maps.Map(document.getElementById('map'), {{
                center: {{lat: {avg_lat}, lng: {avg_lng}}},  // Escaped curly braces
                zoom: 10
            }});

            // Marker data
            const groupedData = {grouped_data};
            const colors = {colors};

            // Create markers and store them in the appropriate group
            for (const [groupName, locations] of Object.entries(groupedData)) {{
                const color = colors[groupName];
                markerGroups[groupName] = locations.map(([lat, lng]) => {{
                    const marker = new google.maps.Marker({{
                        position: {{lat, lng}},
                        map: map, // All markers visible by default for "ALL"
                        icon: {{
                            path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                            scale: 3,
                            fillColor: color,
                            fillOpacity: 1,
                            strokeWeight: 1
                        }}
                    }});
                    return marker;
                }});
                groupCounts[groupName] = markerGroups[groupName].length;  // Store the count
            }}

            // Create menu buttons
            const menuButtons = ["ALL", ...Object.keys(groupedData)];
            menuButtons.forEach(groupName => {{
                const button = document.createElement('button');
                button.textContent = groupName;
                button.onclick = () => showOnlyMarkers(groupName);
                document.getElementById('menu').appendChild(button);
            }});

            // Initially show "ALL"
            showOnlyMarkers("ALL");
        }}

        // Initialize the map
        window.onload = initMap;
    </script>
</body>
</html>
"""



# Write HTML content to file
with open(html_file, 'w') as file:
    file.write(html_content)

print(f"Interactive map with 'ALL' menu has been successfully generated and saved to {html_file}")
