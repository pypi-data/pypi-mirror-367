# 🚀 AnomaX

**Universal LSTM-based Anomaly Detection for Autonomous Drones and Satellites**  
Sensor-agnostic, real-time, and plug-and-play.

---

## 🧠 Overview

AnomaX is a powerful time-series anomaly detection system built using LSTM neural networks. Designed for real-world autonomous systems like drones, satellites, and IoT platforms, it flags unusual sensor behavior — even when labels aren’t available.

📁 labeled_anomalies.csv – Dataset Metadata Summary
This file contains metadata for 81 telemetry channels from NASA's SMAP spacecraft. It defines where and what kind of anomalies are present in each time series.

🔑 Columns
Column	Description
chan_id	Unique identifier for each sensor channel (e.g., A-1, P-2, S-13)
spacecraft	Mission source — all entries are "SMAP" (Soil Moisture Active Passive)
anomaly_sequences	List of time index ranges [start, end] where anomalies occurred
class	Type(s) of anomalies — "point" or "contextual" (can be mixed)
num_values	Number of time steps (length) in each test sequence for that channel

📊 Key Stats
Total rows: 82

Unique channels: 81

➜ One channel (chan_id) may be duplicated – check for duplicates

Unique time series lengths (num_values): 73

➜ Channel time series are not all the same length

🧠 Anomaly Class Combinations
The class column may include multiple anomaly types per channel.
Here are the unique combinations found:

csharp
Copy
Edit
[
  [contextual, contextual, contextual],
  [point],
  [contextual, contextual],
  [contextual],
  [point, point, point],
  [point, contextual],
  [point, point],
  [contextual, point, contextual]
]
🔎 Some channels include both point and contextual anomalies — training must account for mixed anomaly types.

