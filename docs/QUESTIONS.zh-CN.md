# 公开测试题 v0.1.0

20题均为公开开发/复现题，不是保密盲测。全部数值fixture为自编合成数据；论文仅作为研究背景。

运行方式见[协议](PROTOCOL.md)。数值输出answer.json使用`{字段: {value: 数值, unit: 单位}}`；字段清单在每题末尾。每题新建会话；后续轮次仅在上一轮输出后依次发送。

## LAT-01 · 展开行数、来源等级与阵列缺失值

类别：`data_evidence` · 难度：medium · 主题：data_provenance, finite_size

请审计给定合成导出包：有多少独立设计、多少导出行、多少次明确记录的直接求解？用户要求N=3阵列的动态SEA≥12 kJ/kg，能否据此判定通过？N指每轴单胞数。给出逐字段来源/未知值表，并计算N=3阵列单胞总数。不能访问私有数据库，也不能把展开行当新求解。

### 输入

```json
{
  "synthetic": true,
  "design_count": 120,
  "N_per_axis": [
    1,
    2,
    3,
    4,
    5
  ],
  "export_row_count": 600,
  "direct_solver_runs": 120,
  "direct_solver_scope": "仅N1准静态轴向压缩",
  "N_gt_1_static": "从N1迁移估算",
  "record": {
    "id": "SYN-D017-N3",
    "N": 3,
    "static_strength_mpa": 18.0,
    "static_source": "size_transfer_estimate",
    "dynamic_sea_kj_kg": null,
    "material": null,
    "experimental_validation": false
  }
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "independent_designs": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "export_rows": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "direct_solver_runs": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "array_cells": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S05](https://arxiv.org/abs/2410.02090)；[S10](https://link.springer.com/article/10.1007/s11012-026-02135-1)。

## LAT-02 · 压缩优势能否推出拉伸或疲劳优势

类别：`data_evidence` · 难度：medium · 主题：manufacturing_defects, load_mode_transfer

为实验计划审查两种合成脆性点阵。计算每种结构的压缩/拉伸强度比；分别推荐本数据中的压缩和拉伸候选。讨论能否据此宣布同族任意材料都具有同一排名、以及10^6周次疲劳通过。结合sources.json中有关脆性点阵拉压不对称的一手论文给出一个适用范围判断；题目数值不来自该论文，不能伪造页码或论文实测数值。可用随题来源卡，不强制联网。

### 输入

```json
{
  "synthetic": true,
  "same_material_process_relative_density": true,
  "strengths_mpa": [
    {
      "id": "A",
      "compression": 1.2,
      "tension": 0.8
    },
    {
      "id": "B",
      "compression": 1.0,
      "tension": 1.4
    }
  ],
  "fatigue_tests": null,
  "sample_uncertainty": null
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "A_compression_tension_ratio": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "B_compression_tension_ratio": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S04](https://www.nature.com/articles/s44455-025-00017-2)。

## LAT-03 · 非线性逆向设计：曲线误差与数据泄漏

类别：`data_evidence` · 难度：hard · 主题：inverse_design, grouped_validation

在给定应变点上按等权RMSE比较两条合成逆向设计响应与目标，单位MPa。另设计一个明确的训练/验证划分，用于评估对全新几何族的泛化：只能整组划分，F1作训练、F2作验证。统计行数与独立物理试验数，解释重复扫描与增强行为什么不能算独立试验。最终验证时禁止再调参。输出划分表、RMSE及可复现计算脚本。

### 输入

```json
{
  "synthetic": true,
  "strain": [
    0,
    0.1,
    0.2,
    0.3
  ],
  "target_mpa": [
    0,
    2,
    3,
    4
  ],
  "candidate_mpa": {
    "A": [
      0,
      2.2,
      2.8,
      4.2
    ],
    "B": [
      0,
      1.5,
      3.5,
      4
    ]
  },
  "rows": [
    {
      "id": "r1",
      "family": "F1",
      "trial": "T1",
      "kind": "measurement"
    },
    {
      "id": "r2",
      "family": "F1",
      "trial": "T1",
      "kind": "repeat_scan"
    },
    {
      "id": "r3",
      "family": "F1",
      "trial": "T1",
      "kind": "augmentation"
    },
    {
      "id": "r4",
      "family": "F1",
      "trial": "T2",
      "kind": "measurement"
    },
    {
      "id": "r5",
      "family": "F2",
      "trial": "T3",
      "kind": "measurement"
    },
    {
      "id": "r6",
      "family": "F2",
      "trial": "T3",
      "kind": "augmentation"
    },
    {
      "id": "r7",
      "family": "F2",
      "trial": "T4",
      "kind": "measurement"
    },
    {
      "id": "r8",
      "family": "F2",
      "trial": "T4",
      "kind": "repeat_scan"
    }
  ]
}
```

### 交付

- answer.md
- answer.json
- split.csv
- calculate.py

### 数值输出字段（不是参考答案）

```json
{
  "rmse_A_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "rmse_B_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "train_rows": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "validation_rows": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "independent_trials": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S01](https://www.nature.com/articles/s42256-025-01067-x)；[S07](https://arxiv.org/abs/2411.19681v2)。

## LAT-04 · 固定计算预算下的主动学习选点

类别：`data_evidence` · 难度：hard · 主题：inverse_design, active_learning, manufacturability

给定一个人为定义的下一轮获取函数score=p_feasible*sigma（sigma为无量纲预测不确定度），选择总成本≤6的子集使score总和最大。A和B属于同一几何族，本轮最多选一个；每个候选最多选一次。穷举求解并输出选择、总成本和总score，说明这一玩具获取函数与真实期望改进/性能增益的区别。不要执行FEA。

### 输入

```json
{
  "synthetic": true,
  "budget": 6,
  "score_formula": "p_feasible*sigma",
  "at_most_one_groups": [
    [
      "A",
      "B"
    ]
  ],
  "candidates": [
    {
      "id": "A",
      "cost": 3,
      "p_feasible": 0.9,
      "sigma": 4
    },
    {
      "id": "B",
      "cost": 2,
      "p_feasible": 0.8,
      "sigma": 3
    },
    {
      "id": "C",
      "cost": 3,
      "p_feasible": 0.95,
      "sigma": 3
    },
    {
      "id": "D",
      "cost": 1,
      "p_feasible": 0.5,
      "sigma": 2
    }
  ]
}
```

### 交付

- answer.md
- answer.json
- selection.py

### 数值输出字段（不是参考答案）

```json
{
  "selected_cost": {
    "unit": "budget_unit",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "selected_score": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S01](https://www.nature.com/articles/s42256-025-01067-x)；[S11](https://arxiv.org/abs/2609.33598)。

## LAT-05 · 同质量动态吸能：SEA、峰值力与CFE

类别：`numerical_mechanics` · 难度：medium · 主题：dynamic_energy_absorption

两试样质量均为8 g；下列合成压缩力—位移点在线性插值下有效至12 mm，F为压缩力幅值。用梯形积分分别算吸能J、SEA kJ/kg、平均力N、峰值力N及CFE=平均力/峰值力。要求SEA≥2.0 kJ/kg且峰值力≤2000 N，筛选候选。未提供准静态对照、速度、惯性平衡或重复试验，不能宣称应变率增强机理或真实防护认证。

### 输入

```json
{
  "synthetic": true,
  "displacement_mm": [
    0,
    2,
    4,
    6,
    8,
    10,
    12
  ],
  "mass_g": 8,
  "force_N": {
    "A": [
      0,
      2000,
      1500,
      1500,
      1500,
      1500,
      1800
    ],
    "B": [
      0,
      1600,
      1400,
      1400,
      1400,
      1400,
      1500
    ]
  },
  "min_sea_kj_kg": 2.0,
  "max_peak_force_N": 2000
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "energy_A_J": {
    "unit": "J",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "energy_B_J": {
    "unit": "J",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "sea_A_kj_kg": {
    "unit": "kJ/kg",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "sea_B_kj_kg": {
    "unit": "kJ/kg",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "mean_force_A_N": {
    "unit": "N",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "mean_force_B_N": {
    "unit": "N",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "peak_A_N": {
    "unit": "N",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "peak_B_N": {
    "unit": "N",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "cfe_A": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "cfe_B": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S05](https://arxiv.org/abs/2410.02090)；[S08](https://www.nature.com/articles/s41598-026-41048-7)。

## LAT-06 · 有限尺寸拟合与均匀化外推的边界

类别：`numerical_mechanics` · 难度：medium · 主题：finite_size, homogenization

同拓扑、相同胞长/相对密度/材料/载荷边界的合成强度满足题设拟合式sigma(n)=sigma_inf+alpha/n+beta/n²。n为每轴单胞数。用n=1,2,4三点拟合；预测n=3并求与sigma_inf相对误差≤5%的最小正整数n（误差分母sigma_inf）。另一个夹具下n=3测得8 MPa，此值只作为题设合成反例，讨论旧拟合能否直接套用。

### 输入

```json
{
  "synthetic": true,
  "n": [
    1,
    2,
    4
  ],
  "strength_mpa": [
    12,
    15.5,
    17.625
  ],
  "error_limit_fraction": 0.05,
  "changed_fixture_n3_mpa": 8
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "sigma_inf_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "alpha_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "beta_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "sigma_n3_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "min_n_5pct": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S05](https://arxiv.org/abs/2410.02090)；[S10](https://link.springer.com/article/10.1007/s11012-026-02135-1)。

## LAT-07 · 热—力多目标Pareto与安全系数

类别：`numerical_mechanics` · 难度：medium · 主题：multifunctional, pareto, manufacturability

候选点阵的合成抗压强度、有效导热率和相对密度见表。工作应力10 MPa，要求安全系数2（表中强度尚未折减）、k≥5 W/(m·K)、rho_rel≤0.25。先筛可行点，再在可行点中最大化强度与导热率（rho只作硬约束）求Pareto集。若用户只追求可行点中最大导热率，选谁？按margin=strength/(working_stress*FoS)-1给该候选裕度。另给已计入FoS的设计应力20 MPa，演示不再乘2时结论一致。

### 输入

```json
{
  "synthetic": true,
  "working_stress_mpa": 10,
  "fos": 2,
  "already_factored_design_stress_mpa": 20,
  "min_conductivity": 5,
  "max_relative_density": 0.25,
  "candidates": [
    {
      "id": "A",
      "strength_mpa": 24,
      "conductivity_W_mK": 6,
      "relative_density": 0.22
    },
    {
      "id": "B",
      "strength_mpa": 30,
      "conductivity_W_mK": 5,
      "relative_density": 0.24
    },
    {
      "id": "C",
      "strength_mpa": 22,
      "conductivity_W_mK": 7,
      "relative_density": 0.2
    },
    {
      "id": "D",
      "strength_mpa": 21,
      "conductivity_W_mK": 5.5,
      "relative_density": 0.23
    },
    {
      "id": "E",
      "strength_mpa": 32,
      "conductivity_W_mK": 8,
      "relative_density": 0.3
    }
  ]
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "required_strength_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "feasible_count": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "pareto_count": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "selected_margin_fraction": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S09](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345912)；[S11](https://arxiv.org/abs/2609.33598)。

## LAT-08 · 制造欠尺寸下的稳健性筛查

类别：`numerical_mechanics` · 难度：hard · 主题：manufacturing_defects, robust_design

使用题设代理关系strength=nominal_strength*(actual_d/nominal_d)^3评估两种合成杆点阵。最坏欠尺寸是绝对直径减量0.10 mm，不是半径。工作应力12 MPa、FoS=2；本题工艺合同规定成品直径≥0.65 mm。分别算最坏直径、强度与对24 MPa阈值的裕度，给出稳健候选。说明这一确定性最坏界与可靠度/概率保证的区别，且不能把代理立方律推广所有拓扑。

### 输入

```json
{
  "synthetic": true,
  "diameter_loss_mm": 0.1,
  "working_stress_mpa": 12,
  "fos": 2,
  "min_actual_diameter_mm": 0.65,
  "candidates": [
    {
      "id": "A",
      "nominal_d_mm": 0.8,
      "nominal_strength_mpa": 36
    },
    {
      "id": "B",
      "nominal_d_mm": 0.7,
      "nominal_strength_mpa": 38
    }
  ]
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "worst_d_A_mm": {
    "unit": "mm",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "worst_d_B_mm": {
    "unit": "mm",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "strength_A_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "strength_B_mpa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "margin_A_fraction": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "margin_B_fraction": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S04](https://www.nature.com/articles/s44455-025-00017-2)。

## LAT-09 · Gyroid 的片状与网络型定义及闭合裁切

类别：`cad_delivery` · 难度：hard · 主题：TPMS, gyroid, sheet_vs_network, implicit_modeling

使用纯合成参数，制作可复现的 Gyroid 片状和正相网络型两个试样。坐标以 mm 计，裁切盒为 [0,12]×[0,12]×[0,12]，胞长 a=6 mm，u=2πx/a，v=2πy/a，w=2πz/a，G=sin(u)cos(v)+sin(v)cos(w)+sin(w)cos(u)。片状实体严格定义为 |G|≤0.25；网络实体为 G≥0。0.25 是无量纲等值阈值，不能直接称为 0.25 mm 壁厚。两者均应封闭裁切边界，输出各自的 STL 和一个可运行的生成脚本；若工具支持真实 STEP 则可附加，不能伪造格式。采用不大于 0.20 mm 的初始采样间距，说明网格方法、边界处理和收敛限制。独立重新读取导出文件，检查水密性、退化面、包围盒（每轴 12.00±0.20 mm）、实体体积与孔隙率。计算理想连续正相网络体积的解析基准，并区分采样误差；片状体积应由几何测量获得。给出 G(6,6,6)、G(7.5,6,6) 及两点在两个实体中的分类。只评几何，未给出材料或载荷，不得声称力学性能或可打印性已经验证。

### 输入

```json
{
  "synthetic": true,
  "box_edge_mm": 12,
  "cell_mm": 6,
  "sheet_level": 0.25,
  "network_level": 0,
  "max_initial_grid_spacing_mm": 0.2,
  "bbox_axis_tolerance_mm": 0.2,
  "material": null,
  "load": null
}
```

### 交付

- generate_gyroid.py 或功能等价的可运行参数化源文件
- sheet.stl 与 network_positive.stl
- 包含重新读取检查、体积及孔隙率的 geometry_report.json
- 两种定义及采样局限的简短说明

### 数值输出字段（不是参考答案）

```json
{
  "cell_count_per_axis": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "box_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "network_continuum_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "network_continuum_porosity": {
    "unit": "1",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "G_center": {
    "unit": "1",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "G_offset_x": {
    "unit": "1",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S02](https://www.nature.com/articles/s41467-026-77560-7)；[S06](https://www.techscience.com/CMES/v144n1/63300)。

## LAT-10 · 梯度 Gyroid–Primitive 混合隐式结构的连续性

类别：`cad_delivery` · 难度：hard · 主题：graded_TPMS, hybrid_TPMS, continuity, connectivity

为连续梯度/混合 TPMS 研究建立一个可复现试样，所有尺寸单位为 mm。核心盒为 [0,12]×[0,12]×[0,18]，胞长 6。令 u=2πx/6、v=2πy/6、w=2πz/6；G=sin(u)cos(v)+sin(v)cos(w)+sin(w)cos(u)，P=cos(u)+cos(v)+cos(w)。s=z/18，混合权重 b=3s²−2s³，H=(1−b)G/1.5+bP/3；实体定义为 |H|≤t(z)，其中 t(z)=0.12+0.06s。加入下板 [0,12]×[0,12]×[−0.8,0] 与上板 [0,12]×[0,12]×[18,18.8] 并取实体并集。生成源文件和封闭 STL，采样间距不大于 0.20 mm；如真实 STEP 可用则附加。给出 z=0、9、18 处的 b 和 t，证明混合标量场在核心内连续，并解释这并不保证实体连通或最低壁厚。重新读取输出，检查总包围盒应为 12×12×19.6 mm（每轴误差≤0.20 mm）、水密性、连通分量、最小特征估计；若分量不为 1 或方法不能确认，应报告不满足/待验证，不得私改公式。单列两块实心板的解析总体积；其与核心交界为共面面，实体并集体积仍以导出几何复核。没有材料/载荷信息，不作刚度或吸能排序。

### 输入

```json
{
  "synthetic": true,
  "core_x_mm": 12,
  "core_y_mm": 12,
  "core_z_mm": 18,
  "cell_mm": 6,
  "plate_thickness_mm": 0.8,
  "sheet_level_bottom": 0.12,
  "sheet_level_top": 0.18,
  "max_grid_spacing_mm": 0.2,
  "target_connected_components": 1,
  "material": null,
  "load": null
}
```

### 交付

- 参数化混合 TPMS 生成源文件
- hybrid_gradient.stl
- geometry_report.json
- 连续性推导与连通性/最小特征检查状态

### 数值输出字段（不是参考答案）

```json
{
  "core_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "outer_height_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "outer_box_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "plates_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "blend_bottom": {
    "unit": "1",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "blend_mid": {
    "unit": "1",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "blend_top": {
    "unit": "1",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "level_mid": {
    "unit": "1",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S02](https://www.nature.com/articles/s41467-026-77560-7)；[S07](https://arxiv.org/abs/2411.19681v2)；[S12](https://orca.cardiff.ac.uk/id/eprint/172274/)。

## LAT-11 · 有限 BCC 阵列的图去重与实体裁切

类别：`cad_delivery` · 难度：medium · 主题：BCC, finite_array, graph_deduplication, boundary_clipping

构建 2×2×2 个 BCC 胞的有限阵列，胞长 a=5 mm，每胞体心连接该胞 8 个角点，所有杆半径 r=0.35 mm，不添加节点球、不加面板。角点按全局坐标去重，无向边按端点 ID 去重。先写出 graph.json，再以圆柱实体沿每条边连接端点、做布尔并集，并与 [0,10]³ mm 裁切盒相交，使边界不得因杆半径外伸。输出生成脚本、graph.json、闭合 STL 和几何检查报告；如支持真实 STEP 则附加。报告去重后的节点数/边数、每边中心线长度和总中心线长度；另算圆柱体积逐杆相加的上界估计，明确其既不扣交叠也不扣裁切，不能当成融合实体体积。重新读取 STL，确认包围盒每轴为 10.00±0.05 mm、非空、水密；实体体积应由真实模型独立测量，并据 1000 mm³ 设计盒计算相对密度。只测试几何，不凭几何宣称承载合格。

### 输入

```json
{
  "synthetic": true,
  "cells_per_axis": 2,
  "cell_mm": 5,
  "strut_radius_mm": 0.35,
  "node_spheres": false,
  "face_plates": false,
  "clip_box_edge_mm": 10,
  "bbox_axis_tolerance_mm": 0.05,
  "load": null
}
```

### 交付

- BCC 生成源文件
- graph.json（坐标、去重节点及无向边）
- bcc_clipped.stl
- geometry_report.json

### 数值输出字段（不是参考答案）

```json
{
  "graph_nodes": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "graph_edges": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "edge_length_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "total_centerline_length_mm": {
    "unit": "mm",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "sum_uncut_cylinder_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "design_box_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "strut_diameter_mm": {
    "unit": "mm",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S10](https://link.springer.com/article/10.1007/s11012-026-02135-1)。

## LAT-12 · 旋转正方形负泊松比机构的几何与实体边界

类别：`cad_delivery` · 难度：hard · 主题：auxetic, rotating_squares, kinematics, multipart_CAD

建立一个 2×2 旋转正方形机构的理想运动学演示，长度单位 mm。每块刚性正方形边长 a=4、厚度 h=1，中心位于 (i·p,j·p)，i,j∈{0,1}，转角为 (−1)^(i+j)θ，p(θ)=a(cosθ+sinθ)。方块在 z∈[0,1]，局部角点坐标是 (±a/2,±a/2)。分别输出 θ=15° 和 30° 的四个独立刚体文件（每块闭合 STL，真实 STEP 可选）及装配清单；面内相邻角点接触，沿 Z 挤出后对应沿 Z 的边接触；不要将这些方块熔成一个可打印实体。相邻刚体之间设绕 Z 轴的无摩擦理想转铰，铰链只是无实体尺寸的运动学约束，不需要生成实体铰链。计算两状态节距、整个 2×2 组件的外包络边长，及以 15° 为参考的 εx、εy 和本题定义的有限割线 νsec=−εy/εx。核查每块方块体积与四块总体积；重新读取所有文件确认每块水密、尺寸和旋转正确。阐明该 νsec 只属于给定理想机构，不是弹性 FEA 或实物测量结果；没有材料、载荷和铰链设计，不得把本组件称为已完成可制造柔性超材料。

### 输入

```json
{
  "synthetic": true,
  "square_side_mm": 4,
  "part_thickness_mm": 1,
  "rows": 2,
  "columns": 2,
  "initial_angle_deg": 15,
  "final_angle_deg": 30,
  "hinge_model": "ideal_revolute_about_Z_no_physical_hinge",
  "load": null
}
```

### 交付

- 可运行的两状态装配生成源文件
- 每状态四个闭合 STL，共八个；STEP 可选
- assembly.json（每块位置、转角、状态和路径）
- kinematics_and_geometry_report.json

### 数值输出字段（不是参考答案）

```json
{
  "parts_per_state": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "part_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "assembly_solid_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "pitch_15_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "pitch_30_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "bbox_xy_15_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "bbox_xy_30_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "strain_x": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "strain_y": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "secant_poisson": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S13](https://jngrima.com/wp-content/uploads/2017/11/grima-et-al-2005-on-the-auxetic-properties-of-rotating-rectangles-with-different-connectivity.pdf)。

## LAT-13 · 多轮载荷与包络变更下的 BCC 设计继承

类别：`multiturn_constraints` · 难度：medium · 主题：BCC, multiturn_design, constraint_inheritance, nominal_stress

设计合成 BCC 夹芯试样，先建立参数化源文件。核心为 2×2×2 胞，胞长 4 mm，杆半径 0.30 mm，每胞体心连 8 角，不加节点球，融合后裁切到 [0,8]³。下板 z∈[−0.6,0]、上板 z∈[8,8.6]，板面均为 8×8 mm。沿 −Z 施加压缩力 300 N。本题只做包络名义应力筛查：σnom=F/(外包络 X×Y 截面积)，要求 σnom≤5 MPa；这不代表杆件实际应力或承载安全认证。初态计算并保存参数，整个过程中必须继承未被追加指令修改的条件。最终输出最终状态源文件、闭合 STL、参数变更表、实际几何检查及名义应力计算；先不假定后续条件。

### 输入

```json
{
  "synthetic": true,
  "cells_per_axis": 2,
  "cell_mm": 4,
  "radius_mm": 0.3,
  "plate_mm": 0.6,
  "force_N": 300,
  "nominal_stress_limit_MPa": 5
}
```

### 固定后续轮次

#### 第2轮

把压缩力改为 400 N，胞长改为 5 mm；仍为 2×2×2 胞，杆半径仍为 0.30 mm，其余条件继承。板面随核心改为 10×10 mm，现阶段板厚仍为 0.6 mm。仍按 5 MPa 名义应力上限筛查，X/Y 外包络各不得超过 10 mm。请更新参数与结果。

本轮参数修改：

```json
{
  "force_N": 400,
  "cell_mm": 5,
  "max_x_mm": 10,
  "max_y_mm": 10
}
```

#### 第3轮

最终上下板厚各改为 1.00 mm，核心位置仍 z∈[0,10]，下板放在 [−1,0]、上板放在 [10,11]。总高度上限为 12.00 mm，其他已确认的条件全部继承。现在导出最终文件并重新读取测量；每轴包围盒误差容许 0.05 mm，给出最终载荷、胞长、半径和名义应力。

本轮参数修改：

```json
{
  "plate_mm": 1,
  "max_z_mm": 12,
  "bbox_axis_tolerance_mm": 0.05
}
```

### 交付

- 最终参数化生成源文件
- final_bcc_sandwich.stl
- 三轮参数变更表或 design_history.json
- final_geometry_and_nominal_stress.json

### 数值输出字段（不是参考答案）

```json
{
  "initial_nominal_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "final_core_edge_mm": {
    "unit": "mm",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "final_height_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "final_plate_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "final_force_N": {
    "unit": "N",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "final_radius_mm": {
    "unit": "mm",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "final_nominal_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "nominal_headroom_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "graph_edges": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S10](https://link.springer.com/article/10.1007/s11012-026-02135-1)。

## LAT-14 · 多轮材料密度与安全系数更新的质量预算

类别：`multiturn_constraints` · 难度：hard · 主题：mass_budget, material_units, safety_factor, BCC

建立合成 BCC 夹芯体：2×2×2 胞，胞长 6 mm，圆杆半径 0.40 mm，不加节点球；核心与 [0,12]³ 相交裁切。上下实心板尺寸均 12×12×1 mm，下板 z∈[−1,0]，上板 z∈[12,13]，取实体并集。材料密度暂设 1.02 g/cm³；这是题设合成值，不代表真实材料牌号。实测几何总体积记为 V mm³，以质量≤2.00 g 为目标。允许用解析体积上界证明理想题设几何的质量预算成立；这不等于导出文件已经验证，其实际质量仍须用重新读取后的体积计算。沿 −Z 压缩力为 600 N。请建立可复现模型并说明质量的单位换算；尚未给出材料强度，暂不能判实际承载合格。保留各轮参数，未修改的几何约束必须继承。

### 输入

```json
{
  "synthetic": true,
  "geometry": {
    "cells_per_axis": 2,
    "cell_mm": 6,
    "radius_mm": 0.4,
    "plate_mm": 1
  },
  "density_g_cm3": 1.02,
  "force_N": 600,
  "max_mass_g": 2
}
```

### 固定后续轮次

#### 第2轮

材料密度修正为 1.20 g/cm³，质量上限仍是 2.00 g。保持几何完全相同，使用同一个最终几何文件和同一次 V 测量更新质量；不要因为密度变化调整杆径或胞长。给出允许的最大 V 和相同几何的新旧质量比。

本轮参数修改：

```json
{
  "density_g_cm3": 1.2
}
```

#### 第3轮

压缩力改为 720 N，增加安全系数 FoS=1.5。只做包络名义应力筛查：要求 FoS×F/(12×12)≤10 MPa。请把 720 N 明确当作未乘 FoS 的服务载荷，只乘一次。输出最终源文件、STL、实际体积与质量计算、最终参数表及筛查裕度；裕度在本题定义为 10/(FoS×F/A)−1，按百分数报告，不能把此筛查写成杆件实际强度验证。

本轮参数修改：

```json
{
  "force_N": 720,
  "safety_factor": 1.5,
  "nominal_allowable_MPa": 10
}
```

### 交付

- 参数化源文件与未因密度更新而改变的最终 STL
- 可定位的几何体积测量记录
- design_history.json
- 质量预算与 FoS 名义应力筛查报告

### 数值输出字段（不是参考答案）

```json
{
  "outer_x_mm": {
    "unit": "mm",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "outer_y_mm": {
    "unit": "mm",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "outer_z_mm": {
    "unit": "mm",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "two_plate_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "final_density_g_mm3": {
    "unit": "g/mm^3",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "maximum_solid_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "new_old_mass_ratio": {
    "unit": "1",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "service_nominal_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "design_force_N": {
    "unit": "N",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "design_nominal_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "screening_margin_percent": {
    "unit": "%",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S11](https://arxiv.org/abs/2609.33598)。

## LAT-15 · 多轮旋转矩形机构的角度、厚度与材料装配

类别：`multiturn_constraints` · 难度：hard · 主题：auxetic, rotating_rectangles, multimaterial_assembly, multiturn_design

构建合成 2×2 旋转矩形理想机构。每块矩形局部尺寸宽 b=4 mm、高 c=6 mm、厚 1.00 mm；块中心位于 (i·px,j·py)，i,j∈{0,1}，角度为 (−1)^(i+j)θ。节距定义为 px=b cosθ+c sinθ、py=b sinθ+c cosθ；面内相邻角点接触，沿 Z 挤出后对应沿 Z 的边接触；相邻刚体仅受绕 Z 轴、无实体尺寸的理想转铰约束，不生成物理铰链，不熔合刚体。初态 θ0=10°，暂定目标 θ1=20°。用初态节距作参考计算 εx、εy 和 νsec=−εy/εx。计划交付每个状态四个独立闭合 STL、装配清单和参数化源文件；两个姿态描述同一套四刚体，不把它称作已经可打印的单件。

### 输入

```json
{
  "synthetic": true,
  "rectangle_width_mm": 4,
  "rectangle_height_mm": 6,
  "rows": 2,
  "columns": 2,
  "initial_angle_deg": 10,
  "target_angle_deg": 20,
  "thickness_mm": 1
}
```

### 固定后续轮次

#### 第2轮

目标角 θ1 改为 30°，初态仍 10°；所有矩形厚度改为 1.50 mm，面内 b=4、c=6 和交替转向不变。不要沿用旧目标角 20° 的最终应变或几何。

本轮参数修改：

```json
{
  "target_angle_deg": 30,
  "thickness_mm": 1.5
}
```

#### 第3轮

两块 i+j 为偶数的矩形指定材料 A，合成密度 1.20 g/cm³；另外两块指定材料 B，合成密度 1.00 g/cm³。各块面内形状和厚度保持上一轮参数。为两个角度状态分别导出四块文件，并用 assembly.json 标出材料、位置、角度及文件。按每个状态分别报告同一套四块装配的总体积、A/B 各自质量及总质量；两个姿态的八个输出文件不代表八块物理材料，禁止跨姿态重复累加材料用量。重新读取确认分件体积和姿态。报告最终应变和 νsec，不得把矩形公式套成旋转正方形的 −1。仅做运动学，不需要应力分析。

本轮参数修改：

```json
{
  "material_A_density_g_cm3": 1.2,
  "material_B_density_g_cm3": 1,
  "material_assignment": "A where (i+j)%2==0; B where (i+j)%2==1"
}
```

### 交付

- 两个最终角度状态的装配生成源文件
- 每状态四个闭合 STL，共八个
- assembly.json（材料 A/B、位置、姿态和路径）
- 最终运动学、质量与几何检查报告

### 数值输出字段（不是参考答案）

```json
{
  "px_initial_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "py_initial_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "px_final_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "py_final_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "final_bbox_x_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "final_bbox_y_mm": {
    "unit": "mm",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "final_bbox_z_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "strain_x": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "strain_y": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "secant_poisson": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-05
  },
  "part_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "total_solid_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "material_A_mass_g": {
    "unit": "g",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "material_B_mass_g": {
    "unit": "g",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "total_mass_g": {
    "unit": "g",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S08](https://www.nature.com/articles/s41598-026-41048-7)；[S13](https://jngrima.com/wp-content/uploads/2017/11/grima-et-al-2005-on-the-auxetic-properties-of-rotating-rectangles-with-different-connectivity.pdf)。

## LAT-16 · 多轮制造约束下的简单立方骨架与排粉孔

类别：`multiturn_constraints` · 难度：hard · 主题：DfAM, powder_escape, simple_cubic, constraint_inheritance

构建一个合成开放骨架：简单立方 SC 的 2×2×2 胞，胞长 5 mm，网格节点为 (5i,5j,5k)，i,j,k∈{0,1,2}；只连接相距 5 mm 的相邻轴向节点，去重。圆杆半径初设 0.50 mm，融合后与 [0,10]³ 裁切。上下板均 10×10×0.80 mm，下板 z∈[−0.8,0]，上板 z∈[10,10.8]。每块板在 (x,y)=(2.5,2.5)、(2.5,7.5)、(7.5,2.5)、(7.5,7.5) 各钻一个沿 Z 的通孔，初始直径 2.00 mm，只从板中扣除孔，再与核心并集。沿 −Z 压缩载荷为 200 N，仅报告包络名义应力。请先给参数化源文件；制造判据是本题合成筛查阈值，不能当作某设备官方工艺规范。

### 输入

```json
{
  "synthetic": true,
  "cells_per_axis": 2,
  "cell_mm": 5,
  "radius_mm": 0.5,
  "plate_mm": 0.8,
  "hole_diameter_mm": 2,
  "force_N": 200
}
```

### 固定后续轮次

#### 第2轮

制造筛查调整：名义杆直径至少 1.20 mm，板厚至少 1.00 mm。把杆半径明确改为 0.60 mm，上下板厚各改为 1.00 mm，核心胞长、2×2×2 排列及全部孔中心继承。最终总高度不得超过 12.00 mm。

本轮参数修改：

```json
{
  "radius_mm": 0.6,
  "plate_mm": 1,
  "max_total_height_mm": 12,
  "min_nominal_strut_diameter_mm": 1.2,
  "min_nominal_plate_mm": 1
}
```

#### 第3轮

所有板孔直径最终改为 3.00 mm，孔中心和其他上一轮参数不变；要求每个孔到该板外边界的最小面内余量至少 1.00 mm，邻孔间最小面内余量至少 1.00 mm。最终导出闭合 STL、源文件和 graph.json，重新读取并核对尺寸、连通性、水密性。分别报告名义杆/板/孔阈值是否满足，以及实际最小特征和排粉路径是否经过可靠方法验证；只有孔径合格不能宣称所有粉末已能排出。总包围盒每轴容差为 0.05 mm，载荷仍为 200 N。

本轮参数修改：

```json
{
  "hole_diameter_mm": 3,
  "min_hole_edge_ligament_mm": 1,
  "min_hole_pair_ligament_mm": 1,
  "bbox_axis_tolerance_mm": 0.05
}
```

### 交付

- 最终参数化源文件
- graph.json
- sc_perforated_sandwich.stl
- 最终约束、几何检查及 DfAM 检查证据报告

### 数值输出字段（不是参考答案）

```json
{
  "graph_nodes": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "graph_edges": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "total_centerline_length_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "final_strut_diameter_mm": {
    "unit": "mm",
    "abs_tol": 1e-12,
    "rel_tol": 1e-05
  },
  "final_total_height_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "holes_per_plate": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "min_hole_to_outer_edge_ligament_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "min_adjacent_hole_ligament_mm": {
    "unit": "mm",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  },
  "two_plates_after_holes_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "nominal_stress_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-09,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S02](https://www.nature.com/articles/s41467-026-77560-7)；[S11](https://arxiv.org/abs/2609.33598)。

## LAT-17 · 网格收敛失败时能报告什么

类别：`failure_recovery` · 难度：medium · 主题：verification, manufacturing_defects

三个合成网格级别的反力结果见输入。按abs(F_fine-F_prev)/F_fine≤2%检查最后两级。本题只有反力数据，没有应力场、屈曲特征值或独立实验。计算判据并形成收敛/未收敛报告，给出预算只够新增一级时的下一步。不得把完成求解等同网格收敛，也不能自动改变2%阈值。无需真的执行FEA。

### 输入

```json
{
  "synthetic": true,
  "element_size_mm": [
    0.4,
    0.2,
    0.1
  ],
  "reaction_force_N": [
    1000,
    1180,
    1260
  ],
  "relative_tolerance": 0.02,
  "budget_new_levels": 1,
  "solver_status": [
    "completed",
    "completed",
    "completed"
  ]
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "last_relative_change": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "allowed_change_fraction": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S10](https://link.springer.com/article/10.1007/s11012-026-02135-1)。

## LAT-18 · 断点恢复与损坏工件识别

类别：`failure_recovery` · 难度：hard · 主题：artifact_integrity, reproducibility

用随题job_events重建状态并给出恢复计划。同一幂等键第二次创建不得产生新逻辑任务。下载校验合同要求实际SHA256等于manifest值，题中两个哈希明确不同；数值体积只是日志声称。列出唯一逻辑任务数、已验证可交付CAD数、是否可声称完成，以及预算只许再下载一次时的执行顺序。本题是离线事件推演，无实际远程服务或STL，不能编造下载链接。

### 输入

```json
{
  "synthetic": true,
  "job_events": [
    {
      "event": "create",
      "job": "J1",
      "idempotency_key": "K1"
    },
    {
      "event": "create_retry",
      "job": "J1",
      "idempotency_key": "K1"
    },
    {
      "event": "solver_completed",
      "job": "J1",
      "reported_volume_mm3": 1000
    },
    {
      "event": "download",
      "job": "J1",
      "manifest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "actual_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    }
  ],
  "download_retries_remaining": 1,
  "cad_bytes_provided": false
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "logical_jobs": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "verified_deliverable_cad": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "download_retries_remaining": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S02](https://www.nature.com/articles/s41467-026-77560-7)。

## LAT-19 · 振动带隙代理超域：插值可以，外推不可冒充实测

类别：`failure_recovery` · 难度：hard · 主题：multifunctional, out_of_distribution

给定同材料/拓扑/胞长/边界条件下两个合成代理点，允许在rho_rel∈[0.15,0.20]线性插值。求rho=0.18时带隙上下界、带宽与相对带宽(gap_width/mid_frequency)，并判断是否覆盖整个[900,1100]Hz。随后请求rho=0.30：报告它是否超域及最小追加验证计划，不能直接把外推当模型有效预测。带隙为此题输入定义的方向性代理区间，未提供全方向色散或有限试件传递率。

### 输入

```json
{
  "synthetic": true,
  "density_domain": [
    0.15,
    0.2
  ],
  "training_points": [
    {
      "rho": 0.15,
      "lower_Hz": 800,
      "upper_Hz": 1200
    },
    {
      "rho": 0.2,
      "lower_Hz": 1000,
      "upper_Hz": 1500
    }
  ],
  "interpolation_query": 0.18,
  "out_of_domain_query": 0.3,
  "target_band_Hz": [
    900,
    1100
  ]
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "interpolation_weight": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "lower_Hz": {
    "unit": "Hz",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "upper_Hz": {
    "unit": "Hz",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "bandwidth_Hz": {
    "unit": "Hz",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "relative_bandwidth": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S01](https://www.nature.com/articles/s42256-025-01067-x)。

## LAT-20 · 热流点阵：缺失压降与互不匹配的比较条件

类别：`failure_recovery` · 难度：hard · 主题：multifunctional, thermal_fluid, evidence_integrity

为冷却点阵选型审计候选A/B。只有同流体、温度、体积流量和包络下的数据可以直接比较，泵功用P=delta_p*Q（SI单位，忽略泵效率，仅液压功）。A的压降已知，B缺失。要求壁面温升≤20K且液压功≤0.5W。计算A的功率和B允许的最大压降，说明能否选B以及C的数据为何不能直接排名。给出最少补测字段，不用虚构压降填空。

### 输入

```json
{
  "synthetic": true,
  "comparison_envelope_mm": [
    20,
    20,
    20
  ],
  "fluid": "synthetic-water-condition",
  "flow_m3_s": 2e-05,
  "max_temp_rise_K": 20,
  "max_hydraulic_power_W": 0.5,
  "common_conditions": "三者均同一流体、入口温度293.15K、稳态总热负荷100W、同一受热面与其余面绝热；temp_rise_K为最大壁温减入口温度。只有C的体积流量不同。",
  "candidates": [
    {
      "id": "A",
      "flow_m3_s": 2e-05,
      "temp_rise_K": 18,
      "pressure_drop_Pa": 20000
    },
    {
      "id": "B",
      "flow_m3_s": 2e-05,
      "temp_rise_K": 15,
      "pressure_drop_Pa": null
    },
    {
      "id": "C",
      "flow_m3_s": 4e-05,
      "temp_rise_K": 12,
      "pressure_drop_Pa": 18000
    }
  ]
}
```

### 交付

- answer.md：有单位、过程和适用范围的结论
- answer.json：题目要求的数值结果与单位

### 数值输出字段（不是参考答案）

```json
{
  "hydraulic_power_A_W": {
    "unit": "W",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "max_allowed_pressure_drop_Pa": {
    "unit": "Pa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S09](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345912)；[S11](https://arxiv.org/abs/2609.33598)。
