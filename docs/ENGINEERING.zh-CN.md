# 数据库支撑的工程应用题 v0.3.0

LAT-25—32单独计分。以同一份可核查ATLAS数据库快照为两组共同证据，考查载荷换算、结构性能估计、屈服判读及反馈修正。工程场景为合成，反馈按各附件provenance区分真实实验与合成数据，数据库内仿真和外推记录保持各自来源标签。

数据库中的0.5%偏移屈服是本题采用的整体曲线指标，不能直接证明局部首屈服位置或安全认证。正确使用工具可能改善准确性和交付，但不预设ATLAS获胜。

[运行与评分协议](PROTOCOL.md) · [全部题目](QUESTIONS.zh-CN.md)

## LAT-25 · PA12支承块：全曲线载荷—位移与偏移屈服

类别：`database_engineering` · 难度：hard · 主题：force_displacement_and_offset_yield, database_evidence, structural_performance, yield_feedback

为一个25 mm立方Kelvin点阵支承块出具准静态轴压估算。使用指定N5完整曲线，沿首次达到的加载分支逐段线性插值得到三个载荷的首次达到位移，不能把屈服后的点都按F/k算。计算初始刚度、库定义的0.5%偏移屈服力/位移、筛查允许载荷及压到20%应变的吸收能量。偏移屈服按库的首次差值由正转非正后的保存采样点规则核对，不能自行换成0.2%或插值交点。将整条原曲线换算成F-u CSV，标注三个工况与偏移屈服点；解释800 N工况能确认什么。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p4_4__N5"
    ]
  },
  "record_id": "Kelvin_5_0p4_4__N5",
  "load_levels_N": [
    100,
    400,
    800
  ],
  "safety_factor": 1.5,
  "energy_end_strain": 0.2,
  "boundary_conditions": "uniform quasi-static axial compression; nominal 25 mm cube; match of actual fixtures is unverified",
  "yield_offset_strain": 0.005,
  "yield_sampling_rule": "saved first sample after positive-to-nonpositive offset-line difference; do not interpolate intersection"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- force_displacement.csv：完整F-u曲线、单位及屈服标记
- load_feedback.json：三个载荷逐项反馈与允许载荷比较

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "effective_modulus_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "stiffness_N_per_mm": {
    "unit": "N/mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "offset_yield_force_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "offset_yield_displacement_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "screening_allowable_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "displacement_load1_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "displacement_load2_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "displacement_load3_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "absorbed_energy_J": {
    "unit": "J",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "load3_yield_ratio": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-26 · 六拓扑柔顺支承：刚度—位移—屈服约束选型

类别：`database_engineering` · 难度：hard · 主题：constrained_structure_selection, database_evidence, structural_performance, yield_feedback

从六个同包络25 mm立方N5候选中，按给定线弹性初筛模型筛选400 N支承：F/k不得超过位移上限，整体偏移屈服力不得小于安全系数乘载荷。在可行者中选择刚度最小的一项以提高柔顺性，刚度相同按record_id排序。输出全部候选的刚度、位移、屈服裕度和淘汰原因；不能仅选最高模量或最高强度。再说明未提供质量/局部应力证据如何限制最终选型。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p4_4__N5",
      "Octet_truss_5_0p4_4__N5",
      "FCC_5_0p4_4__N5",
      "Auxetic_5_0p4_4__N5",
      "AFCC_5_0p4_4__N5",
      "BCC_5_0p4_4__N5"
    ]
  },
  "candidate_ids": [
    "Kelvin_5_0p4_4__N5",
    "Octet_truss_5_0p4_4__N5",
    "FCC_5_0p4_4__N5",
    "Auxetic_5_0p4_4__N5",
    "AFCC_5_0p4_4__N5",
    "BCC_5_0p4_4__N5"
  ],
  "service_force_N": 400,
  "safety_factor": 1.5,
  "max_displacement_mm": 0.3,
  "selection_rule": "minimize stiffness among candidates passing both stated proxy constraints; ties lexicographic record_id"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- selection.json：选中record_id和目标函数
