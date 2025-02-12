import pandas as pd
import matplotlib.pyplot as plt
import datetime

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
    plt.savefig(f"Visualizations/Prediction_graph_{str(pd.Timestamp.today().floor('s').strftime('%Y_%m_%d_%H_%M_%S')).replace(' ', '_').replace(':', ' ').replace('-', '_')}.png", dpi=300, bbox_inches='tight')