"""Validate suite structure, scoring weights, and independent numerical oracles."""
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path
from oracles import oracle
from input_assets import checked_asset
ROOT=Path(__file__).resolve().parents[1]

def load_suite():
    cases=[json.loads(line) for line in (ROOT/"cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    read=lambda name:json.loads((ROOT/name).read_text(encoding="utf-8-sig"))
    return cases,read("reference_answers.json"),read("rubrics.json"),read("sources.json"),read("benchmark.json")

def validate(cases,refs,rubrics,sources,manifest):
    errors=[]; count=0
    ids=[c["id"] for c in cases]; expected=[f"LAT-{i:02}" for i in range(1,manifest["case_count"]+1)]
    if ids!=expected: errors.append("case IDs must be unique, ordered and match manifest")
    if set(refs)!=set(ids) or set(rubrics)!=set(ids): errors.append("reference/rubric ID mismatch")
    if len(sources)!=manifest["source_count"]: errors.append("source count mismatch")
    if manifest["case_count"]!=len(cases): errors.append("case count mismatch")
    if sum(manifest["weights"].values())!=100: errors.append("global weights !=100")
    source_ids={s["id"] for s in sources}
    if len(source_ids)!=len(sources): errors.append("duplicate source ID")
    cutoff=date.fromisoformat(manifest["research_cutoff"])
    for s in sources:
        if not s["url"].startswith("https://"): errors.append(f"{s['id']}: non-HTTPS source")
        if s.get("published_on") and date.fromisoformat(s["published_on"])>cutoff: errors.append(f"{s['id']}: source after cutoff")
        if not s.get("supports_zh") or not s.get("limits_zh"): errors.append(f"{s['id']}: missing source applicability")
    tracks=manifest["tracks"]
    assigned=[cid for track in tracks.values() for cid in track["case_ids"]]
    if len(assigned)!=len(set(assigned)) or set(assigned)!=set(ids): errors.append("track membership mismatch")
    core=[c for c in cases if c.get("track")=="core"]
    counts=Counter(c["stratum"] for c in core)
    if counts!={k:4 for k in manifest["strata"]}: errors.append("expected five strata, four cases each")
    metrics=set(manifest["weights"])-{"efficiency"}
    for c in cases:
        cid=c["id"]
        if c.get("track") not in tracks or cid not in tracks[c["track"]]["case_ids"]: errors.append(f"{cid}: invalid track")
        if c.get("track")=="research_challenge":
            if not c.get("acceptance_contract") or not c.get("trial_budget") or not c.get("challenge_family"): errors.append(f"{cid}: incomplete challenge contract")
            if not refs.get(cid,{}).get("numeric"): errors.append(f"{cid}: missing independent numeric anchors")
        for asset in c.get("input_assets",[]):
            try: checked_asset(asset)
            except (ValueError,OSError) as exc: errors.append(f"{cid}: {exc}")
        if not c["inputs"].get("synthetic"): errors.append(f"{cid}: missing synthetic label")
        if c["split"]!="public_development": errors.append(f"{cid}: public cases not a hidden test")
        if not set(c["source_ids"])<=source_ids or not c["source_ids"]: errors.append(f"{cid}: source mapping missing")
        if c["stratum"]=="multiturn_constraints":
            if len(c["followup_turns"])!=2: errors.append(f"{cid}: expected two followups")
            if "final" in c["inputs"]: errors.append(f"{cid}: future state leaked in initial inputs")
            if any(t["turn"]!=i+2 or not t.get("inputs_update") for i,t in enumerate(c["followup_turns"])): errors.append(f"{cid}: malformed scripted turn")
        if not c["required_deliverables"]: errors.append(f"{cid}: no deliverables")
        if cid not in rubrics or cid not in refs: continue
        dims=rubrics[cid]["criteria"]
        if set(dims)!=metrics: errors.append(f"{cid}: metric coverage mismatch")
        for metric,checks in dims.items():
            if sum(item["points"] for item in checks)!=100: errors.append(f"{cid}/{metric}: checks !=100")
            if len({item["id"] for item in checks})!=len(checks): errors.append(f"{cid}/{metric}: duplicate check ID")
        if not rubrics[cid]["fatal_errors"] or not refs[cid]["assertions"]: errors.append(f"{cid}: missing manual review")
        values=oracle(c); numeric=refs[cid]["numeric"]
        if set(values)!=set(numeric) or set(numeric)!=set(c["numeric_output_schema"]): errors.append(f"{cid}: scalar key mismatch oracle={set(values)^set(numeric)}")
        for key,ref in numeric.items():
            count+=1
            if not isinstance(ref["value"],(int,float)) or isinstance(ref["value"],bool) or not math.isfinite(ref["value"]): errors.append(f"{cid}/{key}: invalid scalar")
            if ref["abs_tol"]<0 or ref.get("rel_tol",0)<0: errors.append(f"{cid}/{key}: negative tolerance")
            schema=c["numeric_output_schema"].get(key,{})
            if any(schema.get(k)!=ref[k] for k in ("unit","abs_tol","rel_tol")): errors.append(f"{cid}/{key}: public schema mismatch")
            if key in values and not math.isclose(ref["value"],values[key],rel_tol=1e-10,abs_tol=1e-10): errors.append(f"{cid}/{key}: reference={ref['value']} oracle={values[key]}")
    return errors,count

def main():
    suite=load_suite();errors,count=validate(*suite)
    print(json.dumps({"status":"fail" if errors else "pass","cases":len(suite[0]),"tracks":{k:len(v['case_ids']) for k,v in suite[4]['tracks'].items()},"sources":len(suite[3]),"independent_numeric_anchors":count,"model_runs":suite[4]['model_runs_completed'],"cad_artifacts_verified":False,"errors":errors},ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)
if __name__=="__main__": main()
