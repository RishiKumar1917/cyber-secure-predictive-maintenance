import json
import pickle
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import numpy as np
import pandas as pd

PORT = 8505
BASE_DIR = Path(__file__).resolve().parent

print("=" * 72)
print("Loading Dataset & Trained Dual-Layer AI Models for AEGIS-WELL Server...")
print("=" * 72)

df = pd.read_csv(BASE_DIR / "wellhead_scada_2month_telemetry.csv")
with open(BASE_DIR / "model_evaluation_summary.json", "r", encoding="utf-8") as f:
    eval_summary = json.load(f)

with open(BASE_DIR / "trained_models_bundle.pkl", "rb") as f:
    models_bundle = pickle.load(f)

SCENARIO_PRESETS = {
    "scenario_a": {
        "id": "scenario_a",
        "name": "Scenario A: Pre-Failure Degradation",
        "badge": "MECHANICAL RISK",
        "color": "#ef4444",
        "desc": "Day 48: THP drops, gas/water flow declines, ESP motor current & downhole temp rise prior to pump trip.",
        "start_day": 48.0,
        "end_day": 49.0,
        "focus_idx": int(48 * 1440 + 18 * 60),
    },
    "scenario_b": {
        "id": "scenario_b",
        "name": "Scenario B: Sensor Freeze (DoS)",
        "badge": "MEASUREMENT ANOMALY",
        "color": "#a855f7",
        "desc": "Day 44: THP & BHP freeze flatline (zero variance) while CHP fluctuates and network packet loss spikes.",
        "start_day": 44.0,
        "end_day": 45.0,
        "focus_idx": int(44 * 1440 + 17.5 * 60),
    },
    "scenario_c": {
        "id": "scenario_c",
        "name": "Scenario C: Combined Failure + Cyber Attack",
        "badge": "CRITICAL DUAL ALERT",
        "color": "#f43f5e",
        "desc": "Day 56: High ML failure risk AND physically inconsistent sensor tampering occur simultaneously. Verify sensors first!",
        "start_day": 56.0,
        "end_day": 57.0,
        "focus_idx": int(56 * 1440 + 14 * 60),
    },
    "spike": {
        "id": "spike",
        "name": "Anomaly: Sensor Spike",
        "badge": "SPIKE ALERT",
        "color": "#f59e0b",
        "desc": "Day 43: Sudden extreme high/low pressure transient spikes injected into THP and BHP.",
        "start_day": 43.0,
        "end_day": 44.0,
        "focus_idx": int(43 * 1440 + 12 * 60),
    },
    "drift": {
        "id": "drift",
        "name": "Anomaly: Slow Sensor Drift",
        "badge": "DRIFT WARNING",
        "color": "#eab308",
        "desc": "Day 46: Stealthy +145 PSI creeping bias on Casing Head Pressure (CHP) while pump load stays normal.",
        "start_day": 46.0,
        "end_day": 47.0,
        "focus_idx": int(46 * 1440 + 13 * 60),
    },
    "fdi": {
        "id": "fdi",
        "name": "Anomaly: False-Data Injection (BHP)",
        "badge": "MODBUS TAMPER",
        "color": "#8b5cf6",
        "desc": "Day 51: Unauthorized Modbus Function 16 register write spoofs Downhole BHP to 420 PSI.",
        "start_day": 51.0,
        "end_day": 52.0,
        "focus_idx": int(51 * 1440 + 4.5 * 60),
    },
    "normal": {
        "id": "normal",
        "name": "Normal Baseline Operation",
        "badge": "NOMINAL",
        "color": "#10b981",
        "desc": "Day 45: Healthy artificial-lift ESP operation within diurnal pressure and flow envelopes.",
        "start_day": 45.0,
        "end_day": 46.0,
        "focus_idx": int(45 * 1440 + 12 * 60),
    },
}


