import math
from typing import Any, Dict, List

# =============================================================================
# Case-Study Physics Reconstruction & Replay Engine
# =============================================================================
# IMPORTANT: All numerical series (depths, pressures, flow rates, LEL, timing)
# are illustrative engineering reconstructions for educational/demo replay,
# grounded in documented findings from OISD, Havtil, and OIL press releases.

AS_HAPPENED: Dict[str, Dict[str, Any]] = {
    "oisd": {
        "fluid_sg": 1.02,
        "fix_pore_estimate": False,
        "cement_good": False,
        "trip_tank_online": False,
        "shear_ram": False,
        "ai_monitoring": False,
    },
    "bollsta": {
        "log_calibrated": False,
        "gauge_maintained": False,
        "dp_trended": False,
        "outer_barrier_test": False,
        "ai_monitoring": False,
    },
    "oil_idbh": {
        "double_block_bleed": False,
        "residual_pressure_monitor": False,
        "ai_monitoring": False,
        "purge_before_work": False,
        "continuous_gas_test": False,
    },
}

ALL_FIXES: Dict[str, Dict[str, Any]] = {
    "oisd": {
        "fluid_sg": 1.15,
        "fix_pore_estimate": True,
        "cement_good": True,
        "trip_tank_online": True,
        "shear_ram": True,
        "ai_monitoring": True,
    },
    "bollsta": {
        "log_calibrated": True,
        "gauge_maintained": True,
        "dp_trended": True,
        "outer_barrier_test": True,
        "ai_monitoring": True,
    },
    "oil_idbh": {
        "double_block_bleed": True,
        "residual_pressure_monitor": True,
        "ai_monitoring": True,
        "purge_before_work": True,
        "continuous_gas_test": True,
    },
}

