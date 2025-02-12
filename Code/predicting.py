import pandas as pd
import numpy as np

def calculate_increase(
    predicted_df: pd.DataFrame, 
    historic_df: pd.DataFrame
    ) -> float:
    """
    Calculate the increase of a predicted value compared to the last known value

    Parameters
    ----------
    predicted_df : pd.DataFrame
        DataFrame with the predicted values
    historic_df : pd.DataFrame
        DataFrame with the historical values

    Returns
    -------
    float
        Increase of the predicted value compared to the last known value

    Raises
    ------
    ValueError
        predicted_df must be a DataFrame
    ValueError
        historic_df must be a DataFrame
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(predicted_df, pd.DataFrame):
        raise ValueError("predicted_df must be a DataFrame")
    if not isinstance(historic_df, pd.DataFrame):
        raise ValueError("historic_df must be a DataFrame")
    
    # Calculate the increase
    value_yesterday = (historic_df['y'].values)[-1]
    predicted_value = (predicted_df['yhat'].values)[0]
    increase = round(((predicted_value - value_yesterday) / predicted_value) * 100, 2)
    return increase

def calculate_lower_increase(
    predicted_df: pd.DataFrame, 
    historic_df: pd.DataFrame
    ) -> float:
    """
    Calculate the increase of the lower limit of a predicted value compared to the last known value

    Parameters
    ----------
    predicted_df : pd.DataFrame
        DataFrame with the predicted values
    historic_df : pd.DataFrame
        DataFrame with the historical values

    Returns
    -------
    float
        Increase of the lower limit of the predicted value compared to the last known value

    Raises
    ------
    ValueError
        predicted_df must be a DataFrame
    ValueError
        historic_df must be a DataFrame
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(predicted_df, pd.DataFrame):
        raise ValueError("predicted_df must be a DataFrame")
    if not isinstance(historic_df, pd.DataFrame):
        raise ValueError("historic_df must be a DataFrame")
    
    # Calculate the increase
    value_yesterday = (historic_df['y'].values)[-1]
    predicted_value = (predicted_df['yhat_lower'].values)[0]
    increase = round(((predicted_value - value_yesterday) / predicted_value) * 100, 2)
    return increase

def calculate_upper_increase(
    predicted_df: pd.DataFrame, 
    historic_df: pd.DataFrame
    ) -> float:
    """
    Calculate the increase of the upper limit of a predicted value compared to the last known value

    Parameters
    ----------
    predicted_df : pd.DataFrame
        DataFrame with the predicted values
    historic_df : pd.DataFrame
        DataFrame with the historical values

    Returns
    -------
    float
        Increase of the upper limit of the predicted value compared to the last known value

    Raises
    ------
    ValueError
        predicted_df must be a DataFrame
    ValueError
        historic_df must be a DataFrame
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(predicted_df, pd.DataFrame):
        raise ValueError("predicted_df must be a DataFrame")
    if not isinstance(historic_df, pd.DataFrame):
        raise ValueError("historic_df must be a DataFrame")
    
    # Calculate the increase
    value_yesterday = (historic_df['y'].values)[-1]
    predicted_value = (predicted_df['yhat_upper'].values)[0]
    increase = round(((predicted_value - value_yesterday) / predicted_value) * 100, 2)
    return increase

def print_increases(
    predicted: pd.DataFrame, 
    increase: float, 
    lower_increase: float, 
    upper_increase: float
    ):
    """
    Print the predicted value and the increase compared to the last known value

    Parameters
    ----------
    predicted : pd.DataFrame
        DataFrame with the predicted values
    increase : float
        Increase of the predicted value compared to the last known value
    lower_increase : float
        Increase of the lower limit of the predicted value compared to the last known value
    upper_increase : float
        Increase of the upper limit of the predicted value compared to the last known value

    Raises
    ------
    ValueError
        predicted must be a DataFrame
    ValueError
        increase must be a float
    ValueError
        lower_increase must be a float
    ValueError
        upper_increase must be a float
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(predicted, pd.DataFrame):
        raise ValueError("predicted must be a DataFrame")
    if not isinstance(increase, float):
        raise ValueError("increase must be a float")
    if not isinstance(lower_increase, float):
        raise ValueError("lower_increase must be a float")
    if not isinstance(upper_increase, float):
        raise ValueError("upper_increase must be a float")
    
    # Print the increases
    date = pd.Timestamp((predicted['ds'].values)[0]).strftime('%d-%m-%Y')
    prediction = round((predicted['yhat'].values)[0], 2)
    prediction_lower = round((predicted['yhat_lower'].values)[0], 2)
    prediction_upper = round((predicted['yhat_upper'].values)[0], 2)
    print(f'Prediction for {date}: €{prediction}. This represents an increase of {increase}%')
    print(f'For this prediction, the lower limit is €{prediction_lower}. This represent an increase of {lower_increase}%')
    print(f'The upper limit is €{prediction_upper}. This represents an increase of {upper_increase}%\n')
    
