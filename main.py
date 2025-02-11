### IMPORTING LIBRARIES
import pandas as pd

from datetime import timedelta
from loading_api_key import *
from loading_data import *
from feature_engineering import *
from modelling import *
from visualizing import *
from predicting import *

import warnings
warnings.filterwarnings('ignore')

import logging
logging.getLogger("cmdstanpy").setLevel(logging.CRITICAL)


### LOADING API KEY
#api_key = load_api_key()['API_KEY']
api_key = load_api_key_github_actions()


### LOADING S&P500 DATA
sp_prices = load_sp()


### FEATURE ENGINEERING
aapl_future, aapl = load_stock_data('AAPL', 'aapl', api_key)
nvda_future, nvda = load_stock_data('NVDA', 'nvda', api_key)
tsla_future, tsla = load_stock_data('TSLA', 'tsla', api_key)

df_to_merge = [aapl, nvda, tsla]
sp_prices_merged = merge_sp_features(sp_prices, df_to_merge)


### MODELLING
future_cols = ['day_of_week', 'month', 'aapl', 'nvda', 'tsla']
future_dfs = [aapl_future, nvda_future, tsla_future]
forecast = modelling(sp_prices_merged, future_cols=future_cols, future_dfs=future_dfs)

### VISUALIZING
visualization(sp_prices, forecast)

### PREDICTIONS
today = pd.Timestamp.today().normalize()
one_week_ahead = today + timedelta(weeks=1)
two_week_ahead = today + timedelta(weeks=2)
three_week_ahead = today + timedelta(weeks=3)
four_week_ahead = today + timedelta(weeks=4)

yesterday = today - timedelta(days=1)
one_week_ago = today - timedelta(weeks=1)
two_week_ago = today - timedelta(weeks=2)
three_week_ago = today - timedelta(weeks=3)
four_week_ago = today - timedelta(weeks=4)

prediction_today = forecast[forecast['ds'] == today]
prediction_one_week = forecast[forecast['ds'] == one_week_ahead]
prediction_two_week = forecast[forecast['ds'] == two_week_ahead]
prediction_three_week = forecast[forecast['ds'] == three_week_ahead]
prediction_four_week = forecast[forecast['ds'] == four_week_ahead]

increase_today = calculate_increase(prediction_today, sp_prices)
increase_one_week = calculate_increase(prediction_one_week, sp_prices)
increase_two_week = calculate_increase(prediction_two_week, sp_prices)
increase_three_week = calculate_increase(prediction_three_week, sp_prices)
increase_four_week = calculate_increase(prediction_four_week, sp_prices)

lower_increase_today = calculate_lower_increase(prediction_today, sp_prices)
lower_increase_one_week = calculate_lower_increase(prediction_one_week, sp_prices)
lower_increase_two_week = calculate_lower_increase(prediction_two_week, sp_prices)
lower_increase_three_week = calculate_lower_increase(prediction_three_week, sp_prices)
lower_increase_four_week = calculate_lower_increase(prediction_four_week, sp_prices)

upper_increase_today = calculate_upper_increase(prediction_today, sp_prices)
upper_increase_one_week = calculate_upper_increase(prediction_one_week, sp_prices)
upper_increase_two_week = calculate_upper_increase(prediction_two_week, sp_prices)
upper_increase_three_week = calculate_upper_increase(prediction_three_week, sp_prices)
upper_increase_four_week = calculate_upper_increase(prediction_four_week, sp_prices)

print_increases(prediction_today, increase_today, lower_increase_today, upper_increase_today)
print_increases(prediction_one_week, increase_one_week, lower_increase_one_week, upper_increase_one_week)
print_increases(prediction_two_week, increase_two_week, lower_increase_two_week, upper_increase_two_week)
print_increases(prediction_three_week, increase_three_week, lower_increase_three_week, upper_increase_three_week)
print_increases(prediction_four_week, increase_four_week, lower_increase_four_week, upper_increase_four_week)


### COMPARING PREDICTIONS TO ACTUAL VALUES
compare_predictions_to_actual(sp_prices, prediction_today, today, yesterday, '1-day', 'Predicted closing values 1_day.csv', '1_day_error.csv')
compare_predictions_to_actual(sp_prices, prediction_one_week, one_week_ahead, one_week_ago, '1-week', 'Predicted closing values 1_week.csv', '1_week_error.csv')
compare_predictions_to_actual(sp_prices, prediction_two_week, two_week_ahead, two_week_ago, '2-week', 'Predicted closing values 2_week.csv', '2_week_error.csv')
compare_predictions_to_actual(sp_prices, prediction_three_week, three_week_ahead, three_week_ago, '3-week', 'Predicted closing values 3_week.csv', '3_week_error.csv')
compare_predictions_to_actual(sp_prices, prediction_four_week, four_week_ahead, four_week_ago, '4-week', 'Predicted closing values 4_week.csv', '4_week_error.csv')