- candidate_comparison.csv：六候选逐约束数值和淘汰原因

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "feasible_count": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "selected_stiffness_N_per_mm": {
    "unit": "N/mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "selected_offset_yield_force_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "selected_displacement_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "selected_yield_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-27 · 40 mm阵列：N5主体参考、尺寸证据与敏感性

类别：`database_engineering` · 难度：hard · 主题：bulk_proxy_and_size_evidence, database_evidence, structural_performance, yield_feedback

估算每轴8胞、单胞5 mm的Kelvin支承块在600 N下的响应。以当前参数N5的有效E和整体偏移屈服应力作主体参考，保留N5代理标签。再做E和屈服应力各降低10%的工程敏感性分析，给出不利位移和允许载荷；10%为客户指定扰动，不是数据库置信区间。独立核对Kelvin直接参考N4→N5的E和屈服相邻变化率，以及BCC是否真的有直接N5参考。解释它们是否足以证明当前参数N8误差小于5%。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p4_4__N5",
      "Kelvin_5_0p4_4__N4",
      "BCC_5_0p4_4__N5"
    ]
  },
  "record_id": "Kelvin_5_0p4_4__N5",
  "target_cells_per_axis": 8,
  "service_force_N": 600,
  "safety_factor": 1.5,
  "sensitivity_fraction": 0.1,
  "reference_asset": "fixtures/engineering/size_references.json"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见
- [fixtures/engineering/size_references.json](../fixtures/engineering/size_references.json) · SHA256 `02bfb1d630e4cb978e46ceb80542237fff7d9a61cbb550a1d4f2ab2323f4c8b7` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- size_evidence.json：各N的source_kind/run_id、相邻变化、适用范围和验证计划

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "target_cell_count": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "nominal_area_mm2": {
    "unit": "mm^2",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "proxy_stiffness_N_per_mm": {
    "unit": "N/mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "proxy_yield_force_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "sensitivity_low_allowable_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "sensitivity_high_displacement_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "reference_E_relative_change": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "reference_yield_relative_change": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "bcc_direct_n5_count": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-28 · 双点阵并联支承：载荷升级与设计反馈

类别：`database_engineering` · 难度：hard · 主题：parallel_load_redistribution, database_evidence, structural_performance, yield_feedback

两个25 mm高、各25×25 mm承压面积的点阵块并联支承刚性导向压板，压板被导向机构约束为纯平移，不发生转动；因此两块位移相同。使用给定数据库E形成两弹簧初筛模型，F_i=k_i·u。计算1000 N总载荷下位移、左右受力与裕度。系统筛查允许总载荷按各块线弹性外推至其整体偏移屈服力的最小共同位移，再除安全系数。输出并保存initial_state.json供后续载荷变更使用。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p4_4__N5",
      "Octet_truss_5_0p4_4__N5"
    ]
  },
  "left_record_id": "Kelvin_5_0p4_4__N5",
  "right_record_id": "Octet_truss_5_0p4_4__N5",
  "total_force_N": 1000,
  "safety_factor": 1.5,
  "model": "parallel axial springs under guided rigid pure-translation platen; linear screening only"
}
```

### 固定后续轮次

#### 第2轮

总载荷升级至2200 N。保留首轮输出，先按原结构作线弹性筛查并报告失效约束；再只允许把左侧Kelvin换成右侧同型号Octet，包络与材料不变，复算两支承的受力、位移和裕度。不得把超过整体偏移阈值后的线弹性力分配当真实塑性重分配。

本轮参数修改：

```json
{
  "total_force_N": 2200,
  "replacement_left_record_id": "Octet_truss_5_0p4_4__N5"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- initial_state.json：首轮冻结结果
- load_upgrade.json：原方案与授权改型的逐块受力/裕度和变化记录

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "initial_displacement_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "initial_left_force_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "initial_allowable_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "upgraded_original_left_force_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "upgraded_original_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "revised_displacement_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "revised_allowable_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "revised_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-29 · 偏心受压：宏观危险边缘与局部屈服证据

类别：`database_engineering` · 难度：hard · 主题：eccentric_loading_and_local_limits, database_evidence, structural_performance, yield_feedback

一个25 mm立方Kelvin块受到500 N偏心压力。先把它视为均质矩形连续体做名义截面初筛，Z=b·h²/6，σ边缘=F/A±F·e/Z，用保存的轴压整体偏移屈服应力作条件性的压缩筛查阈值。计算e=3 mm时两边缘应力、允许载荷和裕度，指出压缩最危险侧。再检查e=6 mm时无黏结压板是否仍满足全截面受压；如失去接触，不能继续将全截面公式当实际接触解。用户还要“哪根杆先屈服、最大塑性应变及屈曲载荷”，请明确现有数据能给什么、缺什么，并提交具体FE载荷/边界/输出请求。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p45_4__N5"
    ]
  },
  "record_id": "Kelvin_5_0p45_4__N5",
  "force_N": 500,
  "eccentricity_mm": 3,
  "secondary_eccentricity_mm": 6,
  "safety_factor": 1.5,
  "contact": "unbonded compression-only platen; full-section formula is a screening assumption"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- stress_screening.json：两偏心工况、危险边缘、接触有效性和unknown字段
