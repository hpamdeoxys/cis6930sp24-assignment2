import requests
import pypdf
from bs4 import BeautifulSoup
import re
from urllib.request import urlretrieve
import argparse
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import math
import googlemaps
import openmeteo_requests
import requests_cache
from retry_requests import retry
import csv
from datetime import datetime
import requests

def main(url):
    incidents = extract_incidents(url)
    df = pd.DataFrame(incidents)
    df['day_of_week'] = df['incident_time'].apply(get_day_of_week)
    df['time_of_data'] = df['incident_time'].apply(get_time_of_data)
    df = rank_locations(df)
    df = rank_nature(df)

    # Initialize the Google Maps and OpenMeteo clients
    gmaps = googlemaps.Client(key='AIzaSyCGje5tE1-7V1A3f3M3VP_tQ6vINmecbAs')
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo_client = openmeteo_requests.Client(session=retry_session)

    df = add_side_of_town_column(df, gmaps)
    df = get_weather_condition(df, openmeteo_client)
    df = check_emsstat(df)

    # print(df.columns)
    return df


def fetch_incidents(url):
    page_response = requests.get(url)
    if page_response.status_code != 200:
        raise Exception(f"Webpage request failed with status code {page_response.status_code}")
    
    parsed_content = BeautifulSoup(page_response.text, 'html.parser')
    accordion_group = parsed_content.select_one('div.paragraph--type--accordion-group')
    
    pdf_links = []
    for accordion_item in accordion_group.select('div.accordion-item'):
        paragraphs = accordion_item.select('p')
        for paragraph in paragraphs[2::3]:
            anchor = paragraph.find('a', href=True)
            if anchor and 'href' in anchor.attrs:
                full_link = f"https://www.normanok.gov{anchor['href']}"
                pdf_links.append(full_link)
                
    return pdf_links

def extract_incidents(pdf_url):
    rx = r"\s+(?=\d+/\d+/\d+\s)"
    l=0
    incidents=[]
    urlretrieve(pdf_url, str(l) + '.pdf')
    with open(str(l) + '.pdf', 'rb') as file:
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text(extraction_mode="layout")
            text += "\n\n\n"
        text = text.strip(r'\s{2,}')
        text = re.split(rx, text)
        i = 0
        while i < len(text) - 2:
            parts = re.split(r'\s{2,}', text[i+1], maxsplit=4)
            if len(parts) == 5:
                temps = {'incident_time': parts[0], 'incident_number': parts[1], 'incident_location': parts[2], 'nature': parts[3], 'incident_ori': parts[4]}
            else:
                temps = {'incident_time': parts[0], 'incident_number': parts[1], 'incident_ori': parts[2], 'nature': '', 'incident_location': 'None'}
            i += 1
            incidents.append(temps)
        l += 1

    return incidents

def get_day_of_week(date_str):
    date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M')
    return (date_obj.weekday() + 1) % 7 + 1

def get_time_of_data(date_str):
    date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M')
    return date_obj.hour

from collections import Counter

def rank_locations(df):
    location_counts = Counter(df['incident_location'])
    
    sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    rank = 1
    cnt = 0
    prev_freq = None
    location_ranks = {}

    for location, freq in sorted_locations:
        if freq != prev_freq:
            rank += cnt
            cnt = 0  
        location_ranks[location] = rank
        cnt += 1
        prev_freq = freq
    df['location_rank'] = df['incident_location'].apply(lambda x: location_ranks[x])
    # print(location_counts)
    
    return df


def rank_nature(df):
    nature_counts = Counter(df['nature'])
    

    sorted_natures = sorted(nature_counts.items(), key=lambda x: x[1], reverse=True)
    

    rank = 1
    cnt = 0
    prev_freq = None


    nature_ranks = {}

    for nature, freq in sorted_natures:
        if freq != prev_freq:
            rank += cnt
            cnt = 0  
        nature_ranks[nature] = rank
        cnt += 1
        prev_freq = freq


    df['incident_rank'] = df['nature'].apply(lambda x: nature_ranks[x])
    
    return df



# Global cache for geocoding results
geo_cache = {}

