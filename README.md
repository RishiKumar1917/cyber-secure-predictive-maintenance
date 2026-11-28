# 🛢️ Cyber-Secure Predictive Maintenance for Oil & Gas Wells

An integrated **Petroleum Engineering + Dual-Layer AI Decision-Support System** combining:
1. **AI Layer 1 — Predictive Maintenance (`Random Forest` / `XGBoost`)**: Early-warning prediction of ESP pump degradation, downtime, and workover risk using multivariate wellhead and downhole telemetry.
2. **AI Layer 2 — Cyber & Sensor Integrity (`Physics-Informed Isolation Forest`)**: Real-time detection of **5 SCADA / Sensor Anomaly classes** (*Sensor Spike, Slow Drift, Sensor Freezing, False-Data Injection, and Physical Flow Inconsistency*).
3. **Interactive Custom Web Dashboard & Well Anatomy Simulator**:
   - **Tab 1 (`1. Live Well Monitor`)**: Animated 6-zone Well Digital Twin (`Well W-001`), Dual-AI verdict cards, and an interactive 24-hour trend player with a glowing playhead and color-coded risk zones.
   - **Tab 2 (`2. Interactive Simulator`)**: Adjust pressures, motor current, flow rates, or inject cyber attacks and click directly on affected well parts to inspect what went wrong and repair them with one click.
   - **Tab 3 (`3. Incident Replay (Case Studies)`)**: Interactive **Incident Replay Lab** for the **OISD Onshore Workover Rig Blowout (2026)**, **Equinor Deepsea Bollsta Well-Control Incident (2025)**, and **Oil India Tank Farm Heater Fire (2026)** — replay what happened minute-by-minute, toggle engineering/AI fixes, and compare outcomes side-by-side.
   - **Tab 4 (`4. ML Model Results`)**: Chronological train/test validation metrics across `Logistic Regression`, `Decision Tree`, `Random Forest`, and `HistGradientBoostingClassifier` (XGBoost-style).

---

## 🎬 Incident Replay Lab (Case Studies)

Tab 3 provides physics-based reconstructed time-series replays showing **what happened** and **how specific fixes prevent the incident**:
1. **OISD Onshore Workover Rig Gas Blowout (India, Feb 2026)** — *Main case*: Replays fluid swap, wireline perforation, gas influx, trip-tank isolation, and BOP shear-ram vs blind-ram failure (`BLOWOUT -> CONTROLLED / SAFE`).
2. **Equinor Deepsea Bollsta Well-Control Incident (Norway, Sep 2025)**: Replays faulty logging calibration, frozen ΔP gauge, outer barrier failure, and ~930 kg gas release at casing cut (`RELEASE -> SAFE`).
3. **Oil India Tank Farm Indirect Bath Heater Fire (Assam, Nov 2026)**: *Hypothetical training reconstruction* of one plausible pathway (passing isolation valve + residual hydrocarbon vapour + hot work, `FIRE -> SAFE`).

> **Note:** All numerical series (depths, pressures, flow rates, LEL, timing) are illustrative engineering assumptions for replay/decision-support demonstration, not raw incident telemetry. For Oil India, the official inquiry into the ignition cause was ongoing in the supplied press release.

To regenerate the 6 case-study CSV datasets and summary JSON in `case_studies/`:
```bash
python generate_case_study_datasets.py
```

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
