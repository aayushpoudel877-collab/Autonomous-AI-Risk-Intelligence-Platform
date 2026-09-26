import pandas as pd
FEATURES=["baseline_signal","volatility","event_rate","text_signal","image_signal","trend"]
def feature_importance_table(model)->pd.DataFrame:
    return pd.DataFrame({"feature":FEATURES,"importance":model.feature_importances_}).sort_values("importance",ascending=False).reset_index(drop=True)
