import pandas as pd

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def load_sp(file_path='Historical Prices Vanguard SP500.csv'):
    sp_prices = pd.read_csv(f'Datasets/{file_path}')
    sp_prices['Date'] = pd.to_datetime(sp_prices['Date'].astype(str))
    
    yesterday = pd.to_datetime(datetime.today().date() - timedelta(days=1))
    
    if sp_prices[sp_prices['Date'] == yesterday].empty:
        sp_prices = update_df(sp_prices, file_path=file_path)      

    sp_prices = transform(sp_prices)
    
    return sp_prices
    
def update_df(df, file_path='Historical Prices Vanguard SP500.csv'):
    new_data = scrape()
    if not new_data:
        return df
    
    new_date, new_price_usd, new_price_eur = new_data
    first_row_date = df.iloc[0, 0] 
    
    if new_date != first_row_date:
        new_row = pd.DataFrame([[new_date, new_price_usd, new_price_eur]], columns=df.columns)
        df = pd.concat([new_row, df], ignore_index=True)
        df.to_csv(f'Datasets/{file_path}', index=False)
        print('New data added!')
    else:
        print('No new data added!')
        
    return df

def transform(df):
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
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