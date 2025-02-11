### IMPORTING LIBRARIES
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os

from datetime import timedelta, datetime
from prophet import Prophet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def load_api_key():
    keys = {}
    if os.path.exists('personal_key.txt'):
        pass
    else:
        api_key = input('Enter your API key:')
        with open('personal_key.txt', 'w') as file:
            file.write(f'API_KEY={api_key}')
    
    with open('personal_key.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            keys[key] = value
        return keys


def load_sp(file_path='Historical Prices Vanguard SP500.csv'):
    sp_prices = pd.read_csv(file_path)
    sp_prices['Date'] = pd.to_datetime(sp_prices['Date'])
    
    yesterday = pd.to_datetime(datetime.today().date() - timedelta(days=1))
    
    if sp_prices[sp_prices['Date'] == yesterday].empty:
        sp_prices = update_df(sp_prices)      

    sp_prices = transform(sp_prices)
    
    return sp_prices
    
def update_df(df):
    new_data = scrape()
    if not new_data:
        return df
    
    new_date, new_price_usd, new_price_eur = new_data
    first_row_date = df.iloc[0, 0] 
    
    if new_date != first_row_date:
        new_row = pd.DataFrame([[new_date, new_price_usd, new_price_eur]], columns=df.columns)
        df = pd.concat([new_row, df], ignore_index=True)
        df.to_csv("Historical Prices Vanguard SP500.csv", index=False)
        print('New data added!')
    else:
        print('No new data added!')
        
    return df

def transform(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[['Date', 'Market price (EUR)']]
    df = df.copy()
    df['Market price (EUR)'] = pd.to_numeric(df['Market price (EUR)'])
    
    df = df.iloc[::-1].reset_index(drop=True)
    
    df = df[df['Date'] >= '2020-01-31']
    
    df = df.rename(columns={'Date': 'ds', 'Market price (EUR)':'y'})
    
    df['day'] = df['ds'].dt.day
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['week'] = df['ds'].dt.isocalendar().week
    df['month'] = df['ds'].dt.month
    df['year'] = df['ds'].dt.year
    
    return df

def scrape():
    url = "https://www.nl.vanguard/professional/product/etf/equity/9694/sp-500-ucits-etf-usd-accumulating"
    
    options = Options()
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-12[data-cq-data-path*='historical_prices']"))
        )
        
        container = driver.find_element(By.CSS_SELECTOR, "div.col-12[data-cq-data-path*='historical_prices']")
        
        table_wrap = container.find_element(By.CLASS_NAME, 'table-wrap')
        tbody = table_wrap.find_element(By.TAG_NAME, 'tbody')
        first_row = tbody.find_elements(By.TAG_NAME, 'tr')[0]
        cells = first_row.find_elements(By.TAG_NAME, 'td')

        if len(cells) < 3:
            print('Error: Expected 3 columns but found fewer.')
            return None
        
        date = cells[0].text.strip()
        price_usd = cells[1].text.strip().replace('$', '')
        price_eur = cells[2].text.strip().replace('€', '')
    
        return date, price_usd, price_eur
    
    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()
        
def load_stock_data(symbol, col_name, api_key, date_lower_lim='2020-01-31', periods=60):
    if os.path.exists(f'stock_data_{symbol}.csv'):
        modified_time = datetime.fromtimestamp(os.path.getmtime(f'stock_data_{symbol}.csv'))
        today = datetime.today().date()
        
        if modified_time.date() == today:
            df = pd.read_csv(f'stock_data_{symbol}.csv')
            
        
        else:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
            r = requests.get(url)
            data = r.json()
            df = pd.DataFrame(data['Time Series (Daily)']).T.reset_index().rename(columns={'index': 'Date'})
            df.to_csv(f'stock_data_{symbol}.csv', index=False)
            
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

def modelling(df, future_cols=None, future_dfs=None, fillna=True, periods=60):
    model = Prophet()
    model.add_country_holidays(country_name='US')
    
    if future_cols:
        for col in future_cols:
            model.add_regressor(col)
            
    model.fit(df)
    
    future = model.make_future_dataframe(periods=periods)
    
    if 'day_of_week' in future_cols:
        future['day_of_week'] = future['ds'].dt.dayofweek
    if 'month' in future_cols:
        future['month'] = future['ds'].dt.month
    if future_dfs:
        for fdf in future_dfs:
            future = future.merge(fdf, how='left', on='ds')
            
    for col in future.columns:
        if col != 'ds':
            future[col] = pd.to_numeric(future[col], errors='coerce')
            
    if fillna:
        future = future.fillna(method='ffill')
        future = future.fillna(method='bfill')
        
    forecast = model.predict(future)
    
    forecast = forecast[['ds', 'yhat_lower', 'yhat_upper', 'yhat']]
    forecast = forecast[forecast['ds'] > df['ds'].max()]

    return forecast

def visualization(historic_df, future_df, title='Forecasted value S&P500 closing values (€)', x_label='Date', y_label='Predicted closing value (€)', figsize=(10,7)):
    plt.figure(figsize=figsize)
    
    plt.plot(historic_df['ds'], historic_df['y'], color='b', label='Historic values')
    plt.plot(future_df['ds'], future_df['yhat'], color='r', label='Predicted future values')
    plt.fill_between(future_df['ds'], future_df['yhat_lower'], future_df['yhat_upper'], alpha=0.2)
    
    if title:
        plt.title(title)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    
    plt.legend(loc='upper left')
    plt.show()
    
def calculate_increase(predicted_df, historic_df):
    value_yesterday = (historic_df['y'].values)[-1]
    predicted_value = (predicted_df['yhat'].values)[0]
    increase = round(((predicted_value - value_yesterday) / predicted_value) * 100, 2)
    return increase

def calculate_lower_increase(predicted_df, historic_df):
    value_yesterday = (historic_df['y'].values)[-1]
    predicted_value = (predicted_df['yhat_lower'].values)[0]
    increase = round(((predicted_value - value_yesterday) / predicted_value) * 100, 2)
    return increase

def calculate_upper_increase(predicted_df, historic_df):
    value_yesterday = (historic_df['y'].values)[-1]
    predicted_value = (predicted_df['yhat_upper'].values)[0]
    increase = round(((predicted_value - value_yesterday) / predicted_value) * 100, 2)
    return increase

def print_increases(predicted, increase, lower_increase, upper_increase):
    date = pd.Timestamp((predicted['ds'].values)[0]).strftime('%d-%m-%Y')
    prediction = round((predicted['yhat'].values)[0], 2)
    prediction_lower = round((predicted['yhat_lower'].values)[0], 2)
    prediction_upper = round((predicted['yhat_upper'].values)[0], 2)
    print(f'Prediction for {date}: €{prediction}. This represents an increase of {increase}%')
    print(f'For this prediction, the lower limit is €{prediction_lower}. This represent an increase of {lower_increase}%')
    print(f'The upper limit is €{prediction_upper}. This represents an increase of {upper_increase}%\n')
    
def compare_predictions_to_actual(actual_df, predicted_df, timestamp, timestamp_historic, prediction_duration, prediction_file_path, error_file_path):
    predicted = pd.read_csv(prediction_file_path)
    predicted['ds'] = pd.to_datetime(predicted['ds'])
    
    if predicted[predicted['ds'] == timestamp].empty:
        y_pred = round((predicted_df['yhat'].values)[0], 2)
        predicted_new = pd.DataFrame({'ds': [timestamp], 'y_pred': [y_pred]})
        predicted_new = pd.concat([predicted, predicted_new], ignore_index=True)
        predicted_new.to_csv(prediction_file_path, index=False)
        predicted = predicted_new
        
    accuracy = pd.read_csv(error_file_path)
    accuracy['ds'] = pd.to_datetime(accuracy['ds'])
    
    if accuracy[accuracy['ds'] == timestamp_historic].empty:
        if not predicted[predicted['ds'] == timestamp_historic].empty:
            if not actual_df[actual_df['ds'] == timestamp_historic].empty:
                y_pred = (accuracy[accuracy['ds'] == timestamp_historic]['y_pred'].values)[0]
                y_true = (actual_df[actual_df['ds'] == timestamp_historic]['y'].values)[0]
                error = round(y_pred - y_true, 2)
                perc_error = round(error / y_true, 2)
                accuracy_new = pd.DataFrame({'ds': [timestamp_historic], 'y_pred': [y_pred], 'y_true': [y_true], 'error': [error], 'perc_error': [perc_error]})
                accuracy_new = pd.concat([accuracy, accuracy_new], ignore_index=True)
            else:
                accuracy_new = pd.DataFrame({'ds': [timestamp_historic], 'y_pred': [np.nan], 'y_true': [np.nan], 'error': [np.nan], 'perc_error': [np.nan]})
                accuracy_new = pd.concat([accuracy, accuracy_new], ignore_index=True)
            accuracy_new.to_csv(error_file_path, index=False)
            accuracy = accuracy_new
            
    accuracy['error'] = pd.to_numeric(accuracy['error'], errors='coerce')
    accuracy['perc_error'] = pd.to_numeric(accuracy['perc_error'], errors='coerce')
    mean_error = round(np.mean(np.abs(accuracy['error'])), 2)
    mean_perc_error = round(np.mean(np.abs(accuracy['perc_error'])), 2)
    print(f'Average error for {prediction_duration} predictions: €{mean_error}')
    print(f'Average error for {prediction_duration} predictions: {mean_perc_error}%\n')