import pandas as pd

from datetime import timedelta

def historic_data(timestamp, df, time_period):
    today = pd.Timestamp.today().normalize()
    yesterday = today - timedelta(days=1)
    try:
        yesterday_value = (df[df['ds'] == yesterday]['y'].values)[0]
        value = (df[df['ds'] == timestamp]['y'].values)[0]
        increase = round(((yesterday_value - value) / value) * 100, 2)

        print(f"Yesterday's closing values was: €{round(yesterday_value, 2)}. Which is an increase over {time_period} of {increase}%\n")
    except:
        print(f"No data for {timestamp} ago\n")