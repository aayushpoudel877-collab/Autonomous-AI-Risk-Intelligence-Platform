import pandas as pd
REQUIRED_COLUMNS={"baseline_signal","volatility","event_rate","text_signal","image_signal","trend","risk_target","risk_score"}
def validate_dataset(df: pd.DataFrame)->list[str]:
    errors=[]
    missing=REQUIRED_COLUMNS-set(df.columns)
    if missing: errors.append(f"missing columns: {sorted(missing)}")
    if df.empty: errors.append("dataset is empty")
    if df.isna().any().any(): errors.append("dataset contains missing values")
    return errors
