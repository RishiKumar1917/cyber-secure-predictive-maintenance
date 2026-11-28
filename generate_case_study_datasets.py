import json
from pathlib import Path
import pandas as pd
from case_study_sim import ALL_FIXES, AS_HAPPENED, CASE_META, simulate_case


def main():
    out_dir = Path("case_studies")
    out_dir.mkdir(exist_ok=True)

    summary = {}
    table_rows = []

    for cid in ["oisd", "bollsta", "oil_idbh"]:
        res_as = simulate_case(cid, AS_HAPPENED[cid])
        res_fix = simulate_case(cid, ALL_FIXES[cid])

        for tag, res in [("as_happened", res_as), ("with_fixes", res_fix)]:
            data = {
                "t": res["t"],
                "t_label": res["t_labels"],
                "phase": res["phase"],
            }
            data.update(res["series"])
            data.update(res["states"])
            df_out = pd.DataFrame(data)
            df_out.to_csv(out_dir / f"{cid}_{tag}.csv", index=False)

        summary[cid] = {
            "title": CASE_META[cid]["title"],
            "as_happened": res_as["outcome"],
            "with_fixes": res_fix["outcome"],
        }
        table_rows.append((cid, res_as["outcome"]["status"], res_fix["outcome"]["status"]))

    with open(out_dir / "case_study_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("=" * 64)
    print(f"{'Case ID':15s} | {'As-Happened Outcome':20s} | {'With-Fixes Outcome':20s}")
    print("-" * 64)
    for cid, st_as, st_fix in table_rows:
        print(f"{cid:15s} | {st_as:20s} | {st_fix:20s}")
    print("=" * 64)
    print(f"[SUCCESS] Wrote 6 CSV datasets and case_study_summary.json to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
