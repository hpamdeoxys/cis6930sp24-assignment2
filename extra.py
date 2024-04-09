# import requests
# import pypdf
# from bs4 import BeautifulSoup
# import re
# from urllib.request import urlretrieve
# import argparse
# import pandas as pd
# from datetime import datetime
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
# import math
# import googlemaps
# import openmeteo_requests
# import requests_cache
# from retry_requests import retry
# import csv

# def main(url):
#     incidents = extract_incidents(url)
#     df = pd.DataFrame(incidents)
#     df['day_of_week'] = df['incident_time'].apply(get_day_of_week)
#     df['time_of_data'] = df['incident_time'].apply(get_time_of_data)
#     # df['location_rank'] = df['incident_location'].apply(rank_locations)
#     df = rank_locations(df)
#     df = rank_nature(df)
#     print(df)
#     # Initialize the Google Maps client with your API key outside of the function
#     gmaps = googlemaps.Client(key='AIzaSyCGje5tE1-7V1A3f3M3VP_tQ6vINmecbAs')  # Replace with your actual API key
#     cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
#     retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
#     openmeteo_client = openmeteo_requests.Client(session=retry_session)
#     df = add_side_of_town_column(df, gmaps)
#     # After you have the dataframe ready with 'latitude' and 'longitude' columns:
#     df = get_weather_condition(df, openmeteo_client)
#     # Then, apply your add_side_of_town_column function with the Google Maps client
    

#     df = check_emsstat(df)
#     df.to_csv('normanok.csv', sep=',', index=False, encoding='utf-8')
    
#     print(df.columns)
#     columns_to_export = ['day_of_week', 'time_of_data', 'weather_code', 'location_rank', 'side_of_town', 'incident_rank', 'nature', 'EMSSTAT']

#     # Export the selected columns to a TSV file
#     df[columns_to_export].to_csv('export.tsv', sep='\t', index=False)

# def fetch_incidents(url):
#     page_response = requests.get(url)
#     if page_response.status_code != 200:
#         raise Exception(f"Webpage request failed with status code {page_response.status_code}")
    
#     parsed_content = BeautifulSoup(page_response.text, 'html.parser')
#     accordion_group = parsed_content.select_one('div.paragraph--type--accordion-group')
    
#     pdf_links = []
#     for accordion_item in accordion_group.select('div.accordion-item'):
#         paragraphs = accordion_item.select('p')
#         for paragraph in paragraphs[2::3]:
#             anchor = paragraph.find('a', href=True)
#             if anchor and 'href' in anchor.attrs:
#                 full_link = f"https://www.normanok.gov{anchor['href']}"
#                 pdf_links.append(full_link)
                
#     return pdf_links

# def extract_incidents(pdf_url):
#     rx = r"\s+(?=\d+/\d+/\d+\s)"
#     l=0
#     incidents=[]
#     urlretrieve(pdf_url, str(l) + '.pdf')
#     with open(str(l) + '.pdf', 'rb') as file:
#         pdf_reader = pypdf.PdfReader(file)
#         text = ""
#         for page_num in range(len(pdf_reader.pages)):
#             page = pdf_reader.pages[page_num]
#             text += page.extract_text(extraction_mode="layout")
#             text += "\n\n\n"
#         text = text.strip(r'\s{2,}')
#         text = re.split(rx, text)
#         i = 0
#         while i < len(text) - 2:
#             parts = re.split(r'\s{2,}', text[i+1], maxsplit=4)
#             if len(parts) == 5:
#                 temps = {'incident_time': parts[0], 'incident_number': parts[1], 'incident_location': parts[2], 'nature': parts[3], 'incident_ori': parts[4]}
#             else:
#                 temps = {'incident_time': parts[0], 'incident_number': parts[1], 'incident_ori': parts[2], 'nature': '', 'incident_location': 'None'}
#             i += 1
#             incidents.append(temps)
#         l += 1

#     return incidents

# def get_day_of_week(date_str):
#     date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M')
#     return (date_obj.weekday() + 1) % 7 + 1

# def get_time_of_data(date_str):
#     # Convert the date string to a datetime object
#     date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M')
#     # Return the hour component of the time
#     return date_obj.hour

# from collections import Counter

# def rank_locations(df):
#     # Use Counter to get the frequency of each location
#     location_counts = Counter(df['incident_location'])
    
#     # Sort locations by frequency in descending order
#     sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    
#     # Initialize the rank and the counter
#     rank = 1
#     cnt = 0
#     prev_freq = None

#     # A dictionary to hold the location ranks
#     location_ranks = {}

#     for location, freq in sorted_locations:
#         if freq != prev_freq:
#             rank += cnt
#             cnt = 0  # Reset counter for the new frequency
#         location_ranks[location] = rank
#         cnt += 1
#         prev_freq = freq

