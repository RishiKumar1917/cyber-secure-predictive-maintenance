import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(
    page_title="Cyber-Secure Predictive Maintenance | Oil & Gas Wells",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling for dark/industrial control room look
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.2rem; padding-bottom: 1.5rem; }
    .status-banner {
        padding: 14px 20px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 14px;
        border-left: 6px solid;
    }
    .alert-normal { background-color: rgba(16, 185, 129, 0.12); border-color: #10b981; color: #065f46; }
    .alert-maint  { background-color: rgba(245, 158, 11, 0.15); border-color: #f59e0b; color: #92400e; }
    .alert-high   { background-color: rgba(239, 68, 68, 0.15);  border-color: #ef4444; color: #991b1b; }
    .alert-cyber  { background-color: rgba(139, 92, 246, 0.15); border-color: #8b5cf6; color: #5b21b6; }
    .alert-crit   { background-color: rgba(220, 38, 38, 0.22);  border-color: #dc2626; color: #7f1d1d; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading 2-Month Wellhead SCADA Dataset...")
def load_dataset():
    csv_path = Path("wellhead_scada_2month_telemetry.csv")
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    return df


@st.cache_data
def load_eval_summary():
    summary_path = Path("model_evaluation_summary.json")
    if summary_path.exists():
        with open(summary_path, "r") as f:
            return json.load(f)
    return None


@st.cache_resource
def load_models_bundle():
    bundle_path = Path("trained_models_bundle.pkl")
    if bundle_path.exists():
        with open(bundle_path, "rb") as f:
            return pickle.load(f)
    return None


df = load_dataset()
eval_summary = load_eval_summary()
models_bundle = load_models_bundle()

# -----------------------------------------------------------------------------
# Sidebar: Scenario Preset Selector & Interactive Controls
# -----------------------------------------------------------------------------
st.sidebar.title("🛢️ Well Control & AI Console")
st.sidebar.caption("Well ID: **W-001 (ESP Artificial-Lift Well)**")

SCENARIO_PRESETS = {
    "Scenario A: Equipment Degradation (Pre-Failure)": {
        "desc": "Day 48: THP drops, gas/water flow declines, pump current & DHG temp rise prior to ESP trip.",
        "start_day": 48,
        "end_day": 49,
        "focus_idx": int(48 * 1440 + 18 * 60),
    },
    "Scenario B: Measurement Anomaly (Sensor Freezing)": {
        "desc": "Day 44: THP & BHP freeze flatline while CHP continues changing and network packet loss spikes.",
        "start_day": 44,
        "end_day": 45,
        "focus_idx": int(44 * 1440 + 17.5 * 60),
    },
    "Scenario C: Combined High Failure Risk + Cyber Anomaly": {
        "desc": "Day 56: High ML failure risk AND physically inconsistent sensor tampering occur together. Operator must verify sensor integrity first!",
        "start_day": 56,
        "end_day": 57,
        "focus_idx": int(56 * 1440 + 14 * 60),
    },
    "Anomaly Demo: Sensor Spike (Sudden Surge)": {
        "desc": "Day 43: Sudden extreme high/low pressure spikes in THP and BHP.",
        "start_day": 43,
        "end_day": 44,
        "focus_idx": int(43 * 1440 + 12 * 60),
    },
    "Anomaly Demo: Slow Sensor Drift (Creeping CHP Bias)": {
        "desc": "Day 46: Stealthy +145 PSI creeping drift on Casing Head Pressure (CHP).",
        "start_day": 46,
        "end_day": 47,
        "focus_idx": int(46 * 1440 + 13 * 60),
    },
    "Anomaly Demo: False-Data Injection (Spoofed BHP)": {
        "desc": "Day 51: Modbus Function 16 register spoofing reports 420 PSI downhole pressure while well operates normally.",
        "start_day": 51,
        "end_day": 52,
        "focus_idx": int(51 * 1440 + 4.5 * 60),
    },
    "Normal Baseline Operation": {
        "desc": "Day 45: Normal diurnal operating behavior across all wellhead and downhole sensors.",
        "start_day": 45,
        "end_day": 46,
        "focus_idx": int(45 * 1440 + 12 * 60),
    },
    "Full 60-Day Historical Overview (Downsampled)": {
        "desc": "Complete 2-month (86,400-minute) historical telemetry across all 6 workovers & 5 anomaly classes.",
        "start_day": 0,
        "end_day": 60,
        "focus_idx": int(56 * 1440 + 14 * 60),
    },
}

selected_preset_name = st.sidebar.selectbox(
    "🎯 Select Demonstration Scenario",
    list(SCENARIO_PRESETS.keys()),
    index=0,
)
preset = SCENARIO_PRESETS[selected_preset_name]
st.sidebar.info(preset["desc"])

day_range = st.sidebar.slider(
    "📅 Timeline Window (Day of 60-Day Dataset)",
    min_value=0,
    max_value=60,
    value=(preset["start_day"], preset["end_day"]),
    step=1,
)

start_min_idx = max(0, day_range[0] * 1440)
end_min_idx = min(len(df) - 1, max(start_min_idx + 60, day_range[1] * 1440))
window_df = df.iloc[start_min_idx:end_min_idx].copy()

# Downsample if window is large so Plotly stays snappy
if len(window_df) > 3000:
    step_stride = max(1, len(window_df) // 2500)
    plot_df = window_df.iloc[::step_stride].copy()
else:
    plot_df = window_df

# Current inspection snapshot row
default_snap = min(max(preset["focus_idx"], start_min_idx), end_min_idx - 1)
snap_row = df.iloc[default_snap]

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Architecture Layers")
st.sidebar.markdown(
    """
- **Layer 1 (Predictive Maintenance)**: `Random Forest` / `XGBoost` early-warning failure risk + feature attribution.
- **Layer 2 (Cyber / Measurement Integrity)**: Physics-informed `Isolation Forest` detecting *Spike, Drift, Freeze, FDI & Physical Inconsistency*.
- **Decision Support**: Distinguishes equipment degradation from sensor corruption.
"""
)

# -----------------------------------------------------------------------------
# Header & Live Integrated Alert Banner
# -----------------------------------------------------------------------------
st.title("🛡️ Cyber-Secure Predictive Maintenance Dashboard for Oil & Gas Wells")
st.markdown(
    "**Integration of Petroleum Engineering, Machine Learning Failure Prediction, and SCADA/OT Measurement-Anomaly Detection**"
)

alert_level = snap_row.get("integrated_alert_level", "Normal")
risk_pct = float(snap_row.get("predicted_failure_risk_pct", 0.0))
risk_cat = snap_row.get("risk_category", "Low")
cyber_score = float(snap_row.get("cyber_anomaly_score", 0.0))
anom_cat = snap_row.get("anomaly_category", "Normal")
op_status = snap_row.get("operational_status", "Normal")

ALERT_CONFIG = {
    "Normal": (
        "alert-normal",
        "🟢 WELL STATUS: NORMAL OPERATION — Parameters within expected physical & statistical baseline. Continue routine monitoring.",
    ),
    "Maintenance warning": (
        "alert-maint",
        "🟡 WELL STATUS: MAINTENANCE WARNING — Abnormal operating trend detected. Schedule engineering assessment.",
    ),
    "High failure risk": (
        "alert-high",
        "🔴 WELL STATUS: HIGH FAILURE RISK — ML model predicts elevated downtime/workover risk. Prioritise inspection and maintenance planning.",
    ),
    "Measurement anomaly": (
        "alert-cyber",
        f"🟣 WELL STATUS: MEASUREMENT INTEGRITY WARNING ({anom_cat}) — Sensor data are inconsistent or unusual. Verify instrument & telemetry integrity before making operational changes.",
    ),
    "Critical operational warning": (
        "alert-crit",
        f"🚨 WELL STATUS: CRITICAL OPERATIONAL WARNING (Scenario C: High Failure Risk + {anom_cat}) — Verify sensor/measurement reliability FIRST before interpreting failure prediction!",
    ),
}
css_class, banner_text = ALERT_CONFIG.get(alert_level, ALERT_CONFIG["Normal"])
st.markdown(
    f'<div class="status-banner {css_class}">{banner_text}<br>'
    f'<span style="font-size:0.88rem;font-weight:500;">Snapshot Timestamp: {snap_row["timestamp"]} | '
    f'Operational State: {op_status} | Anomaly Type: {anom_cat}</span></div>',
    unsafe_allow_html=True,
)

# Top KPI Cards
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric(
    "Predicted Failure Risk",
    f"{risk_pct:.1f}%",
    f"{risk_cat} Risk",
    delta_color="inverse" if risk_pct > 35 else "normal",
)
kpi2.metric(
    "Cyber Anomaly Score",
    f"{cyber_score:.1f} / 100",
    anom_cat,
    delta_color="inverse" if cyber_score >= 60 else "normal",
)
kpi3.metric(
    "Tubing Head Pressure (THP)",
    f"{snap_row['tubing_head_pressure_psi']:.1f} PSI",
    f"{snap_row['thp_baseline_dev']:+.1f} vs baseline",
)
kpi4.metric(
    "Casing Head Pressure (CHP)",
    f"{snap_row['casing_head_pressure_psi']:.1f} PSI",
    f"{snap_row['chp_baseline_dev']:+.1f} vs baseline",
)
kpi5.metric(
    "Downhole Pressure (BHP)",
    f"{snap_row['downhole_gauge_pressure_psi']:.1f} PSI",
    f"ΔP: {snap_row['diff_pressure_bhp_thp_psi']:.0f} PSI",
)
kpi6.metric(
    "ESP Pump Current / RPM",
    f"{snap_row['pump_torque_current_amps']:.1f} A",
    f"{snap_row['pump_rpm']:.0f} RPM",
)

# -----------------------------------------------------------------------------
# Main Navigation Tabs (Aligned with PDF Modules 1–4 + Case Studies + Simulator)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Module 1: Well Health Monitoring",
        "⚙️ Module 2: Predictive Maintenance (ML Layer 1)",
        "🔐 Module 3: Cyber & Sensor Integrity (ML Layer 2)",
        "🚨 Module 4: Integrated Alerts (Scenarios A/B/C)",
        "🏗️ Real-World Case Studies (OISD, Bollsta, OIL)",
        "🧪 Live What-If & Anomaly Simulator",
    ]
)

# =============================================================================
# TAB 1: MODULE 1 - WELL HEALTH MONITORING
# =============================================================================
with tab1:
    st.subheader("Module 1: Multivariate Well Health & Petroleum Parameter Trends")
    st.caption(
        "Displays Tubing Head Pressure (THP), Casing Head Pressure (CHP), Downhole Gauge Pressure (BHP), "
        "Differential Pressure (ΔP), Gas/Water Flow Rates, Annular Water Level, Pump RPM, and Motor Current."
    )

    fig_health = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=(
            "Wellbore & Surface Pressures (THP, CHP, Downhole BHP & Differential ΔP)",
            "Production Flow Rates (Water BPD, Gas MSCFD) & Annular Water Level (ft)",
            "ESP Artificial-Lift Telemetry (Pump RPM, Motor Current Amps & Downhole Temp °F)",
        ),
    )

    # Subplot 1: Pressures
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["tubing_head_pressure_psi"],
            name="THP (PSI)",
            line=dict(color="#2563eb", width=2),
        ),
        row=1,
        col=1,
    )
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["casing_head_pressure_psi"],
            name="CHP (PSI)",
            line=dict(color="#d97706", width=2),
        ),
        row=1,
        col=1,
    )
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["downhole_gauge_pressure_psi"],
            name="Downhole BHP (PSI)",
            line=dict(color="#059669", width=1.8, dash="dot"),
        ),
        row=1,
        col=1,
    )

    # Subplot 2: Rates & Water Level
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["water_rate_bpd"],
            name="Water Rate (BPD)",
            line=dict(color="#0891b2", width=1.8),
        ),
        row=2,
        col=1,
    )
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["gas_rate_mscfd"],
            name="Gas Rate (MSCFD)",
            line=dict(color="#dc2626", width=1.8),
        ),
        row=2,
        col=1,
    )
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["water_level_ft"],
            name="Water Level (ft)",
            line=dict(color="#7c3aed", width=1.5, dash="dash"),
        ),
        row=2,
        col=1,
    )

    # Subplot 3: ESP RPM, Current, Temp
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["pump_torque_current_amps"],
            name="Pump Current (Amps)",
            line=dict(color="#e11d48", width=2),
        ),
        row=3,
        col=1,
    )
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["downhole_temp_f"],
            name="Downhole Temp (°F)",
            line=dict(color="#ea580c", width=1.8),
        ),
        row=3,
        col=1,
    )
    fig_health.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["choke_opening_pct"],
            name="Choke Opening (%)",
            line=dict(color="#4b5563", width=1.5, dash="dot"),
        ),
        row=3,
        col=1,
    )

    fig_health.update_layout(height=680, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=1.05))
    st.plotly_chart(fig_health, width="stretch")

    # Differential Pressure & Engineered Feature Summary Table
    c_dp1, c_dp2 = st.columns(2)
    with c_dp1:
        st.markdown("#### 📐 Differential Pressure & Derived Indicators (Current Window)")
        fig_dp = go.Figure()
        fig_dp.add_trace(
            go.Scatter(
                x=plot_df["timestamp"],
                y=plot_df["diff_pressure_bhp_thp_psi"],
                name="ΔP Wellbore (BHP - THP)",
                line=dict(color="#0d9488", width=2),
            )
        )
        fig_dp.add_trace(
            go.Scatter(
                x=plot_df["timestamp"],
                y=plot_df["diff_pressure_thp_chp_psi"],
                name="ΔP Surface (THP - CHP)",
                line=dict(color="#6366f1", width=2),
            )
        )
        fig_dp.update_layout(height=280, margin=dict(l=10, r=10, t=25, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig_dp, width="stretch")

    with c_dp2:
        st.markdown("#### 📋 Module 1 Parameter Reference & Live Reading")
        param_table = pd.DataFrame(
            [
                ("THP (Tubing Head Pressure)", f"{snap_row['tubing_head_pressure_psi']:.1f} PSI", "280.0 PSI", "Pressure at tubing head; drops during pump wear or surges when choked"),
                ("CHP (Casing Head Pressure)", f"{snap_row['casing_head_pressure_psi']:.1f} PSI", "150.0 PSI", "Annulus pressure; rises with gas influx or slow gauge drift"),
                ("Downhole Pressure (BHP)", f"{snap_row['downhole_gauge_pressure_psi']:.1f} PSI", "1242.5 PSI", "Bottomhole flowing pressure; key input for ΔP & FDI detection"),
                ("Differential Pressure (THP-CHP)", f"{snap_row['diff_pressure_thp_chp_psi']:.1f} PSI", "130.0 PSI", "Cross-checks pressure consistency across tubing and casing"),
                ("Gas / Water Flow Rate", f"{snap_row['gas_rate_mscfd']:.1f} MSCFD / {snap_row['water_rate_bpd']:.0f} BPD", "320 MSCFD / 850 BPD", "Production output; declines prior to ESP downtime"),
                ("Pump RPM & Motor Current", f"{snap_row['pump_rpm']:.0f} RPM / {snap_row['pump_torque_current_amps']:.1f} A", "3200 RPM / 58.0 A", "Mechanical load indicator; current rises during stage/bearing wear"),
            ],
            columns=["Parameter", "Current Reading", "Normal Baseline", "Engineering Significance"],
        )
        st.dataframe(param_table, width="stretch", hide_index=True)

# =============================================================================
# TAB 2: MODULE 2 - PREDICTIVE MAINTENANCE (ML LAYER 1)
# =============================================================================
with tab2:
    st.subheader("Module 2: Predictive Maintenance & Explainable Failure-Risk Assessment")

    # Compute top contributing features for the selected snapshot
    feature_deviations = {
        "Pump Motor Current Trend (current_roll_mean_15m)": abs(snap_row["pump_torque_current_amps"] - 58.0) / 5.0,
        "Abnormal THP Trend (thp_baseline_dev)": abs(snap_row["thp_baseline_dev"]) / 18.0,
        "Declining Gas Flow Rate (gas_rate_roll_mean_15m)": abs(snap_row["gas_rate_mscfd"] - 320.0) / 25.0,
        "Downhole Temperature Rise (downhole_temp_f)": abs(snap_row["downhole_temp_f"] - 185.0) / 3.0,
        "Declining Water Flow Rate (water_rate_bpd)": abs(snap_row["water_rate_bpd"] - 850.0) / 60.0,
        "Differential Pressure ΔP (THP - CHP)": abs(snap_row["diff_pressure_thp_chp_psi"] - 130.0) / 20.0,
        "Annular Water Level Change (water_level_ft)": abs(snap_row["water_level_ft"] - 450.0) / 20.0,
    }
    sorted_contribs = sorted(feature_deviations.items(), key=lambda x: x[1], reverse=True)
    major_param = sorted_contribs[0][0]
    secondary_param = sorted_contribs[1][0]

    if risk_pct > 65:
        rec_action = "Immediate engineering inspection, verify sensor integrity, and prepare workover/maintenance crew."
    elif risk_pct > 35:
        rec_action = "Schedule preventive engineering review and monitor ESP current & THP trends closely."
    else:
        rec_action = "Continue standard automated well monitoring."

    col_pdm_left, col_pdm_right = st.columns([1.15, 1.35])

    with col_pdm_left:
        st.markdown("#### 🎯 Structured Predictive Maintenance Output (Per PDF Spec p. 23)")
        pdm_card_df = pd.DataFrame(
            [
                ("Well ID", "W-001"),
                ("Operational Status", op_status),
                ("Predicted Failure / Downtime Risk", f"{risk_pct:.1f}%"),
                ("Risk Category", risk_cat),
                ("Major Contributing Parameter", major_param),
                ("Secondary Contributing Parameter", secondary_param),
                ("Recommended Action", rec_action),
            ],
            columns=["Dashboard Parameter", "Model Output"],
        )
        st.table(pdm_card_df)

    with col_pdm_right:
        st.markdown("#### 🔍 Feature Importance & Local Parameter Contribution")
        if eval_summary and "pdm_feature_importances" in eval_summary:
            fi_dict = eval_summary["pdm_feature_importances"]
            top_fi = list(fi_dict.items())[:10]
            fi_df = pd.DataFrame(top_fi, columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)
            fig_fi = px.bar(
                fi_df,
                x="Importance",
                y="Feature",
                orientation="h",
                title="Top 10 Predictive Maintenance Features (Trained Random Forest)",
                color="Importance",
                color_continuous_scale="Blues",
            )
            fig_fi.update_layout(height=320, margin=dict(l=10, r=10, t=35, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig_fi, width="stretch")

    # Failure risk timeline over current window
    st.markdown("#### 📈 Predicted Failure-Risk Score (%) & Historical Downtime/Workover Events")
    fig_risk = go.Figure()
    fig_risk.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["predicted_failure_risk_pct"],
            name="Predicted Failure Risk (%)",
            fill="tozeroy",
            line=dict(color="#ef4444", width=2),
        )
    )
    fig_risk.add_hline(y=65, line_dash="dash", line_color="#dc2626", annotation_text="High Risk Threshold (65%)")
    fig_risk.add_hline(y=35, line_dash="dot", line_color="#f59e0b", annotation_text="Maintenance Warning (35%)")
    fig_risk.update_layout(height=290, yaxis=dict(range=[0, 105], title="Failure Risk (%)"), margin=dict(l=20, r=20, t=25, b=20))
    st.plotly_chart(fig_risk, width="stretch")

    # Model Comparison Table from Chronological Test Split
    if eval_summary and "pdm_metrics" in eval_summary:
        st.markdown("#### 🏆 Objective 2: Machine Learning Model Comparison (Chronological Test Split: Days 43–60)")
        st.caption(
            "All models were trained strictly on Days 1–42 and evaluated on unseen future data (Days 43–60) to prevent time-series leakage."
        )
        rows_m = []
        for m_name, m_vals in eval_summary["pdm_metrics"].items():
            tn, fp, fn, tp = (
                m_vals["Confusion_Matrix"][0][0],
                m_vals["Confusion_Matrix"][0][1],
                m_vals["Confusion_Matrix"][1][0],
                m_vals["Confusion_Matrix"][1][1],
            )
            rows_m.append(
                {
                    "Model": m_name,
                    "Accuracy": f"{m_vals['Accuracy']*100:.2f}%",
                    "Precision": f"{m_vals['Precision']:.4f}",
                    "Recall": f"{m_vals['Recall']:.4f}",
                    "F1-Score": f"{m_vals['F1_Score']:.4f}",
                    "ROC-AUC": f"{m_vals['ROC_AUC']:.4f}",
                    "True Positives (TP)": tp,
                    "False Positives (FP)": fp,
                    "False Negatives (FN)": fn,
                }
            )
        st.dataframe(pd.DataFrame(rows_m), width="stretch", hide_index=True)

