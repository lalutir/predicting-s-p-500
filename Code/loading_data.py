import pandas as pd
import requests

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def load_sp(
    api_key: str,
    file_path: str = 'Historical Prices Vanguard SP500.csv'
    ) -> pd.DataFrame:
    """
    Load the historical prices of the Vanguard SP500 ETF

    Parameters
    ----------
    api_key : str
        API key for Alpha Vantage
    file_path : str, optional
        The file to load, by default 'Historical Prices Vanguard SP500.csv'

    Returns
    -------
    pd.DataFrame
        DataFrame with the historical prices of the Vanguard SP500 ETF

    Raises
    ------
    ValueError
        file_path must be a string
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(file_path, str):
        raise ValueError("file_path must be a string")
    
    # Load the data
    sp_prices = pd.read_csv(f'Datasets/{file_path}')
    
    sp_prices = update_df(sp_prices, api_key, file_path=file_path)   
    sp_prices.to_csv(f'Datasets/{file_path}', index=False)

    # Transform the data
    sp_prices = transform(sp_prices)
    
    return sp_prices
    
def update_df(
    df: pd.DataFrame, 
    api_key: str,
    file_path: str = 'Historical Prices Vanguard SP500.csv'
    ) -> pd.DataFrame:
    """
    Update the historical prices of the Vanguard SP500 ETF

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the historical prices of the Vanguard
    api_key : str
        API key for Alpha Vantage
    file_path : str, optional
        The path to write the file to, by default 'Historical Prices Vanguard SP500.csv'

    Returns
    -------
    pd.DataFrame
        DataFrame with the historical prices of the Vanguard SP500 ETF

    Raises
    ------
    ValueError
        df must be a DataFrame
    ValueError
        file_path must be a string
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    if not isinstance(file_path, str):
        raise ValueError("file_path must be a string")
    
    # Scrape the data
    new_data = scrape(api_key)
    if not new_data:
        return df
    
    # Update the data
    new_date, new_price_eur = new_data
    first_row_date = df.iloc[0, 0] 
    
    if new_date != first_row_date:
        new_row = pd.DataFrame([[new_date, new_price_eur]], columns=df.columns)
        df = pd.concat([new_row, df], ignore_index=True)        
        
    return df

def transform(
    df: pd.DataFrame
    ) -> pd.DataFrame:
    """
    Transform the historical prices of the Vanguard SP500 ETF

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the historical prices of the Vanguard

    Returns
    -------
    pd.DataFrame
        DataFrame with the transformed historical prices of the Vanguard SP500 ETF

    Raises
    ------
    ValueError
        df must be a DataFrame
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a DataFrame")
    
    # Transform the data
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[['Date', 'Market price (EUR)']]
    df = df.copy()
    df['Market price (EUR)'] = pd.to_numeric(df['Market price (EUR)'])
    
    # Reverse the data
    df = df.iloc[::-1].reset_index(drop=True)
    
    # Filter the data
    df = df[df['Date'] >= '2020-01-31']
    
    # Rename the columns
    df = df.rename(columns={'Date': 'ds', 'Market price (EUR)':'y'})
    
    # Add timeseries features
    df['day_of_week'] = df['ds'].dt.day_of_week
    df['month'] = df['ds'].dt.month
    
    return df

def scrape(
    api_key: str
    ) -> tuple:
    """
    Scrape the historical prices of the Vanguard SP500 ETF

    Parameters
    ----------
    api_key : str
        API key for Alpha Vantage
    
    Returns
    -------
    tuple
        Tuple with the date, price in USD and price in EUR
    """    
    
    url = "https://www.nl.vanguard/professional/product/etf/equity/9694/sp-500-ucits-etf-usd-accumulating"
    
    # Set up the webdriver
    options = Options()
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Start the webdriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Scrape the data
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
        price_eur = cells[2].text.strip().replace('€', '')
        if price_eur == "—":
            price_usd = float(cells[1].text.strip().replace('$', ''))
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=usdeur&outputsize=full&apikey={api_key}'
            r = requests.get(url)
            data = r.json()
            df = pd.DataFrame(data['Time Series (Daily)']).T.reset_index().rename(columns={'index': 'Date'})
            conversion = df['4. close'][0]
            price_eur = price_usd * float(conversion)
    
        return date, price_eur
    
    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()