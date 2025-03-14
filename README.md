---

# HelpingCops
![Norman PD Dataset Visualization](AFBEA59B-6D0A-464E-BF34-7321C93B807B.webp "Norman PD Dataset Visualization")

## 📜 Assignment Description
In this assignment, I've constructed a dataset from incident reports sourced from PDF files. The data was structured into a pandas DataFrame after processing and extracting relevant information.

## 🔧 How to Install
**Requirements:** Python 3.8+ with pip.

Install dependencies using `pipenv`:

```bash
pip install pipenv
pipenv install requests numpy pypdf bs4 pandas geopy googlemaps openmeteo-requests requests-cache retry-requests pytest  
```

## 🚀 How to Run
Execute the script with the following command:

```bash
pipenv run python assignment2.py --urls files.csv
```



## 📋 Functions Overview
- `extract_incidents`: Parses incidents from PDFs.
- `get_day_of_week`: Extracts the day of the week.
- `get_time_of_data`: Retrieves incident hour.
- `rank_locations`: Ranks frequency of incident locations.
- `rank_nature`: Ranks types of incidents.
- `get_side_of_town`: Uses Google Maps API for locations.
- `get_weather_condition`: Gathers weather data via Open-Meteo API.
- `check_emsstat`: Flags EMSSTAT-related incidents.

## 🛠 Special Techniques Used
- **Google Maps API**: For geolocation processing.
- **Open-Meteo API**: To fetch real-time weather data.

## 🐞 Bugs and Assumptions
The current implementation assumes consistent PDF formats. If formats change, parsing logic may need adjustments.

## 🧪 Testing with Pytest
Test files are structured to validate each function using `pytest`.

Execute tests:

```bash
pipenv run python -m pytest
```

## 📄 Test Files

- `test_extract_incidents.py`: Tests PDF parsing logic.
- `test_day_of_the_week.py`: Validates day extraction from dates.
- `test_get_time_of_data.py`: Ensures correct hour is extracted from timestamps.
- `test_rank_locations.py`: Checks ranking logic for locations.
- `test_rank_nature.py`: Assesses ranking mechanism for the nature of incidents.
- `test_get_side_of_town.py`: Verifies location classification based on geocoding.
- `test_get_weather_condition.py`: Tests weather data retrieval and parsing.
- `test_check_emsstat.py`: Confirms EMSSTAT flagging functionality.

## ✉️ Contact
For bugs, features, or questions, please [email here](mailto:harshakparmar12@gmail.com).

---

Thank you for using this dataset. For more information and updates, please check the project's [GitHub repository](https://github.com/hpamdeoxys/cis6930sp24-assignment2).

