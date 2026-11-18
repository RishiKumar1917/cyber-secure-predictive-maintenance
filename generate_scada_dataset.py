import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_2month_wellhead_scada():
    print("=" * 72)
    print("Generating 2-Month (60 Days) Cyber-Secure Predictive Maintenance Dataset")
    print("Aligned with Project PPT (Objectives 1-4) & Oil & Gas Case Studies")
    print("=" * 72)

    np.random.seed(42)

    # 60 days at 1-minute intervals (86,400 rows)
    num_days = 60
    total_minutes = num_days * 24 * 60  # 86,400 data points
    start_time = datetime(2026, 7, 1, 0, 0, 0)

    timestamps = [start_time + timedelta(minutes=i) for i in range(total_minutes)]
    time_index = np.arange(total_minutes)

    # -------------------------------------------------------------------------
    # 1. Base Petroleum Parameters & Natural Reservoir/ESP Dynamics
    # -------------------------------------------------------------------------
    # Downhole gauge pressure (BHP): ~1250 PSI with natural reservoir depletion (~15 PSI over 60 days)
    depletion_drift = -15.0 * (time_index / total_minutes)
    base_bhp = 1250.0 + depletion_drift + np.random.normal(0, 3.5, total_minutes)

    # Downhole gauge temperature (DHG Temp): ~185 F with slight thermal coupling
    base_dhg_temp = 185.0 + 0.8 * np.sin(2 * np.pi * time_index / 1440.0) + np.random.normal(0, 0.4, total_minutes)

    # Diurnal (24h = 1440 mins) ambient cycle affecting surface measurements
    diurnal_cycle = 3.5 * np.sin(2 * np.pi * time_index / 1440.0)

    # ESP Pump RPM (normal ~3200 RPM)
    base_rpm = 3200.0 + np.random.normal(0, 9.0, total_minutes)

    # Pump Motor Current / Torque (Amps): coupled to RPM & load (normal ~58 A)
    base_current = 58.0 + (base_rpm - 3200.0) * 0.015 + np.random.normal(0, 0.7, total_minutes)

    # Tubing Head Pressure (THP): ~280 PSI, physically coupled to RPM & BHP
    base_thp = (
        280.0
        + (base_rpm - 3200.0) * 0.04
        + (base_bhp - 1250.0) * 0.08
        + diurnal_cycle
        + np.random.normal(0, 2.2, total_minutes)
    )

    # Casing Head Pressure (CHP): ~150 PSI
    base_chp = 150.0 + diurnal_cycle * 0.5 + np.random.normal(0, 1.6, total_minutes)

    # Production Flow Rates (Water BPD & Gas MSCFD)
    base_water_rate = 850.0 + (base_rpm - 3200.0) * 0.35 + np.random.normal(0, 7.5, total_minutes)
    base_gas_rate = 320.0 + (base_rpm - 3200.0) * 0.12 + np.random.normal(0, 3.8, total_minutes)

    # Annular Fluid / Water Level (ft above pump intake: normal ~450 ft)
    base_water_level = 450.0 + (base_bhp - 1250.0) * 0.6 - (base_rpm - 3200.0) * 0.08 + np.random.normal(0, 3.0, total_minutes)

    # Surface Choke Opening: ~80%
    choke_pct = np.full(total_minutes, 80.0) + np.random.normal(0, 0.4, total_minutes)

    # SCADA / Modbus Telemetry Layer
    modbus_function = np.full(total_minutes, 3)  # Function 3 = Read Holding Registers
    packet_loss_pct = np.clip(np.random.exponential(scale=0.18, size=total_minutes), 0.0, 4.5)

    # -------------------------------------------------------------------------
    # 2. Target Labels for Both Parallel Intelligence Layers
    # -------------------------------------------------------------------------
    # Layer 1: Operational / Predictive Maintenance Labels (Objective 1 & 2)
    # Values: "Normal", "Pre-failure", "Downtime", "Workover"
    operational_status = ["Normal"] * total_minutes
    is_failure_risk = np.zeros(total_minutes, dtype=int)  # 1 during Pre-failure / Downtime

    # Layer 2: Cyber / Measurement Anomaly Labels (Objective 3)
    # 5 Canonical Categories from PDF:
    # "Normal", "Sensor_Spike", "Sensor_Drift", "Sensor_Freezing",
    # "False_Data_Injection", "Physical_Inconsistency"
    anomaly_category = ["Normal"] * total_minutes
    attack_campaign = ["Normal"] * total_minutes
    is_anomaly = np.zeros(total_minutes, dtype=int)

    def get_indices(start_day, start_hour, duration_hours):
        start_min = int(start_day * 1440 + start_hour * 60)
        end_min = int(start_min + duration_hours * 60)
        return range(start_min, min(end_min, total_minutes))

    # -------------------------------------------------------------------------
    # 3. Inject Operational Degradation -> Downtime -> Workover Cycles
    #    (Follows Scenario A in Case Studies PDF: THP drops, Gas flow declines,
    #     Pump current & DHG temperature rise before trip -> Downtime -> Workover)
    # -------------------------------------------------------------------------
    maintenance_events = [
        # (start_day, start_hour, pre_fail_hrs, downtime_hrs, workover_hrs, event_name)
        (7, 6.0, 12.0, 4.0, 6.0, "ESP_Stage_Wear_Workover_1"),
        (16, 12.0, 14.0, 5.0, 7.0, "Tubing_Scale_Buildup_Workover_2"),
        (29, 4.0, 15.0, 4.0, 8.0, "Gas_Lock_Pump_Degradation_3"),
        (38, 10.0, 12.0, 4.0, 6.0, "Intake_Screen_Plugging_4"),
        (48, 8.0, 14.0, 5.0, 7.0, "Bearing_Overheat_Degradation_5"),
        (56, 6.0, 12.0, 4.0, 6.0, "Valve_Wear_PreFailure_6"),
    ]

    for day, hr, pre_h, down_h, wo_h, ev_name in maintenance_events:
        # Phase A: Pre-failure gradual degradation (Scenario A)
        idx_pre = list(get_indices(day, hr, pre_h))
        n_pre = len(idx_pre)
        for step, i in enumerate(idx_pre):
            prog = (step + 1) / n_pre  # 0.0 -> 1.0 progression toward failure
            operational_status[i] = "Pre-failure"
            is_failure_risk[i] = 1
            # Physical degradation signature (Scenario A):
            # THP decreases (-35 to -65 PSI), Gas & Water flow decline,
            # Pump motor current increases (+12 to +22 A), Downhole temp increases (+8 to +14 F)
            base_thp[i] -= 55.0 * (prog ** 1.3) + np.random.normal(0, 1.5)
            base_gas_rate[i] -= 85.0 * (prog ** 1.2) + np.random.normal(0, 2.5)
            base_water_rate[i] -= 210.0 * (prog ** 1.2) + np.random.normal(0, 5.0)
            base_current[i] += 18.5 * (prog ** 1.1) + np.random.normal(0, 0.8)
            base_dhg_temp[i] += 11.0 * prog + np.random.normal(0, 0.3)
            base_rpm[i] -= 180.0 * (prog ** 1.5) + np.random.normal(0, 18.0)
            base_chp[i] += 22.0 * prog  # Annulus gas accumulation raises CHP
            base_water_level[i] += 45.0 * prog  # Fluid level rises as pump efficiency drops

        # Phase B: Unplanned Downtime (Well shut-in / pump tripped)
        idx_down = list(get_indices(day, hr + pre_h, down_h))
        for step, i in enumerate(idx_down):
            operational_status[i] = "Downtime"
            is_failure_risk[i] = 1
            base_rpm[i] = 0.0
            base_current[i] = 0.0
            base_water_rate[i] = 0.0
            base_gas_rate[i] = 0.0
            choke_pct[i] = 0.0
            # Shut-in pressure build-up in BHP and CHP, THP bleeds down
            base_thp[i] = 95.0 + 30.0 * np.exp(-step / 60.0) + np.random.normal(0, 1.0)
            base_chp[i] = 210.0 + np.random.normal(0, 1.2)
            base_bhp[i] = 1340.0 + np.random.normal(0, 2.5)
            base_dhg_temp[i] = 178.0 + np.random.normal(0, 0.3)
            base_water_level[i] = 620.0 + np.random.normal(0, 2.0)

        # Phase C: Workover / Maintenance Intervention
        idx_wo = list(get_indices(day, hr + pre_h + down_h, wo_h))
        for step, i in enumerate(idx_wo):
            operational_status[i] = "Workover"
            is_failure_risk[i] = 0
            # Workover circulation / testing before restart
            base_rpm[i] = 0.0 if step < len(idx_wo) * 0.7 else 2400.0 + np.random.normal(0, 15.0)
            base_current[i] = 0.0 if step < len(idx_wo) * 0.7 else 42.0 + np.random.normal(0, 1.0)
            base_water_rate[i] = 0.0 if step < len(idx_wo) * 0.7 else 520.0 + np.random.normal(0, 10.0)
            base_gas_rate[i] = 0.0 if step < len(idx_wo) * 0.7 else 195.0 + np.random.normal(0, 5.0)
            choke_pct[i] = 15.0 if step < len(idx_wo) * 0.7 else 55.0
            base_thp[i] = 120.0 if step < len(idx_wo) * 0.7 else 235.0 + np.random.normal(0, 3.0)
            base_chp[i] = 165.0 + np.random.normal(0, 1.5)
            base_bhp[i] = 1290.0 + np.random.normal(0, 3.0)

    # -------------------------------------------------------------------------
    # 4. Inject the 5 Canonical Cyber / Measurement Anomaly Types
    #    (Spanning both Train [Days 1-42] and Test [Days 43-60] periods)
    # -------------------------------------------------------------------------

    # --- Type 1: Sensor_Spike (Sudden high/low measurement spikes) ---
    spike_windows = [
        (3, 14.0, 2.0, "THP_Pressure_Spike_Train"),
        (24, 9.0, 2.0, "Multi_Sensor_Spike_Train"),
        (43, 11.0, 2.5, "THP_BHP_Spike_Test"),
    ]
    for d, h, dur, name in spike_windows:
        for i in get_indices(d, h, dur):
            anomaly_category[i] = "Sensor_Spike"
            attack_campaign[i] = name
            is_anomaly[i] = 1
            spike_sign = np.random.choice([1.0, -1.0], p=[0.75, 0.25])
            base_thp[i] += spike_sign * np.random.uniform(140.0, 240.0)
            base_bhp[i] += spike_sign * np.random.uniform(250.0, 420.0)
            packet_loss_pct[i] += np.random.uniform(1.5, 4.5)

    # --- Type 2: Sensor_Drift (Gradual creeping measurement deviation) ---
    drift_windows = [
        (11, 8.0, 5.0, "Slow_Drift_Bias_CHP_Train"),
        (34, 10.0, 5.5, "Gradual_THP_Gauge_Drift_Train"),
        (46, 9.0, 5.0, "Slow_Drift_Bias_CHP_Test"),
    ]
    for d, h, dur, name in drift_windows:
        idx_d = list(get_indices(d, h, dur))
        for step, i in enumerate(idx_d):
            anomaly_category[i] = "Sensor_Drift"
            attack_campaign[i] = name
            is_anomaly[i] = 1
            prog = (step + 1) / len(idx_d)
            # Slow creeping bias up to +145 PSI on CHP and -95 PSI on BHP
            base_chp[i] += 145.0 * prog
            base_bhp[i] -= 95.0 * prog

    # --- Type 3: Sensor_Freezing (Scenario B: THP freezes constant while CHP & others change) ---
    freeze_windows = [
        (14, 15.0, 3.5, "THP_Sensor_Freeze_ScenarioB_Train"),
        (32, 18.0, 3.0, "DoS_Telemetry_Freeze_Train"),
        (44, 16.0, 3.5, "THP_Sensor_Freeze_ScenarioB_Test"),
    ]
    for d, h, dur, name in freeze_windows:
        idx_f = list(get_indices(d, h, dur))
        anchor = idx_f[0] - 1
        frozen_thp = base_thp[anchor]
        frozen_bhp = base_bhp[anchor]
        for step, i in enumerate(idx_f):
            anomaly_category[i] = "Sensor_Freezing"
            attack_campaign[i] = name
            is_anomaly[i] = 1
            # THP and BHP stay completely flatlined while CHP & flow rates vary noticeably
            base_thp[i] = frozen_thp
            base_bhp[i] = frozen_bhp
            base_chp[i] += 18.0 * np.sin(2 * np.pi * step / 45.0) + np.random.normal(0, 3.0)
            packet_loss_pct[i] = np.random.uniform(28.0, 68.0)

    # --- Type 4: False_Data_Injection (Spoofed sensor payloads via Modbus write) ---
    fdi_windows = [
        (6, 2.0, 3.0, "False_Data_Injection_BHP_Train"),
        (21, 13.0, 3.0, "Modbus_Register_Spoofing_Train"),
        (51, 3.0, 3.5, "False_Data_Injection_BHP_Test"),
    ]
    for d, h, dur, name in fdi_windows:
        for i in get_indices(d, h, dur):
            anomaly_category[i] = "False_Data_Injection"
            attack_campaign[i] = name
            is_anomaly[i] = 1
            base_bhp[i] = 420.0 + np.random.normal(0, 3.0)  # Spoofed low downhole pressure
            modbus_function[i] = 16  # Write Multiple Registers
            packet_loss_pct[i] += np.random.uniform(3.0, 9.0)

    # --- Type 5: Physical_Inconsistency (Coupled parameters violate well physics + Scenario C) ---
    phys_windows = [
        (19, 9.5, 2.5, "Unauthorized_RPM_Flow_Mismatch_Train", False),
        (27, 21.0, 2.5, "Surface_Choke_Sabotage_Train", False),
        (53, 14.0, 3.0, "Physical_Inconsistency_Choke_Flow_Test", False),
        # Scenario C on Day 56 (overlaps with Pre-failure window 6 so both ML models trigger!)
        (56, 12.0, 4.0, "Scenario_C_Combined_Failure_And_Sensor_Anomaly", True),
    ]
    for d, h, dur, name, is_scenario_c in phys_windows:
        for i in get_indices(d, h, dur):
            anomaly_category[i] = "Physical_Inconsistency"
            attack_campaign[i] = name
            is_anomaly[i] = 1
            if is_scenario_c:
                # Keep operational_status = "Pre-failure" and is_failure_risk = 1,
                # while injecting physically inconsistent choke/RPM/pressure spoofing
                base_rpm[i] = 4380.0 + np.random.normal(0, 14.0)
                choke_pct[i] = 8.0 + np.random.normal(0, 0.6)
                modbus_function[i] = 6
                packet_loss_pct[i] = np.random.uniform(12.0, 28.0)
            else:
                # High RPM (4450) with choked valve (6%), surging THP (540 PSI), yet spoofed normal/contradictory rates
                base_rpm[i] = 4450.0 + np.random.normal(0, 15.0)
                choke_pct[i] = 6.0 + np.random.normal(0, 0.5)
                base_thp[i] = 545.0 + np.random.normal(0, 10.0)
                base_water_rate[i] = 45.0 + np.random.normal(0, 3.0)
                base_gas_rate[i] = 460.0 + np.random.normal(0, 8.0)  # Physically impossible gas surge while choked
                modbus_function[i] = 5

    # -------------------------------------------------------------------------
    # 5. Build DataFrame & Engineer Petroleum Domain Features (Objective 1)
    # -------------------------------------------------------------------------
    df = pd.DataFrame({
        "timestamp": timestamps,
        "tubing_head_pressure_psi": np.round(base_thp, 2),
        "casing_head_pressure_psi": np.round(base_chp, 2),
        "downhole_gauge_pressure_psi": np.round(base_bhp, 2),
        "downhole_temp_f": np.round(base_dhg_temp, 2),
        "pump_rpm": np.round(base_rpm, 1),
        "pump_torque_current_amps": np.round(base_current, 2),
        "water_rate_bpd": np.round(base_water_rate, 2),
        "gas_rate_mscfd": np.round(base_gas_rate, 2),
        "water_level_ft": np.round(base_water_level, 2),
        "choke_opening_pct": np.round(choke_pct, 1),
        "modbus_function_code": modbus_function,
        "packet_loss_pct": np.round(packet_loss_pct, 2),
        # Derived Petroleum Engineering Features (Slide 3 & Case Studies PDF p. 17)
        "diff_pressure_bhp_thp_psi": np.round(base_bhp - base_thp, 2),
        "diff_pressure_thp_chp_psi": np.round(base_thp - base_chp, 2),
    })

    # Rolling statistics, rate of change, and baseline deviations (15-min window)
    df["thp_roll_mean_15m"] = df["tubing_head_pressure_psi"].rolling(15, min_periods=1).mean().round(2)
    df["thp_roll_std_15m"] = df["tubing_head_pressure_psi"].rolling(15, min_periods=1).std().fillna(0.0).round(3)
    df["chp_roll_std_15m"] = df["casing_head_pressure_psi"].rolling(15, min_periods=1).std().fillna(0.0).round(3)
    df["gas_rate_roll_mean_15m"] = df["gas_rate_mscfd"].rolling(15, min_periods=1).mean().round(2)
    df["current_roll_mean_15m"] = df["pump_torque_current_amps"].rolling(15, min_periods=1).mean().round(2)

    # Rate of change over 15 minutes
    df["thp_roc_15m"] = df["tubing_head_pressure_psi"].diff(15).fillna(0.0).round(2)
    df["chp_roc_15m"] = df["casing_head_pressure_psi"].diff(15).fillna(0.0).round(2)
    df["bhp_roc_15m"] = df["downhole_gauge_pressure_psi"].diff(15).fillna(0.0).round(2)
    df["current_roc_15m"] = df["pump_torque_current_amps"].diff(15).fillna(0.0).round(2)

    # Deviation from normal operating baseline
    df["thp_baseline_dev"] = (df["tubing_head_pressure_psi"] - 280.0).round(2)
    df["chp_baseline_dev"] = (df["casing_head_pressure_psi"] - 150.0).round(2)
    df["bhp_baseline_dev"] = (df["downhole_gauge_pressure_psi"] - 1242.5).round(2)

    # Labels for Layer 1 (Predictive Maintenance) & Layer 2 (Cyber/Measurement Anomaly)
    df["operational_status"] = operational_status
    df["is_failure_risk"] = is_failure_risk
    df["anomaly_category"] = anomaly_category
    df["attack_type"] = attack_campaign  # Preserved column name for backward compatibility
    df["is_anomaly"] = is_anomaly

    output_filename = "wellhead_scada_2month_telemetry.csv"
    df.to_csv(output_filename, index=False)

    print(f"\n[SUCCESS] Enhanced 2-Month Dataset Saved to: {output_filename}")
    print(f"Total Rows: {len(df):,} records (1-minute resolution across 60 days)")
    print(f"Total Columns: {len(df.columns)} (including primary parameters, derived features & dual-layer labels)")
    print(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print("\n--- Layer 1: Operational / Predictive Maintenance Status Distribution ---")
    print(df["operational_status"].value_counts())
    print("\n--- Layer 2: Cyber / Measurement Anomaly Category Distribution ---")
    print(df["anomaly_category"].value_counts())
    print("\n--- Combined Scenario C (High Failure Risk + Cyber Anomaly) Rows ---")
    scen_c_count = len(df[(df["is_failure_risk"] == 1) & (df["is_anomaly"] == 1)])
    print(f"Scenario C Overlapping Minutes: {scen_c_count}")


if __name__ == "__main__":
    generate_2month_wellhead_scada()
