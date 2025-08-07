from drone_anomoly.data_loader import load_all_datasets
from drone_anomoly.models import load_models, predict_all_models
from drone_anomoly.rules import rule_checker
import pandas as pd

def run_pipeline(base_path: str, phase: str = None, export_path: str = None):
    # Step 1: Load datasets
    base_df, features_dict = load_all_datasets(base_path)
    crash_df = features_dict["crash"]
    # Load all datasets once, get full crash data from base_df (if needed, adjust logic)
    full_crash_df = base_df  # Assuming base_df is the full crash data with all columns

    # Step 2: Load models (use only numeric feature columns)
    base_features = features_dict["base"]
    crash_features = features_dict["crash"]
    models = load_models(base_features)

    # Step 3: Rule-based anomaly detection (only apply rule checking if phase is given)
    rule_alerts = []
    for _, dp in full_crash_df.iterrows():
        if phase is None or dp.get("PHASE") == phase:
            rule_alerts.append(rule_checker(dp))
        else:
            rule_alerts.append(0)

    # Step 4: Model-based anomaly detection (use only numeric features)
    model_predictions = predict_all_models(models, base_features, crash_features)

    # Step 5: Combine rule and model predictions using majority voting
    final_alerts = []
    for i in range(len(crash_df)):
        votes = [
            model_predictions["kmeans"][i],
            model_predictions["lof"][i],
            model_predictions["svm"][i],
            model_predictions["dbscan"][i],
            model_predictions["optics"][i]
        ]
        # Normalize to binary format
        votes = [1 if v == 1 else -1 for v in votes]
        if rule_alerts[i] > 0:
            votes.append(-1)
        final_alerts.append(max(set(votes), key=votes.count))


    # Step 6: Report (majority voting only)
    detected = sum(1 for alert in final_alerts if alert == -1)
    total = len(final_alerts)
    print(f"\n[RESULT] {detected} anomalies detected out of {total} datapoints ({(detected/total)*100:.2f}%)")

    # Step 6b: Prototype-style accuracy (anomaly if either rule or model triggers)
    overall_crash_count = 0
    for i in range(len(final_alerts)):
        if final_alerts[i] < 0 or rule_alerts[i] > 0:
            overall_crash_count += 1
    print(f"[PROTOTYPE LOGIC] For crash, out of the {len(final_alerts)} anomalies {overall_crash_count} were detected, which is {(overall_crash_count/len(final_alerts))*100:.2f}%")

    # Step 7: Export if requested
    if export_path:
        result_df = crash_df.copy()
        result_df["anomaly"] = final_alerts
        result_df.to_csv(export_path, index=False)
        print(f"[INFO] Results saved to {export_path}")

    return final_alerts
