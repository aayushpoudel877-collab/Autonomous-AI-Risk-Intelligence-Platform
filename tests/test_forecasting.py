import pandas as pd
from ml.forecasting.baseline import MovingAverageForecaster

def test_forecast_horizon(): assert len(MovingAverageForecaster(5).forecast(pd.Series(range(30)),7))==7