- fea_request.json：复核真实局部屈服所需几何/本构/边界/网格/场输出

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "section_modulus_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "nominal_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "max_edge_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "min_edge_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "screening_allowable_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "yield_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "kern_limit_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "secondary_min_edge_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-30 · 制造半径偏差：邻点性能包络与最小改型

类别：`database_engineering` · 难度：hard · 主题：manufacturing_tolerance_feedback, database_evidence, structural_performance, yield_feedback

名义杆半径0.40 mm的Kelvin支承实测工艺偏差范围为±0.02 mm（题设工况）。使用同slider、同N5的0.35/0.40/0.45 mm三条数据库记录，在相邻半径间对E和整体偏移屈服应力作逐段线性插值；不外推，也不自选r²/r³幂律。估算450 N服役载荷的名义、最不利和最有利屈服裕度，以及最小半径下刚度。求在相同±0.02 mm公差下满足安全系数的最小名义半径，并核对其全部公差区间仍在记录支持范围内。输出可用于设计反馈的半径—性能表。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p35_4__N5",
      "Kelvin_5_0p4_4__N5",
      "Kelvin_5_0p45_4__N5"
    ]
  },
  "radius_records": [
    "Kelvin_5_0p35_4__N5",
    "Kelvin_5_0p4_4__N5",
    "Kelvin_5_0p45_4__N5"
  ],
  "nominal_radius_mm": 0.4,
  "radius_tolerance_mm": 0.02,
  "service_force_N": 450,
  "safety_factor": 1.5,
  "interpolation_rule": "piecewise linear in saved effective modulus and macro offset yield stress; no extrapolation"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- radius_sensitivity.csv：至少低/名义/高/建议半径及性能
- design_feedback.json：改型量、制造适用范围和额外验证需求

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "nominal_yield_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "low_radius_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "high_radius_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "low_stiffness_N_per_mm": {
    "unit": "N/mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "low_offset_yield_force_N": {
    "unit": "N",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "worst_yield_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "best_yield_margin": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "required_nominal_radius_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-31 · 换材料：保留结构弹性特性与屈服未知项

类别：`database_engineering` · 难度：hard · 主题：conditional_material_transfer, database_evidence, structural_performance, yield_feedback