CASE_META: Dict[str, Dict[str, Any]] = {
    "oisd": {
        "id": "oisd",
        "title": "Gas Blowout at Onshore Workover Rig",
        "short": "OISD Workover Rig Blowout (2026)",
        "badge": "Main Case",
        "date": "4 February 2026",
        "location": "Onshore workover rig, India",
        "source": "Oil Industry Safety Directorate — OISD/CS/2025-26/E&P/21",
        "summary": (
            "Uncontrolled gas flow occurred immediately after conventional perforation. "
            "The production BOP blind ram could not seal the well because the wireline string "
            "remained across the BOP and no shear ram was installed."
        ),
        "what_went_wrong": [
            "GTO indicated an oil-bearing zone while offset-well and drilling records showed gas influxes.",
            "CBL-VDL log indicated poor cement bond quality across the interval.",
            "Lighter completion fluid reduced hydrostatic pressure compared with final drilling mud.",
            "BOP stack had no shear ram to cut the wireline string and seal the well.",
            "Trip tank was kept isolated during perforation (OISD-STD-174 lapse).",
        ],
        "disclaimer": (
            "Values (depths, pressures, rates) are illustrative engineering assumptions, not data from the report. "
            "This replay is a decision-support demonstration and cannot replace physical barriers or well-control design."
        ),
        "fixes": [
            {
                "key": "fix_pore_estimate",
                "label": "Use offset-well & drilling gas data (re-weight fluid to SG 1.15)",
                "why": "Revises assumed pore pressure from 3000 to 3350 psi so fluid provides positive overbalance.",
            },
            {
                "key": "cement_good",
                "label": "Verify & remediate CBL-VDL cement bond before perforating",
                "why": "Eliminates annular gas migration channels behind casing (influx multiplier 1.6x -> 1.0x).",
            },
            {
                "key": "trip_tank_online",
                "label": "Keep trip tank online (OISD-STD-174 compliance)",
                "why": "Detects pit/trip-tank volume gain at 2 bbl instead of waiting for gas at surface.",
            },
            {
                "key": "shear_ram",
                "label": "Install certified BOP shear-seal ram for wireline operations",
                "why": "Cuts wireline and seals the well in 2 min instead of failing and pulling out of hole.",
            },
            {
                "key": "ai_monitoring",
                "label": "Enable Dual-Layer AI monitoring (flow-balance + sensor integrity)",
                "why": "Flags 1 bbl kick early and detects frozen/isolated trip-tank telemetry.",
            },
        ],
        "chart_series": [
            {"key": "hydrostatic_psi", "label": "Hydrostatic Ph (psi)", "color": "#38bdf8", "axis": "y"},
            {"key": "pore_psi", "label": "Formation Pore (psi)", "color": "#f59e0b", "axis": "y"},
            {"key": "well_gain_bbl", "label": "True Well Gain (bbl)", "color": "#ef4444", "axis": "y1"},
            {"key": "trip_tank_reading_bbl", "label": "Trip Tank Reading (bbl)", "color": "#a855f7", "axis": "y1"},
        ],
        "tiles": [
            {"key": "overbalance_psi", "label": "Overbalance (Ph-Pp)", "unit": "psi", "decimals": 0},
            {"key": "well_gain_bbl", "label": "Well Fluid Gain", "unit": "bbl", "decimals": 1},
            {"key": "trip_tank_reading_bbl", "label": "Trip Tank Reading", "unit": "bbl", "decimals": 1},
            {"key": "casing_pressure_psi", "label": "Casing Pressure", "unit": "psi", "decimals": 0},
        ],
    },
    "bollsta": {
        "id": "bollsta",
        "title": "Deepsea Bollsta Well-Control Incident (Q-21)",
        "short": "Equinor Deepsea Bollsta (2025)",
        "badge": "Calibration & ΔP",
        "date": "23 September 2025 (Report: 18 May 2026)",
        "location": "Q-21 Well, Troll Field, Offshore Norway (114 POB)",
        "source": "Norwegian Ocean Industry Authority (Havtil Investigation)",
        "summary": (
            "During permanent plugging and abandonment (P&A), cutting the 13 3/8-inch casing at ~510 m "
            "released ~930 kg of gas and water onto the drilling facility due to outer barrier failure "
            "and faulty logging calibration."
        ),
        "what_went_wrong": [
            "Outer well barrier failed, allowing gas to accumulate behind the 13 3/8-inch casing.",
            "Faulty calibration of logging equipment led to misinterpretation of casing logs.",
            "Available differential-pressure (ΔP) data were not adequately trended or used.",
            "Differential-pressure gauges suffered from inadequate maintenance.",
        ],
        "disclaimer": (
            "Values (depths, pressures, rates) are illustrative engineering assumptions, not data from the report. "
            "ML/monitoring flags suspicious data and overdue QA, and cannot replace independent tool calibration."
        ),
        "fixes": [
            {
                "key": "log_calibrated",
                "label": "Verify logging tool calibration QA before interpreting logs",
                "why": "Prevents misreading poor outer barrier (0.35) as good (0.80).",
            },
            {
                "key": "outer_barrier_test",
                "label": "Perform independent outer-barrier pressure verification test",
                "why": "Confirms annular integrity and bleeds trapped 620 psi gas prior to cutting.",
            },
            {
                "key": "gauge_maintained",
                "label": "Complete ΔP gauge maintenance & calibration on schedule",
                "why": "Prevents the ΔP transmitter from sticking flatline at ~9 psi.",
            },
            {
                "key": "dp_trended",
                "label": "Actively monitor & alarm on differential pressure (ΔP = P1 - P2)",
                "why": "Triggers an engineering hold when ΔP reaches 100 psi (requires working gauge).",
            },
            {
                "key": "ai_monitoring",
                "label": "Enable AI Layer 2 measurement-integrity & ΔP anomaly monitor",
                "why": "Catches a frozen/unmaintained ΔP gauge (zero variance) even before cutting.",
            },
        ],
        "chart_series": [
            {"key": "true_dp_psi", "label": "True ΔP (psi)", "color": "#38bdf8", "axis": "y"},
            {"key": "gauge_dp_psi", "label": "Gauge ΔP Reading (psi)", "color": "#a855f7", "axis": "y"},
            {"key": "trapped_annulus_psi", "label": "Trapped Annulus (psi)", "color": "#f59e0b", "axis": "y"},
            {"key": "cumulative_release_kg", "label": "Gas Released (kg)", "color": "#ef4444", "axis": "y1"},
        ],
        "tiles": [
            {"key": "logged_bond_index", "label": "Logged Bond Index", "unit": "", "decimals": 2},
            {"key": "gauge_dp_psi", "label": "Gauge ΔP Reading", "unit": "psi", "decimals": 1},
            {"key": "trapped_annulus_psi", "label": "Annulus Pressure", "unit": "psi", "decimals": 0},
            {"key": "cumulative_release_kg", "label": "Cumulative Release", "unit": "kg", "decimals": 1},
        ],
    },
    "oil_idbh": {
        "id": "oil_idbh",
        "title": "Intermediate Tank Farm Indirect Bath Heater Fire",
        "short": "Oil India Tank Farm Fire (2026)",
        "badge": "Surface Extension",
        "date": "6 November 2026",
        "location": "Tengakhat Intermediate Tank Farm, Dibrugarh, Assam, India",
        "source": "Oil India Limited Official Press Release (6 Nov 2026)",
        "summary": (
            "A major fire broke out at the Indirect Bath Heater (IDBH) area during maintenance activities, "
            "despite the heater area having reportedly been isolated since 4 November 2026."
        ),
        "what_went_wrong": [
            "Official press release confirms fire during maintenance on an isolated IDBH (exact ignition root cause under formal inquiry).",
            "Illustrates maintenance-phase risks: physical isolation verification vs software status, residual pressure/hydrocarbons, and transmitter integrity.",
        ],
        "disclaimer": (
            "Hypothetical training reconstruction of ONE plausible pathway (passing isolation valve + residual hydrocarbons + hot work). "
            "Not an official finding — exact root cause was under inquiry in the supplied press release. "
            "Values (depths, pressures, rates) are illustrative engineering assumptions, not data from the report."
        ),
        "fixes": [
            {
                "key": "double_block_bleed",
                "label": "Enforce verified physical Double-Block & Bleed (LOTO)",
                "why": "Stops slow valve leakage so hydrocarbon pressure and LEL never enter the coil.",
            },
            {
                "key": "residual_pressure_monitor",
                "label": "Keep live local pressure transmitter active & verified",
                "why": "Detects creeping residual pressure (>5 psi) so heater is re-isolated and purged early.",
            },
            {
                "key": "ai_monitoring",
                "label": "Enable AI Layer 2 frozen-transmitter check",
                "why": "Flags pressure transmitter stuck at 0.0 psi while bath temperature changes.",
            },
            {
                "key": "purge_before_work",
                "label": "Enforce mandatory gas-free purge before maintenance starts (Hour 46)",
                "why": "Clears accumulated hydrocarbon vapour below 10% LEL prior to hot work.",
            },
            {
                "key": "continuous_gas_test",
                "label": "Enforce continuous portable gas testing (stop-work at >=10% LEL)",
                "why": "Immediately suspends hot work at Hour 48 if >=10% LEL vapour is detected.",
            },
        ],
        "chart_series": [
            {"key": "true_coil_pressure_psi", "label": "True Coil Pressure (psi)", "color": "#38bdf8", "axis": "y"},
            {"key": "transmitter_pressure_psi", "label": "Transmitter PT (psi)", "color": "#a855f7", "axis": "y"},
            {"key": "lel_pct", "label": "Vapour (% LEL)", "color": "#f59e0b", "axis": "y"},
            {"key": "bath_temp_c", "label": "Bath Temp (°C)", "color": "#ef4444", "axis": "y1"},
        ],
        "tiles": [
            {"key": "transmitter_pressure_psi", "label": "PT Transmitter", "unit": "psi", "decimals": 1},
            {"key": "true_coil_pressure_psi", "label": "True Coil Pressure", "unit": "psi", "decimals": 1},
            {"key": "lel_pct", "label": "Hydrocarbon LEL", "unit": "%", "decimals": 1},
            {"key": "bath_temp_c", "label": "Bath / Heater Temp", "unit": "°C", "decimals": 1},
        ],
    },
}