# =============================================================================
# TAB 3: MODULE 3 - CYBERSECURITY & MEASUREMENT INTEGRITY (ML LAYER 2)
# =============================================================================
with tab3:
    st.subheader("Module 3: Cybersecurity & SCADA Measurement-Anomaly Detection")
    st.caption(
        "Detects abnormal or potentially manipulated sensor readings across 5 anomaly classes: "
        "Sensor Spike, Sensor Drift, Sensor Freezing, False-Data Injection, and Physically Inconsistent Measurements."
    )

    fig_cyber = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "Cyber / Measurement Anomaly Score (0–100) with Alert Threshold",
            "SCADA Protocol Telemetry: Network Packet Loss (%) & Modbus Function Code",
        ),
    )
    fig_cyber.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["cyber_anomaly_score"],
            name="Cyber Anomaly Score",
            fill="tozeroy",
            line=dict(color="#8b5cf6", width=2),
        ),
        row=1,
        col=1,
    )
    fig_cyber.add_hline(y=60, line_dash="dash", line_color="#7c3aed", annotation_text="Anomaly Threshold (60)", row=1, col=1)

    fig_cyber.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["packet_loss_pct"],
            name="Packet Loss (%)",
            line=dict(color="#f97316", width=1.8),
        ),
        row=2,
        col=1,
    )
    fig_cyber.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df["modbus_function_code"],
            name="Modbus Function Code (Normal=3)",
            line=dict(color="#14b8a6", width=1.8, dash="dot"),
        ),
        row=2,
        col=1,
    )
    fig_cyber.update_layout(height=480, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=1.06))
    st.plotly_chart(fig_cyber, width="stretch")

    c_cy1, c_cy2 = st.columns(2)
    with c_cy1:
        st.markdown("#### 🛡️ Five Simulated Anomaly Classes & Expected Dashboard Response")
        anom_spec_df = pd.DataFrame(
            [
                ("Sensor_Spike", "Introduce unusually high/low pressure reading", "Sudden anomaly alert", "Flag spike & cross-check adjacent pressure gauges"),
                ("Sensor_Drift", "Gradually increase CHP (+145 PSI creeping bias)", "Gradual deviation warning", "Check gauge calibration & differential pressure ΔP"),
                ("Sensor_Freezing", "Keep THP/BHP constant (0 variance) while CHP changes", "Frozen sensor warning", "Inspect RTU/PLC polling link & packet loss"),
                ("False_Data_Injection", "Spoof low BHP (420 PSI) via Modbus Func 16 write", "Data-integrity warning", "Audit Modbus write logs & verify against THP/RPM"),
                ("Physical_Inconsistency", "Choke closed (6%) + high RPM (4450) with mismatched flow", "Measurement inconsistency alert", "Verify valve actuator & physical mass-balance"),
            ],
            columns=["Anomaly Type", "Simulation Approach", "Dashboard Alert", "Operator Action"],
        )
        st.dataframe(anom_spec_df, width="stretch", hide_index=True)

    with c_cy2:
        st.markdown("#### 📊 Detection Performance by Anomaly Category (Test Set)")
        if eval_summary and "anomaly_type_recall" in eval_summary:
            rec_rows = []
            for a_cat, a_info in eval_summary["anomaly_type_recall"].items():
                rec_rows.append(
                    {
                        "Anomaly Category": a_cat,
                        "Test Duration ( mins )": a_info["Test_Minutes"],
                        "Detection Rate (%)": f"{a_info['Detection_Rate_Pct']:.1f}%",
                        "Mean Anomaly Score": a_info["Mean_Anomaly_Score"],
                    }
                )
            st.dataframe(pd.DataFrame(rec_rows), width="stretch", hide_index=True)

        if eval_summary and "cyber_metrics" in eval_summary:
            st.markdown("**Anomaly Detector Model Comparison:**")
            cy_rows = []
            for cm_name, cm_vals in eval_summary["cyber_metrics"].items():
                cy_rows.append(
                    {
                        "Detector": cm_name,
                        "Precision": f"{cm_vals['Precision']:.4f}",
                        "Recall": f"{cm_vals['Recall']:.4f}",
                        "F1-Score": f"{cm_vals['F1_Score']:.4f}",
                        "ROC-AUC": f"{cm_vals['ROC_AUC']:.4f}",
                    }
                )
            st.dataframe(pd.DataFrame(cy_rows), width="stretch", hide_index=True)

