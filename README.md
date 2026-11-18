# 🛢️ Cyber-Secure Predictive Maintenance for Oil & Gas Wells

An integrated **Petroleum Engineering + Dual-Layer AI Decision-Support System** combining:
1. **AI Layer 1 — Predictive Maintenance (`Random Forest` / `XGBoost`)**: Early-warning prediction of ESP pump degradation, downtime, and workover risk using multivariate wellhead and downhole telemetry.
2. **AI Layer 2 — Cyber & Sensor Integrity (`Physics-Informed Isolation Forest`)**: Real-time detection of **5 SCADA / Sensor Anomaly classes** (*Sensor Spike, Slow Drift, Sensor Freezing, False-Data Injection, and Physical Flow Inconsistency*).
3. **Interactive Custom Web Dashboard & Well Anatomy Simulator**:
   - **Tab 1 (`1. Live Well Monitor`)**: Animated 6-zone Well Digital Twin (`Well W-001`), Dual-AI verdict cards, and an interactive 24-hour trend player with a glowing playhead and color-coded risk zones.
   - **Tab 2 (`2. Interactive Simulator`)**: Adjust pressures, motor current, flow rates, or inject cyber attacks and click directly on affected well parts to inspect what went wrong and repair them with one click.
   - **Tab 3 (`3. Real-World Case Studies`)**: Interactive mapping to the **OISD Onshore Workover Rig Blowout (2026)**, **Equinor Deepsea Bollsta Well-Control Incident (2025)**, and **Oil India Tank Farm Heater Fire (2026)**.
   - **Tab 4 (`4. ML Model Results`)**: Chronological train/test validation metrics across `Logistic Regression`, `Decision Tree`, `Random Forest`, and `XGBoost`.

---

## 🚀 Quick Start (For Friends / Teammates)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Regenerate the 2-Month Dataset & Retrain AI Models
The repository already includes the pre-trained models (`trained_models_bundle.pkl` and `model_evaluation_summary.json`). If you want to regenerate the 86,400-minute dataset and retrain from scratch:
```bash
python generate_scada_dataset.py
python ml_pipeline.py
```

### 3. Launch the Custom Interactive Dashboard
```bash
python server.py
```
Then open **http://localhost:8505** in your browser!
