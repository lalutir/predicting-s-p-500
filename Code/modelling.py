import pandas as pd

from prophet import Prophet
from typing import Annotated

def modelling(
    df: pd.DataFrame, 
    future_cols: list = None, 
    future_dfs: list = None, 
    fillna: bool = True, 
    periods:  Annotated[int, 'Must be at least 36'] = 60
    ) -> pd.DataFrame:
    """
    Create a model and predict the future values of a stock

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the stock data
    future_cols : list of str, optional
        Exogenous columns to add to model, by default None
    future_dfs : list of pd.DataFrame, optional
        Exogenous columns to add to future DataFrame, by default None
    fillna : bool, optional
        Whether to fill missing values, by default True
    periods : Annotated[int, Must be at least 36], optional
        Amount of days to predict in the future, by default 60

    Returns
    -------
    pd.DataFrame
        DataFrame with the future values of the stock

    Raises
    ------
    ValueError
        df must be a DataFrame
    ValueError
        future_cols must be a list
    ValueError
        future_dfs must be a list
    ValueError
        fillna must be a boolean
    ValueError
        periods must be an integer
    ValueError
        periods must be at least 36
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    if future_cols:
        if not isinstance(future_cols, list):
            raise ValueError("future_cols must be a list")
    if future_dfs:
        if not isinstance(future_dfs, list):
            raise ValueError("future_dfs must be a list")
    if not isinstance(fillna, bool):
        raise ValueError("fillna must be a boolean")
    if not isinstance(periods, int):
        raise ValueError("periods must be an integer")
    if periods < 36:
        raise ValueError("periods must be at least 36")
    
    # Create the model
    model = Prophet()
    model.add_country_holidays(country_name='US')
    
    # Add the exogenous columns
    if future_cols:
        for col in future_cols:
            model.add_regressor(col)
            
    # Fit the model
    model.fit(df)
    
    # Create the future DataFrame
    future = model.make_future_dataframe(periods=periods)
    if future_cols:
        if 'day_of_week' in future_cols:
            future['day_of_week'] = future['ds'].dt.dayofweek
        if 'month' in future_cols:
            future['month'] = future['ds'].dt.month
    if future_dfs:
        for fdf in future_dfs:
            future = future.merge(fdf, how='left', on='ds')
            
    # Set all columns to numeric
    for col in future.columns:
        if col != 'ds':
            future[col] = pd.to_numeric(future[col], errors='coerce')
            
    # Fill missing values
    if fillna:
        future = future.fillna(method='ffill')
        future = future.fillna(method='bfill')
        
    # Predict the future values
    forecast = model.predict(future)
    
    # Filter the future values
    forecast = forecast[['ds', 'yhat_lower', 'yhat_upper', 'yhat']]
    forecast = forecast[forecast['ds'] > df['ds'].max()]

    return forecast