# =============================================================================
# TAB 4: MODULE 4 - INTEGRATED ALERT SYSTEM & SCENARIOS A / B / C
# =============================================================================
with tab4:
    st.subheader("Module 4: Integrated Dual-Layer Alert System & Decision Matrix")
    st.markdown(
        "Combines **Layer 1 (Predictive Maintenance)** and **Layer 2 (Cyber/Measurement Integrity)** so operators can distinguish "
        "a genuine mechanical degradation from a corrupted or manipulated sensor stream."
    )

    sc_col1, sc_col2, sc_col3 = st.columns(3)
    with sc_col1:
        st.info(
            "**Scenario A: Predicted Equipment Failure**\n\n"
            "- **Indicators**: THP decreases, Gas flow declines, Pump motor current increases.\n"
            "- **Layer 1 Output**: High Failure Risk (75–98%).\n"
            "- **Layer 2 Output**: Normal sensor integrity (<30).\n"
            "- **Decision**: Prioritise mechanical inspection & workover planning."
        )
    with sc_col2:
        st.warning(
            "**Scenario B: Measurement-Integrity Issue**\n\n"
            "- **Indicators**: THP suddenly freezes constant while CHP continues changing; packet loss spikes.\n"
            "- **Layer 1 Output**: Low Failure Risk.\n"
            "- **Layer 2 Output**: High Anomaly Score (>85 — Sensor Freezing).\n"
            "- **Decision**: Verify sensor, wiring, calibration & RTU communication."
        )
    with sc_col3:
        st.error(
            "**Scenario C: Combined High Risk + Sensor Anomaly**\n\n"
            "- **Indicators**: High ML failure risk AND abnormal/spoofed sensor behavior detected simultaneously.\n"
            "- **Layer 1 & 2 Outputs**: Both layers trigger alerts.\n"
            "- **Decision**: **CRITICAL** — Verify measurement reliability FIRST before acting on failure prediction!"
        )

    st.markdown("#### 🔔 Five-Tier Integrated Alert Structure & 60-Day Distribution")
    alert_dist = eval_summary["alert_distribution"] if eval_summary and "alert_distribution" in eval_summary else {}
    alert_ref_df = pd.DataFrame(
        [
            ("Normal", "Parameters are within expected operating behaviour", "Continue routine monitoring", alert_dist.get("Normal", 0)),
            ("Maintenance warning", "Abnormal operating trend detected (Risk 35–65%)", "Schedule engineering assessment", alert_dist.get("Maintenance warning", 0)),
            ("High failure risk", "ML model predicts elevated downtime risk (>65%)", "Prioritise inspection and maintenance planning", alert_dist.get("High failure risk", 0)),
            ("Measurement anomaly", "Sensor data are inconsistent, frozen, drifting, or spoofed", "Verify instrument, calibration and telemetry integrity", alert_dist.get("Measurement anomaly", 0)),
            ("Critical operational warning", "Multiple serious indicators (High Failure Risk + Cyber Anomaly)", "Verify measurement reliability first; escalate under approved procedures", alert_dist.get("Critical operational warning", 0)),
        ],
        columns=["Alert Type", "Meaning", "Suggested Operator Response", "Total Minutes (60 Days)"],
    )
    st.dataframe(alert_ref_df, width="stretch", hide_index=True)

    st.markdown("#### 📜 Active Window Alert Log (Non-Normal Events in Selected Window)")
    alerts_in_win = window_df[window_df["integrated_alert_level"] != "Normal"][
        [
            "timestamp",
            "integrated_alert_level",
            "operational_status",
            "predicted_failure_risk_pct",
            "anomaly_category",
            "cyber_anomaly_score",
            "tubing_head_pressure_psi",
            "casing_head_pressure_psi",
            "downhole_gauge_pressure_psi",
            "pump_torque_current_amps",
        ]
    ]
    st.dataframe(alerts_in_win.head(200), width="stretch", hide_index=True)

