from case_study_sim import ALL_FIXES, AS_HAPPENED, CASE_META, simulate_case


def check_oisd():
    cases = [
        ("oisd: as_happened", {}, "BLOWOUT"),
        ("oisd: all_fixes", ALL_FIXES["oisd"], "SAFE"),
        ("oisd: only fluid_sg 1.15", {"fluid_sg": 1.15}, "SAFE"),
        ("oisd: only fix_pore_estimate", {"fix_pore_estimate": True}, "SAFE"),
        ("oisd: only trip_tank_online", {"trip_tank_online": True}, "CONTROLLED"),
        ("oisd: only ai_monitoring", {"ai_monitoring": True}, "CONTROLLED"),
        ("oisd: only shear_ram", {"shear_ram": True}, "CONTROLLED"),
        ("oisd: only cement_good", {"cement_good": True}, "BLOWOUT"),
    ]
    for label, p, expected in cases:
        res = simulate_case("oisd", p)
        actual = res["outcome"]["status"]
        assert actual == expected, f"{label} expected {expected}, got {actual}"
        print(f"OK | {label:36s} -> {actual} (gain={res['series']['well_gain_bbl'][-1]:.1f} bbl)")


def check_bollsta():
    res_base = simulate_case("bollsta", AS_HAPPENED["bollsta"])
    rel = res_base["series"]["cumulative_release_kg"][-1]
    assert res_base["outcome"]["status"] == "RELEASE", f"Expected RELEASE, got {res_base['outcome']['status']}"
    assert 930.0 * 0.95 <= rel <= 930.0 * 1.05, f"Expected ~930 kg (±5%), got {rel}"
    print(f"OK | {'bollsta: as_happened':36s} -> RELEASE ({rel:.1f} kg)")

    cases = [
        ("bollsta: all_fixes", ALL_FIXES["bollsta"], "SAFE"),
        ("bollsta: only log_calibrated", {"log_calibrated": True}, "SAFE"),
        ("bollsta: only outer_barrier_test", {"outer_barrier_test": True}, "SAFE"),
        ("bollsta: only ai_monitoring", {"ai_monitoring": True}, "SAFE"),
        ("bollsta: only dp_trended", {"dp_trended": True}, "RELEASE"),
        ("bollsta: only gauge_maintained", {"gauge_maintained": True}, "RELEASE"),
        ("bollsta: dp_trended + gauge_maintained", {"dp_trended": True, "gauge_maintained": True}, "SAFE"),
    ]
    for label, p, expected in cases:
        res = simulate_case("bollsta", p)
        actual = res["outcome"]["status"]
        assert actual == expected, f"{label} expected {expected}, got {actual}"
        print(f"OK | {label:36s} -> {actual} (rel={res['series']['cumulative_release_kg'][-1]:.1f} kg)")


def check_oil_idbh():
    cases = [
        ("oil_idbh: as_happened", {}, "FIRE"),
        ("oil_idbh: all_fixes", ALL_FIXES["oil_idbh"], "SAFE"),
        ("oil_idbh: only double_block_bleed", {"double_block_bleed": True}, "SAFE"),
        ("oil_idbh: only residual_pressure_monitor", {"residual_pressure_monitor": True}, "SAFE"),
        ("oil_idbh: only ai_monitoring", {"ai_monitoring": True}, "SAFE"),
        ("oil_idbh: only purge_before_work", {"purge_before_work": True}, "SAFE"),
        ("oil_idbh: only continuous_gas_test", {"continuous_gas_test": True}, "SAFE"),
    ]
    for label, p, expected in cases:
        res = simulate_case("oil_idbh", p)
        actual = res["outcome"]["status"]
        assert actual == expected, f"{label} expected {expected}, got {actual}"
        print(f"OK | {label:36s} -> {actual}")


def check_schema_consistency():
    for cid in CASE_META:
        r1 = simulate_case(cid, AS_HAPPENED[cid])
        r2 = simulate_case(cid, ALL_FIXES[cid])
        l1 = [m["label"] for m in r1["outcome"]["metrics"]]
        l2 = [m["label"] for m in r2["outcome"]["metrics"]]
        assert l1 == l2, f"{cid} metric labels differ: {l1} vs {l2}"
        n = len(r1["t"])
        for k, arr in r1["series"].items():
            assert len(arr) == n, f"{cid} series {k} len {len(arr)} != {n}"
        for k, arr in r1["states"].items():
            assert len(arr) == n, f"{cid} states {k} len {len(arr)} != {n}"
        # JSON serialisability check
        import json
        json.dumps(r1)
        json.dumps(r2)
    print("OK | Schema consistency & JSON serialisability verified for all 3 cases")


if __name__ == "__main__":
    check_oisd()
    check_bollsta()
    check_oil_idbh()
    check_schema_consistency()
    print("\nALL CASE STUDY SIMULATION TESTS PASSED.")
