"""Independent sanity anchors for research challenges; no design-solution scoring."""
import math
from decimal import Decimal,ROUND_CEILING

def oracle(case):
    d=case["inputs"];cid=case["id"]
    if cid=="LAT-21":
        # Integrate a linearly tapered circular cross section; all holes are interior.
        removed=d["inner_radius_mm"]**2+len(d["bolt_centers_xy_mm"])*d["bolt_radius_mm"]**2+d["channel_radius_mm"]**2
        def integrate(z0,z1):
            def primitive(z): return 400*z-(10/3)*z*z+z**3/108-removed*z
            return math.pi*(primitive(z1)-primitive(z0))
        plates=sum(integrate(*interval) for interval in d["mandatory_plate_z_intervals_mm"])
        rho=d["synthetic_density_g_cm3"]/1000
        return {"dense_design_domain_volume_mm3":integrate(*d["z_range_mm"]),"mandatory_plates_volume_mm3":plates,
          "mandatory_plates_mass_g":plates*rho,"mass_budget_equivalent_total_solid_volume_mm3":d["mass_limit_g"]/rho}
    if cid=="LAT-22":
        # Construct the stated graph independently; zero reference stretch follows U(1)=0.
        nodes={(i,j) for i in range(5) for j in range(5)};edges=set()
        for i,j in nodes:
            if i<4: edges.add(tuple(sorted(((i,j),(i+1,j)))))
            if j<4: edges.add(tuple(sorted(((i,j),(i,j+1)))))
            if i<4 and j<4:
                ends=((i,j),(i+1,j+1)) if (i+j)%2==0 else ((i+1,j),(i,j+1))
                edges.add(tuple(sorted(ends)))
        return {"node_count":len(nodes),"edge_count":len(edges),"free_dof_count":2*sum(0<j<4 for i,j in nodes),
          "coarse_load_point_count":round(4/.1)+1,"refined_load_point_count":round(4/.05)+1,
          "undeformed_energy_N_mm":1**2-1-2*math.log(1),"undeformed_reaction_N":1-1/1}
    if cid=="LAT-23":
        volume=math.prod(b-a for a,b in d["box_mm"]);dense_mass=volume*d["synthetic_density_g_cm3"]/1000
        limits=d["original_constraints"];phi_E=math.sqrt(limits["E_syn_MPa_min"]/1000);phi_k=(limits["k_syn_W_mK_min"]-.2)/2
        lower=max(phi_E,phi_k);min_mass=dense_mass*lower
        step=Decimal(str(d["authorized_relaxation"]["grid_step_g"]))
        cap=float((Decimal(str(min_mass))/step).to_integral_value(rounding=ROUND_CEILING)*step)
        upper=cap/dense_mass;target=(lower+upper)/2
        # Check finite geometry-family attainability and K, rather than only two proxy bounds.
        lo,hi=d["radius_interval_mm"]
        density=lambda r:3*math.pi*(r/d["cell_mm"])**2-16*(math.sqrt(2)-1)*(r/d["cell_mm"])**3
        if not density(lo)<lower<upper<density(hi): raise ValueError("Proxy feasible interval not attained by declared geometry family")
        if (1-upper)**3/upper**2<limits["K_syn_mm2_min"]: raise ValueError("K constraint invalidates proposed relaxed interval")
        return {"dense_box_volume_mm3":volume,"dense_box_mass_g":dense_mass,"phi_lower_from_E":phi_E,"phi_lower_from_k":phi_k,
          "phi_upper_original_mass":limits["mass_g_max"]/dense_mass,"continuous_minimum_mass_g":min_mass,"authorized_mass_cap_g":cap,
          "authorized_mass_cap_increase_g":cap-limits["mass_g_max"],"phi_upper_relaxed_mass":upper,"phi_calibration_target":target,
          "target_continuum_mass_g":target*dense_mass,"target_continuum_E_syn_MPa":1000*target**2,
          "target_continuum_k_syn_W_mK":.2+2*target,"target_continuum_K_syn_mm2":(1-target)**3/target**2}
    if cid=="LAT-24":
        # Independent inclusion-exclusion for the fixture's orthogonal rectangular strut bands.
        # The reconstruction recipe is evaluator-side only; it is not a candidate input.
        volume=3*(6*6*12)-2*(6**3)
        return {"coordinate_scale_to_mm":1000,"repaired_volume_mm3":volume,
          "repaired_mass_g":volume*d["density_g_cm3"]/1000,"repaired_euler_characteristic":2-2*(54-27+1),"repaired_components":1}
    raise ValueError(f"No challenge oracle: {cid}")