def compare_predictions_to_actual(
    actual_df: pd.DataFrame, 
    predicted_df: pd.DataFrame, 
    timestamp: str, 
    timestamp_historic: str, 
    prediction_duration: str, 
    prediction_file_path: str, 
    error_file_path: str
    ):
    """
    Compare the predicted values to the actual values and calculate the error

    Parameters
    ----------
    actual_df : pd.DataFrame
        DataFrame with the actual values
    predicted_df : pd.DataFrame
        DataFrame with the predicted values
    timestamp : str
        Date of the prediction
    timestamp_historic : str
        Date of the historic prediction
    prediction_duration : str
        Duration of the prediction
    prediction_file_path : str
        Path to the file with the predictions
    error_file_path : str
        Path to the file with the errors

    Raises
    ------
    ValueError
        actual_df must be a DataFrame
    ValueError
        predicted_df must be a DataFrame
    ValueError
        timestamp must be a string
    ValueError
        timestamp_historic must be a string
    ValueError
        prediction_duration must be a string
    ValueError
        prediction_file_path must be a string
    ValueError
        error_file_path must be a string
    """    
    
    # Check if the input is correct if not, raise an error
    if not isinstance(actual_df, pd.DataFrame):
        raise ValueError("actual_df must be a DataFrame")
    if not isinstance(predicted_df, pd.DataFrame):
        raise ValueError("predicted_df must be a DataFrame")
    if not isinstance(timestamp, str):
        raise ValueError("timestamp must be a string")
    if not isinstance(timestamp_historic, str):
        raise ValueError("timestamp_historic must be a string")
    if not isinstance(prediction_duration, str):
        raise ValueError("prediction_duration must be a string")
    if not isinstance(prediction_file_path, str):
        raise ValueError("prediction_file_path must be a string")
    if not isinstance(error_file_path, str):
        raise ValueError("error_file_path must be a string")
    
    # Prepare the data
    predicted = pd.read_csv(f'Datasets/{prediction_file_path}')
    predicted['ds'] = pd.to_datetime(predicted['ds'])
    
    # Check if the prediction is already in the file, if not, add it
    if predicted[predicted['ds'] == timestamp].empty:
        y_pred = round((predicted_df['yhat'].values)[0], 2)
        predicted_new = pd.DataFrame({'ds': [timestamp], 'y_pred': [y_pred]})
        predicted_new = pd.concat([predicted, predicted_new], ignore_index=True)
        predicted_new.to_csv(f'Datasets/{prediction_file_path}', index=False)
        predicted = predicted_new
    
    # Calculate the error
    accuracy = pd.read_csv(f'Datasets/{error_file_path}')
    accuracy['ds'] = pd.to_datetime(accuracy['ds'])
    
    # Check if the error is already in the file, if not, add it
    if accuracy[accuracy['ds'] == timestamp_historic].empty:
        if not predicted[predicted['ds'] == timestamp_historic].empty:
            if not actual_df[actual_df['ds'] == timestamp_historic].empty:
                y_pred = (predicted[predicted['ds'] == timestamp_historic]['y_pred'].values)[0]
                y_true = (actual_df[actual_df['ds'] == timestamp_historic]['y'].values)[0]
                error = round(y_pred - y_true, 2)
                perc_error = round(error / y_true, 2)
                accuracy_new = pd.DataFrame({'ds': [timestamp_historic], 'y_pred': [y_pred], 'y_true': [y_true], 'error': [error], 'perc_error': [perc_error]})
                accuracy_new = pd.concat([accuracy, accuracy_new], ignore_index=True)
            else:
                accuracy_new = pd.DataFrame({'ds': [timestamp_historic], 'y_pred': [np.nan], 'y_true': [np.nan], 'error': [np.nan], 'perc_error': [np.nan]})
                accuracy_new = pd.concat([accuracy, accuracy_new], ignore_index=True)
            accuracy_new.to_csv(f'Datasets/{error_file_path}', index=False)
            accuracy = accuracy_new
    
    # Print the error
    accuracy['error'] = pd.to_numeric(accuracy['error'], errors='coerce')
    accuracy['perc_error'] = pd.to_numeric(accuracy['perc_error'], errors='coerce')
    mean_error = round(np.mean(np.abs(accuracy['error'])), 2)
    mean_perc_error = round(np.mean(np.abs(accuracy['perc_error'])), 2)
    print(f'Average error for {prediction_duration} predictions: €{mean_error}')
    print(f'Average error for {prediction_duration} predictions: {mean_perc_error}%\n')