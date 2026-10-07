# 研究挑战题 v0.2.0

LAT-21—24单独计分。要求实际几何、求解与操作记录，数值锚点正确不代表任务完成。仍是公开开发题，未验证模型区分度。

[运行与评分协议](PROTOCOL.md) · [全部题目](QUESTIONS.zh-CN.md)

## LAT-21 · 陌生锥形环状包络中的可交付点阵与接口约束

类别：`research_challenge` · 难度：research · 主题：free_form_lattice, interface_preservation, manufacturability, geometry_optimization

完成一个真实几何交付任务，所有坐标和长度单位为 mm。设计域 D 为 0≤z≤24、6≤sqrt(x²+y²)≤20−z/6 的锥形环状实体，再扣除五个沿 z 贯通的圆柱禁入区：四个螺栓孔的轴线在 (12,0)、(−12,0)、(0,12)、(0,−12)，半径均为 1.6；一个电缆通道轴线在 (8.5,8.5)，半径为 1.8。D 的 z∈[0,2] 与 z∈[22,24] 两段必须完整保留为实心接口板；其余体积允许自由设计连接两端接口的三维点阵，拓扑不限。通道和孔均不得填充。点阵须为分布于核心的互连胞元结构，沿 z 至少三个重复或渐变胞元层，不能用少量平行直柱或空心外壳替代。要求成品为一个连通、水密实体，合成材料密度为 1.02 g/cm³，成品总质量≤8.00 g；核心的三个审查带 z∈(2,8)、(8,14)、(14,22) 各自相对设计域体积分数均在 [0.12,0.35]。所有设计杆径/壁厚≥1.00 mm；对杆件中部、壁面中部及接口连接附近执行独立的网格截面/局部厚度检查并报告分辨率与未覆盖区域，不能仅凭输入半径宣称全局最小厚度已证明。可变胞元或厚度均可，但必须显式参数化。至少制作并实际检查两个不同参数的候选，保留失败的候选记录，在相同约束下选择质量更低且检查充分的可行候选；不要求证明全局最优。交付可运行源文件、最终封闭 STL、独立重读结果与候选记录。用两级几何离散（网格/采样间距均≤0.20 mm，细级≤0.10 mm，若使用精确 B-rep 则用相应三角化容差）检查质量、体积分数及特征估计的变化。孔和通道的违反体积、保留接口的缺失体积、包络外溢体积均须独立计算，并提供体积误差估计；每项误差上界≤5 mm³ 才可记几何约束通过。最终质量加所报告的体积误差换算值必须≤8.00 g，三个带的体积分数误差区间须整体落在目标区间内。厚度无法完全证实时明确标记估计或待验证，不能计作完整通过。请给出密实设计域与强制接口板体积的解析基准，区分其与实际点阵体积。这里只考几何与规定材料密度下的质量，不得声称完成了力学、疲劳或制造工艺验证。

### 输入

```json
{
  "synthetic": true,
  "units": "mm",
  "z_range_mm": [
    0,
    24
  ],
  "outer_radius_expression": "20-z/6",
  "inner_radius_mm": 6,
  "bolt_centers_xy_mm": [
    [
      12,
      0
    ],
    [
      -12,
      0
    ],
    [
      0,
      12
    ],
    [
      0,
      -12
    ]
  ],
  "bolt_radius_mm": 1.6,
  "channel_center_xy_mm": [
    8.5,
    8.5
  ],
  "channel_radius_mm": 1.8,
  "mandatory_plate_z_intervals_mm": [
    [
      0,
      2
    ],
    [
      22,
      24
    ]
  ],
  "core_audit_bands_z_mm": [
    [
      2,
      8
    ],
    [
      8,
      14
    ],
    [
      14,
      22
    ]
  ],
  "core_audit_band_solid_fraction_interval": [
    0.12,
    0.35
  ],
  "synthetic_density_g_cm3": 1.02,
  "mass_limit_g": 8,
  "minimum_designed_feature_mm": 1,
  "minimum_axial_cell_layers": 3,
  "max_boolean_error_upper_bound_mm3": 5,
  "geometry_coverage": "whole exported solid, including interfaces and boundary cut cells",
  "material_mechanics": null,
  "physical_process_validation": false
}
```

### 交付