def get_side_of_town(address, gmaps, center=(35.220833, -97.443611)):
    if address in geo_cache:
        side, lat, lng = geo_cache[address]
    else:
        geocode_result = gmaps.geocode(address + ', Norman, OK')
        if geocode_result:
            location_coords = geocode_result[0]['geometry']['location']
            lat, lng = location_coords['lat'], location_coords['lng']
            
            bearing = math.atan2(lng - center[1], lat - center[0])
            bearing = math.degrees(bearing) % 360
            if 0 <= bearing < 22.5 or bearing >= 337.5:
                side = 'N'
            elif 22.5 <= bearing < 67.5:
                side = 'NE'
            elif 67.5 <= bearing < 112.5:
                side = 'E'
            elif 112.5 <= bearing < 157.5:
                side = 'SE'
            elif 157.5 <= bearing < 202.5:
                side = 'S'
            elif 202.5 <= bearing < 247.5:
                side = 'SW'
            elif 247.5 <= bearing < 292.5:
                side = 'W'
            elif 292.5 <= bearing < 337.5:
                side = 'NW'
            else:
                side = 'Unknown'

            geo_cache[address] = (side, lat, lng)
        else:
            side, lat, lng = 'Unknown', None, None
            geo_cache[address] = (side, lat, lng)

    return side, lat, lng


def add_side_of_town_column(df, gmaps):
    df[['side_of_town', 'latitude', 'longitude']] = df.apply(
        lambda x: get_side_of_town(x['incident_location'], gmaps),
        axis=1,
        result_type='expand'
    )
    return df




def get_weather_condition(df, openmeteo_client):
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    if 'weather_code' not in df.columns:
        df['weather_code'] = None

    for index, row in df.iterrows():
        formatted_date = datetime.strptime(row['incident_time'], '%m/%d/%Y %H:%M').strftime('%Y-%m-%d')
        hour_of_incident = datetime.strptime(row['incident_time'], '%m/%d/%Y %H:%M').hour

        params = {
            "latitude": row.get('latitude'),
            "longitude": row.get('longitude'),
            "start_date": formatted_date,
            "end_date": formatted_date,
            "hourly": "weather_code"
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            hourly_weather_codes = data.get('hourly', {}).get('weather_code', [])

            if hourly_weather_codes and hour_of_incident < len(hourly_weather_codes):
                df.at[index, 'weather_code'] = hourly_weather_codes[hour_of_incident]
            else:
                df.at[index, 'weather_code'] = None

        else:
            print(f"Error fetching weather data: {response.status_code}, {response.text}")
            df.at[index, 'weather_code'] = None

    return df



def check_emsstat(df):
    df['EMSSTAT'] = False

    for i in range(len(df)):
        if df.loc[i, 'incident_ori'] == 'EMSSTAT':
            df.loc[i, 'EMSSTAT'] = True
        else:
            if i > 0 and df.loc[i - 1, 'incident_ori'] == 'EMSSTAT' and \
                    df.loc[i - 1, 'incident_time'] == df.loc[i, 'incident_time'] and \
                    df.loc[i - 1, 'incident_location'] == df.loc[i, 'incident_location']:
                df.loc[i, 'EMSSTAT'] = True

            if i < len(df) - 1 and df.loc[i + 1, 'incident_ori'] == 'EMSSTAT' and \
                    df.loc[i + 1, 'incident_time'] == df.loc[i, 'incident_time'] and \
                    df.loc[i + 1, 'incident_location'] == df.loc[i, 'incident_location']:
                df.loc[i, 'EMSSTAT'] = True

    return df



def process_url(url):
    main(url)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", type=str, required=True, help="CSV file containing incident summary URLs.")
    
    args = parser.parse_args()
    combined_data = pd.DataFrame()

    if args.urls:
        with open(args.urls, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url = row[0]
                df = main(url)
                combined_data = pd.concat([combined_data, df], ignore_index=True)

        combined_data.to_csv('normanok.csv', sep=',', index=False)
        columns_to_export = ['day_of_week', 'time_of_data', 'weather_code', 'location_rank', 'side_of_town', 'incident_rank', 'nature', 'EMSSTAT']
        combined_data[columns_to_export].to_csv('export.tsv', sep='\t', index=False)
    final_df = pd.read_csv('export.tsv', sep='\t')
    print(final_df)