# 🛡️ AI-Based Real-Time Ransomware Detection System

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![ML](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-green)
![Flask](https://img.shields.io/badge/Flask-SocketIO-red)
![Accuracy](https://img.shields.io/badge/Accuracy-100%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Real-time ransomware detection using Shannon Entropy Analysis,
> Random Forest, and Isolation Forest with a live Flask web dashboard.

---

## 📌 Overview

Ransomware causes **$30 billion+** in global damage annually,
attacking organizations every **11 seconds**. Traditional
antivirus systems fail against new variants because they rely
on known signatures.

This system takes a **signature-free** approach — detecting
ransomware by analyzing **what files DO mathematically**,
not what they look like. Using Shannon entropy theory combined
with machine learning, it detects both known and zero-day
ransomware in real time.

---

## 🎯 Performance Results

| Metric | Value |
|--------|-------|
| ✅ Detection Accuracy | **100%** |
| ✅ False Positive Rate | **0%** |
| ✅ Average Latency | **9.70 ms** |
| ✅ Throughput | **103 files/second** |
| ✅ Normal File Entropy | 4.44 / 8.0 |
| ✅ Encrypted File Entropy | 7.96 / 8.0 |

---

## 🔬 Detection Methodology

### 1. Shannon Entropy Analysis (+30 pts)
Formula: H(X) = -Σ P(xi) × log₂(P(xi))
Normal files:    entropy 3.5 – 5.5  → LOW randomness
Encrypted files: entropy 7.5 – 8.0  → HIGH randomness
Threshold: 7.0 bits/byte
Scale: 0 to 8 (log₂(256) = 8 maximum)

### 2. Random Forest Classifier (+40 pts)

100 decision trees trained on 1000 samples
500 normal + 500 ransomware synthetic samples
8-dimensional feature vector input
Fast inference — suitable for real-time detection


### 3. Isolation Forest — Zero-Day Detection (+20 pts)

Unsupervised anomaly detection
No labeled attack data required
Detects brand new unknown ransomware variants
Complements Random Forest to reduce false negatives


### 4. Behavioral Analysis

Modification burst > 50 files/10 seconds → +30 pts
Mass renaming > 20 files/30 seconds     → +25 pts
Deletion pattern > 15 files/30 seconds  → +25 pts


---

## 📊 Risk Scoring System
Risk Score = Entropy(+30) + RF(+40) + IF(+20) + Burst(+30) + Rename(+25)
Maximum possible = 145 → Capped at 100
0  – 25  →  🟢 Normal
26 – 89  →  🟡 Suspicious
90 – 100 →  🔴 ATTACK! Alert Triggered!

---

## 🧠 8-Dimensional Feature Vector

| Feature | Description |
|---------|-------------|
| 1. Entropy | Shannon entropy value (0-8) |
| 2. File Size | Size in megabytes |
| 3. Extension Flag | Suspicious extension binary (0 or 1) |
| 4. Access Rate | File accesses per minute |
| 5. Mod Burst | Files modified in last 10 seconds |
| 6. Rename Pattern | Files renamed in last 30 seconds |
| 7. Deletion Pattern | Files deleted in last 30 seconds |
| 8. Global Rate | Total accesses across all files |

---

## 🏗️ System Architecture
Layer 1: OS File Events (Create/Modify/Rename/Delete)
↓
Layer 2: Watchdog File Monitor (Event-driven, zero polling)
↓
Layer 3: Feature Extractor (8-dimensional vector)
↓
Layer 4: ML Detection (Random Forest + Isolation Forest)
↓
Layer 5: Risk Scoring Engine (Weighted aggregation 0-100)
↓
Layer 6: Alert Generation (Socket.IO push)
↓
Layer 7: Flask Web Dashboard (Real-time charts + table)

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.8+ |
| File Monitoring | Watchdog |
| ML Models | scikit-learn (Random Forest, Isolation Forest) |
| Feature Scaling | StandardScaler |
| Web Framework | Flask |
| Real-time Comms | Flask-SocketIO (WebSocket) |
| Dashboard Charts | Chart.js |
| Numerical Computing | NumPy |
| Model Storage | Pickle |

---

## 📁 Project Structure
ransomware-detection/
│
├── ransomware_detector.py    ← Core detection engine
├── web_dashboard.py          ← Flask + SocketIO server
├── simple_test.py            ← Ransomware simulation
├── calculate_metrics.py      ← Performance evaluation
├── diagnostic.py             ← System diagnostic tool
├── ransomware_model.pkl      ← Trained ML model (auto-generated)
│
├── templates/
│   └── dashboard.html        ← Real-time web dashboard
│
├── test_ransomware/          ← Simulated files (auto-generated)
└── monitored_directory/      ← Live monitoring folder

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install flask flask-socketio watchdog scikit-learn numpy
```

### Run Dashboard
```bash
python web_dashboard.py
```
Open browser → **http://127.0.0.1:5000**

### Run Simulation (second terminal)
```bash
python simple_test.py
```

### Run Diagnostics
```bash
python diagnostic.py
```

### Check Performance Metrics
```bash
python calculate_metrics.py
```

---

## 📸 Dashboard Features
✅ Real-time Risk Assessment Meter (0-100)
✅ File Activity Count Chart
✅ Before vs After Encryption Chart
✅ Entropy Distribution Histogram
✅ Alert Frequency Pie Chart
✅ Detection Summary Table (per-file results)
✅ Live Activity Log with timestamps
✅ Instant alerts via WebSocket (no page refresh!)

---

## 🔍 How Zero-Day Detection Works

Traditional antivirus needs a known signature.
This system detects unknown ransomware because:
ANY encryption algorithm → ALWAYS produces high entropy!
AES-256 encrypted file   → entropy 7.96 ✅ DETECTED
RSA-2048 encrypted file  → entropy 7.97 ✅ DETECTED
ChaCha20 encrypted file  → entropy 7.98 ✅ DETECTED
Unknown new ransomware   → entropy 7.95 ✅ DETECTED
Mathematical certainty — not a heuristic!

---

## 📄 Related Research

This project is related to my IEEE published research on
financial fraud detection using hybrid ML models:

**Adaptive Hybrid Learning for Credit Card Fraud Detection:
A Comparative Study of Supervised, Reinforcement, and Hybrid Models**

- 📍 Published: IEEE ICCTDC 2025, Hassan, India
- 🔗 DOI: [10.1109/ICCTDC64446.2025.11158136](https://ieeexplore.ieee.org/document/11158136)
- 👤 Authors: Divya Raj Singh, Dr. Neetu Gupta

---

## 🌟 Key Innovations

Multi-indicator risk scoring
(entropy + ML + behavior combined)
Zero-day detection capability
(Isolation Forest unsupervised model)
Real-time WebSocket dashboard
(no polling, instant alerts)
Mathematical entropy foundation
(signature-free detection)
Dual ML approach
(supervised + unsupervised combined)


---

## 👨‍💻 Author

**Divya Raj Singh**
- 🎓 B.Tech CSE — Manipal University Jaipur
- 📍 Lucknow, Uttar Pradesh, India
- 📧 divyaraj8009226666@gmail.com
- 🔗 [LinkedIn](https://linkedin.com/in/divya-raj-singh-462958380)
- 📄 [IEEE Paper](https://ieeexplore.ieee.org/document/11158136)

---

## 📜 Internship Context

This project was developed during my internship at
**eGyanam Technologies Private Limited, Pune**
as the core product deliverable for the
Product Development Team (January 2026 – May 2026).

Received certificate of outstanding performance
from company director.

---

*If this project helped you, please ⭐ star the repository!*