def _ph_psi(sg: float, depth_m: float = 2200.0) -> float:
    return sg * 1000.0 * 9.81 * depth_m / 6894.76


def _simulate_oisd(params: Dict[str, Any]) -> Dict[str, Any]:
    depth_m = 2200.0
    mud_sg = 1.18
    actual_pore = 3350.0
    gto_pore = 3000.0

    fix_pore = bool(params.get("fix_pore_estimate", False))
    cement_good = bool(params.get("cement_good", False))
    trip_online = bool(params.get("trip_tank_online", False))
    shear_ram = bool(params.get("shear_ram", False))
    ai_mon = bool(params.get("ai_monitoring", False))

    raw_sg = float(params.get("fluid_sg", 1.02))
    eff_sg = max(raw_sg, 1.15) if fix_pore else raw_sg
    assumed_pore = actual_pore if fix_pore else gto_pore
    ph_target = _ph_psi(eff_sg, depth_m)
    planned_ob = ph_target - assumed_pore
    true_ob = ph_target - actual_pore

    t_list = list(range(151))
    t_labels = [f"T+{t} min" for t in t_list]

    events: List[Dict[str, Any]] = []
    if fix_pore:
        events.append({
            "i": 0,
            "t_label": "T+0 min",
            "type": "success",
            "text": (
                f"Pre-job review used offset-well gas data: pore pressure revised 3000->3350 psi; "
                f"completion fluid re-weighted to SG {eff_sg:.2f} (true overbalance {true_ob:+.0f} psi)."
            ),
        })
    else:
        events.append({
            "i": 0,
            "t_label": "T+0 min",
            "type": "warn" if true_ob < 0 else "info",
            "text": (
                f"Job started using GTO pore assumption (3000 psi): planned overbalance {planned_ob:+.0f} psi, "
                f"but TRUE overbalance against gas zone (3350 psi) is {true_ob:+.0f} psi."
            ),
        })

    hydro_s, pore_s, ob_s, sg_s = [], [], [], []
    rate_s, gain_s, trip_s, flow_out_s, cp_s, lel_s = [], [], [], [], [], []
    bop_states, wire_states, phases = [], [], []

    gain = 0.0
    detect_t = None
    fail_t = None
    seal_t = None
    kill_start_t = None
    kill_end_t = None
    blowout = False
    blowout_t = None
    sicp = 0.0
    max_cp = 0.0
    wireline_in = False

    for t in t_list:
        if t < 30:
            phase = "Fluid swap"
            cur_sg = mud_sg + (eff_sg - mud_sg) * (t / 30.0)
        elif t < 75:
            phase = "Wireline perforating gun RIH"
            cur_sg = eff_sg
        elif t == 75:
            phase = "Perforation"
            cur_sg = eff_sg
        else:
            phase = "Post-perforation"
            cur_sg = eff_sg

        if t == 30:
            wireline_in = True
            events.append({
                "i": t,
                "t_label": t_labels[t],
                "type": "info",
                "text": "Fluid swap complete. Wireline perforating gun running in hole.",
            })
        if t == 75:
            events.append({
                "i": t,
                "t_label": t_labels[t],
                "type": "info",
                "text": f"Perforation fired at {depth_m:.0f} m (hydrostatic {ph_target:.0f} psi vs formation {actual_pore:.0f} psi).",
            })

        # Evaluate sealing / POOH completion at start of minute t
        if seal_t is not None and not blowout and t == seal_t:
            if not shear_ram:
                wireline_in = False
                events.append({
                    "i": t,
                    "t_label": t_labels[t],
                    "type": "success",
                    "text": "Wireline pulled out of hole (POOH); blind ram closed and sealed wellbore.",
                })
            else:
                wireline_in = False
                events.append({
                    "i": t,
                    "t_label": t_labels[t],
                    "type": "success",
                    "text": "Shear-seal ram cut wireline and sealed well.",
                })
            sicp = max(0.0, actual_pore - (ph_target - 8.0 * gain))
            kill_start_t = t + 10
            kill_end_t = t + 40

        if fail_t is not None and not blowout and t == fail_t:
            events.append({
                "i": t,
                "t_label": t_labels[t],
                "type": "danger",
                "text": "Blind ram could not seal — wireline across BOP! Starting emergency wireline POOH (10 min).",
            })

        if kill_start_t is not None and t == kill_start_t:
            events.append({
                "i": t,
                "t_label": t_labels[t],
                "type": "info",
                "text": "Bullheading / circulating SG 1.20 kill fluid to bring well back to hydrostatic control.",
            })
        if kill_end_t is not None and t == kill_end_t:
            events.append({
                "i": t,
                "t_label": t_labels[t],
                "type": "success",
                "text": "Well killed with SG 1.20 fluid — casing pressure reduced to 0 psi.",
            })

        # Compute hydrostatic & influx
        sealed_now = (seal_t is not None and t >= seal_t and not blowout)
        if t < 75:
            ph_eff = _ph_psi(cur_sg, depth_m)
            q = 0.0
        elif sealed_now:
            if kill_start_t is not None and t >= kill_start_t:
                frac = min(1.0, (t - kill_start_t) / max(1, kill_end_t - kill_start_t))
                ph_kill = _ph_psi(1.20, depth_m)
                ph_base = ph_target - 8.0 * gain
                ph_eff = ph_base + (ph_kill - ph_base) * frac
                cur_sg = eff_sg + (1.20 - eff_sg) * frac
            else:
                ph_eff = ph_target - 8.0 * gain
            q = 0.0
        else:
            # Open wellbore post-perforation
            ph_eff = ph_target - 8.0 * gain
            if ph_target < actual_pore:
                cf = 1.0 if cement_good else 1.6
                q = min(6.0, 0.004 * max(0.0, actual_pore - ph_eff) * cf)
                gain += q
                ph_eff = ph_target - 8.0 * gain
            else:
                q = 0.0

        # Detection check (only while influx is occurring and not yet detected/sealed)
        if detect_t is None and gain > 0.0 and not sealed_now:
            if ai_mon and gain >= 1.0:
                detect_t = t
                if not trip_online:
                    msg = "AI Layer 2: return flow rising while trip-tank signal is flat -> measurement-inconsistency alarm"
                else:
                    msg = "AI: flow-out > flow-in, 1 bbl gain -> kick alarm"
                events.append({"i": t, "t_label": t_labels[t], "type": "ai", "text": msg})
            elif trip_online and gain >= 2.0:
                detect_t = t
                events.append({
                    "i": t,
                    "t_label": t_labels[t],
                    "type": "warn",
                    "text": "Trip tank shows 2 bbl gain -> kick detected.",
                })
            elif gain >= 25.0:
                detect_t = t
                events.append({
                    "i": t,
                    "t_label": t_labels[t],
                    "type": "warn",
                    "text": "Gas reaches surface — kick noticed visually (25+ bbl already in wellbore).",
                })

            if detect_t is not None:
                if shear_ram:
                    seal_t = detect_t + 2
                else:
                    fail_t = detect_t + 2
                    seal_t = detect_t + 13

        # Blowout threshold check BEFORE seal completes
        if not blowout and not sealed_now and gain >= 40.0:
            blowout = True
            blowout_t = t
            events.append({
                "i": t,
                "t_label": t_labels[t],
                "type": "danger",
                "text": "BLOWOUT — uncontrolled gas release exceeds 40 bbl threshold, rig evacuated!",
            })

        # Surface Casing Pressure & Gas LEL
        if blowout:
            cp = (3.0 if not cement_good else 1.0) * gain
            lel = 100.0
        elif sealed_now:
            if kill_start_t is not None and t >= kill_start_t:
                frac = min(1.0, (t - kill_start_t) / max(1, kill_end_t - kill_start_t))
                cp = sicp * (1.0 - frac)
            else:
                cp = sicp
            # Decay any surface gas after sealing
            prev_lel = lel_s[-1] if lel_s else 0.0
            lel = max(0.0, prev_lel * 0.78)
        else:
            cp = (3.0 if not cement_good else 1.0) * gain
            if gain >= 20.0:
                lel = min(100.0, (gain - 20.0) / 15.0 * 100.0)
            else:
                lel = 0.0

        max_cp = max(max_cp, cp)

        # BOP State string
        if blowout:
            bop_st = "Seal Failed" if (fail_t is not None and t >= fail_t) else "Open"
        elif sealed_now:
            bop_st = "Sealed"
        elif detect_t is not None and t >= detect_t:
            if not shear_ram and fail_t is not None and t >= fail_t:
                bop_st = "Seal Failed"
            else:
                bop_st = "Closing"
        else:
            bop_st = "Open"

        hydro_s.append(round(ph_eff, 2))
        pore_s.append(round(actual_pore, 2))
        ob_s.append(round(ph_eff - actual_pore, 2))
        sg_s.append(round(cur_sg, 3))
        rate_s.append(round(q, 3))
        gain_s.append(round(gain, 2))
        trip_s.append(round(gain, 2) if trip_online else 0.0)
        flow_out_s.append(round(q * 42.0, 2))
        cp_s.append(round(cp, 2))
        lel_s.append(round(lel, 1))
        bop_states.append(bop_st)
        wire_states.append("yes" if wireline_in else "no")
        phases.append(phase)

    # Outcome summary
    if blowout:
        outcome = {
            "status": "BLOWOUT",
            "severity": "danger",
            "headline": "BLOWOUT — Uncontrolled Gas Flow",
            "detail": (
                f"Lighter fluid ({eff_sg:.2f} SG) underbalanced the gas zone; kick escalated to {gain:.1f} bbl "
                f"before the well could be sealed."
            ),
            "event_index": int(blowout_t),
            "metrics": [
                {"label": "Total gas influx (bbl)", "value": f"{gain:.1f} bbl"},
                {"label": "Kick detected at", "value": f"T+{detect_t} min" if detect_t is not None else "Late"},
                {"label": "Well secured at", "value": "Not sealed (Blowout)"},
                {"label": "Max casing pressure (psi)", "value": f"{max_cp:.0f} psi"},
                {"label": "Outcome", "value": "BLOWOUT"},
            ],
        }
    elif gain > 0.0 and seal_t is not None:
        outcome = {
            "status": "CONTROLLED",
            "severity": "warn",
            "headline": "KICK CONTROLLED — Well Safely Sealed & Killed",
            "detail": (
                f"Although fluid ({eff_sg:.2f} SG) was underbalanced, early detection at T+{detect_t} min "
                f"allowed sealing at T+{seal_t} min ({gain:.1f} bbl total influx) before blowout."
            ),
            "event_index": int(seal_t),
            "metrics": [
                {"label": "Total gas influx (bbl)", "value": f"{gain:.1f} bbl"},
                {"label": "Kick detected at", "value": f"T+{detect_t} min"},
                {"label": "Well secured at", "value": f"T+{seal_t} min"},
                {"label": "Max casing pressure (psi)", "value": f"{max_cp:.0f} psi"},
                {"label": "Outcome", "value": "CONTROLLED"},
            ],
        }
    else:
        outcome = {
            "status": "SAFE",
            "severity": "success",
            "headline": f"SAFE — Perforated with +{true_ob:.0f} psi Overbalance (No Kick)",
            "detail": (
                f"Completion fluid (SG {eff_sg:.2f}, Ph {ph_target:.0f} psi) balanced the 3350 psi gas formation. "
                f"Zero influx occurred during or after perforation."
            ),
            "event_index": 75,
            "metrics": [
                {"label": "Total gas influx (bbl)", "value": "0.0 bbl"},
                {"label": "Kick detected at", "value": "No kick"},
                {"label": "Well secured at", "value": "Intact overbalance"},
                {"label": "Max casing pressure (psi)", "value": "0 psi"},
                {"label": "Outcome", "value": "SAFE"},
            ],
        }

    return {
        "case_id": "oisd",
        "dt_label": "min",
        "t": t_list,
        "t_labels": t_labels,
        "series": {
            "hydrostatic_psi": hydro_s,
            "pore_psi": pore_s,
            "overbalance_psi": ob_s,
            "fluid_sg": sg_s,
            "influx_rate_bpm": rate_s,
            "well_gain_bbl": gain_s,
            "trip_tank_reading_bbl": trip_s,
            "flow_out_gpm": flow_out_s,
            "casing_pressure_psi": cp_s,
            "gas_lel_pct": lel_s,
        },
        "states": {
            "bop_state": bop_states,
            "wireline_in_hole": wire_states,
        },
        "phase": phases,
        "events": events,
        "outcome": outcome,
        "params": {
            "fluid_sg": round(eff_sg, 2),
            "fix_pore_estimate": fix_pore,
            "cement_good": cement_good,
            "trip_tank_online": trip_online,
            "shear_ram": shear_ram,
            "ai_monitoring": ai_mon,
        },
    }


