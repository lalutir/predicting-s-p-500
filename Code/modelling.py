import pandas as pd

from prophet import Prophet

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