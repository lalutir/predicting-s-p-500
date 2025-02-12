import pandas as pd

from datetime import timedelta

def historic_data(
    timestamp: str, 
    df: pd.DataFrame, 
    time_period: str
    ):
    """
    Compare the closing value of a stock from a given timestamp to the closing value of the stock from a given time period ago

    Parameters
    ----------
    timestamp : str
        Date to compare the closing value of the stock
    df : pd.DataFrame
        DataFrame with the historical values of the stock
    time_period : str
        Time period to compare the closing value of the stock

    Raises
    ------
    ValueError
        timestamp must be a string
    ValueError
        df must be a DataFrame
    ValueError
        time_period must be a string
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(timestamp, str):
        raise ValueError("timestamp must be a string")
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    if not isinstance(time_period, str):
        raise ValueError("time_period must be a string")
    
    # Get the closing value of the stock from the given timestamp
    today = pd.Timestamp.today().normalize()
    yesterday = today - timedelta(days=1)
    try:
        yesterday_value = (df[df['ds'] == yesterday]['y'].values)[0]
        value = (df[df['ds'] == timestamp]['y'].values)[0]
        increase = round(((yesterday_value - value) / value) * 100, 2)
        print(f"Yesterday's closing values was: €{round(yesterday_value, 2)}. Which is an increase over {time_period} of {increase}%\n")
    except:
        print(f"No data for {timestamp} ago\n")