def _simulate_bollsta(params: Dict[str, Any]) -> Dict[str, Any]:
    log_cal = bool(params.get("log_calibrated", False))
    gauge_ok = bool(params.get("gauge_maintained", False))
    dp_trend = bool(params.get("dp_trended", False))
    barrier_test = bool(params.get("outer_barrier_test", False))
    ai_mon = bool(params.get("ai_monitoring", False))

    t_list = list(range(241))
    t_labels = [f"T+{t} min" for t in t_list]

    true_bond = 0.35
    logged_bond = 0.35 if log_cal else 0.80

    # Precompute ΔP curves (true vs gauge)
    true_dp_raw = []
    gauge_dp_raw = []
    stuck_val = 0.3 * (180.0 * (70 - 60) / 60.0)  # 9.0 psi after t=70
    for t in t_list:
        if t < 60:
            tdp = 0.0
        elif t <= 120:
            tdp = 180.0 * (t - 60) / 60.0
        else:
            tdp = 180.0
        true_dp_raw.append(tdp)
        if gauge_ok:
            gauge_dp_raw.append(tdp)
        else:
            if t <= 70:
                gauge_dp_raw.append(0.3 * tdp)
            else:
                gauge_dp_raw.append(stuck_val)

    # Determine earliest recognition time
    rec_candidates: List[tuple] = []
    if log_cal:
        rec_candidates.append((45, "info", "Calibrated log shows POOR outer barrier behind 13 3/8-in casing (bond index 0.35)."))
    if barrier_test:
        rec_candidates.append((100, "warn", "Independent outer-barrier pressure test failed — trapped annular gas confirmed."))
    if dp_trend and gauge_ok:
        t_dp = next((t for t in t_list if gauge_dp_raw[t] >= 100.0), 94)
        rec_candidates.append((t_dp, "warn", f"ΔP trending alert: differential pressure exceeded 100 psi ({gauge_dp_raw[t_dp]:.0f} psi)."))
    if ai_mon:
        if not gauge_ok:
            rec_candidates.append((85, "ai", "AI Layer 2: ΔP gauge frozen (zero variance) while annulus conditions change — measurement integrity warning."))
        else:
            t_ai = next((t for t in t_list if true_dp_raw[t] >= 80.0), 87)
            rec_candidates.append((t_ai, "ai", f"AI: ΔP rising trend detected ({true_dp_raw[t_ai]:.0f} psi) — hold P&A casing cut."))

    rec_t = min(c[0] for c in rec_candidates) if rec_candidates else None
    bleed_start_t = (rec_t + 10) if rec_t is not None else None
    secured_t = (bleed_start_t + 40) if bleed_start_t is not None else None
    cut_t = max(150, secured_t + 10) if secured_t is not None else 150

    events: List[Dict[str, Any]] = []
    if log_cal:
        events.append({
            "i": 45,
            "t_label": t_labels[45],
            "type": "warn",
            "text": "Calibrated log shows POOR outer barrier behind 13 3/8-in casing (bond index 0.35).",
        })
    else:
        events.append({
            "i": 45,
            "t_label": t_labels[45],
            "type": "info",
            "text": "Log interpreted as GOOD barrier (0.80) due to faulty tool calibration offset.",
        })

    if not gauge_ok:
        events.append({
            "i": 70,
            "t_label": t_labels[70],
            "type": "warn",
            "text": f"Unmaintained ΔP gauge stuck flatline at {stuck_val:.1f} psi (zero variance).",
        })

    if rec_t is not None:
        for ct, ctype, cmsg in sorted(rec_candidates, key=lambda x: x[0]):
            if not (log_cal and ct == 45):  # already emitted log_cal at t=45
                events.append({"i": ct, "t_label": t_labels[ct], "type": ctype, "text": cmsg})
        events.append({
            "i": bleed_start_t,
            "t_label": t_labels[bleed_start_t],
            "type": "info",
            "text": f"Casing cut postponed to T+{cut_t} min; bleeding trapped 620 psi annular gas.",
        })
        events.append({
            "i": secured_t,
            "t_label": t_labels[secured_t],
            "type": "success",
            "text": "Annulus depressurised and outer barrier verified — safe to resume casing cut.",
        })
        events.append({
            "i": cut_t,
            "t_label": t_labels[cut_t],
            "type": "success",
            "text": "13 3/8-in casing cut at 510 m completed safely with zero uncontrolled gas release.",
        })
    else:
        if dp_trend and not gauge_ok:
            events.append({
                "i": 100,
                "t_label": t_labels[100],
                "type": "info",
                "text": "ΔP trend monitor saw no alarm — gauge reading is stuck flat at 9.0 psi.",
            })
        events.append({
            "i": 150,
            "t_label": t_labels[150],
            "type": "danger",
            "text": "13 3/8-in casing cut at 510 m breached failed outer barrier — uncontrolled release of water & ~930 kg gas!",
        })

    events.sort(key=lambda e: e["i"])

    true_bond_s, logged_bond_s, true_dp_s, gauge_dp_s = [], [], [], []
    trapped_s, rel_rate_s, cum_rel_s, lel_s = [], [], [], []
    barrier_states, phases = [], []

    for t in t_list:
        if t < 60:
            phase = "Barrier logging behind 13 3/8-in casing"
        elif t < cut_t:
            phase = "Pressure monitoring / ΔP hold"
        else:
            phase = "Casing cut at 510 m"

        tdp = true_dp_raw[t]
        gdp = gauge_dp_raw[t]
        trapped = 620.0
        rel_rate = 0.0
        cum_rel = 0.0
        lel = 0.0

        if rec_t is not None:
            if t >= bleed_start_t:
                frac = min(1.0, (t - bleed_start_t) / 40.0)
                trapped = 620.0 * (1.0 - frac)
                tdp = tdp * (1.0 - frac)
                if gauge_ok:
                    gdp = tdp
            if t < rec_t:
                b_stat = "Assumed OK"
            elif t < secured_t:
                b_stat = "NOT verified"
            else:
                b_stat = "Secured"
        else:
            b_stat = "Assumed OK" if t < 150 else "NOT verified"
            if t >= 150:
                tp = t - 150
                cum_rel = 930.0 * (1.0 - math.exp(-tp / 6.0))
                rel_rate = (930.0 / 6.0) * math.exp(-tp / 6.0)
                trapped = 620.0 * math.exp(-tp / 6.0)
                tdp = 180.0 * math.exp(-tp / 6.0)
                lel = min(100.0, 100.0 * (1.0 - math.exp(-tp / 4.0))) if tp < 35 else max(0.0, 100.0 * math.exp(-(tp - 35) / 15.0))

        true_bond_s.append(round(true_bond, 2))
        logged_bond_s.append(round(logged_bond, 2))
        true_dp_s.append(round(tdp, 2))
        gauge_dp_s.append(round(gdp, 2))
        trapped_s.append(round(trapped, 1))
        rel_rate_s.append(round(rel_rate, 2))
        cum_rel_s.append(round(cum_rel, 1))
        lel_s.append(round(lel, 1))
        barrier_states.append(b_stat)
        phases.append(phase)

    final_rel = cum_rel_s[-1]
    if rec_t is None:
        outcome = {
            "status": "RELEASE",
            "severity": "danger",
            "headline": "UNCONTROLLED RELEASE — ~930 kg Gas & Water at Casing Cut",
            "detail": (
                "Faulty logging calibration masked the weak outer barrier and the unmaintained ΔP gauge froze, "
                "causing trapped annular gas to escape when the 13 3/8-in casing was cut at T+150 min."
            ),
            "event_index": 150,
            "metrics": [
                {"label": "Hazard recognised at", "value": "Not detected before cut"},
                {"label": "Gas/water released (kg)", "value": f"{final_rel:.0f} kg"},
                {"label": "Casing cut at", "value": "T+150 min"},
                {"label": "Outcome", "value": "RELEASE"},
            ],
        }
    else:
        outcome = {
            "status": "SAFE",
            "severity": "success",
            "headline": f"SAFE — Outer Barrier Hazard Caught at T+{rec_t} min",
            "detail": (
                f"Hazard recognised at T+{rec_t} min; casing cut postponed to T+{cut_t} min while "
                f"annular pressure was safely bled to 0 psi."
            ),
            "event_index": int(rec_t),
            "metrics": [
                {"label": "Hazard recognised at", "value": f"T+{rec_t} min"},
                {"label": "Gas/water released (kg)", "value": f"{final_rel:.1f} kg"},
                {"label": "Casing cut at", "value": f"T+{cut_t} min"},
                {"label": "Outcome", "value": "SAFE"},
            ],
        }

    return {
        "case_id": "bollsta",
        "dt_label": "min",
        "t": t_list,
        "t_labels": t_labels,
        "series": {
            "true_bond_index": true_bond_s,
            "logged_bond_index": logged_bond_s,
            "true_dp_psi": true_dp_s,
            "gauge_dp_psi": gauge_dp_s,
            "trapped_annulus_psi": trapped_s,
            "release_rate_kg_min": rel_rate_s,
            "cumulative_release_kg": cum_rel_s,
            "rig_floor_lel_pct": lel_s,
        },
        "states": {
            "barrier_status": barrier_states,
        },
        "phase": phases,
        "events": events,
        "outcome": outcome,
        "params": {
            "log_calibrated": log_cal,
            "gauge_maintained": gauge_ok,
            "dp_trended": dp_trend,
            "outer_barrier_test": barrier_test,
            "ai_monitoring": ai_mon,
        },
    }


