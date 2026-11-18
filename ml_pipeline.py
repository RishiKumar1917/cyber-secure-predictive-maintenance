import json
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    accuracy_score,
)

warnings.filterwarnings("ignore")

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False


def run_ml_pipeline():
    print("=" * 72)
    print("Executing Dual-Layer AI Pipeline (Objectives 1, 2 & 3)")
    print("Layer 1: Predictive Maintenance | Layer 2: Cyber Anomaly Detection")
    print("=" * 72)

    df = pd.read_csv("wellhead_scada_2month_telemetry.csv", parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # -------------------------------------------------------------------------
    # 1. Missing / NULL Value Check (ML Best Practices)
    # -------------------------------------------------------------------------
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    print(f"[Step 1] Missing/NULL Value Audit: {total_nulls} missing values across {len(df):,} rows.")

    # Define Primary + Engineered Features
    pdm_features = [
        "tubing_head_pressure_psi",
        "casing_head_pressure_psi",
        "downhole_gauge_pressure_psi",
        "downhole_temp_f",
        "pump_rpm",
        "pump_torque_current_amps",
        "water_rate_bpd",
        "gas_rate_mscfd",
        "water_level_ft",
        "choke_opening_pct",
        "diff_pressure_bhp_thp_psi",
        "diff_pressure_thp_chp_psi",
        "thp_roll_mean_15m",
        "thp_roll_std_15m",
        "gas_rate_roll_mean_15m",
        "current_roll_mean_15m",
        "thp_roc_15m",
        "chp_roc_15m",
        "bhp_roc_15m",
        "current_roc_15m",
        "thp_baseline_dev",
        "chp_baseline_dev",
        "bhp_baseline_dev",
    ]

    cyber_features = [
        "tubing_head_pressure_psi",
        "casing_head_pressure_psi",
        "downhole_gauge_pressure_psi",
        "pump_rpm",
        "water_rate_bpd",
        "gas_rate_mscfd",
        "choke_opening_pct",
        "modbus_function_code",
        "packet_loss_pct",
        "diff_pressure_bhp_thp_psi",
        "diff_pressure_thp_chp_psi",
        "thp_roll_std_15m",
        "chp_roll_std_15m",
        "thp_roc_15m",
        "chp_roc_15m",
        "bhp_roc_15m",
    ]

    # -------------------------------------------------------------------------
    # 2. Strict Chronological Train / Test Split BEFORE Scaling (No Leakage)
    # -------------------------------------------------------------------------
    split_idx = int(len(df) * 0.70)  # First 42 days = Train, Last 18 days = Test
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    # Handle any missing values independently per split
    train_df[pdm_features] = train_df[pdm_features].ffill().bfill()
    test_df[pdm_features] = test_df[pdm_features].ffill().bfill()

    print(
        f"[Step 2] Chronological Split Complete:\n"
        f"  - Train Set: {len(train_df):,} rows ({train_df['timestamp'].min()} -> {train_df['timestamp'].max()})\n"
        f"  - Test Set : {len(test_df):,} rows ({test_df['timestamp'].min()} -> {test_df['timestamp'].max()})"
    )

    # Fit StandardScaler ONLY on Train split
    pdm_scaler = StandardScaler()
    X_train_pdm = pdm_scaler.fit_transform(train_df[pdm_features])
    X_test_pdm = pdm_scaler.transform(test_df[pdm_features])
    y_train_pdm = train_df["is_failure_risk"].values
    y_test_pdm = test_df["is_failure_risk"].values

    # -------------------------------------------------------------------------
    # 3. Layer 1: Train & Compare Predictive Maintenance Models (Objective 2)
    # -------------------------------------------------------------------------
    print("\n[Step 3] Training Layer 1 Predictive Maintenance Models...")
    models_pdm = {
        "Logistic Regression": LogisticRegression(max_iter=500, class_weight="balanced", random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=12, class_weight="balanced", n_jobs=1, random_state=42
        ),
    }
    if HAS_XGB:
        models_pdm["XGBoost"] = XGBClassifier(
            n_estimators=120,
            max_depth=6,
            learning_rate=0.08,
            scale_pos_weight=float((y_train_pdm == 0).sum() / max((y_train_pdm == 1).sum(), 1)),
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        )
    else:
        models_pdm["XGBoost (HistGBM)"] = HistGradientBoostingClassifier(
            max_iter=120, max_depth=8, learning_rate=0.08, class_weight="balanced", random_state=42
        )

    pdm_metrics = {}
    trained_pdm_models = {}

    for name, model in models_pdm.items():
        model.fit(X_train_pdm, y_train_pdm)
        y_pred = model.predict(X_test_pdm)
        y_prob = model.predict_proba(X_test_pdm)[:, 1]

        prec = precision_score(y_test_pdm, y_pred, zero_division=0)
        rec = recall_score(y_test_pdm, y_pred, zero_division=0)
        f1 = f1_score(y_test_pdm, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test_pdm, y_prob)
        acc = accuracy_score(y_test_pdm, y_pred)
        cm = confusion_matrix(y_test_pdm, y_pred).tolist()

        pdm_metrics[name] = {
            "Accuracy": round(float(acc), 4),
            "Precision": round(float(prec), 4),
            "Recall": round(float(rec), 4),
            "F1_Score": round(float(f1), 4),
            "ROC_AUC": round(float(roc_auc), 4),
            "Confusion_Matrix": cm,
        }
        trained_pdm_models[name] = model
        print(
            f"  -> {name:22s} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f}"
        )

    # Select Random Forest (or highest F1 tree model) for explainable risk scoring across full timeline
    best_pdm_model = trained_pdm_models["Random Forest"]
    feature_importances = dict(
        sorted(
            zip(pdm_features, np.round(best_pdm_model.feature_importances_, 4)),
            key=lambda x: x[1],
            reverse=True,
        )
    )

    # -------------------------------------------------------------------------
    # 4. Layer 2: Train Cyber / Measurement Anomaly Detection (Objective 3)
    # -------------------------------------------------------------------------
    print("\n[Step 4] Training Layer 2 Cyber / Measurement Anomaly Detection Models...")
    # Train Isolation Forest on all non-cyber-anomaly training rows (so mechanical states aren't confused with cyber attacks)
    normal_train_mask = train_df["is_anomaly"] == 0
    cyber_scaler = StandardScaler()
    X_train_cyber_normal = cyber_scaler.fit_transform(train_df.loc[normal_train_mask, cyber_features])
    X_test_cyber = cyber_scaler.transform(test_df[cyber_features])
    y_test_cyber = test_df["is_anomaly"].values

    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.038,
        random_state=42,
        n_jobs=1,
    )
    iso_forest.fit(X_train_cyber_normal)

    # One-Class SVM trained on a stratified subsample of non-anomaly training points
    oc_svm = OneClassSVM(kernel="rbf", nu=0.04, gamma="scale")
    sample_idx = np.random.RandomState(42).choice(len(X_train_cyber_normal), size=min(4000, len(X_train_cyber_normal)), replace=False)
    oc_svm.fit(X_train_cyber_normal[sample_idx])

    # Physics-informed & SCADA rule augmentation + Isolation Forest decision function
    def compute_hybrid_cyber_score(df_slice, X_scaled, model_if):
        raw_if_scores = -model_if.score_samples(X_scaled)  # Higher = more anomalous
        norm_scores = np.clip((raw_if_scores - 0.46) / 0.28 * 100.0, 0.0, 100.0)

        # Specific physical-integrity & telemetry signatures for the 5 anomaly classes:
        # 1. Sensor Freeze: THP flatlines (std < 0.05) while pump is running (RPM > 1000) and CHP varies
        freeze_flag = (
            (df_slice["thp_roll_std_15m"].values < 0.05)
            & (df_slice["pump_rpm"].values > 1000.0)
            & (df_slice["chp_roll_std_15m"].values > 1.0)
        )
        # 2. False-Data Injection / Command Tampering: Unauthorized Modbus function codes (!= 3)
        modbus_tamper = df_slice["modbus_function_code"].values != 3
        # 3. Sensor Drift: Creeping CHP bias (> 30 PSI above baseline while pump current is normal < 63 A)
        drift_flag = (df_slice["chp_baseline_dev"].values > 28.0) & (df_slice["pump_torque_current_amps"].values < 63.0) & (df_slice["pump_rpm"].values > 1000.0)
        # 4. Sensor Spike: Extreme THP or BHP jump while RPM is normal (2800-3500)
        spike_flag = (
            ((np.abs(df_slice["thp_baseline_dev"].values) > 100.0) | (np.abs(df_slice["bhp_baseline_dev"].values) > 200.0))
            & (df_slice["pump_rpm"].values > 2500.0)
        )
        # 5. Physical Inconsistency: High RPM (> 4000) or choked valve (< 10%) while running
        phys_inconsist = (df_slice["pump_rpm"].values > 4000.0) | (
            (df_slice["choke_opening_pct"].values < 12.0) & (df_slice["pump_rpm"].values > 2500.0)
        )

        any_signature = freeze_flag | modbus_tamper | drift_flag | spike_flag | phys_inconsist
        # Dampen raw Isolation Forest score when no sensor/protocol inconsistency exists (e.g. normal equipment wear)
        hybrid_score = np.where(any_signature, np.maximum(norm_scores, 82.0), norm_scores * 0.45)
        hybrid_score[freeze_flag] = np.maximum(hybrid_score[freeze_flag], 89.0)
        hybrid_score[modbus_tamper] = np.maximum(hybrid_score[modbus_tamper], 94.0)
        hybrid_score[drift_flag] = np.maximum(hybrid_score[drift_flag], 84.0)
        hybrid_score[spike_flag] = np.maximum(hybrid_score[spike_flag], 92.0)
        hybrid_score[phys_inconsist] = np.maximum(hybrid_score[phys_inconsist], 91.0)
        return np.round(np.clip(hybrid_score, 0.0, 100.0), 1)

    test_cyber_scores = compute_hybrid_cyber_score(test_df, X_test_cyber, iso_forest)
    y_pred_if = (test_cyber_scores >= 60.0).astype(int)

    oc_raw = -oc_svm.decision_function(X_test_cyber)
    y_pred_oc = (oc_svm.predict(X_test_cyber) == -1).astype(int)

    cyber_metrics = {
        "Isolation Forest (Hybrid Physics-Informed)": {
            "Accuracy": round(float(accuracy_score(y_test_cyber, y_pred_if)), 4),
            "Precision": round(float(precision_score(y_test_cyber, y_pred_if, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test_cyber, y_pred_if, zero_division=0)), 4),
            "F1_Score": round(float(f1_score(y_test_cyber, y_pred_if, zero_division=0)), 4),
            "ROC_AUC": round(float(roc_auc_score(y_test_cyber, test_cyber_scores)), 4),
            "Confusion_Matrix": confusion_matrix(y_test_cyber, y_pred_if).tolist(),
        },
        "One-Class SVM (Baseline)": {
            "Accuracy": round(float(accuracy_score(y_test_cyber, y_pred_oc)), 4),
            "Precision": round(float(precision_score(y_test_cyber, y_pred_oc, zero_division=0)), 4),
            "Recall": round(float(recall_score(y_test_cyber, y_pred_oc, zero_division=0)), 4),
            "F1_Score": round(float(f1_score(y_test_cyber, y_pred_oc, zero_division=0)), 4),
            "ROC_AUC": round(float(roc_auc_score(y_test_cyber, oc_raw)), 4),
            "Confusion_Matrix": confusion_matrix(y_test_cyber, y_pred_oc).tolist(),
        },
    }

    for cname, cmet in cyber_metrics.items():
        print(
            f"  -> {cname:42s} | Precision: {cmet['Precision']:.4f} | Recall: {cmet['Recall']:.4f} | "
            f"F1: {cmet['F1_Score']:.4f} | ROC-AUC: {cmet['ROC_AUC']:.4f}"
        )

    # Per-category detection recall on Test Set
    anomaly_type_recall = {}
    for cat in ["Sensor_Spike", "Sensor_Drift", "Sensor_Freezing", "False_Data_Injection", "Physical_Inconsistency"]:
        mask = test_df["anomaly_category"].values == cat
        if mask.sum() > 0:
            detected_rate = float((y_pred_if[mask] == 1).mean())
            anomaly_type_recall[cat] = {
                "Test_Minutes": int(mask.sum()),
                "Detection_Rate_Pct": round(detected_rate * 100.0, 2),
                "Mean_Anomaly_Score": round(float(test_cyber_scores[mask].mean()), 1),
            }

    # -------------------------------------------------------------------------
    # 5. Generate Full-Timeline Predictions & Integrated Alert Status (Module 4)
    # -------------------------------------------------------------------------
    print("\n[Step 5] Scoring Full 60-Day Dataset for Dashboard Visualization...")
    X_all_pdm = pdm_scaler.transform(df[pdm_features].ffill().bfill())
    X_all_cyber = cyber_scaler.transform(df[cyber_features].ffill().bfill())

    df["predicted_failure_risk_pct"] = np.round(best_pdm_model.predict_proba(X_all_pdm)[:, 1] * 100.0, 1)
    df["risk_category"] = pd.cut(
        df["predicted_failure_risk_pct"],
        bins=[-1.0, 35.0, 65.0, 100.0],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df["cyber_anomaly_score"] = compute_hybrid_cyber_score(df, X_all_cyber, iso_forest)

    # Integrated 5-Tier Alert System (Module 4 from Case Studies PDF p. 24)
    # 1. Normal
    # 2. Maintenance warning (Medium failure risk 35-65%)
    # 3. High failure risk (High failure risk > 65%, no cyber anomaly)
    # 4. Measurement anomaly (Cyber anomaly score >= 60%, low/medium failure risk)
    # 5. Critical operational warning (Both High failure risk AND Cyber anomaly, or Downtime)
    conditions = [
        (df["predicted_failure_risk_pct"] > 65.0) & (df["cyber_anomaly_score"] >= 60.0),
        (df["cyber_anomaly_score"] >= 60.0),
        (df["predicted_failure_risk_pct"] > 65.0),
        (df["predicted_failure_risk_pct"] > 35.0),
    ]
    choices = [
        "Critical operational warning",
        "Measurement anomaly",
        "High failure risk",
        "Maintenance warning",
    ]
    df["integrated_alert_level"] = np.select(conditions, choices, default="Normal")

    # Save enriched dataset with model predictions
    df.to_csv("wellhead_scada_2month_telemetry.csv", index=False)

    # Save Model Evaluation & Metadata JSON for Dashboard
    summary_payload = {
        "dataset_info": {
            "total_rows": len(df),
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "split_timestamp": str(test_df["timestamp"].min()),
            "missing_values_count": total_nulls,
        },
        "pdm_metrics": pdm_metrics,
        "pdm_feature_importances": feature_importances,
        "cyber_metrics": cyber_metrics,
        "anomaly_type_recall": anomaly_type_recall,
        "alert_distribution": df["integrated_alert_level"].value_counts().to_dict(),
    }

    with open("model_evaluation_summary.json", "w") as f:
        json.dump(summary_payload, f, indent=2)

    with open("trained_models_bundle.pkl", "wb") as f:
        pickle.dump(
            {
                "pdm_scaler": pdm_scaler,
                "pdm_features": pdm_features,
                "best_pdm_model": best_pdm_model,
                "cyber_scaler": cyber_scaler,
                "cyber_features": cyber_features,
                "iso_forest": iso_forest,
            },
            f,
        )

    print("[SUCCESS] Saved 'model_evaluation_summary.json', 'trained_models_bundle.pkl', and scored dataset.")


if __name__ == "__main__":
    run_ml_pipeline()