- 一个可运行的参数化生成入口及锁定依赖/工具版本
- final.stl 与至少一个候选 STL；真实 STEP 可选，不能用改后缀伪造
- candidate_journal.json：至少两个实际运行候选的参数、错误、质量、各带体积分数和选择理由
- geometry_report.json：实际文件 SHA256、重读方法、体积、包围盒、连通性、水密性、退化面、三个布尔违反量及误差
- feature_audit.json：设计特征与独立测量、采样位置、方法/容差、最小值、未覆盖区域与状态
- 最终约束状态表以及两级离散收敛记录

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "version": "0.2.0",
    "status": "authored_targets_not_prevalidated_by_reference_CAD",
    "required_artifact_types": [
      "reproducible_source",
      "nonempty_closed_STL",
      "candidate_journal",
      "geometry_report",
      "feature_audit"
    ],
    "independent_evaluator_must": [
      "rerun_generator",
      "reload_final_STL_from_disk",
      "recompute_mass_from_mesh_volume",
      "recompute_band_volume_fractions",
      "check_CSG_keepouts_and_preserved_interfaces",
      "inspect_local_features_and_coverage",
      "verify_candidate_journal_against_logs"
    ],
    "thresholds": {
      "watertight": true,
      "connected_solid_components": 1,
      "degenerate_faces": 0,
      "mass_with_error_g_max": 8,
      "band_solid_fraction_confidence_interval_min": 0.12,
      "band_solid_fraction_confidence_interval_max": 0.35,
      "outside_envelope_volume_upper_bound_mm3_max": 5,
      "keepout_intersection_volume_upper_bound_mm3_max": 5,
      "mandatory_plate_missing_volume_upper_bound_mm3_max": 5,
      "designed_feature_mm_min": 1,
      "independent_sampled_feature_lower_bound_mm_min": 1,
      "actual_candidate_count_min": 2,
      "axial_cell_layers_min": 3,
      "coarse_spacing_or_chord_error_mm_max": 0.2,
      "fine_spacing_or_chord_error_mm_max": 0.1
    },
    "review_required": [
      "genuine interconnected cellular core rather than a shell or sparse straight posts",
      "feature method is appropriate near interfaces and includes uncertainty; unmeasured areas do not silently pass",
      "all refinement comparisons use the same underlying geometry parameters"
    ],
    "failure_conditions": [
      "missing or unreadable mesh",
      "any hard geometry target violated",
      "reported error interval overlaps a forbidden value",
      "unverified feature coverage marked complete",
      "only theoretical topology names or screenshots without real artifacts"
    ],
    "incomplete_execution_policy": "Honest limitations receive applicable evidence credit; missing geometry or unchecked hard constraints do not receive delivery/engineering pass credit.",
    "tool_environment": "Both arms receive the identical installed Python, CAD kernel, mesh/CSG and DfAM tools, compute, source access and versions; freeze the environment before running. A tool unavailable to both is recorded, not replaced by fabricated evidence.",
    "trial_budget": {
      "status": "proposed_not_pilot_calibrated",
      "per_arm_wall_clock_seconds": 3600,
      "max_model_turns": 16,
      "max_tool_calls": 80,
      "max_design_candidates": 12,
      "max_aggregate_input_tokens": 250000,
      "max_aggregate_output_tokens_including_reasoning": 60000,
      "refinements_count_as_new_design_candidate": false,
      "freeze_before_live_run": true,
      "same_hardware_both_arms": true
    }
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 3600,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 60000,
    "model_calls": 16,
    "tool_calls": 80
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "dense_design_domain_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-05,
    "rel_tol": 1e-06
  },
  "mandatory_plates_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-05,
    "rel_tol": 1e-06
  },
  "mandatory_plates_mass_g": {
    "unit": "g",
    "abs_tol": 1e-06,
    "rel_tol": 1e-06
  },
  "mass_budget_equivalent_total_solid_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 1e-05,
    "rel_tol": 1e-06
  }
}
```

研究背景：[S02](https://www.nature.com/articles/s41467-026-77560-7)；[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S07](https://arxiv.org/abs/2411.19681v2)；[S11](https://arxiv.org/abs/2609.33598)。

## LAT-22 · 非线性点阵闭环：真实建模、位移续接求解与受预算约束的曲线匹配

类别：`research_challenge` · 难度：research · 主题：inverse_design, nonlinear_truss, buckling, target_response, solver_verification, cad_delivery

完成一个可离线复现的几何建模→实际非线性数值求解→目标曲线比较→设计修改→独立复核闭环。严格使用 inputs 中的二维铰接杆系、合成轴向储能、边界条件和初始几何缺陷；它是公开的离散模型研究任务，既不是连续体有限元，也不是任何真实材料的试验。必须真实生成与设计参数一致的三维杆系 STL，并重新读取检查。以给定 baseline 开始，最多尝试 8 组不同设计参数（包括 baseline），匹配 10 个目标压缩力点；baseline 未达标时至少真实求解一个不同设计，不得只建议优化。用稳定平衡续接计算所有载荷点，保留失败和未收敛记录。独立新进程对最终选定设计将位移步长减半，复算反力并检查能量梯度。给出已达到的误差、相对 baseline 的改进和是否满足全部验收条件；未达标时允许诚实交付最佳有效设计与失败分析，不能伪造收敛或宣称最优。参考文献只说明研究方向，全部计算依据由本题自包含定义。

### 输入

```json
{
  "synthetic": true,
  "units": {
    "length": "mm",
    "force": "N",
    "energy": "N mm",
    "stress": "MPa=N/mm^2"
  },
  "geometry": {
    "node_id": "n=5*j+i, i,j in {0,1,2,3,4}",
    "reference_coordinates": "For j=0 or j=4: X_n=(5*i,5*j,0). For j in {1,2,3}: X_n=(5*i+0.04*sin(i+3*j),5*j+0.03*cos(2*i+j),0). Angles are radians. The imperfections define the stress-free reference, not an applied displacement.",
    "horizontal_edges": "(5*j+i,5*j+i+1), j=0..4, i=0..3; 20 members",
    "vertical_edges": "(5*j+i,5*(j+1)+i), j=0..3, i=0..4; 20 members",
    "diagonal_edges": "One diagonal per square, j,i=0..3: if (i+j) is even use (5*j+i,5*(j+1)+i+1), otherwise use (5*j+i+1,5*(j+1)+i); 16 members. Do not add both diagonals.",
    "joint_model": "2D frictionless pins; members carry axial force only. There are no contact, bending, shear, gravity, plasticity, damping or inertial terms. All z coordinates stay zero in the solver. Crossing deformed centerlines do not create new graph joints or contact; report this idealization and any detected intersections.",
    "cad_representation": "For the selected design, make the Boolean union of circular cylinders along every undeformed graph edge and a sphere at every node, sphere radius equal to the largest incident member radius. Export a closed connected STL. This union is a geometric representation; its fused joints are not physical realizations of the solver's frictionless pins. Do not infer continuum stiffness, fatigue, printability or experimental performance from the truss result."
  },
  "design_space": {
    "parameters": [
      "r_vertical_mm",
      "r_diagonal_mm"
    ],
    "bounds_mm": {
      "r_vertical_mm": [
        0.2,
        0.55
      ],
      "r_diagonal_mm": [
        0.15,
        0.45
      ]
    },
    "fixed_horizontal_radius_mm": 0.25,
    "baseline": {
      "r_vertical_mm": 0.35,
      "r_diagonal_mm": 0.22
    },
    "max_distinct_designs_including_baseline": 8,
    "max_design_evaluations_including_failed_attempts": 8,
    "budget_accounting": "Each attempted parameter vector counts once even if its solver fails. Replaying the identical vector for debugging is allowed only within its originally declared solver iteration/retry limits and must be logged; changing a vector creates a new design. The one required independent refinement of the selected vector is exempt. No unlogged optimization calls, surrogate training runs or parameter sweeps."
  },
  "constitutive_law": {
    "E_mpa": 100.0,
    "area": "A_e=pi*r_e^2",
    "reference_length": "L0_e=norm(X_b-X_a)",
    "stretch": "lambda_e=norm(x_b-x_a)/L0_e > 0",
    "member_energy_N_mm": "U_e=(E*A_e*L0_e/4)*(lambda_e^2-1-2*ln(lambda_e)); U=sum_e U_e",
    "member_axial_force_N": "N_e=dU_e/dl_e=(E*A_e/2)*(lambda_e-1/lambda_e), positive in tension",
    "axial_tangent_N_per_mm": "dN_e/dl_e=(E*A_e/(2*L0_e))*(1+1/lambda_e^2)",
    "qualification": "A synthetic conservative 1D axial law with initial tangent E*A/L0. Material and geometric nonlinearity must both be retained. E is not a calibrated property of PA12 or another real material."
  },
  "boundary_conditions": {
    "bottom": "Nodes 0..4: x_n=X_n at every step.",
    "top": "Nodes 20..24: x_n=(X_n,x,20-u,0); horizontal displacement fixed to zero, common prescribed vertical compression u>=0.",
    "free": "Nodes 5..19 have 30 free x/y degrees of freedom. Solve grad_free(U)=0. Do not hold interior x coordinates fixed or impose affine displacements.",
    "reaction_sign": "F(u)=-sum_{n=20..24}(dU/dy_n), so positive F is compressive; equivalently dU_equilibrium/du. Do not take abs() to hide a sign error."
  },
  "target": {
    "u_mm": [
      0.4,
      0.8,
      1.2,
      1.6,
      2.0,
      2.4,
      2.8,
      3.2,
      3.6,
      4.0
    ],
    "compression_force_N": [
      4.0,
      8.0,
      12.0,
      15.5,
      16.0,
      16.2,
      16.4,
      16.6,
      16.8,
      17.0
    ],
    "origin": "Author-defined synthetic desired response; not experimental data or a claim of an optimum.",
    "objective": "NRMSE=sqrt(mean_k((F_k-F_target,k)^2))/17.0; compare only the 10 prescribed points, equally weighted, and never omit failed points.",
    "max_nrmse": 0.03,
    "min_fractional_error_reduction_from_baseline": 0.3,
    "improvement_definition": "(NRMSE_baseline-NRMSE_selected)/NRMSE_baseline, using successful coarse traces of both. A baseline convergence failure is not an infinite baseline error and cannot earn an improvement score."
  },
  "solver_contract": {
    "coarse_u_mm": "u=0,0.10,0.20,...,4.00 (41 points including zero)",
    "continuation": "Start at the stress-free X. At each new u, update prescribed top coordinates, retain the previous converged free coordinates as the initial guess and find a nearby stable equilibrium using a safeguarded Newton/trust-region/energy-minimization method. Do not reset to an affine guess at every step or jump to an unreported branch. The energy is nonconvex: record branch changes and the continuation path.",
    "max_iterations_per_step": 200,
    "max_line_search_trials_per_iteration": 40,
    "residual_infinity_norm_max_N": 1e-05,
    "minimum_free_tangent_eigenvalue_min_N_per_mm": -1e-06,
    "stretch_lower_bound_exclusive": 0.0,
    "mandatory_log_fields": [
      "design_id",
      "r_vertical_mm",
      "r_diagonal_mm",
      "u_mm",
      "iterations",
      "residual_inf_N",
      "energy_N_mm",
      "reaction_N",
      "min_free_tangent_eigenvalue_N_per_mm",
      "converged",
      "failure_reason",
      "branch_change_note"
    ],
    "acceptance": "Every reported curve point needs an actual converged free equilibrium and stable free tangent within tolerances. A plotted target, imposed nodal interpolation, closed-form stiffness approximation or fixed number of unconverged iterations does not count as a solve. Failed intermediate steps invalidate that continuation trace; do not silently interpolate past them."
  },
  "independent_recheck": {
    "execution": "Launch a fresh process, reconstruct graph/reference lengths/areas from the exported design and source, and restart from u=0. Do not reuse coarse free-node states or cached reaction values.",
    "fine_u_mm": "u=0,0.05,0.10,...,4.00 (81 points including zero)",
    "force_refinement_error": "max_k(abs(F_fine,k-F_coarse,k))/17.0 <= 0.01 at the same 10 target displacements",
    "target_check": "The refined curve must also satisfy NRMSE<=0.03, with all equilibrium/stability conditions. Refinement failure means the design is not verified even if its coarse fit is good.",
    "gradient_check": "At the refined final state, independently central-difference total scalar U in each of the 30 free coordinates with h=1e-5 mm; compare with the solver's assembled gradient. max absolute gradient discrepancy <=1e-4 N. Also central-difference scalar U with respect to the common top compression, keeping free coordinates fixed at that state; compare to the assembled F with absolute discrepancy <=1e-4 N. This local derivative check is additional to the fresh refined equilibrium solve.",
    "geometry_check": "Re-read selected_lattice.stl in a separate validation step; report finite vertices, positive volume, watertightness, connected-component count=1, and actual bounding box. Compare node/edge identities and radii in graph.json and design.json against the generated source. STL dimensions alone cannot verify every radius; retain the parameterized construction and edge-to-radius table."
  }
}
```

### 交付

- solve_and_design.py (or equivalent runnable open-source implementation), requirements.txt and one-command offline reproduction instructions
- graph.json with stress-free node coordinates, unique edge endpoint IDs, families, radii, rest lengths and units
- design.json with the baseline, every attempted design, selected parameters, stated evaluation budget and explicit target_met boolean
- iterations.csv or JSON with every attempted design and every attempted load step, including failures; baseline and selected force curves
- selected_lattice.stl and runnable parameterized CAD generation source; actual re-read geometry_report.json; STEP optional only if genuinely exported
- refinement_report.json with fresh-process commands, coarse/fine comparisons, finite-difference checks and independent convergence/stability traces
- answer.md distinguishing measured artifact geometry, solved discrete mechanics, unmet constraints and limits of the idealization

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "success_requires_all": [
      "Complete graph, synthetic nonlinear law, boundary conditions and undeformed zero-state anchors are correct.",
      "A valid baseline and at least one different design if baseline fails are actually solved within the 8-design budget; all attempted designs and failed steps remain visible.",
      "Selected coarse and independently refined target NRMSE are both <=0.03; coarse error reduction from baseline is >=30%.",
      "All equilibrium/stability, <=1% refinement and finite-difference thresholds pass without omitted load steps or unexplained branch substitution.",
      "Actual connected watertight positive-volume CAD and all reproduction/trace files can be opened and checked; geometry matches the selected parameter vector.",
      "Conclusion keeps the discrete pin-joint synthetic model separate from continuum FEA, experimental performance and manufacturing certification."
    ],
    "honest_unmet_target": "Report target_met=false with actual errors, usable source/artifacts where available and a bounded diagnosis. Award only rubric checks supported by evidence; do not convert honest failure into full task success.",
    "no_solution_claim": "The challenge does not require proof of global optimality. A feasible design establishes only the specified numerical-model acceptance conditions."
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 3600,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 60000,
    "model_calls": 16,
    "tool_calls": 80
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "node_count": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "edge_count": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "free_dof_count": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "coarse_load_point_count": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "refined_load_point_count": {
    "unit": "1",
    "abs_tol": 0,
    "rel_tol": 1e-05
  },
  "undeformed_energy_N_mm": {
    "unit": "N mm",
    "abs_tol": 1e-10,
    "rel_tol": 1e-05
  },
  "undeformed_reaction_N": {
    "unit": "N",
    "abs_tol": 1e-10,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S01](https://www.nature.com/articles/s42256-025-01067-x)；[S05](https://arxiv.org/abs/2410.02090)。

## LAT-23 · 多功能约束冲突的有限模型证书与最小授权放宽重建

类别：`research_challenge` · 难度：research · 主题：multifunctional_design, feasibility_certificate, geometry_calibration, decision_under_constraints

这是一个明确限定模型的合成多目标设计任务，不是材料真实性能试验。外包络固定为 [0,20]³ mm，合成实体材料密度 1.20 g/cm³。唯一允许的拓扑是四胞元/轴、胞长 a=5 mm 的简单立方杆系：对每对 i,j∈{0,1,2,3,4}，建立分别平行 x、y、z 轴、另外两个坐标为 (5i,5j)、轴向长度覆盖 [0,20] 的圆柱，共 75 根连续圆柱；所有圆柱同半径 r∈[0.40,1.75] mm，取实体并集并裁切到固定盒中。必须计算节点重叠后的真实实体体积，不能直接相加圆柱体积。令 φ=实际导出实体体积/8000。只在本题中定义三个合成代理响应：E_syn=1000φ² MPa，k_syn=0.20+2φ W/(m·K)，K_syn=(1−φ)³/φ² mm²。这些等式是题设给定的响应模型，没有物理验证。原要求为质量≤3.20 g、E_syn≥160 MPa、k_syn≥1.10 W/(m·K)、K_syn≥0.60 mm²，最小设计杆径≥0.80 mm。先证明在该拓扑/密度/代理模型范围内是否存在同时满足条件的 φ：给出相互冲突的定量上下界，不可把搜索失败当作证明，更不能宣布任意点阵都不可能。然后执行事先授权的放宽规则：所有几何、三个响应目标和材料密度保持不变，只允许质量上限增加，候选上限必须为 0.05 g 的整数倍；选取使约束存在可行解的最小上限。给出连续质量下界、离散授权上限和改变量。按放宽后模型实际生成、导出并检查一个简单立方点阵。为避免靠容差钻边界，几何校准目标为 φ_target=(由固定响应约束导出的 φ 下界+推导得到的最小授权质量上限/密实盒质量)/2，校准可改变 r，至少保留两个实际构建/测量的不同 r 候选和最终选择记录。重新读取最终 STL，采用至少两级几何精度（粗级≤0.15 mm，细级≤0.075 mm 的采样间距或三角化弦差），估计体积/φ误差；整个 φ 误差区间必须满足所有放宽后约束才能宣布代理模型可行。提供完整源文件、原问题无解证书、放宽决策、候选日志、最终 STL 和结果 JSON。水密、单一连通分量、非空、包围盒 [0,20]³（每侧偏差≤0.075 mm）均需实测；节点并集和边界裁切必须正确。明确最终结论只在题设代理模型内成立，不等于通过 FEA、热流模拟、渗透试验或实际加工验证。

### 输入

```json
{
  "synthetic": true,
  "box_mm": [
    [
      0,
      20
    ],
    [
      0,
      20
    ],
    [
      0,
      20
    ]
  ],
  "cell_mm": 5,
  "nodes_per_axis": 5,
  "continuous_cylinder_count": 75,
  "radius_interval_mm": [
    0.4,
    1.75
  ],
  "synthetic_density_g_cm3": 1.2,
  "proxy_domain": "0<phi<1; phi equals measured Boolean-union volume divided by 8000 mm^3",
  "proxy_models": {
    "E_syn_MPa": "1000*phi^2",
    "k_syn_W_mK": "0.2+2*phi",
    "K_syn_mm2": "(1-phi)^3/phi^2"
  },
  "original_constraints": {
    "mass_g_max": 3.2,
    "E_syn_MPa_min": 160,
    "k_syn_W_mK_min": 1.1,
    "K_syn_mm2_min": 0.6,
    "designed_diameter_mm_min": 0.8
  },
  "authorized_relaxation": {
    "modifiable_constraint": "mass_g_max_only",
    "grid_step_g": 0.05,
    "objective": "smallest mass-cap grid point admitting a feasible phi in the specified topology and model",
    "all_other_constraints_fixed": true
  },
  "density_calibration_target_expression": "(phi_lower_bound_derived_from_fixed_response_constraints + derived_minimal_authorized_mass_cap_g / derived_dense_box_mass_g) / 2",
  "physical_validation": false
}
```

### 交付

- infeasibility_certificate.json：原问题的 φ 上下界、导出公式和模型作用域
- relaxation_decision.json：连续最小质量、最小 0.05 g 网格上限、保持不变的条件以及可行密度区间
- 可运行的参数化简单立方杆系生成器和真实 final.stl
- candidate_journal.json：至少两个不同半径候选的实际构建、并集体积、响应和失败/通过记录
- geometry_report.json：重读体积、φ误差区间、质量与三个代理响应区间、包围盒、水密性、分量和收敛
- 简明结论：原限定模型无解、授权放宽后是否实际满足代理及几何目标、仍未做的物理验证

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "version": "0.2.0",
    "status": "analytic_proxy_oracles_checked_CAD_targets_not_prevalidated",
    "required_artifact_types": [
      "restricted_infeasibility_certificate",
      "authorized_relaxation_decision",
      "reproducible_source",
      "nonempty_closed_STL",
      "candidate_journal",
      "geometry_report"
    ],
    "independent_evaluator_must": [
      "recompute_analytic_bounds",
      "verify_0.05g_grid_minimality",
      "rerun_generator",
      "reload_mesh_and_measure_boolean_union_volume",
      "evaluate_proxies_from_measured_phi_interval",
      "verify_only_uniform_radius_was_tuned",
      "verify_actual_candidate_and_refinement_logs"
    ],
    "thresholds": {
      "watertight": true,
      "connected_solid_components": 1,
      "degenerate_faces": 0,
      "bbox_per_side_abs_error_mm_max": 0.075,
      "relaxed_mass_upper_bound_g_max": "derived_minimal_authorized_mass_cap_g",
      "E_syn_interval_lower_MPa_min": 160,
      "k_syn_interval_lower_W_mK_min": 1.1,
      "K_syn_interval_lower_mm2_min": 0.6,
      "designed_strut_diameter_mm_min": 0.8,
      "actual_different_radius_candidate_count_min": 2,
      "coarse_spacing_or_chord_error_mm_max": 0.15,
      "fine_spacing_or_chord_error_mm_max": 0.075
    },
    "interval_evaluation": "For measured [phi_low,phi_high], evaluate mass, E_syn and k_syn lower/upper at matching endpoints. K_syn is strictly decreasing for 0<phi<1, so its lower bound uses phi_high. All necessary bounds must pass; use no tolerance to excuse a violated engineering inequality.",
    "failure_conditions": [
      "nonoverlap claimed from optimizer failure rather than analytic bounds",
      "changes another hard constraint or topology without authorization",
      "uses sum of overlapping cylinder volumes",
      "missing actual rebuilt lattice after the certificate",
      "proxy pass presented as validated mechanical/thermal/flow performance"
    ],
    "incomplete_execution_policy": "A correct infeasibility proof alone earns only its dedicated correctness/evidence checks; it does not earn geometry-delivery or post-relaxation pass credit.",
    "tool_environment": "Both arms receive the identical installed Python, CAD kernel, mesh/CSG and DfAM tools, compute, source access and versions; freeze before running. No proprietary/private data required.",
    "trial_budget": {
      "status": "proposed_not_pilot_calibrated",
      "per_arm_wall_clock_seconds": 3600,
      "max_model_turns": 16,
      "max_tool_calls": 80,
      "max_design_candidates": 12,
      "max_aggregate_input_tokens": 250000,
      "max_aggregate_output_tokens_including_reasoning": 60000,
      "refinements_count_as_new_design_candidate": false,
      "freeze_before_live_run": true,
      "same_hardware_both_arms": true
    }
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 3600,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 60000,
    "model_calls": 16,
    "tool_calls": 80
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "dense_box_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 0,
    "rel_tol": 1e-06
  },
  "dense_box_mass_g": {
    "unit": "g",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "phi_lower_from_E": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "phi_lower_from_k": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "phi_upper_original_mass": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "continuous_minimum_mass_g": {
    "unit": "g",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "authorized_mass_cap_g": {
    "unit": "g",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "authorized_mass_cap_increase_g": {
    "unit": "g",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "phi_upper_relaxed_mass": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "phi_calibration_target": {
    "unit": "1",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "target_continuum_mass_g": {
    "unit": "g",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "target_continuum_E_syn_MPa": {
    "unit": "MPa",
    "abs_tol": 1e-06,
    "rel_tol": 1e-06
  },
  "target_continuum_k_syn_W_mK": {
    "unit": "W/(m*K)",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  },
  "target_continuum_K_syn_mm2": {
    "unit": "mm^2",
    "abs_tol": 1e-08,
    "rel_tol": 1e-06
  }
}
```

