import pandas as pd
import requests
import os

from datetime import datetime
from prophet import Prophet

def load_stock_data(symbol, col_name, api_key, date_lower_lim='2020-01-31', periods=60):
    if os.path.exists(f"Datasets/{f'stock_data_{symbol}.csv'}"):
        modified_time = datetime.fromtimestamp(os.path.getmtime(f"Datasets/{f'stock_data_{symbol}.csv'}"))
        today = datetime.today().date()
        
        if modified_time.date() == today:
            df = pd.read_csv(f"Datasets/{f'stock_data_{symbol}.csv'}")
            
        
        else:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
            r = requests.get(url)
            data = r.json()
            df = pd.DataFrame(data['Time Series (Daily)']).T.reset_index().rename(columns={'index': 'Date'})
            df.to_csv(f"Datasets/{f'stock_data_{symbol}.csv'}", index=False)
            
    df = filter_stock_data(df, date_lower_lim=date_lower_lim)
    
    future, df = predict_exo(df, col_name=col_name, periods=periods)
    
    return future, df

def filter_stock_data(df, date_lower_lim='2020-01-31'):
    df.Date = pd.to_datetime(df.Date)
    df['4. close'] = pd.to_numeric(df['4. close'])
    df = df[df.Date >= date_lower_lim]
    df = df[['Date', '4. close']]
    df = df.rename(columns={'4. close': 'y', 'Date':'ds'})
    df = df.iloc[::-1].reset_index(drop=True)
    df = df.fillna(method='ffill')
    return df

def predict_exo(df, col_name, periods=60):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    forecast = forecast[forecast['ds'] > df['ds'].max()][['ds', 'yhat']]
    forecast = forecast.rename(columns={'yhat': 'y'})
    forecast = pd.concat([df, forecast], ignore_index=True)
    forecast = forecast.rename(columns={'y': col_name})
    df = df.rename(columns={'y': col_name})
    return forecast, df

def merge_sp_features(df, col_mergers, how='left', on='ds', fillna=True):
    for col in col_mergers:
        df = df.merge(col, how=how, on=on)
        
    if fillna:
        df = df.fillna(method='ffill')
        df = df.fillna(method='bfill')
        
    return df