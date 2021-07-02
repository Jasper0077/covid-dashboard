import pandas as pd
import matplotlib.pyplot as plt
import pylab
import numpy as np
import datetime as dt

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR

from urllib.request import urlopen
import json

url_first_dataset = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
url_cumulative_bystate = 'https://raw.githubusercontent.com/ynshung/covid-19-malaysia/master/covid-19-my-states-cases.csv'

population_by_state = [255300, 2192800, 1776700, 2510200, 6560900, 1130400, 935600, 3795300, 1683300, 1269700, 1923000, 3912600, 2823300, 1766700, 114900, 99800]


class Data:
    def __init__(self):
        # First Dataset from url
        self.df = pd.read_csv(url_first_dataset)
        self.data = self.get_data_malaysia(self.df)

        # Read Data from url into dataframe
        self.df_cumulative_bystate = pd.read_csv(url_cumulative_bystate)
        self.df_cumulative_bystate = self.preprocess_data(self.df_cumulative_bystate)

        # Restructured dataframe
        self.df_cumulative_restruct = self.restructure_dataframe(self.df_cumulative_bystate)

        # Daily Case by State Dataframe
        self.df_daily_bystate = self.get_daily_bystate()

        # Monthly Case by State Dataframe
        self.df_monthly_bystate = self.get_monthly_bystate(self.df_daily_bystate)

        # Dataframe with Population
        self.df_case_with_pop = self.get_case_with_pop()



    def preprocess_data(self, df_cumulative_bystate):
        # Data Preprocessing
        df_cumulative_bystate = df_cumulative_bystate.iloc[3:]
        df_cumulative_bystate = df_cumulative_bystate.replace("-", 0)
        df_cumulative_bystate['wp-putrajaya'] = df_cumulative_bystate['wp-putrajaya'].astype(int)
        df_cumulative_bystate.iloc[:, 1:] = df_cumulative_bystate.iloc[:, 1:].astype(int)

        return df_cumulative_bystate

    def extract_year_month(self, df_ori):
        df = df_ori.copy()
        year_month = []
        for date in df['date'].values:
            date_split = date.split("/")
            result = date_split[2] + "/" + date_split[1]
            year_month.append(result)

        df['year_month'] = year_month

        return df

    def restructure_dataframe(self, df):
        # Create a copy of dataframe, drop the unused column
        df_cumulative_restruct = df.copy()
        df_cumulative_restruct = df_cumulative_restruct.drop(['wp-labuan'], axis=1)

        # Rename and rearrange the column according to that on malaysia geojson file
        df_cumulative_restruct.columns = ['date', 'Perlis', 'Kedah', 'Penang', 'Perak', 'Selangor', 'Negeri Sembilan',
                                          'Melaka',
                                          'Johor', 'Pahang', 'Terengganu', 'Kelantan', 'Sabah', 'Sarawak',
                                          'Federal Territory of Kuala Lumpur', 'Federal Territory of Putrajaya']
        df_cumulative_restruct = df_cumulative_restruct[
            ['date', 'Federal Territory of Kuala Lumpur', 'Perlis', 'Sabah', 'Federal Territory of Putrajaya', 'Kedah',
             'Sarawak',
             'Penang', 'Johor', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Perak', 'Selangor', 'Terengganu']]

        columns = df_cumulative_restruct.columns
        df_temp = df_cumulative_restruct[['date', columns[1]]].copy()
        df_temp.columns = ['date', 'cumulative case']
        df_temp['state'] = columns[1]

        for i in range(len(columns)):
            if i == 0 or i == 1:
                continue
            else:
                df2 = df_cumulative_restruct[['date', columns[i]]].copy()
                df2.columns = ['date', 'cumulative case']
                df2['state'] = columns[i]

                df_temp = df_temp.append(df2, ignore_index=True)

        # Extract the year-month from the date
        # df_temp['year_month'] = df_temp['date'].dt.to_period('M')
        # df_temp['year_month'] = df_temp['year_month'].values.astype(str)

        # Extract the year-month from the date
        df_temp = self.extract_year_month(df_temp)

        return df_temp

    def get_daily_bystate(self):
        # Obtain daily case from cumulative dataframe
        df_daily_bystate = self.df_cumulative_bystate.copy()
        df_daily_bystate.iloc[:, 1:] = df_daily_bystate.iloc[:, 1:].diff(axis=0)

        # Fill null value with 0, and convert the datatype to int
        df_daily_bystate = df_daily_bystate.fillna(0)
        df_daily_bystate.iloc[:, 1:] = df_daily_bystate.iloc[:, 1:].astype(int)

        # Handle negative value
        df_daily_bystate.iloc[298, 14] = 101
        df_daily_bystate.iloc[64, 15] = 1

        return df_daily_bystate

    def get_case_with_pop(self):
        # Create Initial Dataframe with population
        d = {'State': self.df_cumulative_bystate.columns[1:],
             'Cumulative Case': self.df_cumulative_bystate.iloc[-1, 1:].values,
             'Latest Daily Increase': self.df_daily_bystate.iloc[-1, 1:].values,
             'Population': population_by_state}
        df_case_with_pop = pd.DataFrame(data=d)

        # Append the column for cumulative Infected Rate
        infected_rate = (df_case_with_pop['Cumulative Case'] / df_case_with_pop['Population']) * 100
        df_case_with_pop['Cumulative Infected Rate'] = infected_rate

        # Append the column for area size
        area_size = [821, 9500, 1048, 21035, 8104, 6686, 1664, 19210, 36137, 13035, 15099, 73631, 124450, 243, 49, 91]
        df_case_with_pop['Area'] = area_size

        # Append the column for population density
        pop_density = df_case_with_pop['Population'] / df_case_with_pop['Area']
        df_case_with_pop['Population Density'] = pop_density

        return  df_case_with_pop

    def get_data_malaysia(self, df):
        data = df[df.iso_code == 'MYS']
        data.isna().values.any()
        data = data.fillna(0)
        data['date'] = pd.to_datetime(data['date'])

        return data

    def get_monthly_bystate(self, df):
        df_monthly_bystate = df.copy()
        df_monthly_bystate = self.extract_year_month(df_monthly_bystate)

        df_monthly_bystate = df_monthly_bystate.groupby(['year_month'], as_index=False).sum()

        return df_monthly_bystate