# =============================================================================
# TAB 5: REAL-WORLD CASE STUDIES (OISD WORKOVER BLOWOUT, DEEPSEA BOLLSTA, OIL FIRE)
# =============================================================================
with tab5:
    st.subheader("🏗️ Real-Life Oil & Gas Incident Mapping & Decision-Support Demonstrations")
    st.caption(
        "Demonstrates how the Cyber-Secure Predictive Maintenance framework supports early warning and engineering review across the three case studies in your report."
    )

    cs_sub1, cs_sub2, cs_sub3, cs_sub4 = st.tabs(
        [
            "🔥 Case Study 2 (Main): OISD Workover Rig Blowout (2026)",
            "🌊 Case Study 3: Equinor Deepsea Bollsta (2025)",
            "🏭 Case Study 1: Oil India Tank Farm Fire (2026)",
            "⚖️ Comparative Matrix & Research Boundaries",
        ]
    )

    # --- Case Study 2: OISD Onshore Workover Rig Blowout ---
    with cs_sub1:
        st.markdown("### Case Study 2: Gas Blowout at Onshore Workover Rig, India (OISD/CS/2025-26/E&P/21 — 4 Feb 2026)")
        st.markdown(
            "**Incident Summary**: Uncontrolled gas flow occurred immediately after conventional perforation. "
            "The production BOP blind ram could not seal because the wireline string was still in the well and no shear ram was installed."
        )

        c_oisd1, c_oisd2 = st.columns([1.1, 1.2])
        with c_oisd1:
            st.markdown("#### 🧪 Interactive Pre-Perforation Readiness & Hydrostatic Overbalance Check")
            well_depth_m = st.number_input("Target Perforation Vertical Depth h (m)", value=2200.0, step=50.0)
            reservoir_press_psi = st.number_input("Estimated Formation Pore Pressure (PSI)", value=3150.0, step=50.0)
            drilling_mud_sg = st.slider("Final Drilling Mud Specific Gravity (SG)", 1.00, 1.40, 1.18, 0.01)
            completion_fluid_sg = st.slider("Perforation Completion Fluid Specific Gravity (SG)", 0.95, 1.35, 1.02, 0.01)

            gto_vs_offset_conflict = st.checkbox("Offset-well data & drilling gas influxes conflict with GTO ('Oil-only')", value=True)
            cbl_vdl_poor = st.checkbox("CBL-VDL Log indicates poor cement bonding across zone", value=True)
            bop_shear_ram_missing = st.checkbox("BOP Stack missing Shear Ram verification for wireline operation", value=True)
            trip_tank_isolated = st.checkbox("Trip Tank isolated during perforation (OISD-STD-174 violation)", value=True)

            # Calculate Hydrostatic Pressure P_h = rho * g * h (in PSI: SG * 1000 * 9.81 * h / 6894.76)
            ph_drilling_psi = drilling_mud_sg * 1000.0 * 9.81 * well_depth_m / 6894.76
            ph_completion_psi = completion_fluid_sg * 1000.0 * 9.81 * well_depth_m / 6894.76
            overbalance_psi = ph_completion_psi - reservoir_press_psi

        with c_oisd2:
            st.markdown("#### 🚨 Pre-Operation Engineering Review Output")
            warnings_oisd = []
            if gto_vs_offset_conflict:
                warnings_oisd.append("Conflicting Geological Info: Offset well & historical drilling records show gas influxes despite oil-only GTO.")
            if cbl_vdl_poor:
                warnings_oisd.append("Cement Bond Concern: CBL-VDL indicates uncertain zonal isolation — barrier review required.")
            if overbalance_psi < 150.0:
                warnings_oisd.append(
                    f"Hydrostatic Underbalance Risk: Completion fluid Ph ({ph_completion_psi:.0f} PSI) drops {ph_drilling_psi - ph_completion_psi:.0f} PSI below drilling mud ({ph_drilling_psi:.0f} PSI); net overbalance is {overbalance_psi:+.0f} PSI!"
                )
            if bop_shear_ram_missing:
                warnings_oisd.append("BOP Readiness Gap: Shear ram unavailable to cut wireline in emergency shut-in.")
            if trip_tank_isolated:
                warnings_oisd.append("Monitoring Loss: Trip tank isolated — active well-volume influx tracking unavailable.")

            if warnings_oisd:
                st.error("WELL STATUS: HIGH OPERATIONAL RISK — ENGINEERING REVIEW REQUIRED BEFORE PERFORATION")
                for idx_w, w_msg in enumerate(warnings_oisd, 1):
                    st.markdown(f"**{idx_w}.** ⚠️ {w_msg}")
            else:
                st.success("WELL STATUS: PRE-PERFORATION CHECKS VERIFIED — ADEQUATE HYDROSTATIC OVERBALANCE & BARRIERS")

            st.latex(r"P_h = \rho g h \implies P_{h,\text{mud}} = " + f"{ph_drilling_psi:.0f}\\text{{ PSI}}, \\quad P_{{h,\\text{{completion}}}} = {ph_completion_psi:.0f}\\text{{ PSI}}")

    # --- Case Study 3: Deepsea Bollsta ---
    with cs_sub2:
        st.markdown("### Case Study 3: Equinor Deepsea Bollsta Well-Control Incident, Norway (23 Sep 2025 / Havtil Report May 2026)")
        st.markdown(
            "**Incident Summary**: During permanent plugging & abandonment (P&A) when cutting 13 3/8-inch casing at 510 m, "
            "~930 kg of gas and water released onto the rig due to outer barrier failure, faulty logging calibration, unused differential-pressure (ΔP) data, and poor ΔP gauge maintenance."
        )
        cb1, cb2 = st.columns(2)
        with cb1:
            st.markdown("#### 🔎 Deepsea Bollsta Measurement-Integrity & Calibration Monitor")
            dp_gauge_overdue = st.checkbox("Differential-Pressure (ΔP) Gauge Calibration Overdue", value=True)
            cbl_cal_fault = st.checkbox("13 3/8-inch Casing Logging Tool QA/Calibration Unverified", value=True)
            dp_mismatch = st.checkbox("Differential Pressure (ΔP = P1 - P2) Inconsistent with Annulus Trend", value=True)
            outer_barrier_unverified = st.checkbox("Outer Well Barrier Pressure-Test Verification Incomplete", value=True)
        with cb2:
            st.markdown("#### 📋 Dashboard System Response (Per PDF p. 20)")
            if any([dp_gauge_overdue, cbl_cal_fault, dp_mismatch, outer_barrier_unverified]):
                st.warning("WELL STATUS: MEASUREMENT INTEGRITY & BARRIER WARNING")
                st.markdown(
                    r"""
1. **Flagged Measurement**: Differential-pressure ($\Delta P = P_1 - P_2$) reading is inconsistent with related pressure measurements.
2. **Calibration Status**: Logging & $\Delta P$ gauge calibration/maintenance records are overdue.
3. **Barrier Alert**: Outer well-barrier verification incomplete prior to casing cut.
4. **Recommendation**: Perform independent instrument calibration and barrier verification before relying on affected logging/pressure data.
"""
                )
            else:
                st.success("All differential-pressure gauges calibrated and outer barrier verified.")

    # --- Case Study 1: Oil India Tank Farm Fire ---
    with cs_sub3:
        st.markdown("### Case Study 1: Oil India Limited Intermediate Tank Farm Fire, Tengakhat Assam (6 Nov 2026)")
        st.markdown(
            "**Incident Summary**: Fire occurred during maintenance on an Indirect Bath Heater (IDBH) isolated since 4 Nov 2026. "
            "Demonstrates how the framework extends to surface production equipment alongside physical isolation and permit-to-work barriers."
        )
        idbh_df = pd.DataFrame(
            [
                ("Bath & Inlet/Outlet Temperature", "Identify abnormal heater temperature trends", "High-temperature deviation warning", "92.4 °C (Trending +6.8 °C above baseline)"),
                ("Inlet / Outlet Pressure", "Detect unusual pressure behavior during isolation", "Residual pressure anomaly", "18.5 PSI (Expected: 0 PSI isolated)"),
                ("Pump / Motor Vibration", "Monitor rotating equipment condition", "Abnormal vibration warning", "4.8 mm/s RMS (Elevated)"),
                ("Sensor Status", "Verify measurements are actively updating", "Frozen sensor warning", "Active (1-min polling verified)"),
                ("Maintenance & Isolation History", "Track overdue inspections & physical LOTO verification", "Physical isolation verification required", "Isolated 4 Nov 2026 — Verify zero residual energy"),
            ],
            columns=["Surface Parameter", "Monitoring Function", "Example Alert", "Simulated IDBH Status"],
        )
        st.dataframe(idbh_df, width="stretch", hide_index=True)

    # --- Comparative Matrix & Research Boundaries ---
    with cs_sub4:
        st.markdown("#### 📊 Comparative Analysis of the Three Case Studies (PDF Section 5)")
        comp_df = pd.DataFrame(
            [
                ("Year & Operation", "2026 — Surface Equipment Maintenance", "2026 — Onshore Well Perforation", "2025 — Offshore Well P&A (Casing Cut)"),
                ("Main Incident", "Indirect Bath Heater (IDBH) Fire", "Uncontrolled Gas Blowout", "Uncontrolled Gas (930 kg) & Water Release"),
                ("Main Technical Concern", "Exact ignition cause under inquiry; maintenance/isolation risk", "Conflicting GTO/offset data, lighter completion fluid, no BOP shear ram, isolated trip tank", "Outer barrier failure, faulty logging calibration, unused ΔP data, poor gauge maintenance"),
                ("Predictive Maintenance Role", "Surface heater temperature, pressure, vibration & inspection tracking", "Well pressure/flow trends, fluid-density overbalance & BOP readiness tracking", "Well-barrier integrity, ΔP trending & gauge calibration/maintenance tracking"),
                ("Cyber / Anomaly Detection Role", "Heater sensor integrity & frozen-value detection", "Well-monitoring sensor freeze, drift, spike & FDI detection", "Logging & differential-pressure measurement consistency verification"),
            ],
            columns=["Comparison Parameter", "Case 1: OIL Tank Farm Fire", "Case 2: OISD Workover Blowout", "Case 3: Deepsea Bollsta"],
        )
        st.dataframe(comp_df, width="stretch", hide_index=True)

        st.markdown("#### ⚖️ Claims, Boundaries & Research Limitations (PDF Section 8)")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.success(
                "**✅ What This Prototype CAN Claim**\n"
                "- Identifies abnormal multivariate patterns in historical/SCADA well data.\n"
                "- Estimates probability/risk of impending downtime using validated ML models.\n"
                "- Flags suspicious, frozen, drifting, or physically inconsistent sensor readings.\n"
                "- Integrates well parameters, maintenance records, and dual-layer alerts into one decision-support dashboard."
            )
        with b_col2:
            st.error(
                "**🚫 What This Prototype Should NOT Claim**\n"
                "- Cannot guarantee prevention of blowouts or fires on its own.\n"
                "- Cannot confirm that every sensor anomaly is a malicious cyberattack (could be faulty wiring/calibration).\n"
                "- Cannot replace physical equipment inspections, CBL-VDL logging, or independent calibration.\n"
                "- Cannot replace physical safety barriers (BOP shear rams, LOTO isolation, gas testing, SIS)."
            )