#     # Map the ranks back to the original DataFrame based on location
#     df['location_rank'] = df['incident_location'].apply(lambda x: location_ranks[x])
#     print(location_counts)
    
#     return df


# #CAN USE THIS
# # def rank_locations(df):
# #     # Count the frequency of each location
# #     location_counts = df['incident_location'].value_counts()

# #     # Assign ranks based on frequency (dense ranking will treat ties correctly)
# #     # We use ascending=False to ensure the most frequent location gets rank 1
# #     location_ranks = location_counts.rank(method='dense', ascending=False)

# #     # Map the ranks back to the original DataFrame based on location
# #     df['location_rank'] = df['incident_location'].map(location_ranks)
    
# #     return df

# # def rank_locations(df):
# #     location_counts = df['incident_location'].value_counts()

# #     # Use 'min' method to rank, which gives the same rank for ties
# #     location_ranks = location_counts.rank(ascending=False, method='min')

# #     # Adjust ranks to increment after ties
# #     adjusted_rank = {}
# #     current_rank = 1
# #     for location in location_counts.index:
# #         adjusted_rank[location] = current_rank
# #         current_rank += location_counts[location]  # Increment rank by the count of occurrences

# #     # Map the adjusted ranks back to the DataFrame based on location
# #     df['location_rank'] = df['incident_location'].map(adjusted_rank)

# #     return df



# #CAN USE THIS 
# # def rank_nature(df):
# #     # Count the frequency of each nature
# #     nature_counts = df['nature'].value_counts()

# #     # Create a dictionary mapping natures to their ranks based on frequency
# #     nature_to_rank = {nature: rank for rank, nature in enumerate(nature_counts.index, start=1)}

# #     # Map the ranks back to the original DataFrame based on nature
# #     df['incident_rank'] = df['nature'].map(nature_to_rank)

# #     return df


# def rank_nature(df):
#     # Use Counter to get the frequency of each nature
#     nature_counts = Counter(df['nature'])
    
#     # Sort natures by frequency in descending order
#     sorted_natures = sorted(nature_counts.items(), key=lambda x: x[1], reverse=True)
    
#     # Initialize the rank and the counter
#     rank = 1
#     cnt = 0
#     prev_freq = None

#     # A dictionary to hold the nature ranks
#     nature_ranks = {}

#     for nature, freq in sorted_natures:
#         if freq != prev_freq:
#             rank += cnt
#             cnt = 0  # Reset counter for the new frequency
#         nature_ranks[nature] = rank
#         cnt += 1
#         prev_freq = freq

#     # Map the ranks back to the original DataFrame based on nature
#     df['incident_rank'] = df['nature'].apply(lambda x: nature_ranks[x])
    
#     return df


# def get_side_of_town(address, gmaps, center=(35.220833, -97.443611)):

#     geocode_result = gmaps.geocode(address + ', Norman, OK')
#     if geocode_result:
#         location_coords = geocode_result[0]['geometry']['location']
#         lat, lng = location_coords['lat'], location_coords['lng']
        
#         bearing = math.atan2(lng - center[1], lat - center[0])
#         bearing = math.degrees(bearing) % 360
#         side = None
#         if 0 <= bearing < 22.5 or bearing >= 337.5:
#             side = 'N'
#         elif 22.5 <= bearing < 67.5:
#             side = 'NE'
#         elif 67.5 <= bearing < 112.5:
#             side = 'E'
#         elif 112.5 <= bearing < 157.5:
#             side = 'SE'
#         elif 157.5 <= bearing < 202.5:
#             side = 'S'
#         elif 202.5 <= bearing < 247.5:
#             side = 'SW'
#         elif 247.5 <= bearing < 292.5:
#             side = 'W'
#         elif 292.5 <= bearing < 337.5:
#             side = 'NW'
        
#         return side, lat, lng
#     else:
#         return 'Unknown', None, None

# def add_side_of_town_column(df, gmaps):
#     # Apply get_side_of_town and create new columns for side of town, latitude, and longitude
#     df[['side_of_town', 'latitude', 'longitude']] = df.apply(
#         lambda x: get_side_of_town(x['incident_location'], gmaps),
#         axis=1,
#         result_type='expand'
#     )
#     return df


# from datetime import datetime
# import requests

# # def get_weather_condition(df, openmeteo_client):
# #     base_url = "https://archive-api.open-meteo.com/v1/archive"
    
# #     # Initialize the 'weather_code' column if it doesn't exist
# #     if 'weather_code' not in df.columns:
# #         df['weather_code'] = None

