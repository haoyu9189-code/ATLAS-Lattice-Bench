"""Check only declared scalar outputs; does not assign an engineering score."""
import argparse
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def check(expected, submitted):
    results={}
    if not isinstance(submitted,dict):
        return {"_format":{"pass":False,"reason":"submission must be an object"}}
    for key, ref in expected.items():
        got=submitted.get(key,{})
        value=got.get("value") if isinstance(got,dict) else None
        unit=got.get("unit") if isinstance(got,dict) else None
        valid=isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
        ok=bool(valid and unit==ref["unit"] and math.isclose(value,ref["value"],abs_tol=ref["abs_tol"],rel_tol=ref.get("rel_tol",0)))
        results[key]={"pass":ok,"expected":ref,"submitted":got}
    return results

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("case_id"); p.add_argument("submission",type=Path)
    args=p.parse_args()
    refs=json.loads((ROOT/"reference_answers.json").read_text(encoding="utf-8"))
    if args.case_id not in refs: p.error("unknown case_id")
    submitted=json.loads(args.submission.read_text(encoding="utf-8-sig"))
    checks=check(refs[args.case_id]["numeric"],submitted)
    passed=all(item["pass"] for item in checks.values())
    print(json.dumps({"case_id":args.case_id,"numeric_only_pass":passed,"not_a_total_score":True,"checks":checks},ensure_ascii=False,indent=2))
    raise SystemExit(0 if passed else 1)
if __name__=="__main__": main()
