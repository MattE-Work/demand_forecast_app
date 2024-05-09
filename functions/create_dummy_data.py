import numpy as np
import pandas as pd


def create_data():
    np.random.seed(42)
    # Example Data Preparation
    data = {
        'ds': pd.date_range(start='2020-01-01', periods=(3*365), freq='D'),
        'y': np.random.poisson(lam=50, size=(3*365))  # Simulating daily patient numbers
    }
    df = pd.DataFrame(data)

    return df