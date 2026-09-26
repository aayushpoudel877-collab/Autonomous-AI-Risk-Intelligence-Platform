import numpy as np
def regression_metrics(actual,predicted):
    actual=np.asarray(actual,float); predicted=np.asarray(predicted,float); e=actual-predicted
    return {"mae":float(np.mean(np.abs(e))),"rmse":float(np.sqrt(np.mean(e**2)))}
