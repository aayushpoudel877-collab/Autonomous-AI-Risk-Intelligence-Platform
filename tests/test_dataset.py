from ml.data.generator import generate_risk_dataset
from ml.data.validation import validate_dataset

def test_generated_dataset_is_valid():
    df=generate_risk_dataset()
    assert len(df)==5000
    assert validate_dataset(df)==[]
