import pandas as pd
from typing import Tuple, Dict

def compute_airspeed_change(df: pd.DataFrame) -> pd.DataFrame:
    df['airspeedchange'] = df['airspeed'] - df['airspeed'].shift(1)
    df['airspeedchange'] = df['airspeedchange'].fillna(0)
    return df

def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=0, index_col=None)
    return compute_airspeed_change(df)

def get_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[['roll', 'pitch', 'yaw', 'rollspeed', 'pitchspeed', 'yawspeed', 'airspeedchange']]

def load_all_datasets(base_path: str) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    files = {
        "base": f"{base_path}/base.csv",
        "random": f"{base_path}/random1.csv",
        "wind": f"{base_path}/wind1.csv",
        "engine": f"{base_path}/engine1.csv",
        "sensor": f"{base_path}/sensor1.csv",
        "crash": f"{base_path}/crash.csv"
    }

    datasets = {name: load_dataset(path) for name, path in files.items()}
    features = {name: get_feature_columns(df) for name, df in datasets.items()}

    return datasets["base"], features
