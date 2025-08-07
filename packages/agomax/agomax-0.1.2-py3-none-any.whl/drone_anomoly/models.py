from sklearn.cluster import KMeans, DBSCAN, OPTICS
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
import pandas as pd

def train_kmeans(data: pd.DataFrame) -> KMeans:
    model = KMeans(init="random", n_clusters=2, n_init=10, random_state=1)
    model.fit(data)
    return model

def train_lof(data: pd.DataFrame) -> LocalOutlierFactor:
    model = LocalOutlierFactor(n_neighbors=14, contamination="auto", novelty=True)
    model.fit(data)
    return model

def train_svm(data: pd.DataFrame) -> OneClassSVM:
    model = OneClassSVM(nu=0.1, kernel='rbf', gamma='scale')
    model.fit(data)
    return model

def train_dbscan(data: pd.DataFrame) -> DBSCAN:
    model = DBSCAN(eps=0.78)
    model.fit(data)
    return model

def train_optics(data: pd.DataFrame) -> OPTICS:
    model = OPTICS(min_samples=50)
    model.fit(data)
    return model

def train_all_models(data: pd.DataFrame) -> dict:
    return {
        "kmeans": train_kmeans(data),
        "lof": train_lof(data),
        "svm": train_svm(data),
        "dbscan": train_dbscan(data),
        "optics": train_optics(data),
    }

# --- Prediction functions ---
def predict_kmeans(model, train_data, data):
    # Prototype-style: anomaly if distance to centroid > threshold
    import numpy as np
    labels = model.predict(data)
    centroids = model.cluster_centers_
    # Calculate distances for training data
    train_labels = model.predict(train_data)
    train_distances = []
    for i in range(len(train_data)):
        centroid = centroids[int(train_labels[i])]
        distance = np.sqrt(np.sum((train_data.iloc[i] - centroid)**2))
        train_distances.append(distance)
    mean = np.mean(train_distances)
    std = np.std(train_distances)
    threshold = mean + 3 * std
    # Calculate distances for prediction data
    pred_distances = []
    for i in range(len(data)):
        centroid = centroids[int(labels[i])]
        distance = np.sqrt(np.sum((data.iloc[i] - centroid)**2))
        pred_distances.append(distance)
    # Assign anomaly if distance > threshold
    return [1 if dist <= threshold else -1 for dist in pred_distances]

def predict_lof(model, data):
    # LOF: -1 is anomaly, 1 is normal
    return model.predict(data)

def predict_svm(model, data):
    # OneClassSVM: -1 is anomaly, 1 is normal
    return model.predict(data)

def predict_dbscan(model, data):
    # DBSCAN: -1 is anomaly, others are normal
    labels = model.fit_predict(data)
    return [1 if lbl != -1 else -1 for lbl in labels]

def predict_optics(model, data):
    # OPTICS: -1 is anomaly, others are normal
    labels = model.fit_predict(data)
    return [1 if lbl != -1 else -1 for lbl in labels]

def predict_all_models(models: dict, base_df: pd.DataFrame, crash_df: pd.DataFrame) -> dict:
    # Use crash_df for prediction, base_df for kmeans training distances
    return {
        "kmeans": predict_kmeans(models["kmeans"], base_df, crash_df),
        "lof": predict_lof(models["lof"], crash_df),
        "svm": predict_svm(models["svm"], crash_df),
        "dbscan": predict_dbscan(models["dbscan"], crash_df),
        "optics": predict_optics(models["optics"], crash_df),
    }

# --- Loader function for pipeline compatibility ---
def load_models(base_df: pd.DataFrame) -> dict:
    # Train all models on base_df features
    return train_all_models(base_df)
