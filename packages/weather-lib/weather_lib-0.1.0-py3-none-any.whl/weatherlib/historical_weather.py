import requests
import pandas as pd
from datetime import datetime
import urllib.request
import json
import os

class HistoricalLocationWeather(object):
    '''
    This class extracts historical weather data from the WorldWeatherOnline API.
    The data is extracted by city for predefined features over a specified date range.

    Arguments:
    - api_key: str, API key from 'https://www.worldweatheronline.com/developer/'.
    - city: str, city for which to retrieve data.
    - start_date: str, start date in the format 'YYYY-mm-dd'.
    - end_date: str, end date in the format 'YYYY-mm-dd'.
    - frequency: int, frequency of extracted data in hours (1, 3, 6, or 12).
    - verbose: bool, whether to print status messages.
    - csv_directory: str, optional directory to save output as a CSV.

    Returns:
    - dataset: Pandas DataFrame containing the requested weather data.
    '''

    def __init__(self, api_key, city, start_date, end_date, frequency, verbose=True, csv_directory=None):
        if not isinstance(api_key, str):
            raise TypeError("API key must be a string. Generate one at https://www.worldweatheronline.com/developer/")
        if not isinstance(city, str):
            raise TypeError("City must be a string.")
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            raise TypeError("Dates must be strings in 'YYYY-mm-dd' format.")

        self.api_key = api_key
        self.city = city
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.verbose = verbose
        self.csv_directory = csv_directory

        # Convert date strings to datetime objects
        self.start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        # Validate dates and frequency
        if self.start_date_datetime >= self.end_date_datetime:
            raise ValueError("End date must be after start date.")
        if frequency not in [1, 3, 6, 12]:
            raise ValueError("Frequency must be one of 1, 3, 6, or 12.")

    def _extract_data(self, dataset):
        '''Transforms raw JSON weather data into a structured DataFrame.'''
        monthly_data = pd.DataFrame()

        for day_data in dataset:
            astronomy_df = pd.DataFrame(day_data.get('astronomy', [{}]))
            hourly_df = pd.DataFrame(day_data.get('hourly', [{}]))

            # Ensure main_df matches hourly_df's row count
            weather_main = {key: day_data.get(key, None) for key in ['date', 'maxtempC', 'mintempC', 'totalSnow_cm', 'sunHour', 'uvIndex']}
            main_df = pd.DataFrame(weather_main, index=range(len(hourly_df)))

            # Combine data, filling any missing values
            try:
                day_df = pd.concat([main_df, astronomy_df, hourly_df], axis=1).ffill()
            except ValueError:
                print("Error: Mismatch in DataFrame row lengths.")
                continue

            # Create a 'date_time' column
            if 'date' in day_df.columns and 'time' in day_df.columns:
                day_df['time'] = day_df['time'].str.zfill(4).str[:2]
                day_df['date_time'] = pd.to_datetime(day_df['date'] + ' ' + day_df['time'], errors='coerce')
            else:
                print("Missing 'date' or 'time' in day_df columns:", day_df.columns)
                continue

            # Select only the required columns, avoiding duplicates
            columns_needed = [
                'date_time', 'maxtempC', 'mintempC', 'totalSnow_cm', 'sunHour', 'uvIndex',
                'moon_illumination', 'moonrise', 'moonset', 'sunrise', 'sunset',
                'DewPointC', 'FeelsLikeC', 'HeatIndexC', 'WindChillC', 'WindGustKmph',
                'cloudcover', 'humidity', 'precipMM', 'pressure', 'tempC', 'visibility',
                'winddirDegree', 'windspeedKmph'
            ]
            day_df = day_df.loc[:, ~day_df.columns.duplicated()]
            monthly_data = pd.concat([monthly_data, day_df[columns_needed]], ignore_index=True)

        if 'date_time' not in monthly_data.columns:
            print("Error: 'date_time' column missing after processing.")
        return monthly_data

    def _retrieve_this_city(self):
        '''Retrieves weather data for the specified city over the date range and frequency.'''
        list_month_begin = pd.date_range(self.start_date, self.end_date, freq='MS')
        list_month_begin = pd.concat([pd.Series(pd.to_datetime(self.start_date)), pd.Series(list_month_begin)], ignore_index=True)

        list_month_end = pd.date_range(self.start_date, self.end_date, freq='M')
        list_month_end = pd.concat([pd.Series(list_month_end), pd.Series(pd.to_datetime(self.end_date))], ignore_index=True)

        historical_data = pd.DataFrame()
        for start_d, end_d in zip(list_month_begin, list_month_end):
            start_d, end_d = start_d.strftime('%Y-%m-%d'), end_d.strftime('%Y-%m-%d')
            if self.verbose:
                print(f'Retrieving data for {self.city} from: {start_d} to: {end_d}')

            url = f'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key={self.api_key}&q={self.city}&format=json&date={start_d}&enddate={end_d}&tp={self.frequency}'
            response = urllib.request.urlopen(url, timeout=10)
            json_data = json.loads(response.read().decode())
            data = json_data['data']['weather']

            # Process and add data
            data_this_month = self._extract_data(data)
            data_this_month['city'] = self.city
            historical_data = pd.concat([historical_data, data_this_month])

        return historical_data

    def retrieve_hist_data(self):
        '''Retrieve and store weather data, saving as CSV if csv_directory is provided.'''
        dataset = self._retrieve_this_city()
        dataset.set_index('date_time', drop=True, inplace=True)

        if self.csv_directory:
            filepath = os.path.join(self.csv_directory, f'{self.city}.csv')
            dataset.to_csv(filepath, header=True, index=True)
            if self.verbose:
                print(f'\nData saved to {filepath}\n')

        return dataset