# =============================================================================
# TAB 6: LIVE WHAT-IF & ANOMALY SIMULATOR
# =============================================================================
with tab6:
    st.subheader("🧪 Live Interactive Well-Parameter & Cyber-Anomaly Simulator")
    st.markdown(
        "Adjust the live wellhead parameters or inject one of the **5 anomaly types** below to test how the trained "
        "**Predictive Maintenance Model (Layer 1)** and **Cyber Anomaly Detector (Layer 2)** respond in real time."
    )

    sim_c1, sim_c2, sim_c3 = st.columns(3)
    with sim_c1:
        s_thp = st.slider("Tubing Head Pressure — THP (PSI)", 80.0, 600.0, float(snap_row["tubing_head_pressure_psi"]), 1.0)
        s_chp = st.slider("Casing Head Pressure — CHP (PSI)", 80.0, 350.0, float(snap_row["casing_head_pressure_psi"]), 1.0)
        s_bhp = st.slider("Downhole Pressure — BHP (PSI)", 350.0, 1450.0, float(snap_row["downhole_gauge_pressure_psi"]), 5.0)
        s_temp = st.slider("Downhole Temp (°F)", 170.0, 215.0, float(snap_row["downhole_temp_f"]), 0.5)
    with sim_c2:
        s_rpm = st.slider("ESP Pump RPM", 0.0, 4600.0, float(snap_row["pump_rpm"]), 10.0)
        s_curr = st.slider("Pump Motor Current (Amps)", 0.0, 95.0, float(snap_row["pump_torque_current_amps"]), 0.5)
        s_wtr = st.slider("Water Flow Rate (BPD)", 0.0, 1350.0, float(snap_row["water_rate_bpd"]), 5.0)
        s_gas = st.slider("Gas Flow Rate (MSCFD)", 0.0, 520.0, float(snap_row["gas_rate_mscfd"]), 2.0)
    with sim_c3:
        s_wlevel = st.slider("Annular Water Level (ft)", 300.0, 700.0, float(snap_row["water_level_ft"]), 5.0)
        s_choke = st.slider("Surface Choke Opening (%)", 0.0, 100.0, float(snap_row["choke_opening_pct"]), 1.0)
        s_modbus = st.selectbox("Modbus Function Code", [3, 5, 6, 16, 1, 8], index=0, help="3 = Normal Read Holding Registers; 5/6/16 = Write/Command Injection")
        s_ploss = st.slider("SCADA Network Packet Loss (%)", 0.0, 80.0, float(snap_row["packet_loss_pct"]), 0.5)
        s_freeze = st.checkbox("Simulate Sensor Freeze (THP Rolling Std = 0.0 while CHP varies)", value=False)

    if models_bundle is not None:
        thp_std_val = 0.001 if s_freeze else 2.2
        chp_std_val = 3.2 if s_freeze else 1.6

        sim_row_dict = {
            "tubing_head_pressure_psi": s_thp,
            "casing_head_pressure_psi": s_chp,
            "downhole_gauge_pressure_psi": s_bhp,
            "downhole_temp_f": s_temp,
            "pump_rpm": s_rpm,
            "pump_torque_current_amps": s_curr,
            "water_rate_bpd": s_wtr,
            "gas_rate_mscfd": s_gas,
            "water_level_ft": s_wlevel,
            "choke_opening_pct": s_choke,
            "modbus_function_code": s_modbus,
            "packet_loss_pct": s_ploss,
            "diff_pressure_bhp_thp_psi": s_bhp - s_thp,
            "diff_pressure_thp_chp_psi": s_thp - s_chp,
            "thp_roll_mean_15m": s_thp,
            "thp_roll_std_15m": thp_std_val,
            "chp_roll_std_15m": chp_std_val,
            "gas_rate_roll_mean_15m": s_gas,
            "current_roll_mean_15m": s_curr,
            "thp_roc_15m": s_thp - 280.0,
            "chp_roc_15m": s_chp - 150.0,
            "bhp_roc_15m": s_bhp - 1242.5,
            "current_roc_15m": s_curr - 58.0,
            "thp_baseline_dev": s_thp - 280.0,
            "chp_baseline_dev": s_chp - 150.0,
            "bhp_baseline_dev": s_bhp - 1242.5,
        }
        sim_df = pd.DataFrame([sim_row_dict])

        X_sim_pdm = models_bundle["pdm_scaler"].transform(sim_df[models_bundle["pdm_features"]])
        sim_fail_prob = float(models_bundle["best_pdm_model"].predict_proba(X_sim_pdm)[0, 1] * 100.0)

        X_sim_cyb = models_bundle["cyber_scaler"].transform(sim_df[models_bundle["cyber_features"]])
        raw_if = float(-models_bundle["iso_forest"].score_samples(X_sim_cyb)[0])
        sim_cyb_score = float(np.clip((raw_if - 0.42) / 0.28 * 100.0, 0.0, 100.0))
        if s_freeze:
            sim_cyb_score = max(sim_cyb_score, 89.0)
        if s_modbus != 3:
            sim_cyb_score = max(sim_cyb_score, 93.0)
        if abs(s_chp - 150.0) > 45.0:
            sim_cyb_score = max(sim_cyb_score, 80.0)
        if abs(s_thp - 280.0) > 110.0:
            sim_cyb_score = max(sim_cyb_score, 91.0)

        r1, r2, r3 = st.columns(3)
        r1.metric("Simulated Failure Risk (Layer 1)", f"{sim_fail_prob:.1f}%", "High Risk" if sim_fail_prob > 65 else ("Medium" if sim_fail_prob > 35 else "Low"))
        r2.metric("Simulated Cyber Anomaly Score (Layer 2)", f"{sim_cyb_score:.1f} / 100", "ANOMALY FLAGGED" if sim_cyb_score >= 60 else "Normal Integrity")
        if sim_fail_prob > 65 and sim_cyb_score >= 60:
            r3.error("🚨 CRITICAL WARNING (Scenario C): Verify sensor integrity before acting on failure prediction!")
        elif sim_cyb_score >= 60:
            r3.warning("🟣 MEASUREMENT ANOMALY (Scenario B): Inspect sensor / RTU / calibration!")
        elif sim_fail_prob > 65:
            r3.error("🔴 HIGH FAILURE RISK (Scenario A): Schedule preventive maintenance!")
        else:
            r3.success("🟢 NORMAL OPERATION: Both AI layers within safe limits.")