希望保留Kelvin几何换一种材料。客户给定源母材E=1500 MPa、目标母材E=2600 MPa及两者密度；这些是题设待确认输入，并非从PA12数据库补出来的本构。只在小应变线弹性、相同几何/泊松比/边界且无屈曲或接触变化的假设下，使用E*/Es不变估算目标有效模量、轴向刚度和400 N下位移，同时给出相同实体几何的质量比。客户追问新材料屈服载荷、SEA和疲劳寿命，输出必要的unknown及需补的材料/结构验证，不得按E比例缩放这些量。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Kelvin_5_0p4_4__N5"
    ]
  },
  "record_id": "Kelvin_5_0p4_4__N5",
  "assumed_source_solid_E_MPa": 1500,
  "target_solid_E_MPa": 2600,
  "assumed_source_density_g_cm3": 1.01,
  "target_density_g_cm3": 1.2,
  "force_N": 400,
  "material_inputs_origin": "synthetic customer assumptions; neither source constitutive card nor target material certification is supplied"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- material_transfer.json：已估算弹性项、质量比、未知屈服/SEA/疲劳及逐项条件

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "normalized_modulus": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "elastic_scale_factor": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "target_effective_modulus_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "target_stiffness_N_per_mm": {
    "unit": "N/mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "elastic_displacement_mm": {
    "unit": "mm",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "mass_ratio_for_identical_geometry": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。

## LAT-32 · 真实压缩实验反馈：N4校正与N5顺序留出检验

类别：`database_engineering` · 难度：hard · 主题：experimental_feedback_and_holdout, database_evidence, structural_performance, yield_feedback

用真实Octet批次20260904、measured归一化的N4实验sigma20均值，除以指定N4模拟sigma20得到一个仅用于本题的强度尺度校正系数，再乘指定N5模拟sigma20形成N5预测。实验与模拟的材料/杆径/slider尚未匹配，故这是相关组上的探索性代理校正，不能称特定设计的验证。使用实验saved metrics（它们来源于完整审核曲线），不要从展示抽样curve重算金标准。保存calibration.json和prediction_n5.json；此轮不得访问尚未揭示的N5实验数据。

目标是帮助用户完成选型、定载荷或改设计：先用现有数据给出题设模型支持的数值估算，再给出约束判定和定量行动建议；缺失局部证据不应阻止可完成的整体估算。所有结果均是给定工况下的工程估算。N>1参数记录是尺寸迁移估计；0.5%偏移屈服不是局部首屈服。不得用N1相对密度填补N5质量/SEA，不得伪造FE应力场、屈曲证明或实物认证。

### 输入

```json
{
  "synthetic": false,
  "scenario_origin": "synthetic",
  "database_snapshot_asset": "fixtures/engineering/atlas_records.json",
  "metric_definitions": {
    "yield_margin": "screening_allowable_force / service_force - 1; allowable includes safety_factor",
    "size_relative_change": "abs(P_N5 - P_N4) / abs(P_N5)",
    "validation_relative_error": "abs(frozen_prediction - observed_mean) / abs(observed_mean)",
    "validation_bias": "frozen_prediction - observed_mean"
  },
  "database_provenance": {
    "source_id": "ATLAS-SNAPSHOT",
    "snapshot_sha256": "097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939",
    "upstream_manifest_sha256": "20f417ca1d0550b0df3f0ed1f893fab0ac73ad3a11218e1f49c7ecb13960e41d",
    "dataset_source_hash": "9b6a76307bb88bf1a99a47cfe8c9dd56aeeb5423c59720cd4d167c556062ad32",
    "record_ids": [
      "Octet_truss_5_0p4_4__N4",
      "Octet_truss_5_0p4_4__N5"
    ]
  },
  "simulation_n4_record_id": "Octet_truss_5_0p4_4__N4",
  "simulation_n5_record_id": "Octet_truss_5_0p4_4__N5",
  "calibration_asset": "fixtures/engineering/experiment_n4.json",
  "validation_relative_error_limit": 0.1,
  "feedback_origin": "real_experiment; geometry and material matching incomplete"
}
```

### 固定后续轮次

#### 第2轮

现在揭示同批次N5实验附件。保持第一轮calibration_factor与prediction_n5.json不变，比较冻结预测和N5实测sigma20均值，报告带符号偏差、相对误差、样本标准差和样本数，按10%门槛给出局部验证结果。禁止再用N5调参后把新值称为原预测；讨论未知材料/杆径/slider及试件离散性意味着什么。

