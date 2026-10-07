"""Independent formula oracles for synthetic scalar anchors, not CAD certification."""
import itertools
import math

def flatten(values):
    result={}
    for key,value in values.items():
        if isinstance(value,dict): result.update(flatten(value))
        else: result[key]=value
    return result

def states(case):
    initial=flatten(case["inputs"])
    final=dict(initial)
    for turn in case["followup_turns"]:
        if isinstance(turn,dict): final.update(flatten(turn.get("inputs_update",{})))
    return initial,final

def gaussian_solve(matrix, rhs):
    a=[list(map(float,row))+[float(y)] for row,y in zip(matrix,rhs)]
    for i in range(len(a)):
        pivot=max(range(i,len(a)),key=lambda j:abs(a[j][i]))
        a[i],a[pivot]=a[pivot],a[i]
        scale=a[i][i]
        if abs(scale)<1e-12: raise ValueError("singular fixture")
        a[i]=[x/scale for x in a[i]]
        for j in range(len(a)):
            if j!=i:
                scale=a[j][i]
                a[j]=[x-scale*y for x,y in zip(a[j],a[i])]
    return [row[-1] for row in a]

def oracle(c):
    i=int(c["id"].split("-")[1]); d=c["inputs"]
    if i>20:
        from challenge_oracles import oracle as challenge_oracle
        return challenge_oracle(c)
    if i==1:
        return {"independent_designs":d["design_count"],"export_rows":d["design_count"]*len(d["N_per_axis"]),"direct_solver_runs":d["direct_solver_runs"],"array_cells":d["record"]["N"]**3}
    if i==2:
        return {f"{r['id']}_compression_tension_ratio":r["compression"]/r["tension"] for r in d["strengths_mpa"]}
    if i==3:
        r={f"rmse_{k}_mpa":math.sqrt(sum((a-b)**2 for a,b in zip(v,d["target_mpa"]))/len(v)) for k,v in d["candidate_mpa"].items()}
        r.update(train_rows=sum(x["family"]=="F1" for x in d["rows"]),validation_rows=sum(x["family"]=="F2" for x in d["rows"]),independent_trials=len({x["trial"] for x in d["rows"]}))
        return r
    if i==4:
        options=[]
        for mask in itertools.product((False,True),repeat=len(d["candidates"])):
            rows=[r for use,r in zip(mask,d["candidates"]) if use]
            ids={r["id"] for r in rows}; cost=sum(r["cost"] for r in rows)
            if cost<=d["budget"] and all(len(ids.intersection(g))<=1 for g in d["at_most_one_groups"]):
                options.append((sum(r["p_feasible"]*r["sigma"] for r in rows),cost,ids))
        best=max(options,key=lambda x:x[0])
        return {"selected_cost":best[1],"selected_score":best[0]}
    if i==5:
        r={}; xs=d["displacement_mm"]
        for name,ys in d["force_N"].items():
            integral=sum((ys[j]+ys[j+1])/2*(xs[j+1]-xs[j]) for j in range(len(xs)-1))
            energy=integral/1000; mean=integral/(xs[-1]-xs[0]); peak=max(ys)
            r.update({f"energy_{name}_J":energy,f"sea_{name}_kj_kg":energy/d["mass_g"],f"mean_force_{name}_N":mean,f"peak_{name}_N":peak,f"cfe_{name}":mean/peak})
        return r
    if i==6:
        inf,alpha,beta=gaussian_solve([[1,1/n,1/n**2] for n in d["n"]],d["strength_mpa"])
        pred=lambda n:inf+alpha/n+beta/n**2
        n=next(n for n in range(1,10001) if abs(pred(n)-inf)/abs(inf)<=d["error_limit_fraction"])
        return {"sigma_inf_mpa":inf,"alpha_mpa":alpha,"beta_mpa":beta,"sigma_n3_mpa":pred(3),"min_n_5pct":n}
    if i==7:
        required=d["working_stress_mpa"]*d["fos"]
        feasible=[r for r in d["candidates"] if r["strength_mpa"]>=required and r["conductivity_W_mK"]>=d["min_conductivity"] and r["relative_density"]<=d["max_relative_density"]]
        objectives=("strength_mpa","conductivity_W_mK")
        pareto=[r for r in feasible if not any(all(s[k]>=r[k] for k in objectives) and any(s[k]>r[k] for k in objectives) for s in feasible)]
        selected=max(feasible,key=lambda r:r["conductivity_W_mK"])
        return {"required_strength_mpa":required,"feasible_count":len(feasible),"pareto_count":len(pareto),"selected_margin_fraction":selected["strength_mpa"]/required-1}
    if i==8:
        r={}
        for row in d["candidates"]:
            name=row["id"]; diameter=row["nominal_d_mm"]-d["diameter_loss_mm"]
            strength=row["nominal_strength_mpa"]*(diameter/row["nominal_d_mm"])**3
            r.update({f"worst_d_{name}_mm":diameter,f"strength_{name}_mpa":strength,f"margin_{name}_fraction":strength/(d["working_stress_mpa"]*d["fos"])-1})
        return r
    initial,f=states(c)
    if i==9:
        b=d["box_edge_mm"]; cell=d["cell_mm"]
        def gyroid(x,y,z):
            u,v,w=(2*math.pi*t/cell for t in (x,y,z))
            return math.sin(u)*math.cos(v)+math.sin(v)*math.cos(w)+math.sin(w)*math.cos(u)
        return {"cell_count_per_axis":b/cell,"box_volume_mm3":b**3,"network_continuum_volume_mm3":b**3/2,"network_continuum_porosity":.5,"G_center":gyroid(6,6,6),"G_offset_x":gyroid(7.5,6,6)}
    if i==10:
        x,y,z,t=(d[k] for k in ("core_x_mm","core_y_mm","core_z_mm","plate_thickness_mm"))
        blend=lambda s:3*s**2-2*s**3
        return {"core_volume_mm3":x*y*z,"outer_height_mm":z+2*t,"outer_box_volume_mm3":x*y*(z+2*t),"plates_volume_mm3":2*x*y*t,"blend_bottom":blend(0),"blend_mid":blend(.5),"blend_top":blend(1),"level_mid":(d["sheet_level_bottom"]+d["sheet_level_top"])/2}
    if i==11:
        n,a,r=d["cells_per_axis"],d["cell_mm"],d["strut_radius_mm"]
        # Enumerate global graph independently, rather than only restating counts.
        corners=set(); centers=set(); edges=set()
        for cell in itertools.product(range(n),repeat=3):
            center=tuple((x+.5)*a for x in cell); centers.add(center)
            for delta in itertools.product((0,1),repeat=3):
                corner=tuple((x+y)*a for x,y in zip(cell,delta));corners.add(corner)
                edges.add(tuple(sorted((center,corner))))
        length=sum(math.dist(*edge) for edge in edges)
        return {"graph_nodes":len(corners|centers),"graph_edges":len(edges),"edge_length_mm":a*math.sqrt(3)/2,"total_centerline_length_mm":length,"sum_uncut_cylinder_volume_mm3":math.pi*r*r*length,"design_box_volume_mm3":d["clip_box_edge_mm"]**3,"strut_diameter_mm":2*r}
    if i==12:
        a,h=d["square_side_mm"],d["part_thickness_mm"];count=d["rows"]*d["columns"]
        pitch=lambda deg:a*(math.cos(math.radians(deg))+math.sin(math.radians(deg)))
        p0,p1=pitch(d["initial_angle_deg"]),pitch(d["final_angle_deg"]);eps=p1/p0-1
        return {"parts_per_state":count,"part_volume_mm3":a*a*h,"assembly_solid_volume_mm3":count*a*a*h,"pitch_15_mm":p0,"pitch_30_mm":p1,"bbox_xy_15_mm":2*p0,"bbox_xy_30_mm":2*p1,"strain_x":eps,"strain_y":eps,"secant_poisson":-eps/eps}
    if i==13:
        n=f["cells_per_axis"];edge=n*f["cell_mm"];stress=f["force_N"]/edge**2
        return {"initial_nominal_stress_MPa":initial["force_N"]/(initial["cells_per_axis"]*initial["cell_mm"])**2,"final_core_edge_mm":edge,"final_height_mm":edge+2*f["plate_mm"],"final_plate_volume_mm3":2*edge**2*f["plate_mm"],"final_force_N":f["force_N"],"final_radius_mm":f["radius_mm"],"final_nominal_stress_MPa":stress,"nominal_headroom_MPa":f["nominal_stress_limit_MPa"]-stress,"graph_edges":8*n**3}
    if i==14:
        edge=f["cells_per_axis"]*f["cell_mm"];rho=f["density_g_cm3"]/1000;F=f["force_N"];fos=f["safety_factor"];design=F*fos/edge**2
        return {"outer_x_mm":edge,"outer_y_mm":edge,"outer_z_mm":edge+2*f["plate_mm"],"two_plate_volume_mm3":2*edge**2*f["plate_mm"],"final_density_g_mm3":rho,"maximum_solid_volume_mm3":f["max_mass_g"]/rho,"new_old_mass_ratio":f["density_g_cm3"]/initial["density_g_cm3"],"service_nominal_stress_MPa":F/edge**2,"design_force_N":F*fos,"design_nominal_stress_MPa":design,"screening_margin_percent":(f["nominal_allowable_MPa"]/design-1)*100}
    if i==15:
        b,cside=f["rectangle_width_mm"],f["rectangle_height_mm"]
        def pitch(deg):
            angle=math.radians(deg)
            return b*math.cos(angle)+cside*math.sin(angle),b*math.sin(angle)+cside*math.cos(angle)
        x0,y0=pitch(initial["initial_angle_deg"]);x1,y1=pitch(f["target_angle_deg"])
        ex,ey=x1/x0-1,y1/y0-1;h=f["thickness_mm"];v=b*cside*h
        ma=2*v*f["material_A_density_g_cm3"]/1000;mb=2*v*f["material_B_density_g_cm3"]/1000
        return {"px_initial_mm":x0,"py_initial_mm":y0,"px_final_mm":x1,"py_final_mm":y1,"final_bbox_x_mm":2*x1,"final_bbox_y_mm":2*y1,"final_bbox_z_mm":h,"strain_x":ex,"strain_y":ey,"secant_poisson":-ey/ex,"part_volume_mm3":v,"total_solid_volume_mm3":4*v,"material_A_mass_g":ma,"material_B_mass_g":mb,"total_mass_g":ma+mb}
    if i==16:
        n,a,r,t,hole=f["cells_per_axis"],f["cell_mm"],f["radius_mm"],f["plate_mm"],f["hole_diameter_mm"]
        edge=n*a;nodes=list(itertools.product(range(n+1),repeat=3))
        edges=[(p,q) for p,q in itertools.combinations(nodes,2) if sum(abs(x-y) for x,y in zip(p,q))==1]
        return {"graph_nodes":len(nodes),"graph_edges":len(edges),"total_centerline_length_mm":len(edges)*a,"final_strut_diameter_mm":2*r,"final_total_height_mm":edge+2*t,"holes_per_plate":n*n,"min_hole_to_outer_edge_ligament_mm":a/2-hole/2,"min_adjacent_hole_ligament_mm":a-hole,"two_plates_after_holes_volume_mm3":2*t*(edge**2-n*n*math.pi*(hole/2)**2),"nominal_stress_MPa":f["force_N"]/edge**2}
    if i==17:
        forces=d["reaction_force_N"]
        return {"last_relative_change":abs(forces[-1]-forces[-2])/abs(forces[-1]),"allowed_change_fraction":d["relative_tolerance"]}
    if i==18:
        jobs={event["job"] for event in d["job_events"] if event["event"] in ("create","create_retry")}
        valid=[e for e in d["job_events"] if e["event"]=="download" and e["manifest_sha256"]==e["actual_sha256"] and d["cad_bytes_provided"]]
        return {"logical_jobs":len(jobs),"verified_deliverable_cad":len(valid),"download_retries_remaining":d["download_retries_remaining"]}
    if i==19:
        p,q=d["training_points"];w=(d["interpolation_query"]-p["rho"])/(q["rho"]-p["rho"])
        lo=p["lower_Hz"]+w*(q["lower_Hz"]-p["lower_Hz"]);hi=p["upper_Hz"]+w*(q["upper_Hz"]-p["upper_Hz"])
        return {"interpolation_weight":w,"lower_Hz":lo,"upper_Hz":hi,"bandwidth_Hz":hi-lo,"relative_bandwidth":(hi-lo)/((hi+lo)/2)}
    if i==20:
        a=next(row for row in d["candidates"] if row["id"]=="A")
        return {"hydraulic_power_A_W":a["pressure_drop_Pa"]*a["flow_m3_s"],"max_allowed_pressure_drop_Pa":d["max_hydraulic_power_W"]/d["flow_m3_s"]}
    raise ValueError(f"No oracle for {c['id']}")
