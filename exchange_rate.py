import sys
from datetime import datetime, timedelta

import requests
import pandas as pd
from config_parser import CustomConfigParser as cp


class FxRate:
    def __init__(self, config):
        self.config = config
        self.fx_api = config.get('fx_api')
        self.load_type = config.get('load_type')
        self.start_at = config.get('start_at')
        self.end_at = config.get('end_at')
        self.symbols = config.get('symbols')
        self.base = config.get('base')
        self.fx_columns = config.get('fx_columns').split(',')
        self.out_csv = config.get('out_csv')

        self.payload = {
            'symbols': self.symbols,
            'base': self.base,
        }

    def get_response(self, payload):
        response = requests.get(self.fx_api + self.load_type, params=payload)
        if response.status_code != 200:
            print(response.json())
        else:
            return response.json()

    def load_csv(self, df):
        try:
            csv_df = pd.read_csv(self.out_csv)
            final = pd.concat([csv_df[~csv_df.Date.isin(df.Date)], df])
            final.sort_values(by=['Date'], inplace=True, ascending=False)
            final.to_csv(self.out_csv, index=False)

        except pd.errors.EmptyDataError:
            df.to_csv(self.out_csv, index=False)

    def get_latest(self):
        response = self.get_response(self.payload)
        l_df = pd.DataFrame(response)

        l_df.reset_index(inplace=True)

        l_df.rename(columns={'date': 'Date',
                             'base': 'From Currency',
                             'index': 'To Currency',
                             'rates': 'Rate'}, inplace=True)

        l_df = l_df[self.fx_columns]
        self.load_csv(l_df)

    def get_historical(self, start, end):
        self.payload.update({'start_at': start,
                             'end_at': end})
        response = self.get_response(self.payload)

        h_df = pd.DataFrame(response['rates'])
        h_df.reset_index(inplace=True)
        h_df.rename(columns={'index': 'To Currency'}, inplace=True)

        h_df = h_df.melt(id_vars=["To Currency"],
                         var_name="Date",
                         value_name="Rate")
        h_df['From Currency'] = response.get('base')
        h_df = h_df[self.fx_columns]
        self.load_csv(h_df)


if __name__ == "__main__":
    usage = "Usage: exchange_rate.py <load_type> <num_days_optional>"
    if len(sys.argv) < 2:
        print(usage)
        exit()
    load_type = sys.argv[1]
    if load_type not in ('latest', 'history'):
        print("not a valid load type. Can be latest or history")
        exit()

    CONFIG = cp.config_parser('config.ini')
    CONFIG.update({'load_type': load_type})

    fx_obj = FxRate(CONFIG)
    if load_type == 'latest':
        fx_obj.get_latest()
    elif load_type == 'history':
        try:
            day = int(sys.argv[2])
            if day:
                if 1 < day > 15:
                    print(f'{usage} \ndays must be less than 15"')
                    exit()
                else:
                    from_day = (datetime.now() + timedelta(days=-day)).strftime('%Y-%m-%d')
                    to_day = (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d')
                    fx_obj.get_historical(from_day, to_day)
        except ValueError as e:
            print(f'{usage} \nerror:{e}')

