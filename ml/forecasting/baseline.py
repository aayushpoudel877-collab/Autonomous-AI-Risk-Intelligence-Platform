import numpy as np
import pandas as pd
class MovingAverageForecaster:
    def __init__(self,window=7):
        if window<2: raise ValueError("window must be at least 2")
        self.window=window
    def forecast(self,series:pd.Series,horizon=7):
        values=series.astype(float).to_numpy()
        if len(values)<self.window: raise ValueError("series shorter than window")
        history=list(values)
        for _ in range(horizon): history.append(float(np.mean(history[-self.window:])))
        return np.asarray(history[-horizon:])
    def evaluate(self,series):
        values=series.astype(float).to_numpy()
        if len(values)<=self.window:return {"mae":0.0,"rmse":0.0}
        actual=values[self.window:]; preds=np.array([np.mean(values[i-self.window:i]) for i in range(self.window,len(values))]); e=actual-preds
        return {"mae":float(np.mean(np.abs(e))),"rmse":float(np.sqrt(np.mean(e**2)))}
