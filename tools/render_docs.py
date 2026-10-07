"""Render readable question book and answer key from canonical JSON. Offline."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    cases=[json.loads(x) for x in (ROOT/"cases.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    refs=json.loads((ROOT/"reference_answers.json").read_text(encoding="utf-8"))
    sources={s["id"]:s for s in json.loads((ROOT/"sources.json").read_text(encoding="utf-8-sig"))}
    rubrics=json.loads((ROOT/"rubrics.json").read_text(encoding="utf-8"))
    q=["# 公开测试题 v0.1.0", "", "20题均为公开开发/复现题，不是保密盲测。全部数值fixture为自编合成数据；论文仅作为研究背景。", "", "运行方式见[协议](PROTOCOL.md)。数值输出answer.json使用`{字段: {value: 数值, unit: 单位}}`；字段清单在每题末尾。每题新建会话；后续轮次仅在上一轮输出后依次发送。", ""]
    a=["# 参考答案与人工验收 v0.1.0", "", "不将此文件或rubrics/reference_answers提供给被测模型。文件虽公开，开发后不能宣称同题盲测。", "", "数值参考已离线核算；CAD题仅完成任务定义与参考几何量校核，尚无模型生成产物或制造试验。", ""]
    for c in cases:
        cid=c["id"]
        q += [f"## {cid} · {c['title']}","",f"类别：`{c['stratum']}` · 难度：{c['difficulty']} · 主题：{', '.join(c['topics'])}","",c["prompt_zh"],"","### 输入","","```json",json.dumps(c["inputs"],ensure_ascii=False,indent=2),"```",""]
        if c["followup_turns"]:
            q += ["### 固定后续轮次",""]
            for i,t in enumerate(c["followup_turns"],2):
                q += [f"#### 第{i}轮","",t if isinstance(t,str) else t["prompt_zh"],""]
                if isinstance(t,dict) and t.get("inputs_update"):
                    q += ["本轮参数修改：","","```json",json.dumps(t["inputs_update"],ensure_ascii=False,indent=2),"```",""]
        q += ["### 交付","",*["- "+d for d in c["required_deliverables"]],"","### 数值输出字段（不是参考答案）","","```json",json.dumps(c["numeric_output_schema"],ensure_ascii=False,indent=2),"```","","研究背景："+"；".join(f"[{sid}]({sources[sid]['url']})" for sid in c["source_ids"])+"。", ""]
        r=refs[cid]
        a += [f"## {cid} · {c['title']}","","```json",json.dumps(r["numeric"],ensure_ascii=False,indent=2),"```","",*["- "+s for s in r["assertions"]],"",*["- "+s for s in r.get("review_notes",[])],""]
        for metric,checks in rubrics[cid]["criteria"].items():
            a += [f"### {metric}","",*[f"- `{ck['id']}` ({ck['points']}%)：{ck['criterion']}" for ck in checks],""]
        a += ["致命错误（该次任务总分为0）：","",*["- "+s for s in rubrics[cid]["fatal_errors"]],""]
    (ROOT/"docs"/"QUESTIONS.zh-CN.md").write_text("\n".join(q).rstrip()+"\n",encoding="utf-8")
    (ROOT/"docs"/"REFERENCE.zh-CN.md").write_text("\n".join(a).rstrip()+"\n",encoding="utf-8")
    print(f"Rendered {len(cases)} questions and references.")
if __name__=="__main__": main()