# #     for index, row in df.iterrows():
# #         formatted_date = datetime.strptime(row['incident_time'], '%m/%d/%Y %H:%M').strftime('%Y-%m-%d')

# #         print(f"\nRow {index}:")
# #         print(f"Latitude: {row.get('latitude', 'Not available')}")
# #         print(f"Longitude: {row.get('longitude', 'Not available')}")
# #         print(f"Start date: {formatted_date}")
# #         print(f"End date: {formatted_date}")

# #         params = {
# #             "latitude": row.get('latitude'),
# #             "longitude": row.get('longitude'),
# #             "start_date": formatted_date,
# #             "end_date": formatted_date,
# #             "hourly": "weather_code"
# #         }

# #         response = requests.get(base_url, params=params)

# #         if response.status_code == 200:
# #             data = response.json()
# #             weather_codes = data.get('hourly', {}).get('weather_code', [])
            
# #             # Ensure we are setting the DataFrame cell correctly
# #             df.at[index, 'weather_code'] = weather_codes if weather_codes else None

# #         else:
# #             print(f"Error fetching weather data: {response.status_code}, {response.text}")
# #             df.at[index, 'weather_code'] = None



# #     return df


# def get_weather_condition(df, openmeteo_client):
#     base_url = "https://archive-api.open-meteo.com/v1/archive"
    
#     # Initialize the 'weather_code' column if it doesn't exist
#     if 'weather_code' not in df.columns:
#         df['weather_code'] = None

#     for index, row in df.iterrows():
#         formatted_date = datetime.strptime(row['incident_time'], '%m/%d/%Y %H:%M').strftime('%Y-%m-%d')
#         hour_of_incident = datetime.strptime(row['incident_time'], '%m/%d/%Y %H:%M').hour

#         params = {
#             "latitude": row.get('latitude'),
#             "longitude": row.get('longitude'),
#             "start_date": formatted_date,
#             "end_date": formatted_date,
#             "hourly": "weather_code"
#         }

#         response = requests.get(base_url, params=params)

#         if response.status_code == 200:
#             data = response.json()
#             hourly_weather_codes = data.get('hourly', {}).get('weather_code', [])

#             # Get the specific weather code for the hour of the incident
#             if hourly_weather_codes and hour_of_incident < len(hourly_weather_codes):
#                 df.at[index, 'weather_code'] = hourly_weather_codes[hour_of_incident]
#             else:
#                 df.at[index, 'weather_code'] = None

#         else:
#             print(f"Error fetching weather data: {response.status_code}, {response.text}")
#             df.at[index, 'weather_code'] = None

#     return df



# def check_emsstat(df):
#     # Add a new column for EMSSTAT and initialize it to False
#     df['EMSSTAT'] = False

#     for i in range(len(df)):
#         # Check current row for EMSSTAT
#         if df.loc[i, 'incident_ori'] == 'EMSSTAT':
#             df.loc[i, 'EMSSTAT'] = True
#         else:
#             # Check previous and next rows for same time and location
#             if i > 0 and df.loc[i - 1, 'incident_ori'] == 'EMSSTAT' and \
#                     df.loc[i - 1, 'incident_time'] == df.loc[i, 'incident_time'] and \
#                     df.loc[i - 1, 'incident_location'] == df.loc[i, 'incident_location']:
#                 df.loc[i, 'EMSSTAT'] = True

#             if i < len(df) - 1 and df.loc[i + 1, 'incident_ori'] == 'EMSSTAT' and \
#                     df.loc[i + 1, 'incident_time'] == df.loc[i, 'incident_time'] and \
#                     df.loc[i + 1, 'incident_location'] == df.loc[i, 'incident_location']:
#                 df.loc[i, 'EMSSTAT'] = True

#     return df


# # if __name__ == '__main__':
# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("--incidents", type=str, required=True, help="Incident summary url.")
    
# #     args = parser.parse_args()
# #     if args.incidents:
# #         main(args.incidents)




# def process_url(url):
#     # Existing logic for processing a single URL
#     main(url)

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--urls", type=str, required=True, help="CSV file containing incident summary URLs.")
    
#     args = parser.parse_args()
#     if args.urls:
#         with open(args.urls, 'r') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 process_url(row[0])  # Assuming each row contains one URL




import requests

def fetch_weather(api_key, latitude, longitude, start_date, end_date):
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': ['weather_code']
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching weather data: {response.status_code}, {response.text}")

# Example usage:
api_key = 'your_api_key'  # If required
latitude = '35.1997634'
longitude = '-97.4442471'
start_date = '2024-03-01'
end_date = '2024-03-01'

try:
    weather_data = fetch_weather(api_key, latitude, longitude, start_date, end_date)
    print(weather_data)
except Exception as e:
    print(e)
