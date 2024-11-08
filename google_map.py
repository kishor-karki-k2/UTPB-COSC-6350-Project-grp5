import pandas as pd
import os
import gmplot

# Setting up the file directory
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(current_directory, 'WigleWifi_data.csv')  # Replace with your CSV file name

# Connecting with API key
API_KEY = 'AIzaSyB_5G4UpMqDbacBCm2bTrfse69KftYheuw'

# Loading data from CSV
data = pd.read_csv(csv_file)

# Checking if the required columns are present or not
if 'CurrentLatitude' not in data.columns or 'CurrentLongitude' not in data.columns:
    raise ValueError("CSV file must contain 'CurrentLatitude' and 'CurrentLongitude' columns")

# Extract the coordinates from the csv file
locations = data[['CurrentLatitude', 'CurrentLongitude']].dropna().values.tolist()

# Creating  the map centered around an average location
if len(locations) > 0:
    avg_lat = sum([loc[0] for loc in locations]) / len(locations)
    avg_lng = sum([loc[1] for loc in locations]) / len(locations)
else:
    raise ValueError("No valid latitude and longitude data found in the CSV file")

# Creating a Google map using gmplot(library)
gmap = gmplot.GoogleMapPlotter(avg_lat, avg_lng, zoom=10, apikey=API_KEY)

# Extracting the latitude and longitude lists
latitudes = [loc[0] for loc in locations]
longitudes = [loc[1] for loc in locations]

# Adding points to the map
gmap.scatter(latitudes, longitudes, color='red', size=20, marker=True)

# Drawing the map to an HTML file
html_file = os.path.join(current_directory, 'map.html')
gmap.draw(html_file)

print(f"Map has been successfully generated and saved to {html_file}")