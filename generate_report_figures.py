import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse
import numpy as np
import pandas as pd

OUT_DIR = Path("report_figures")
OUT_DIR.mkdir(exist_ok=True)

# Academic color palette
NAVY = "#0F2942"
BLUE = "#0284C7"
TEAL = "#0D9488"
AMBER = "#D97706"
CRIMSON = "#DC2626"
VIOLET = "#7C3AED"
SLATE_BG = "#F8FAFC"
BORDER_GRAY = "#CBD5E1"
TEXT_DARK = "#1E293B"
TEXT_MUTED = "#475569"

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Calibri"]
plt.rcParams["axes.edgecolor"] = BORDER_GRAY
plt.rcParams["axes.linewidth"] = 0.9


def draw_box(ax, x, y, w, h, title, body="", fc="#FFFFFF", ec=NAVY, title_color=NAVY, body_color=TEXT_MUTED, lw=1.6, title_fs=9.5, body_fs=8.0):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
    )
    ax.add_patch(box)
    if body:
        ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w / 2, y + h * 0.30, body, ha="center", va="center", fontsize=body_fs, color=body_color, zorder=4)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color=title_color, zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, color=NAVY, lw=1.6, label="", lx=None, ly=None):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=13),
        zorder=2
    )
    if label:
        tx = (x1 + x2) / 2 if lx is None else lx
        ty = (y1 + y2) / 2 if ly is None else ly
        ax.text(tx, ty, label, ha="center", va="center", fontsize=7.8, fontweight="bold",
                color=color, bbox=dict(boxstyle="round,pad=0.18", fc="#FFFFFF", ec="none", alpha=0.9), zorder=5)