def compute_snapshot_attribution(row):
    contribs = [
        {
            "name": "Pump Motor Current (Amps)",
            "key": "pump_torque_current_amps",
            "value": f"{row['pump_torque_current_amps']:.1f} A",
            "baseline": "58.0 A",
            "score": round(min(100.0, abs(row["pump_torque_current_amps"] - 58.0) / 18.0 * 100.0), 1),
        },
        {
            "name": "Tubing Head Pressure (THP)",
            "key": "tubing_head_pressure_psi",
            "value": f"{row['tubing_head_pressure_psi']:.1f} PSI",
            "baseline": "280.0 PSI",
            "score": round(min(100.0, abs(row["thp_baseline_dev"]) / 55.0 * 100.0), 1),
        },
        {
            "name": "Gas Flow Rate (MSCFD)",
            "key": "gas_rate_mscfd",
            "value": f"{row['gas_rate_mscfd']:.1f} MSCFD",
            "baseline": "320.0 MSCFD",
            "score": round(min(100.0, abs(row["gas_rate_mscfd"] - 320.0) / 85.0 * 100.0), 1),
        },
        {
            "name": "Downhole Temp (°F)",
            "key": "downhole_temp_f",
            "value": f"{row['downhole_temp_f']:.1f} °F",
            "baseline": "185.0 °F",
            "score": round(min(100.0, abs(row["downhole_temp_f"] - 185.0) / 11.0 * 100.0), 1),
        },
        {
            "name": "Water Flow Rate (BPD)",
            "key": "water_rate_bpd",
            "value": f"{row['water_rate_bpd']:.0f} BPD",
            "baseline": "850 BPD",
            "score": round(min(100.0, abs(row["water_rate_bpd"] - 850.0) / 210.0 * 100.0), 1),
        },
        {
            "name": "Differential Pressure ΔP (THP-CHP)",
            "key": "diff_pressure_thp_chp_psi",
            "value": f"{row['diff_pressure_thp_chp_psi']:.1f} PSI",
            "baseline": "130.0 PSI",
            "score": round(min(100.0, abs(row["diff_pressure_thp_chp_psi"] - 130.0) / 65.0 * 100.0), 1),
        },
        {
            "name": "Annular Water Level (ft)",
            "key": "water_level_ft",
            "value": f"{row['water_level_ft']:.0f} ft",
            "baseline": "450 ft",
            "score": round(min(100.0, abs(row["water_level_ft"] - 450.0) / 50.0 * 100.0), 1),
        },
    ]
    contribs.sort(key=lambda x: x["score"], reverse=True)
    return contribs


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Keep console clean

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            html_file = BASE_DIR / "dashboard.html"
            content = html_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)
            return

        if path == "/api/init":
            self._send_json(
                {
                    "eval_summary": eval_summary,
                    "presets": SCENARIO_PRESETS,
                    "total_rows": len(df),
                }
            )
            return

        if path == "/api/window":
            qs = parse_qs(parsed.query)
            start_day = float(qs.get("start_day", [48.0])[0])
            end_day = float(qs.get("end_day", [49.0])[0])
            focus_idx = int(qs.get("focus_idx", [int(48 * 1440 + 18 * 60)])[0])

            start_idx = max(0, int(start_day * 1440))
            end_idx = min(len(df), max(start_idx + 60, int(end_day * 1440)))

            win_slice = df.iloc[start_idx:end_idx]
            max_points = 360
            stride = max(1, len(win_slice) // max_points)
            plot_slice = win_slice.iloc[::stride]

            focus_idx = min(max(focus_idx, start_idx), end_idx - 1)
            snap_row = df.iloc[focus_idx]

            # Build alert log in window
            alert_rows = win_slice[win_slice["integrated_alert_level"] != "Normal"].iloc[::5].head(35)
            alerts_list = []
            for idx_val, r in alert_rows.iterrows():
                alerts_list.append(
                    {
                        "row_idx": int(idx_val),
                        "timestamp": str(r["timestamp"]),
                        "alert_level": str(r["integrated_alert_level"]),
                        "op_status": str(r["operational_status"]),
                        "failure_risk": float(r["predicted_failure_risk_pct"]),
                        "anomaly_cat": str(r["anomaly_category"]),
                        "cyber_score": float(r["cyber_anomaly_score"]),
                        "thp": float(r["tubing_head_pressure_psi"]),
                        "chp": float(r["casing_head_pressure_psi"]),
                        "bhp": float(r["downhole_gauge_pressure_psi"]),
                        "current": float(r["pump_torque_current_amps"]),
                    }
                )

            payload = {
                "window": {
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                    "focus_idx": focus_idx,
                    "indices": [int(i) for i in plot_slice.index],
                    "timestamps": plot_slice["timestamp"].astype(str).tolist(),
                    "thp": plot_slice["tubing_head_pressure_psi"].tolist(),
                    "chp": plot_slice["casing_head_pressure_psi"].tolist(),
                    "bhp": plot_slice["downhole_gauge_pressure_psi"].tolist(),
                    "temp": plot_slice["downhole_temp_f"].tolist(),
                    "rpm": plot_slice["pump_rpm"].tolist(),
                    "current": plot_slice["pump_torque_current_amps"].tolist(),
                    "water_rate": plot_slice["water_rate_bpd"].tolist(),
                    "gas_rate": plot_slice["gas_rate_mscfd"].tolist(),
                    "water_level": plot_slice["water_level_ft"].tolist(),
                    "choke": plot_slice["choke_opening_pct"].tolist(),
                    "dp_wellbore": plot_slice["diff_pressure_bhp_thp_psi"].tolist(),
                    "dp_surface": plot_slice["diff_pressure_thp_chp_psi"].tolist(),
                    "modbus": plot_slice["modbus_function_code"].tolist(),
                    "packet_loss": plot_slice["packet_loss_pct"].tolist(),
                    "failure_risk": plot_slice["predicted_failure_risk_pct"].tolist(),
                    "cyber_score": plot_slice["cyber_anomaly_score"].tolist(),
                },
                "snapshot": {
                    "row_idx": int(focus_idx),
                    "timestamp": str(snap_row["timestamp"]),
                    "thp": float(snap_row["tubing_head_pressure_psi"]),
                    "chp": float(snap_row["casing_head_pressure_psi"]),
                    "bhp": float(snap_row["downhole_gauge_pressure_psi"]),
                    "temp": float(snap_row["downhole_temp_f"]),
                    "rpm": float(snap_row["pump_rpm"]),
                    "current": float(snap_row["pump_torque_current_amps"]),
                    "water_rate": float(snap_row["water_rate_bpd"]),
                    "gas_rate": float(snap_row["gas_rate_mscfd"]),
                    "water_level": float(snap_row["water_level_ft"]),
                    "choke": float(snap_row["choke_opening_pct"]),
                    "modbus": int(snap_row["modbus_function_code"]),
                    "packet_loss": float(snap_row["packet_loss_pct"]),
                    "dp_wellbore": float(snap_row["diff_pressure_bhp_thp_psi"]),
                    "dp_surface": float(snap_row["diff_pressure_thp_chp_psi"]),
                    "thp_dev": float(snap_row["thp_baseline_dev"]),
                    "chp_dev": float(snap_row["chp_baseline_dev"]),
                    "bhp_dev": float(snap_row["bhp_baseline_dev"]),
                    "thp_std": float(snap_row["thp_roll_std_15m"]),
                    "chp_std": float(snap_row["chp_roll_std_15m"]),
                    "op_status": str(snap_row["operational_status"]),
                    "failure_risk": float(snap_row["predicted_failure_risk_pct"]),
                    "risk_category": str(snap_row["risk_category"]),
                    "anomaly_category": str(snap_row["anomaly_category"]),
                    "cyber_score": float(snap_row["cyber_anomaly_score"]),
                    "alert_level": str(snap_row["integrated_alert_level"]),
                    "attributions": compute_snapshot_attribution(snap_row),
                },
                "alerts": alerts_list,
            }
            self._send_json(payload)
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/simulate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

            s_thp = float(body.get("thp", 280.0))
            s_chp = float(body.get("chp", 150.0))
            s_bhp = float(body.get("bhp", 1242.5))
            s_temp = float(body.get("temp", 185.0))
            s_rpm = float(body.get("rpm", 3200.0))
            s_curr = float(body.get("current", 58.0))
            s_wtr = float(body.get("water_rate", 850.0))
            s_gas = float(body.get("gas_rate", 320.0))
            s_wlevel = float(body.get("water_level", 450.0))
            s_choke = float(body.get("choke", 80.0))
            s_modbus = int(body.get("modbus", 3))
            s_ploss = float(body.get("packet_loss", 0.2))
            s_freeze = bool(body.get("freeze", False))

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
            ml_fail_prob = float(models_bundle["best_pdm_model"].predict_proba(X_sim_pdm)[0, 1] * 100.0)

            # Smooth physics-coupled equipment stress score so individual slider movements also reflect immediately
            thp_stress = max(0.0, (265.0 - s_thp) * 1.1) if s_thp < 265.0 else max(0.0, (s_thp - 305.0) * 0.45)
            chp_stress = max(0.0, (s_chp - 168.0) * 0.7) if s_chp > 168.0 else max(0.0, (132.0 - s_chp) * 0.6)
            bhp_stress = max(0.0, (1180.0 - s_bhp) * 0.12) if s_bhp < 1180.0 else max(0.0, (s_bhp - 1310.0) * 0.25)
            curr_stress = max(0.0, (s_curr - 61.0) * 3.2) if s_curr > 61.0 else max(0.0, (50.0 - s_curr) * 1.8)
            gas_stress = max(0.0, (295.0 - s_gas) * 0.55) if s_gas < 295.0 else max(0.0, (s_gas - 365.0) * 0.35)
            rpm_stress = max(0.0, abs(s_rpm - 3200.0) * 0.045)

            physics_fail_score = min(99.5, thp_stress + curr_stress + gas_stress + rpm_stress * 0.6 + chp_stress * 0.4)
            sim_fail_prob = round(min(99.8, max(ml_fail_prob, physics_fail_score)), 1)

            X_sim_cyb = models_bundle["cyber_scaler"].transform(sim_df[models_bundle["cyber_features"]])
            raw_if = float(-models_bundle["iso_forest"].score_samples(X_sim_cyb)[0])
            norm_if = float(np.clip((raw_if - 0.46) / 0.28 * 100.0, 0.0, 100.0))

            # Continuous sensor & physical coupling mismatch score when individual sliders diverge
            expected_thp = 280.0 + (s_rpm - 3200.0) * 0.04
            thp_mismatch = abs(s_thp - expected_thp)
            chp_mismatch = abs(s_chp - 150.0)
            bhp_mismatch = abs(s_bhp - 1242.5)

            continuous_cyber = 0.0
            if thp_mismatch > 25.0:
                continuous_cyber = max(continuous_cyber, min(95.0, (thp_mismatch - 20.0) * 0.85))
            if chp_mismatch > 20.0 and s_curr < 63.0:
                continuous_cyber = max(continuous_cyber, min(92.0, (chp_mismatch - 15.0) * 1.1))
            if bhp_mismatch > 80.0:
                continuous_cyber = max(continuous_cyber, min(96.0, (bhp_mismatch - 50.0) * 0.22))

            freeze_flag = s_freeze
            modbus_tamper = s_modbus != 3
            drift_flag = (abs(s_chp - 150.0) > 28.0) and (s_curr < 63.0) and (s_rpm > 1000.0)
            spike_flag = (abs(s_thp - 280.0) > 65.0 or abs(s_bhp - 1242.5) > 150.0) and (s_rpm > 2500.0)
            phys_inconsist = (s_rpm > 3800.0) or (s_choke < 12.0 and s_rpm > 2500.0) or (thp_mismatch > 45.0 and abs(s_curr - 58.0) < 4.0)

            any_sig = freeze_flag or modbus_tamper or drift_flag or spike_flag or phys_inconsist
            sim_cyb_score = max(norm_if, continuous_cyber)
            detected_type = "Normal"
            if any_sig:
                sim_cyb_score = max(sim_cyb_score, 68.0)
            if phys_inconsist:
                detected_type = "Physical_Inconsistency"
            if drift_flag:
                sim_cyb_score = max(sim_cyb_score, 78.0)
                detected_type = "Sensor_Drift"
            if spike_flag:
                sim_cyb_score = max(sim_cyb_score, 88.0)
                detected_type = "Sensor_Spike"
            if freeze_flag:
                sim_cyb_score = max(sim_cyb_score, 91.0)
                detected_type = "Sensor_Freezing"
            if modbus_tamper:
                sim_cyb_score = max(sim_cyb_score, 95.0)
                detected_type = "False_Data_Injection"

            sim_cyb_score = round(min(100.0, max(0.0, sim_cyb_score)), 1)

            if sim_fail_prob > 65.0 and sim_cyb_score >= 60.0:
                alert_lvl = "Critical operational warning"
            elif sim_cyb_score >= 60.0:
                alert_lvl = "Measurement anomaly"
            elif sim_fail_prob > 65.0:
                alert_lvl = "High failure risk"
            elif sim_fail_prob > 35.0:
                alert_lvl = "Maintenance warning"
            else:
                alert_lvl = "Normal"

            self._send_json(
                {
                    "failure_risk": sim_fail_prob,
                    "risk_category": "High" if sim_fail_prob > 65 else ("Medium" if sim_fail_prob > 35 else "Low"),
                    "cyber_score": sim_cyb_score,
                    "detected_anomaly_type": detected_type,
                    "alert_level": alert_lvl,
                    "dp_wellbore": round(s_bhp - s_thp, 1),
                    "dp_surface": round(s_thp - s_chp, 1),
                    "attributions": compute_snapshot_attribution(sim_df.iloc[0]),
                }
            )
            return

        self.send_error(404, "Endpoint not found")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), DashboardRequestHandler)
    print(f"\n[READY] AEGIS-WELL SCADA & Dual-AI Command Center running at:")
    print(f"  -> Local URL  : http://localhost:{PORT}")
    server.serve_forever()
