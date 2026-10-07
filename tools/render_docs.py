"""Render readable question book and answer key from canonical JSON. Offline."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    cases=[json.loads(x) for x in (ROOT/"cases.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    refs=json.loads((ROOT/"reference_answers.json").read_text(encoding="utf-8"))
    sources={s["id"]:s for s in json.loads((ROOT/"sources.json").read_text(encoding="utf-8-sig"))}
    rubrics=json.loads((ROOT/"rubrics.json").read_text(encoding="utf-8"))
    manifest=json.loads((ROOT/"benchmark.json").read_text(encoding="utf-8"));version=manifest["version"]
    counts={name:sum(c.get("track")==name for c in cases) for name in manifest["tracks"]}
    q=[f"# 公开测试题 v{version}", "", f"{len(cases)}题均为公开开发/复现题，不是保密盲测。{counts.get('core',0)}道基础题、{counts.get('research_challenge',0)}道研究挑战与{counts.get('engineering_application',0)}道工程应用分别计分。前两类数值fixture为自编合成数据；工程应用使用哈希固定的ATLAS数据库快照，工程场景为合成，反馈按各附件provenance区分真实实验与合成数据。数据库计算或外推估算不能自动视为实测。", "", "运行方式见[协议](PROTOCOL.md)。数值输出answer.json使用`{字段: {value: 数值, unit: 单位}}`；字段清单在每题末尾。每题新建会话；后续轮次仅在上一轮输出后依次发送。", ""]
    a=[f"# 参考答案与人工验收 v{version}", "", "不将此文件或rubrics/reference_answers提供给被测模型。文件虽公开，开发后不能宣称同题盲测。", "", "数值参考已离线核算。LAT-24的损坏输入已生成；没有被测模型的完整CAD交付或成绩。研究挑战最终设计须实做并重读验收。", ""]
    hard=[f"# 研究挑战题 v{version}","","LAT-21—24单独计分。要求实际几何、求解与操作记录，数值锚点正确不代表任务完成。仍是公开开发题，未验证模型区分度。","","[运行与评分协议](PROTOCOL.md) · [全部题目](QUESTIONS.zh-CN.md)",""]
    engineering=[f"# 数据库支撑的工程应用题 v{version}","","LAT-25—32单独计分。以同一份可核查ATLAS数据库快照为两组共同证据，考查载荷换算、结构性能估计、屈服判读及反馈修正。工程场景为合成，反馈按各附件provenance区分真实实验与合成数据，数据库内仿真和外推记录保持各自来源标签。","","数据库中的0.5%偏移屈服是本题采用的整体曲线指标，不能直接证明局部首屈服位置或安全认证。正确使用工具可能改善准确性和交付，但不预设ATLAS获胜。","","[运行与评分协议](PROTOCOL.md) · [全部题目](QUESTIONS.zh-CN.md)",""]
    for c in cases:
        cid=c["id"]
        start=len(q)
        q += [f"## {cid} · {c['title']}","",f"类别：`{c['stratum']}` · 难度：{c['difficulty']} · 主题：{', '.join(c['topics'])}","",c["prompt_zh"],"","### 输入","","```json",json.dumps(c["inputs"],ensure_ascii=False,indent=2),"```",""]
        if c.get("database_provenance"):
            q += ["### 数据来源与场景性质","","```json",json.dumps({"scenario_origin":c.get("scenario_origin"),"database_provenance":c["database_provenance"]},ensure_ascii=False,indent=2),"```",""]
        if c["followup_turns"]:
            q += ["### 固定后续轮次",""]
            for i,t in enumerate(c["followup_turns"],2):
                q += [f"#### 第{i}轮","",t if isinstance(t,str) else t["prompt_zh"],""]
                if isinstance(t,dict) and t.get("inputs_update"):
                    q += ["本轮参数修改：","","```json",json.dumps(t["inputs_update"],ensure_ascii=False,indent=2),"```",""]
        if c.get("input_assets"):
            q += ["### 实际输入附件","",*[f"- [{asset['path']}](../{asset['path']}) · SHA256 `{asset['sha256']}` · 自第{asset.get('available_from_turn',1)}轮可见" for asset in c["input_assets"]],""]
        q += ["### 交付","",*["- "+d for d in c["required_deliverables"]],""]
        if c.get("acceptance_contract"):
            q += ["### 可执行验收要求与试跑预算","","```json",json.dumps({"acceptance_contract":c["acceptance_contract"],"trial_budget":c.get("trial_budget")},ensure_ascii=False,indent=2),"```",""]
        q += ["### 数值输出字段（不是参考答案）","","```json",json.dumps(c["numeric_output_schema"],ensure_ascii=False,indent=2),"```","","来源与适用范围："+"；".join(f"[{sid}]({sources[sid]['url']})" for sid in c["source_ids"])+"。", ""]
        if c.get("track")=="research_challenge": hard+=q[start:]
        if c.get("track")=="engineering_application": engineering+=q[start:]
        r=refs[cid]
        a += [f"## {cid} · {c['title']}","","```json",json.dumps(r["numeric"],ensure_ascii=False,indent=2),"```","",*["- "+s for s in r["assertions"]],"",*["- "+s for s in r.get("review_notes",[])],""]
        for metric,checks in rubrics[cid]["criteria"].items():
            a += [f"### {metric}","",*[f"- `{ck['id']}` ({ck['points']}%)：{ck['criterion']}" for ck in checks],""]
        a += ["致命错误（该次任务总分为0）：","",*["- "+s for s in rubrics[cid]["fatal_errors"]],""]
    (ROOT/"docs"/"QUESTIONS.zh-CN.md").write_text("\n".join(q).rstrip()+"\n",encoding="utf-8")
    (ROOT/"docs"/"REFERENCE.zh-CN.md").write_text("\n".join(a).rstrip()+"\n",encoding="utf-8")
    (ROOT/"docs"/"CHALLENGES.zh-CN.md").write_text("\n".join(hard).rstrip()+"\n",encoding="utf-8")
    (ROOT/"docs"/"ENGINEERING.zh-CN.md").write_text("\n".join(engineering).rstrip()+"\n",encoding="utf-8")
    print(f"Rendered {len(cases)} questions and references.")
if __name__=="__main__": main()