本轮参数修改：

```json
{
  "validation_asset": "fixtures/engineering/experiment_n5.json"
}
```

### 实际输入附件

- [fixtures/engineering/atlas_records.json](../fixtures/engineering/atlas_records.json) · SHA256 `097d13e51ef72641d4b7d482a65d1e3b2c6bb0488f64bedf0c582d17b6349939` · 自第1轮可见
- [fixtures/engineering/experiment_n4.json](../fixtures/engineering/experiment_n4.json) · SHA256 `1210b266c8ce4abb882beb1c0268ce7ab95cd5eab5a7c7c80608826c07eaef69` · 自第1轮可见
- [fixtures/engineering/experiment_n5.json](../fixtures/engineering/experiment_n5.json) · SHA256 `0664d54543218e12c1385fa85ef76796c79dc00f46e83b9d74c35c9599b67d9b` · 自第2轮可见

### 交付

- answer.json：按公开字段给出数值和单位
- report.md：估算过程、逐约束裕度、判定及适用范围
- estimate.json：载荷/边界条件、材料/几何、模型假设、刚度和屈服指标、未知值
- evidence_trace.json：逐输出绑定record_id、source_kind、method、原始资产与快照SHA256、质量标记
- reproduce.py：离线读取随题附件重新计算全部结果；仅依赖Python标准库或预先统一配置的公共库
- calibration.json与prediction_n5.json：首轮冻结校正和预测
- validation.json：第二轮原预测误差、门槛判定、SD和范围说明

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "evidence_access": "Both arms receive the same frozen candidate-input assets; ATLAS MCP is optional assistance, not an exclusive source of required facts.",
    "source_priority": "Frozen full simulation curves and saved features control; live/display-downsampled values cannot silently replace them.",
    "engineering_outcome": "Estimate supported performance, decide against the stated constraints, and recommend a quantitative next action. Missing local evidence must not suppress supported global calculations.",
    "numeric_pass_is_complete_success": false,
    "complete_success_requires": [
      "required files exist and are consistent",
      "independent numerical and evidence review",
      "reproduce.py executes in the common isolated environment",
      "all case-specific decisions and limitations are reviewed"
    ],
    "design_assumptions": "Engineering load cases and explicit simplified models are synthetic; database and experiment records retain their real provenance.",
    "feedback_protocol": "Only reveal each followup and newly due assets after saving the previous response; never retune a frozen prediction using later measurements. Generic final deliverables are due on the final turn; save specifically requested initial artifacts on turn 1.",
    "required_runner_controls": {
      "evidence_channel": "released_candidate_input_files_only",
      "applies_to": "both arms and all turns",
      "external_network": "disabled",
      "raw_database_and_repository_access": "disabled",
      "atlas_domain_tool_allowlist": [
        "physical_checks",
        "lattice_build"
      ],
      "allowlisted_tools_must_not_read_experiment_results": true,
      "enforcement": "Controller must remove all other database retrieval tools from the actual callable registry before dispatch; fail closed when unavailable.",
      "turn_two_asset": "release only after storing immutable first-turn prediction and response hashes",
      "existing_sol61_five_case_smoke_implements_this_control": false,
      "interpretation": "Sequentially unrevealed public development data, not a secret held-out benchmark."
    }
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 1800,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 40000,
    "model_calls": 8,
    "tool_calls": 60,
    "scope": "cumulative across all turns"
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "calibration_factor": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "predicted_n5_sigma20_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "observed_n5_sigma20_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "validation_relative_error": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "validation_bias_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "observed_n5_sample_sd_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "calibration_specimen_count": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  },
  "validation_specimen_count": {
    "unit": "1",
    "abs_tol": 1e-07,
    "rel_tol": 1e-06
  }
}
```

来源与适用范围：[ATLAS-SNAPSHOT](https://github.com/haoyu9189-code/ATLAS-Lattice-Bench/tree/codex/engineering-applications/fixtures/engineering)。