def fig_1_1_research_methodology():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.955, "Structured 7-Stage Research Methodology Workflow", ha="center", va="center",
            fontsize=14, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.915, "Cyber-Secure Predictive Maintenance for Oil & Gas Wells (7th Semester Research Methodology)",
            ha="center", va="center", fontsize=9.5, color=TEXT_MUTED)

    stages = [
        ("Stage 1: Problem\nFormulation", "Identify single-layer PdM\nblind spot under faulty or\nspoofed SCADA sensors", "#EFF6FF", BLUE),
        ("Stage 2: Literature &\nStandards", "Review 6 AI/OT papers,\nNIST SP 800-82 Rev. 3,\nIEC 62443 & OISD-174", "#F0FDFA", TEAL),
        ("Stage 3: SCADA Data\nSynthesis", "Generate physics-informed\n60-day ESP telemetry\n(86,400 @ 1-min rows)", "#EFF6FF", NAVY),
        ("Stage 4: Feature\nEngineering", "Extract ΔP, 15-min\nrolling mean/std, ROC\n& baseline deviations", "#FEF3C7", AMBER),
        ("Stage 5: Chronological\nDual ML", "Train Days 1–42 (70%)\nTest Days 43–60 (30%)\nRF/HistGBM + Hybrid IF", "#F5F3FF", VIOLET),
        ("Stage 6: Case-Study\nReplay", "Reconstruct OISD, Deepsea\nBollsta & OIL Tank Farm\nincidents + fix toggles", "#FEF2F2", CRIMSON),
        ("Stage 7: Web Console &\nValidation", "Deploy custom dashboard\n(port 8505) & verify claims\nvs safety boundaries", "#ECFDF5", TEAL),
    ]

    # Top row: Stages 1 -> 2 -> 3 -> 4 (left to right)
    w, h = 0.205, 0.25
    xs_top = [0.03, 0.275, 0.52, 0.765]
    y_top = 0.57
    for idx in range(4):
        title, body, fc, ec = stages[idx]
        draw_box(ax, xs_top[idx], y_top, w, h, title, body, fc=fc, ec=ec, title_color=ec, title_fs=8.5, body_fs=7.2)
        if idx < 3:
            draw_arrow(ax, xs_top[idx] + w + 0.006, y_top + h / 2, xs_top[idx + 1] - 0.006, y_top + h / 2, color=NAVY)

    # Downward arrow from Stage 4 to Stage 5
    draw_arrow(ax, xs_top[3] + w / 2, y_top - 0.008, xs_top[3] + w / 2, 0.425, color=NAVY)

    # Bottom row: Stage 5 (right), Stage 6 (center), Stage 7 (left)
    xs_bot = [0.70, 0.39, 0.08]
    w_bot = 0.24
    y_bot = 0.16
    for idx_pos, st_idx in enumerate([4, 5, 6]):
        title, body, fc, ec = stages[st_idx]
        draw_box(ax, xs_bot[idx_pos], y_bot, w_bot, h, title, body, fc=fc, ec=ec, title_color=ec, title_fs=8.5, body_fs=7.2)

    draw_arrow(ax, xs_bot[0] - 0.006, y_bot + h / 2, xs_bot[1] + w_bot + 0.006, y_bot + h / 2, color=NAVY)
    draw_arrow(ax, xs_bot[1] - 0.006, y_bot + h / 2, xs_bot[2] + w_bot + 0.006, y_bot + h / 2, color=NAVY)

    # Iterative feedback loop dashed arrow from Stage 7 back up to Stage 1
    ax.annotate(
        "", xy=(0.135, y_top - 0.008), xytext=(0.135, y_bot + h + 0.008),
        arrowprops=dict(arrowstyle="-|>", color=TEXT_MUTED, lw=1.3, linestyle="--", mutation_scale=12)
    )
    ax.text(0.148, 0.485, "Validation & Boundary\nRefinement Loop", fontsize=7.5, color=TEXT_MUTED, style="italic")

    # Footer bar
    draw_box(ax, 0.03, 0.03, 0.94, 0.075,
             "Core Principle: Petroleum Knowledge -> Data Analytics -> Failure Prediction -> Cyber Detection -> Operator Review",
             fc=SLATE_BG, ec=BORDER_GRAY, title_color=NAVY, lw=1.1, title_fs=8.3)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_1_1_research_methodology_flow.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_3_1_system_architecture():
    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "End-to-End Dual-Layer System Architecture", ha="center", va="center",
            fontsize=14, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.922, "Parallel Operational Failure Prediction & SCADA/OT Measurement-Anomaly Detection",
            ha="center", va="center", fontsize=9.5, color=TEXT_MUTED)

    # Row 1: Data Acquisition
    draw_box(ax, 0.08, 0.77, 0.84, 0.11,
             "1. Wellhead, Downhole & SCADA Telemetry Layer (1-Minute Sampling)",
             "THP | CHP | Downhole BHP & Temp | ESP RPM & Motor Current | Gas & Water Rates | Water Level | Choke % | Modbus Function Code & Packet Loss",
             fc="#EFF6FF", ec=BLUE, title_color=NAVY, title_fs=10, body_fs=8.0)

    draw_arrow(ax, 0.5, 0.768, 0.5, 0.722, color=NAVY)

    # Row 2: Preprocessing & Feature Engineering
    draw_box(ax, 0.12, 0.59, 0.76, 0.125,
             "2. Preprocessing & Physics-Informed Feature Engineering (26 Features)",
             "Chronological Split (Days 1–42 Train / Days 43–60 Test) | Train-Only StandardScaler | ΔP_wellbore = BHP - THP | ΔP_surface = THP - CHP\n15-Min Rolling Mean & Std (Zero-Variance Freeze Check) | 15-Min Rate-of-Change (ROC) | Normal Baseline Deviations",
             fc="#FEF3C7", ec=AMBER, title_color="#92400E", title_fs=9.8, body_fs=7.8)

    # Split arrows to Parallel Layers
    draw_arrow(ax, 0.35, 0.588, 0.25, 0.515, color=CRIMSON)
    draw_arrow(ax, 0.65, 0.588, 0.75, 0.515, color=VIOLET)

    # Row 3: Two Parallel Intelligence Layers
    draw_box(ax, 0.04, 0.34, 0.43, 0.17,
             "3A. AI Layer 1: Predictive Maintenance",
             "Supervised Classifiers (LR, Decision Tree, Random Forest, HistGBM)\nTrained on Normal / Pre-Failure / Downtime / Workover states\nOutput: Failure Risk Score (0–100%) + Risk Category (Low/Med/High)\n+ Feature Importance & Parameter Deviation Attribution",
             fc="#FEF2F2", ec=CRIMSON, title_color="#991B1B", title_fs=9.8, body_fs=7.6)

    draw_box(ax, 0.53, 0.34, 0.43, 0.17,
             "3B. AI Layer 2: Cyber & Sensor Integrity",
             "Hybrid Unsupervised Isolation Forest (trained on anomaly-free rows)\n+ Physics & SCADA Rules (Modbus != 3, Zero-Std Freeze, ΔP Mismatch)\nOutput: Cyber Anomaly Score (0–100) + 5 Anomaly Classes\n(Spike, Slow Drift, Sensor Freeze, False-Data Injection, Physical Mismatch)",
             fc="#F5F3FF", ec=VIOLET, title_color="#5B21B6", title_fs=9.8, body_fs=7.6)

    # Converge arrows
    draw_arrow(ax, 0.25, 0.338, 0.38, 0.265, color=CRIMSON)
    draw_arrow(ax, 0.75, 0.338, 0.62, 0.265, color=VIOLET)

    # Row 4: 5-Tier Integrated Alert Matrix
    draw_box(ax, 0.12, 0.155, 0.76, 0.105,
             "4. Integrated 5-Tier Alert & Decision Fusion Engine",
             "Normal  |  Maintenance Warning  |  High Failure Risk (Scenario A)  |  Measurement Anomaly (Scenario B)  |  Critical Dual Warning (Scenario C)",
             fc="#F0FDFA", ec=TEAL, title_color="#115E59", title_fs=9.8, body_fs=7.9)

    draw_arrow(ax, 0.5, 0.153, 0.5, 0.108, color=NAVY)

    # Row 5: Dashboard & Operator Review
    draw_box(ax, 0.06, 0.02, 0.88, 0.085,
             "5. Custom SCADA Web Dashboard (http://localhost:8505) & Operator Decision Support",
             "Tab 1: Live Well Monitor & 6-Zone Digital Twin | Tab 2: Interactive Fault & Repair Simulator | Tab 3: Case-Study Replay Lab | Tab 4: ML Benchmarks",
             fc=NAVY, ec=NAVY, title_color="#FFFFFF", body_color="#CBD5E1", title_fs=9.5, body_fs=7.8)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_3_1_system_architecture_flow.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_3_2_decision_flowchart():
    fig, ax = plt.subplots(figsize=(11, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "Integrated Dual-Layer Alert & Operator Decision Flowchart", ha="center", va="center",
            fontsize=14, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.922, "Distinguishing Genuine Mechanical Degradation (Scenario A) from Sensor/SCADA Manipulation (Scenarios B & C)",
            ha="center", va="center", fontsize=9.2, color=TEXT_MUTED)

    # Input step
    draw_box(ax, 0.25, 0.80, 0.50, 0.09,
             "Evaluate 1-Minute Telemetry Snapshot",
             "Compute Layer 1 Failure Risk (R %) and Layer 2 Cyber Anomaly Score (C)",
             fc="#EFF6FF", ec=BLUE, title_color=NAVY, title_fs=9.6, body_fs=7.9)

    # Chain of checks on left, Alert actions on right
    checks = [
        ("Condition 1: R > 65% AND C >= 60 ?", "CRITICAL OPERATIONAL WARNING (Scenario C)",
         "Both degradation & sensor anomaly flagged!\nVerify sensor/RTU reliability FIRST before mechanical shut-in.",
         "#FEF2F2", CRIMSON),
        ("Condition 2: C >= 60 (and R <= 65%) ?", "MEASUREMENT INTEGRITY WARNING (Scenario B)",
         "Well pump stable; sensor/SCADA signal abnormal.\nInspect transmitter, calibration & Modbus logs (do not shut in blindly).",
         "#F5F3FF", VIOLET),
        ("Condition 3: R > 65% (and C < 60) ?", "HIGH FAILURE / DOWNTIME RISK (Scenario A)",
         "Sensors verified trustworthy; pump wear detected.\nPrioritise engineering inspection & workover planning.",
         "#FFF1F2", "#E11D48"),
        ("Condition 4: 35% < R <= 65% ?", "MAINTENANCE WARNING",
         "Early operating deviation detected (Risk 35–65%).\nSchedule preventive engineering assessment.",
         "#FEF3C7", AMBER),
        ("Otherwise (R <= 35% and C < 60)", "NORMAL OPERATION",
         "All well parameters & sensors within safe baseline.\nContinue automated telemetry monitoring.",
         "#ECFDF5", TEAL),
    ]

    y_vals = [0.64, 0.49, 0.34, 0.19, 0.04]
    h_box = 0.115
    draw_arrow(ax, 0.25, 0.80, 0.22, y_vals[0] + h_box, color=NAVY)

    for idx, (cond, tier, action, fc, ec) in enumerate(checks):
        yv = y_vals[idx]
        # Left condition box
        draw_box(ax, 0.04, yv, 0.36, h_box, cond, "", fc=SLATE_BG, ec=NAVY, title_color=NAVY, title_fs=8.8)
        # Right outcome box
        draw_box(ax, 0.49, yv, 0.47, h_box, tier, action, fc=fc, ec=ec, title_color=ec, title_fs=9.0, body_fs=7.5)
        # YES arrow horizontally
        draw_arrow(ax, 0.402, yv + h_box / 2, 0.488, yv + h_box / 2, color=ec, label="YES" if idx < 4 else "ALL OK")
        # NO arrow downwards
        if idx < 4:
            draw_arrow(ax, 0.22, yv - 0.002, 0.22, y_vals[idx + 1] + h_box + 0.002, color=TEXT_MUTED, label="NO", lx=0.185)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_3_2_decision_activity_flowchart.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def draw_actor(ax, cx, cy, label):
    # Head
    head = plt.Circle((cx, cy + 0.055), 0.018, fill=False, edgecolor=NAVY, lw=1.8, zorder=4)
    ax.add_patch(head)
    # Torso
    ax.plot([cx, cx], [cy + 0.037, cy - 0.015], color=NAVY, lw=1.8, zorder=4)
    # Arms
    ax.plot([cx - 0.022, cx + 0.022], [cy + 0.02, cy + 0.02], color=NAVY, lw=1.8, zorder=4)
    # Legs
    ax.plot([cx, cx - 0.018], [cy - 0.015, cy - 0.048], color=NAVY, lw=1.8, zorder=4)
    ax.plot([cx, cx + 0.018], [cy - 0.015, cy - 0.048], color=NAVY, lw=1.8, zorder=4)
    ax.text(cx, cy - 0.075, label, ha="center", va="top", fontsize=8.3, fontweight="bold", color=NAVY)


def fig_3_3_use_case():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.955, "System Use-Case & Actor Interaction Diagram", ha="center", va="center",
            fontsize=14, fontweight="bold", color=NAVY)

    # System Boundary
    boundary = FancyBboxPatch((0.23, 0.06), 0.54, 0.83, boxstyle="round,pad=0.01,rounding_size=0.02",
                              facecolor="#F8FAFC", edgecolor=BLUE, linewidth=2.0, linestyle="--", zorder=1)
    ax.add_patch(boundary)
    ax.text(0.50, 0.865, "AEGIS-WELL Cyber-Secure Predictive Maintenance Platform", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=BLUE)

    # Use Case Ellipses
    ucs = [
        (0.50, 0.77, "UC1: Monitor Live 6-Zone Well Digital Twin\n& 24-Hour Time-Series Replay", BLUE),
        (0.50, 0.64, "UC2: Inspect Failure Risk Score & Top\nContributing Petroleum Parameters", CRIMSON),
        (0.50, 0.51, "UC3: Audit SCADA Modbus Function Codes,\nPacket Loss & Sensor Freeze Integrity", VIOLET),
        (0.50, 0.38, "UC4: Inject Live Parameter Faults / Cyber\nAttacks & Click Parts to Repair", AMBER),
        (0.50, 0.25, "UC5: Replay Historical Case Studies\n(OISD, Bollsta, OIL) & Toggle Fixes", TEAL),
        (0.50, 0.13, "UC6: Evaluate Chronological ML Benchmarks\n& Confusion Matrix Metrics", NAVY),
    ]

    for ux, uy, label, col in ucs:
        ell = Ellipse((ux, uy), width=0.44, height=0.10, facecolor="#FFFFFF", edgecolor=col, linewidth=1.7, zorder=3)
        ax.add_patch(ell)
        ax.text(ux, uy, label, ha="center", va="center", fontsize=8.0, fontweight="bold", color=TEXT_DARK, zorder=4)

    # Actors
    draw_actor(ax, 0.09, 0.68, "Petroleum /\nProduction Engineer")
    draw_actor(ax, 0.09, 0.28, "Well-Control /\nSafety Supervisor")
    draw_actor(ax, 0.91, 0.48, "OT / SCADA\nSecurity Analyst")

    # Connections Left Actors
    for uy in [0.77, 0.64, 0.38]:
        ax.plot([0.125, 0.28], [0.68, uy], color=TEXT_MUTED, lw=1.3, zorder=2)
    for uy in [0.25, 0.13, 0.64]:
        ax.plot([0.125, 0.28], [0.28, uy], color=TEXT_MUTED, lw=1.3, zorder=2)

    # Connections Right Actor
    for uy in [0.77, 0.51, 0.38, 0.25, 0.13]:
        ax.plot([0.875, 0.72], [0.48, uy], color=TEXT_MUTED, lw=1.3, zorder=2)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_3_3_use_case_diagram.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_5_1_dataset_overview():
    df = pd.read_csv("wellhead_scada_2month_telemetry.csv")
    df["day"] = np.arange(len(df)) / 1440.0
    sub = df.iloc[::20].copy()  # downsample for crisp plotting

    fig, axes = plt.subplots(3, 1, figsize=(11.5, 7.6), sharex=True)
    fig.patch.set_facecolor("#FFFFFF")

    # Subplot 1: THP & CHP
    axes[0].plot(sub["day"], sub["tubing_head_pressure_psi"], color=BLUE, lw=1.1, label="Tubing Head Pressure (THP, psi)")
    axes[0].plot(sub["day"], sub["casing_head_pressure_psi"], color=AMBER, lw=1.1, label="Casing Head Pressure (CHP, psi)")
    axes[0].axvline(42, color="#000000", ls="--", lw=1.3, label="Train/Test Split (Day 42)")
    axes[0].set_ylabel("Pressure (psi)", fontweight="bold", fontsize=9)
    axes[0].set_title("60-Day Multivariate Wellhead SCADA Dataset (86,400 Minutes) & Dual-AI Scores", fontweight="bold", color=NAVY, fontsize=12)
    axes[0].legend(loc="upper right", fontsize=8, ncol=3)
    axes[0].grid(alpha=0.25)

    # Subplot 2: Downhole BHP & Motor Current
    ax2_r = axes[1].twinx()
    l1, = axes[1].plot(sub["day"], sub["downhole_gauge_pressure_psi"], color=TEAL, lw=1.1, label="Downhole BHP (psi)")
    l2, = ax2_r.plot(sub["day"], sub["pump_torque_current_amps"], color=CRIMSON, lw=1.0, alpha=0.85, label="ESP Motor Current (Amps)")
    axes[1].axvline(42, color="#000000", ls="--", lw=1.3)
    axes[1].set_ylabel("BHP (psi)", fontweight="bold", fontsize=9, color=TEAL)
    ax2_r.set_ylabel("Current (Amps)", fontweight="bold", fontsize=9, color=CRIMSON)
    axes[1].legend([l1, l2], [l1.get_label(), l2.get_label()], loc="lower left", fontsize=8, ncol=2)
    axes[1].grid(alpha=0.25)

    # Subplot 3: Dual-AI Outputs
    axes[2].plot(sub["day"], sub["predicted_failure_risk_pct"], color=CRIMSON, lw=1.2, label="Layer 1: Predicted Failure Risk (%)")
    axes[2].plot(sub["day"], sub["cyber_anomaly_score"], color=VIOLET, lw=1.1, alpha=0.9, label="Layer 2: Cyber Anomaly Score (0–100)")
    axes[2].axvline(42, color="#000000", ls="--", lw=1.3)
    axes[2].text(21, 88, "TRAINING SPLIT (Days 1–42 | 60,479 rows)", ha="center", fontsize=8.5, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.25", fc="#EFF6FF", ec=BLUE))
    axes[2].text(51, 88, "UNSEEN TEST (Days 43–60 | 25,921 rows)", ha="center", fontsize=8.5, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.25", fc="#FEF3C7", ec=AMBER))
    axes[2].set_ylabel("AI Score", fontweight="bold", fontsize=9)
    axes[2].set_xlabel("Timeline (Days across 2-Month Telemetry Window: 2026-07-01 to 2026-08-29)", fontweight="bold", fontsize=9.5)
    axes[2].set_ylim(-5, 108)
    axes[2].set_xlim(0, 60)
    axes[2].legend(loc="center left", fontsize=8)
    axes[2].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_5_1_dataset_telemetry_overview.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_6_1_pdm_benchmark():
    with open("model_evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    pdm = summary["pdm_metrics"]
    models = list(pdm.keys())
    metrics = ["Precision", "Recall", "F1_Score", "ROC_AUC"]
    labels_m = ["Precision", "Recall", "F1-Score", "ROC-AUC"]
    colors = [BLUE, TEAL, AMBER, VIOLET]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0), gridspec_kw={"width_ratios": [1.15, 1.0]})
    fig.patch.set_facecolor("#FFFFFF")

    x = np.arange(len(models))
    width = 0.19
    for idx, (m_key, m_lbl, col) in enumerate(zip(metrics, labels_m, colors)):
        vals = [pdm[mod][m_key] for mod in models]
        bars = ax1.bar(x + (idx - 1.5) * width, vals, width, label=m_lbl, color=col, edgecolor="#FFFFFF", lw=0.6)
        for b in bars:
            hv = b.get_height()
            ax1.text(b.get_x() + b.get_width() / 2, hv + 0.0015, f"{hv:.3f}", ha="center", va="bottom",
                     fontsize=6.8, rotation=90, fontweight="bold", color=TEXT_DARK)

    ax1.set_ylim(0.93, 1.018)
    ax1.set_xticks(x)
    ax1.set_xticklabels(["Logistic\nRegression", "Decision\nTree", "Random\nForest", "HistGBM\n(XGBoost-Style)"], fontsize=8.5, fontweight="bold")
    ax1.set_ylabel("Score (Chronological Test Set)", fontweight="bold", fontsize=9)
    ax1.set_title("Layer 1: Predictive Maintenance Model Comparison", fontweight="bold", color=NAVY, fontsize=10.5)
    ax1.legend(loc="lower right", fontsize=8, framealpha=0.95)
    ax1.grid(axis="y", alpha=0.25)

    # Right panel: Top 10 Feature Importance
    fi = list(summary["pdm_feature_importances"].items())[:10]
    fi_names = [k for k, _ in reversed(fi)]
    fi_vals = [v for _, v in reversed(fi)]

    bars2 = ax2.barh(fi_names, fi_vals, color=BLUE, edgecolor=NAVY, lw=0.6)
    for b in bars2:
        wv = b.get_width()
        ax2.text(wv + 0.003, b.get_y() + b.get_height() / 2, f"{wv:.4f}", va="center", ha="left", fontsize=7.5, fontweight="bold", color=TEXT_DARK)
    ax2.set_xlim(0, max(fi_vals) * 1.22)
    ax2.set_xlabel("Gini Feature Importance (Random Forest)", fontweight="bold", fontsize=9)
    ax2.set_title("Top 10 Predictive Features Driving Failure Risk", fontweight="bold", color=NAVY, fontsize=10.5)
    ax2.tick_params(axis="y", labelsize=8)
    ax2.grid(axis="x", alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_6_1_pdm_benchmark_and_importance.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_cm(ax, cm, title, cmap_color):
    cm_arr = np.array(cm)
    ax.imshow(cm_arr, cmap=cmap_color, alpha=0.85)
    labels = [["TN", "FP"], ["FN", "TP"]]
    for r in range(2):
        for c in range(2):
            val = cm_arr[r, c]
            txt_col = "#FFFFFF" if val > cm_arr.max() * 0.45 else TEXT_DARK
            ax.text(c, r, f"{labels[r][c]}\n{val:,}", ha="center", va="center",
                    fontsize=9.5, fontweight="bold", color=txt_col)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pred Normal", "Pred Positive"], fontsize=8)
    ax.set_yticklabels(["Actual Normal", "Actual Positive"], fontsize=8)
    ax.set_title(title, fontsize=9.8, fontweight="bold", color=NAVY)


def fig_6_2_confusion_and_recall():
    with open("model_evaluation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12.8, 4.3), gridspec_kw={"width_ratios": [1, 1, 1.35]})
    fig.patch.set_facecolor("#FFFFFF")

    plot_cm(ax1, summary["pdm_metrics"]["Random Forest"]["Confusion_Matrix"],
            "Layer 1: Random Forest\n(Precision 1.000 | Recall 0.968)", "Blues")
    plot_cm(ax2, summary["cyber_metrics"]["Isolation Forest (Hybrid Physics-Informed)"]["Confusion_Matrix"],
            "Layer 2: Hybrid Isolation Forest\n(Precision 1.000 | Recall 0.947)", "Purples")

    rec = summary["anomaly_type_recall"]
    cats = [k.replace("_", "\n") for k in rec.keys()]
    rates = [v["Detection_Rate_Pct"] for v in rec.values()]
    bar_cols = [CRIMSON, AMBER, VIOLET, BLUE, TEAL]

    bars = ax3.bar(cats, rates, color=bar_cols, edgecolor=NAVY, lw=0.7)
    for b in bars:
        hv = b.get_height()
        ax3.text(b.get_x() + b.get_width() / 2, hv + 1.5, f"{hv:.1f}%", ha="center", va="bottom",
                 fontsize=8.2, fontweight="bold", color=TEXT_DARK)
    ax3.set_ylim(0, 115)
    ax3.set_ylabel("Test Detection Rate (%)", fontweight="bold", fontsize=9)
    ax3.set_title("Layer 2 Recall Across 5 Simulated Anomaly Types", fontsize=9.8, fontweight="bold", color=NAVY)
    ax3.tick_params(axis="x", labelsize=7.5)
    ax3.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_6_2_confusion_and_cyber_recall.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_7_1_case_studies():
    oisd_as = pd.read_csv("case_studies/oisd_as_happened.csv")
    oisd_fx = pd.read_csv("case_studies/oisd_with_fixes.csv")
    bol_as = pd.read_csv("case_studies/bollsta_as_happened.csv")
    bol_fx = pd.read_csv("case_studies/bollsta_with_fixes.csv")
    oil_as = pd.read_csv("case_studies/oil_idbh_as_happened.csv")
    oil_fx = pd.read_csv("case_studies/oil_idbh_with_fixes.csv")

    fig, axes = plt.subplots(3, 2, figsize=(11.8, 8.6))
    fig.patch.set_facecolor("#FFFFFF")

    # Row 0: OISD
    axes[0, 0].plot(oisd_as["t"], oisd_as["well_gain_bbl"], color=CRIMSON, lw=2.0, label="True Well Gain (bbl)")
    axes[0, 0].plot(oisd_as["t"], oisd_as["trip_tank_reading_bbl"], color=VIOLET, ls="--", lw=1.6, label="Trip Tank (Isolated=0)")
    axes[0, 0].axvline(75, color="#000", ls=":", lw=1.2, label="Perforation (T+75)")
    axes[0, 0].set_title("OISD Workover Rig — As Happened (BLOWOUT: 338.9 bbl)", fontsize=9.5, fontweight="bold", color=CRIMSON)
    axes[0, 0].set_ylabel("Volume (bbl)", fontsize=8.5, fontweight="bold")
    axes[0, 0].legend(fontsize=7.5, loc="upper left")
    axes[0, 0].grid(alpha=0.25)

    axes[0, 1].plot(oisd_fx["t"], oisd_fx["well_gain_bbl"], color=TEAL, lw=2.0, label="True Well Gain (0.0 bbl)")
    axes[0, 1].plot(oisd_fx["t"], oisd_fx["trip_tank_reading_bbl"], color=BLUE, ls="--", lw=1.6, label="Trip Tank Online (0.0 bbl)")
    axes[0, 1].axvline(75, color="#000", ls=":", lw=1.2, label="Perforation (T+75)")
    axes[0, 1].set_ylim(-2, 45)
    axes[0, 1].set_title("OISD Workover Rig — With All Fixes (SAFE: 0.0 bbl)", fontsize=9.5, fontweight="bold", color=TEAL)
    axes[0, 1].legend(fontsize=7.5, loc="upper right")
    axes[0, 1].grid(alpha=0.25)

    # Row 1: Bollsta
    ax_b1 = axes[1, 0].twinx()
    l1, = axes[1, 0].plot(bol_as["t"], bol_as["true_dp_psi"], color=BLUE, lw=1.8, label="True ΔP (psi)")
    l2, = axes[1, 0].plot(bol_as["t"], bol_as["gauge_dp_psi"], color=VIOLET, lw=1.8, label="Frozen Gauge ΔP (~9 psi)")
    l3, = ax_b1.plot(bol_as["t"], bol_as["cumulative_release_kg"], color=CRIMSON, lw=2.0, label="Gas Released (kg)")
    axes[1, 0].axvline(150, color="#000", ls=":", lw=1.2)
    axes[1, 0].set_title("Deepsea Bollsta — As Happened (RELEASE: 930 kg at T+150)", fontsize=9.5, fontweight="bold", color=CRIMSON)
    axes[1, 0].set_ylabel("ΔP (psi)", fontsize=8.5, fontweight="bold")
    ax_b1.set_ylabel("Release (kg)", fontsize=8.5, fontweight="bold", color=CRIMSON)
    axes[1, 0].legend([l1, l2, l3], [l1.get_label(), l2.get_label(), l3.get_label()], fontsize=7.3, loc="center left")
    axes[1, 0].grid(alpha=0.25)

    ax_b2 = axes[1, 1].twinx()
    r1, = axes[1, 1].plot(bol_fx["t"], bol_fx["trapped_annulus_psi"], color=AMBER, lw=1.8, label="Annulus Pressure Bled (psi)")
    r2, = ax_b2.plot(bol_fx["t"], bol_fx["cumulative_release_kg"], color=TEAL, lw=2.0, label="Gas Released (0.0 kg)")
    axes[1, 1].axvline(45, color=TEAL, ls="--", lw=1.2, label="Caught at T+45")
    ax_b2.set_ylim(-20, 1000)
    axes[1, 1].set_title("Deepsea Bollsta — With All Fixes (SAFE: Caught at T+45, 0 kg)", fontsize=9.5, fontweight="bold", color=TEAL)
    axes[1, 1].legend([r1, r2], [r1.get_label(), r2.get_label()], fontsize=7.5, loc="upper right")
    axes[1, 1].grid(alpha=0.25)

    # Row 2: Oil India IDBH
    ax_o1 = axes[2, 0].twinx()
    o1, = axes[2, 0].plot(oil_as["t"], oil_as["lel_pct"], color=AMBER, lw=1.8, label="Vapour (% LEL)")
    o2, = axes[2, 0].plot(oil_as["t"], oil_as["transmitter_pressure_psi"], color=VIOLET, lw=1.5, ls="--", label="PT Transmitter (0.0)")
    o3, = ax_o1.plot(oil_as["t"], oil_as["bath_temp_c"], color=CRIMSON, lw=2.0, label="Heater Temp (°C)")
    axes[2, 0].axvline(48, color="#000", ls=":", lw=1.2)
    axes[2, 0].set_title("Oil India IDBH (Hypothetical) — As Happened (FIRE at Hr 48)", fontsize=9.5, fontweight="bold", color=CRIMSON)
    axes[2, 0].set_ylabel("LEL (%) / PT (psi)", fontsize=8.5, fontweight="bold")
    axes[2, 0].set_xlabel("Time (Hours)", fontsize=8.5, fontweight="bold")
    ax_o1.set_ylabel("Temp (°C)", fontsize=8.5, fontweight="bold", color=CRIMSON)
    axes[2, 0].legend([o1, o2, o3], [o1.get_label(), o2.get_label(), o3.get_label()], fontsize=7.3, loc="upper left")
    axes[2, 0].grid(alpha=0.25)

    ax_o2 = axes[2, 1].twinx()
    p1, = axes[2, 1].plot(oil_fx["t"], oil_fx["lel_pct"], color=TEAL, lw=2.0, label="Vapour LEL (0.0%)")
    p2, = ax_o2.plot(oil_fx["t"], oil_fx["bath_temp_c"], color=BLUE, lw=1.8, label="Bath Temp Cooling (°C)")
    axes[2, 1].axvline(48, color="#000", ls=":", lw=1.2)
    axes[2, 1].set_ylim(-2, 30)
    ax_o2.set_ylim(0, 120)
    axes[2, 1].set_title("Oil India IDBH (Hypothetical) — With All Fixes (SAFE: 0% LEL)", fontsize=9.5, fontweight="bold", color=TEAL)
    axes[2, 1].set_xlabel("Time (Hours)", fontsize=8.5, fontweight="bold")
    axes[2, 1].legend([p1, p2], [p1.get_label(), p2.get_label()], fontsize=7.5, loc="upper right")
    axes[2, 1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_7_1_case_studies_replay_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_1_1_research_methodology()
    fig_3_1_system_architecture()
    fig_3_2_decision_flowchart()
    fig_3_3_use_case()
    fig_5_1_dataset_overview()
    fig_6_1_pdm_benchmark()
    fig_6_2_confusion_and_recall()
    fig_7_1_case_studies()
    print("[SUCCESS] Generated all 8 figures in report_figures/:")
    for p in sorted(OUT_DIR.glob("*.png")):
        print(f"  - {p.name} ({p.stat().st_size:,} bytes)")
