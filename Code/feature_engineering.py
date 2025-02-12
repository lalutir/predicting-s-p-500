import pandas as pd
import requests
import os

from datetime import datetime
from prophet import Prophet
from typing import Annotated

def load_stock_data(
    symbol: str, 
    col_name: str, 
    api_key: str, 
    date_lower_lim: str = '2020-01-31', 
    periods: Annotated[int, 'Must be at least 36'] = 60
    ) -> pd.DataFrame:
    """
    Load stock data from Alpha Vantage API and predict future values using Prophet

    Parameters
    ----------
    symbol : str
        Symbol of the stock to be gathered
    col_name : str
        Name of the column to be predicted
    api_key : str
        API key for Alpha Vantage
    date_lower_lim : str, optional
        First date to be in the dataset, by default '2020-01-31'
    periods : Annotated[int, Must be at least], optional
        Amount of days to predict in the future, by default 60

    Returns
    -------
    future : pd.DataFrame
        DataFrame with the future values of the stock
    df : pd.DataFrame
        DataFrame with the historical values of the stock

    Raises
    ------
    ValueError
        symbol must be a string
    ValueError
        col_name must be a string
    ValueError
        api_key must be a string
    ValueError
        date_lower_lim must be a string
    ValueError
        periods must be an integer
    ValueError
        periods must be at least 36
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(symbol, str):
        raise ValueError("symbol must be a string")
    if not isinstance(col_name, str):
        raise ValueError("col_name must be a string")
    if not isinstance(api_key, str):
        raise ValueError("api_key must be a string")
    if not isinstance(date_lower_lim, str):
        raise ValueError("date_lower_lim must be a string")
    if not isinstance(periods, int):
        raise ValueError("periods must be an integer")
    if periods < 36:
        raise ValueError("periods must be at least 36")
    
    # Check if the file exists and is last updated today, if it does, read it, if not, download it
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
    else:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
        r = requests.get(url)
        data = r.json()
        df = pd.DataFrame(data['Time Series (Daily)']).T.reset_index().rename(columns={'index': 'Date'})
        df.to_csv(f"Datasets/{f'stock_data_{symbol}.csv'}", index=False)

    # Filter the data
    df = filter_stock_data(df, date_lower_lim=date_lower_lim)
    
    # Predict the future values
    future, df = predict_exo(df, col_name=col_name, periods=periods)
    
    return future, df

def filter_stock_data(
    df: pd.DataFrame, 
    date_lower_lim: str = '2020-01-31'
    ) -> pd.DataFrame:
    """
    Filter the stock data to only have the necessary columns and rows

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the stock data
    date_lower_lim : str, optional
        First date to be in the dataset, by default '2020-01-31'

    Returns
    -------
    pd.DataFrame
        DataFrame with the filtered stock data

    Raises
    ------
    ValueError
        df must be a DataFrame
    ValueError
        date_lower_lim must be a string
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    if not isinstance(date_lower_lim, str):
        raise ValueError("date_lower_lim must be a string")
    
    # Filter the data
    df.Date = pd.to_datetime(df.Date)
    df['4. close'] = pd.to_numeric(df['4. close'])
    df = df[df.Date >= date_lower_lim]
    df = df[['Date', '4. close']]
    df = df.rename(columns={'4. close': 'y', 'Date':'ds'})
    df = df.iloc[::-1].reset_index(drop=True)
    df = df.fillna(method='ffill')
    
    return df

def predict_exo(
    df: pd.DataFrame, 
    col_name: str, 
    periods: Annotated[int, 'Must be at least 36'] = 60
    ) -> pd.DataFrame:
    """
    Predict the future values of a column using Prophet

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the stock data
    col_name : str
        Name of the column to be predicted
    periods : Annotated[int, Must be at least], optional
        Amount of days to predict in the future, by default 60

    Returns
    -------
    forecast : pd.DataFrame
        DataFrame with the future values of the stock
    df : pd.DataFrame
        DataFrame with the historical values of the stock

    Raises
    ------
    ValueError
        df must be a DataFrame
    ValueError
        col_name must be a string
    ValueError
        periods must be an integer
    ValueError
        periods must be at least 36
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    if not isinstance(col_name, str):
        raise ValueError("col_name must be a string")
    if not isinstance(periods, int):
        raise ValueError("periods must be an integer")
    if periods < 36:
        raise ValueError("periods must be at least 36")
    
    # Predict the future values
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

def merge_sp_features(
    df: pd.DataFrame, 
    col_mergers: list, 
    how: str = 'left', 
    on: str = 'ds', 
    fillna: bool = True
    ) -> pd.DataFrame:
    """
    Merge the stock data with the features from the S&P 500

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the S&P500 data
    col_mergers : list of pd.DataFrame
        List of DataFrames to be merged with the S&P500 data
    how : str, optional
        Method to use while merging, by default 'left'
    on : str, optional
        Column to merge on, by default 'ds'
    fillna : bool, optional
        Whether to fill NaN values, by default True

    Returns
    -------
    pd.DataFrame
        DataFrame with the merged data

    Raises
    ------
    ValueError
        df must be a DataFrame
    ValueError
        col_mergers must be a list
    ValueError
        how must be a string
    ValueError
        on must be a string
    ValueError
        fillna must be a boolean
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    if not isinstance(col_mergers, list):
        raise ValueError("col_mergers must be a list")
    if not isinstance(how, str):
        raise ValueError("how must be a string")
    if not isinstance(on, str):
        raise ValueError("on must be a string")
    if not isinstance(fillna, bool):
        raise ValueError("fillna must be a boolean")
    
    # Merge the data
    for col in col_mergers:
        df = df.merge(col, how=how, on=on)
        
    # Fill NaN values
    if fillna:
        df = df.fillna(method='ffill')
        df = df.fillna(method='bfill')
        
    return df