研究背景：[S01](https://www.nature.com/articles/s42256-025-01067-x)；[S08](https://www.nature.com/articles/s41598-026-41048-7)；[S09](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345912)；[S11](https://arxiv.org/abs/2609.33598)。

## LAT-24 · 损坏点阵网格：单位、拓扑和孔道保持的可复现修复

类别：`research_challenge` · 难度：research · 主题：artifact_integrity, geometry_repair, manufacturability

请修复附带的真实OBJ输入，不只描述修复方法。该合成文件故意含多个相互叠加的缺陷；文件坐标单位是m，输出必须用mm，主体设计包络[0,12]^3 mm。先保存输入SHA256并实际检测边界边、非流形边、重复/退化面、法向不一致及分量。最多允许3个有记录的修复候选，删除完全位于设计包络外的孤立碎屑，保留主体的每个设计孔道及细杆，不允许用封闭立方体或另一个规则晶格替代。完成单位转换、局部补洞与一致朝向，输出repaired.obj、repaired.stl、repair.py、before_after.json及操作记录。题设主体应为一个封闭可定向连通实体，拓扑验收Euler特征为-54（允许重三角化，按焊接后的唯一顶点/边/面计数）；逐个解释原始破口与设计孔道的区别。边界包络每轴12±0.02mm，未损坏主体表面位置最大偏移0.02mm；新增面必须局限于输入破口，不能横跨设计孔道封口。最终必须重新读取两个输出，报告实际体积/密度1.02g/cm³下质量/水密性/自交/最小特征方法与限制。两种格式的体积差≤0.1%，有一项未可靠检查就列未验证，不能靠欧拉数或法向修复宣称全部几何正确。数值schema中的体积和质量是最终测得结果，不得抄理论值冒充测量。完整成功还要求保留边界几何与孔道；自报成功或只生成检查报告不算交付。

### 输入

```json
{
  "synthetic": true,
  "input_length_unit": "m",
  "output_length_unit": "mm",
  "bbox_edge_mm": 12,
  "density_g_cm3": 1.02,
  "expected_euler_characteristic": -54,
  "max_repair_candidates": 3
}
```

### 实际输入附件

- [fixtures/LAT-24/damaged_lattice.obj](../fixtures/LAT-24/damaged_lattice.obj) · SHA256 `ca203960838d02c9c7ee1383fd9d30393908dcda10c512528dc928fc0e67eadd`
- [fixtures/LAT-24/input_metadata.json](../fixtures/LAT-24/input_metadata.json) · SHA256 `dca4f8d5097802b60560fe9e9f96e179de8681c545db29f46f6274afebd2c591`

### 交付

- repaired.obj与repaired.stl：真实可读且单位为mm
- repair.py：从附带损坏输入可重跑得到输出
- before_after.json：实际几何检查及方法/单位/局限
- repair_log.jsonl：最多3个候选及原始失败/修复步骤
- answer.md与answer.json：结果、证据和数值输出

### 可执行验收要求与试跑预算

```json
{
  "acceptance_contract": {
    "complete_success_requires": [
      "真实文件修复与双格式重读",
      "候选≤3并保存失败记录",
      "正确单位、无碎屑、无坏面、表面与孔道保持",
      "测得体积与质量容差内且OBJ/STL体积一致",
      "自交与表面偏移经过可靠检查且通过要求"
    ],
    "max_boundary_edges": 0,
    "max_nonmanifold_edges": 0,
    "max_duplicate_triangles": 0,
    "max_degenerate_triangles": 0,
    "max_inconsistent_winding_edges": 0,
    "connected_components": 1,
    "euler_characteristic": -54,
    "max_surface_displacement_mm": 0.02,
    "max_format_volume_relative_difference": 0.001,
    "measurement_note": "提供的mesh_audit只检查三角OBJ离散拓扑/包围盒/有向体积，不检查自交、几何偏移或孔道语义，不能代替完整验收。",
    "honest_incomplete_policy": "未能可靠完成自交、表面偏移或孔道检查时如实报告未验证；可获对应证据分，但不得获得相关准确性/交付检查分或完整成功。"
  },
  "trial_budget": {
    "status": "proposed_freeze_after_pilot",
    "wall_seconds": 3600,
    "total_input_tokens": 250000,
    "total_output_tokens_including_reasoning": 60000,
    "model_calls": 16,
    "tool_calls": 80
  }
}
```

### 数值输出字段（不是参考答案）

```json
{
  "coordinate_scale_to_mm": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "repaired_volume_mm3": {
    "unit": "mm^3",
    "abs_tol": 0.5,
    "rel_tol": 1e-05
  },
  "repaired_mass_g": {
    "unit": "g",
    "abs_tol": 0.0006,
    "rel_tol": 1e-05
  },
  "repaired_euler_characteristic": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  },
  "repaired_components": {
    "unit": "1",
    "abs_tol": 1e-06,
    "rel_tol": 1e-05
  }
}
```

研究背景：[S03](https://link.springer.com/article/10.1007/s00170-026-19103-4)；[S11](https://arxiv.org/abs/2609.33598)。
