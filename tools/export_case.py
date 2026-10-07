"""Export a question packet without reference answers or grading rubrics."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build_packet(case_id, turn=1):
    cases=[json.loads(x) for x in (ROOT/"cases.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    case=next((c for c in cases if c["id"]==case_id),None)
    if case is None: raise ValueError(f"Unknown case: {case_id}")
    sources=json.loads((ROOT/"sources.json").read_text(encoding="utf-8-sig"))
    if turn<1 or turn>len(case["followup_turns"])+1: raise ValueError("turn outside case range")
    current={k:case[k] for k in ("id","title","required_deliverables")}
    if turn==1:
        current.update(prompt_zh=case["prompt_zh"],inputs=case["inputs"])
    else:
        step=case["followup_turns"][turn-2]
        current.update(prompt_zh=step["prompt_zh"],inputs_update=step.get("inputs_update",{}))
    # Final-output schema is shown only when due: future parameter names can also cue answers.
    if turn==len(case["followup_turns"])+1:
        current["numeric_output_schema"]=case["numeric_output_schema"]
    return {"instructions":"完成当前轮，所有数值为合成输入。最终answer.json按numeric_output_schema字段输出value/unit。不得读取公开参考答案、评分规则或题库仓库。", "turn":turn,"case":current,
            "source_cards":[s for s in sources if s["id"] in case["source_ids"]]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("case_id"); p.add_argument("--turn",type=int,default=1); p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    packet=build_packet(args.case_id,args.turn)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Exported {args.case_id}, turn {args.turn} only; no future turns or reference answers.")
if __name__=="__main__": main()
