import pandas as pd
import matplotlib.pyplot as plt
import datetime

def visualization(
    historic_df: pd.DataFrame, 
    future_df: pd.DataFrame, 
    title: str = 'Forecasted value S&P500 closing values (€)', 
    x_label: str = 'Date', 
    y_label: str = 'Predicted closing value (€)', 
    figsize: tuple = (10,7)
    ):
    """
    Visualize the historic and future values of a stock

    Parameters
    ----------
    historic_df : pd.DataFrame
        DataFrame with the historic values of the stock
    future_df : pd.DataFrame
        DataFrame with the future values of the stock
    title : str, optional
        Title of the plot, by default 'Forecasted value S&P500 closing values (€)'
    x_label : str, optional
        X-label to assign to the plot, by default 'Date'
    y_label : str, optional
        Y-label to assign to the plot, by default 'Predicted closing value (€)'
    figsize : tuple, optional
        Size of the plot, by default (10,7)

    Raises
    ------
    ValueError
        historic_df must be a DataFrame
    ValueError
        future_df must be a DataFrame
    ValueError
        title must be a string
    ValueError
        x_label must be a string
    ValueError
        y_label must be a string
    ValueError
        figsize must be a tuple
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(historic_df, pd.DataFrame):
        raise ValueError("historic_df must be a DataFrame")
    if not isinstance(future_df, pd.DataFrame):
        raise ValueError("future_df must be a DataFrame")
    if not isinstance(title, str):
        raise ValueError("title must be a string")
    if not isinstance(x_label, str):
        raise ValueError("x_label must be a string")
    if not isinstance(y_label, str):
        raise ValueError("y_label must be a string")
    if not isinstance(figsize, tuple):
        raise ValueError("figsize must be a tuple")

    # Create the plot
    plt.figure(figsize=figsize)
    
    # Plot the data
    plt.plot(historic_df['ds'], historic_df['y'], color='b', label='Historic values')
    plt.plot(future_df['ds'], future_df['yhat'], color='r', label='Predicted future values')
    plt.fill_between(future_df['ds'], future_df['yhat_lower'], future_df['yhat_upper'], alpha=0.2)
    
    # Add labels
    if title:
        plt.title(title)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    
    # Save the plot
    plt.legend(loc='upper left')
    plt.savefig(f"Visualizations/Prediction_graph_{str(pd.Timestamp.today().floor('s').strftime('%Y_%m_%d_%H_%M_%S')).replace(' ', '_').replace(':', ' ').replace('-', '_')}.png", dpi=300, bbox_inches='tight')