def _simulate_oil_idbh(params: Dict[str, Any]) -> Dict[str, Any]:
    dbb = bool(params.get("double_block_bleed", False))
    pt_online = bool(params.get("residual_pressure_monitor", False))
    ai_mon = bool(params.get("ai_monitoring", False))
    purge_work = bool(params.get("purge_before_work", False))
    gas_test = bool(params.get("continuous_gas_test", False))

    n_pts = 325  # 0 to 54 h at 10 min intervals
    t_list = [round(k / 6.0, 4) for k in range(n_pts)]
    t_labels = [f"Hour {t:.1f}" for t in t_list]

    def idx_at_hour(h: float) -> int:
        return min(n_pts - 1, max(0, int(round(h * 6))))

    events: List[Dict[str, Any]] = [
        {
            "i": 0,
            "t_label": t_labels[0],
            "type": "info",
            "text": (
                "Indirect Bath Heater isolated (Double-block & bleed LOTO verified)."
                if dbb
                else "Indirect Bath Heater marked isolated (single isolation valve — passing slowly)."
            ),
        }
    ]

    # Determine re-isolation trigger before hot work
    trigger_idx = None
    reiso_idx = None
    if not dbb:
        if pt_online:
            # First point where true_coil_pressure_psi (35 * t / 48) > 5 psi -> ~6.9 h -> idx 42 (Hour 7.0)
            trigger_idx = next((k for k, t in enumerate(t_list) if 35.0 * min(1.0, t / 48.0) > 5.0), idx_at_hour(7.0))
            reiso_idx = min(n_pts - 1, trigger_idx + 12)  # +2 h
            events.append({
                "i": trigger_idx,
                "t_label": t_labels[trigger_idx],
                "type": "warn",
                "text": "Residual pressure creeping (>5 psi) — isolation valve passing!",
            })
            events.append({
                "i": reiso_idx,
                "t_label": t_labels[reiso_idx],
                "type": "success",
                "text": "Valve re-isolated and coil purged safely before maintenance.",
            })
        elif ai_mon:
            trigger_idx = idx_at_hour(1.0)
            reiso_idx = idx_at_hour(3.0)
            events.append({
                "i": trigger_idx,
                "t_label": t_labels[trigger_idx],
                "type": "ai",
                "text": "AI Layer 2: pressure transmitter frozen at 0.0 while bath temperature changes — verify with local gauge.",
            })
            events.append({
                "i": reiso_idx,
                "t_label": t_labels[reiso_idx],
                "type": "success",
                "text": "Local gauge check caught valve passing — heater re-isolated & purged.",
            })

    purge_idx = idx_at_hour(46.0)
    hotwork_idx = idx_at_hour(48.0)
    resume_idx = idx_at_hour(50.0)

    if purge_work and not dbb and reiso_idx is None:
        events.append({
            "i": purge_idx,
            "t_label": t_labels[purge_idx],
            "type": "success",
            "text": "Pre-work nitrogen/gas-free purge completed — hydrocarbon LEL cleared below 2%.",
        })

    # Precompute arrays
    bath_s, true_p_s, tx_p_s, lel_s = [], [], [], []
    valve_states, hot_states, fire_states, phases = [], [], [], []

    fire_active = False
    suspended = False
    hazard_rec_label = "Prevented (DBB)" if dbb else None
    if trigger_idx is not None:
        hazard_rec_label = t_labels[trigger_idx]

    cur_true_p = 0.0
    cur_lel = 0.0

    for k, t in enumerate(t_list):
        if k == 0:
            phase = "Heater isolated"
        elif k < hotwork_idx:
            phase = "Isolated / cooling"
        else:
            phase = "Maintenance hot work"

        # Update pressure and LEL evolution
        if dbb:
            cur_true_p = 0.0
            cur_lel = 0.0
            v_state = "Double-block & bleed"
        elif reiso_idx is not None and k >= reiso_idx:
            cur_true_p = 0.0
            cur_lel = 0.0
            v_state = "Closed"
        elif suspended and k >= resume_idx:
            cur_true_p = 0.0
            cur_lel = 0.0
            v_state = "Closed"
        else:
            cur_true_p = min(35.0, 35.0 * (t / 48.0))
            if k < idx_at_hour(4.0):
                cur_lel = 0.0
            elif purge_work and k >= purge_idx:
                cur_lel = 0.57 * (t - 46.0)
            else:
                cur_lel = min(40.0, 0.57 * (t - 4.0))
            v_state = "Passing"

        # Snapshot at hot work start (Hour 48.0)
        if k == hotwork_idx:
            lel_at_work = cur_lel
            p_at_work = cur_true_p
            if gas_test and cur_lel >= 10.0:
                suspended = True
                hazard_rec_label = t_labels[k]
                events.append({
                    "i": k,
                    "t_label": t_labels[k],
                    "type": "warn",
                    "text": f"Gas test {cur_lel:.1f}% LEL — hot work suspended, area purged and valve re-isolated.",
                })
                events.append({
                    "i": resume_idx,
                    "t_label": t_labels[resume_idx],
                    "type": "success",
                    "text": "Gas test 0.0% LEL — maintenance hot work resumed safely.",
                })
            elif cur_lel >= 10.0:
                fire_active = True
                events.append({
                    "i": k,
                    "t_label": t_labels[k],
                    "type": "danger",
                    "text": f"FIRE — hot work ignited {cur_lel:.1f}% LEL leaked hydrocarbon vapour!",
                })
            else:
                events.append({
                    "i": k,
                    "t_label": t_labels[k],
                    "type": "success",
                    "text": f"Maintenance hot work started safely (LEL {cur_lel:.1f}% < 10% threshold).",
                })
                if hazard_rec_label is None and purge_work:
                    hazard_rec_label = t_labels[purge_idx]

        # Bath temperature
        base_temp = 25.0 + 60.0 * math.exp(-t / 10.0)
        if fire_active:
            frac = min(1.0, (t - 48.0) / 1.0)
            b_temp = base_temp + (650.0 - base_temp) * frac
        else:
            b_temp = base_temp

        tx_p = cur_true_p if pt_online else 0.0

        if k < hotwork_idx:
            hw_state = "no"
        elif suspended and k < resume_idx:
            hw_state = "suspended"
        else:
            hw_state = "yes"

        bath_s.append(round(b_temp, 1))
        true_p_s.append(round(cur_true_p, 2))
        tx_p_s.append(round(tx_p, 2))
        lel_s.append(round(cur_lel, 2))
        valve_states.append(v_state)
        hot_states.append(hw_state)
        fire_states.append("yes" if fire_active else "no")
        phases.append(phase)

    lel_start = lel_s[hotwork_idx]
    p_start = true_p_s[hotwork_idx]
    if hazard_rec_label is None:
        hazard_rec_label = "Not detected"

    if fire_active:
        outcome = {
            "status": "FIRE",
            "severity": "danger",
            "headline": "FIRE — Hydrocarbon Vapour Ignited During Hot Work",
            "detail": (
                f"With the pressure transmitter frozen at 0.0 psi, a passing valve built up "
                f"{p_start:.1f} psi and {lel_start:.1f}% LEL by Hour 48.0, igniting at maintenance."
            ),
            "event_index": hotwork_idx,
            "metrics": [
                {"label": "LEL at hot-work start (%)", "value": f"{lel_start:.1f}%"},
                {"label": "Residual pressure at work start (psi)", "value": f"{p_start:.1f} psi"},
                {"label": "Hazard recognised at", "value": "Not detected"},
                {"label": "Outcome", "value": "FIRE"},
            ],
        }
    else:
        outcome = {
            "status": "SAFE",
            "severity": "success",
            "headline": "SAFE — Maintenance Completed Without Ignition",
            "detail": (
                f"Hydrocarbon LEL at work start was {lel_start:.1f}% (or stopped at 0.0% after purge/DBB). "
                f"Safeguard triggered at: {hazard_rec_label}."
            ),
            "event_index": int(trigger_idx if trigger_idx is not None else hotwork_idx),
            "metrics": [
                {"label": "LEL at hot-work start (%)", "value": f"{lel_start:.1f}%"},
                {"label": "Residual pressure at work start (psi)", "value": f"{p_start:.1f} psi"},
                {"label": "Hazard recognised at", "value": hazard_rec_label},
                {"label": "Outcome", "value": "SAFE"},
            ],
        }

    return {
        "case_id": "oil_idbh",
        "dt_label": "h",
        "t": t_list,
        "t_labels": t_labels,
        "series": {
            "bath_temp_c": bath_s,
            "true_coil_pressure_psi": true_p_s,
            "transmitter_pressure_psi": tx_p_s,
            "lel_pct": lel_s,
        },
        "states": {
            "valve_state": valve_states,
            "hot_work": hot_states,
            "fire": fire_states,
        },
        "phase": phases,
        "events": events,
        "outcome": outcome,
        "params": {
            "double_block_bleed": dbb,
            "residual_pressure_monitor": pt_online,
            "ai_monitoring": ai_mon,
            "purge_before_work": purge_work,
            "continuous_gas_test": gas_test,
        },
    }


def simulate_case(case_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    if case_id not in AS_HAPPENED:
        raise ValueError(f"Unknown case_id: {case_id}")
    merged = dict(AS_HAPPENED[case_id])
    if params:
        merged.update(params)
    if case_id == "oisd":
        return _simulate_oisd(merged)
    if case_id == "bollsta":
        return _simulate_bollsta(merged)
    return _simulate_oil_idbh(merged)
