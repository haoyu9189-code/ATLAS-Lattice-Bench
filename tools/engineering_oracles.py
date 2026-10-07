"""Independent engineering scalar checks against hash-checked candidate fixtures.

These are conditional screening calculations, not a material model, FEA solver,
or certification. No ATLAS predictor or evaluator reference answer is imported.
"""
import json
import math
from pathlib import Path

from input_assets import checked_asset

ROOT = Path(__file__).resolve().parents[1]


def _number(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0 or nonnegative and value < 0:
        raise ValueError(f"{name} is outside its physical domain")
    return value


def _integer(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _safety(d):
    factor = _number(d["safety_factor"], "safety_factor", positive=True)
    if factor < 1:
        raise ValueError("safety_factor must be at least one")
    return factor


def _asset(c, name, turn=1):
    # The inputs path is only a selector into the declared, hash-checked list.
    matches = [a for a in c.get("input_assets", []) if a.get("path") == name]
    if len(matches) != 1:
        raise ValueError("Requested fixture must have one declared input asset")
    item = matches[0]
    available = item.get("available_from_turn", 1)
    if type(available) is not int or available < 1 or available > turn:
        raise ValueError("Requested fixture is not available in this turn")
    return json.loads(checked_asset(item, root=ROOT).read_text(encoding="utf-8-sig"))


def _records(c, d):
    rows = _asset(c, d["database_snapshot_asset"])["records"]
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate database record IDs")
    return {r["id"]: r for r in rows}


def _dimensions(row, n=None):
    n = _integer(row["n"] if n is None else n, "cells_per_axis")
    edge = n * _number(row["cell_size_mm"], "cell_size_mm", positive=True)
    return edge, edge * edge


def _mechanics(row, n=None):
    height, area = _dimensions(row, n)
    modulus = _number(row["modulus_mpa"], "modulus_mpa", positive=True)
    strength = _number(row["yield_stress_mpa"], "yield_stress_mpa", positive=True)
    return modulus * area / height, strength * area


def _loading_envelope(curve):
    xs, ys = curve["strain"], curve["stress"]
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("Curve arrays must be aligned and contain at least two points")
    points = []
    for x, y in zip(xs, ys):
        x = _number(x, "curve strain", nonnegative=True)
        y = _number(y, "curve stress", nonnegative=True)
        if not points or x > points[-1][0]:
            points.append((x, y))
    if len(points) < 2 or points[0][0] != 0 or points[0][1] != 0:
        raise ValueError("Loading envelope requires an explicit zero origin and increasing strains")
    return points


def _first_crossing(points, stress):
    stress = _number(stress, "requested stress", nonnegative=True)
    if stress == points[0][1]:
        return points[0][0]
    # Traverse in acquisition order: an early upward crossing beats a later
    # exact stress sample after softening/reloading.
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if y0 <= stress <= y1 and y1 > y0:
            return x0 + (stress - y0) * (x1 - x0) / (y1 - y0)
    raise ValueError("Requested load has no first attainment in the supplied curve")


def _offset_yield_sample(row):
    """Check the declared 0.5% offset convention at the saved sample, not its root."""
    modulus = _number(row["modulus_mpa"], "modulus_mpa", positive=True)
    curve = row["curve"]
    # LAT-25's curve has already been shape/finite checked by _loading_envelope;
    # preserve the raw sample order for the database feature convention.
    previous = None
    for strain, stress in zip(curve["strain"], curve["stress"]):
        difference = stress - modulus * (strain - .005)
        if previous is not None and previous > 0 >= difference:
            if not (math.isclose(strain, row["yield_strain"], rel_tol=1e-12, abs_tol=1e-12)
                    and math.isclose(stress, row["yield_stress_mpa"], rel_tol=1e-12, abs_tol=1e-12)):
                raise ValueError("Saved yield does not match the first 0.5% offset crossing sample")
            return strain, stress
        previous = difference
    raise ValueError("No 0.5% offset crossing; an endpoint fallback is not confirmed yield")


def _integral(points, end):
    end = _number(end, "energy_end_strain", nonnegative=True)
    if end > points[-1][0]:
        raise ValueError("Energy integration would extrapolate beyond the supplied curve")
    total = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        right = min(x1, end)
        if right <= x0:
            break
        yright = y0 + (right - x0) * (y1 - y0) / (x1 - x0)
        total += (right - x0) * (y0 + yright) / 2
        if right == end:
            break
    return total


def _final_inputs(c):
    d = dict(c["inputs"])
    turn = 1
    for next_turn, step in enumerate(c.get("followup_turns", []), 2):
        if step.get("turn", next_turn) != next_turn:
            raise ValueError("Followup turns must be explicitly ordered")
        d.update(step["inputs_update"])
        turn = next_turn
    return d, turn


def _parallel(left, right, factor):
    if _dimensions(left)[0] != _dimensions(right)[0]:
        raise ValueError("Guided parallel blocks require equal height")
    kl, fyl = _mechanics(left)
    kr, fyr = _mechanics(right)
    total = kl + kr
    return kl, kr, total * min(fyl / kl, fyr / kr) / factor


def _radius_table(rows):
    ordered = sorted(rows, key=lambda r: r["radius"])
    if len(ordered) < 2:
        raise ValueError("Radius interpolation requires at least two records")
    geometry = {(r["topology"], r["n"], r["cell_size_mm"], r["slider"], r["mode"]) for r in rows}
    if len(geometry) != 1:
        raise ValueError("Radius records must have matching topology, size, slider and loading mode")
    for row in ordered:
        _number(row["radius"], "radius", positive=True)
        _mechanics(row)
    for lo, hi in zip(ordered, ordered[1:]):
        if hi["radius"] <= lo["radius"] or hi["yield_stress_mpa"] <= lo["yield_stress_mpa"]:
            raise ValueError("Radius inversion requires distinct radii and strictly increasing yield stress")
    return ordered


def _interpolate(rows, radius, field):
    radius = _number(radius, "radius", positive=True)
    if not rows[0]["radius"] <= radius <= rows[-1]["radius"]:
        raise ValueError("Radius interpolation cannot extrapolate")
    for lo, hi in zip(rows, rows[1:]):
        if lo["radius"] <= radius <= hi["radius"]:
            weight = (radius - lo["radius"]) / (hi["radius"] - lo["radius"])
            return lo[field] + weight * (hi[field] - lo[field])
    raise ValueError("No bracketing radius records")


def oracle(c):
    """Return scalar anchors from public inputs only; partial turns stay partial."""
    cid = c["id"]
    if cid not in {f"LAT-{i}" for i in range(25, 33)}:
        raise ValueError(f"No engineering oracle: {cid}")
    d = c["inputs"]
    records = _records(c, d)
    if cid == "LAT-25":
        row = records[d["record_id"]]
        height, area = _dimensions(row)
        stiffness, yield_force = _mechanics(row)
        points = _loading_envelope(row["curve"])
        _offset_yield_sample(row)
        loads = d["load_levels_N"]
        if len(loads) != 3:
            raise ValueError("LAT-25 requires exactly three load levels")
        result = {"effective_modulus_MPa": row["modulus_mpa"], "stiffness_N_per_mm": stiffness,
                  "offset_yield_force_N": yield_force,
                  "offset_yield_displacement_mm": _number(row["yield_strain"], "yield_strain", nonnegative=True) * height,
                  "screening_allowable_N": yield_force / _safety(d),
                  "absorbed_energy_J": _integral(points, d["energy_end_strain"]) * area * height / 1000,
                  "load3_yield_ratio": _number(loads[2], "load", nonnegative=True) / yield_force}
        for i, load in enumerate(loads, 1):
            result[f"displacement_load{i}_mm"] = _first_crossing(points, _number(load, "load", nonnegative=True) / area) * height
        return result
    if cid == "LAT-26":
        force = _number(d["service_force_N"], "service_force_N", positive=True)
        factor = _safety(d)
        maximum = _number(d["max_displacement_mm"], "max_displacement_mm", positive=True)
        if len(set(d["candidate_ids"])) != len(d["candidate_ids"]):
            raise ValueError("Candidate records must be unique")
        feasible = []
        for rid in d["candidate_ids"]:
            stiffness, yield_force = _mechanics(records[rid])
            if yield_force >= factor * force and force / stiffness <= maximum:
                feasible.append((stiffness, rid, yield_force))
        if not feasible:
            raise ValueError("No feasible candidate under the stated screening assumptions")
        stiffness, _, yield_force = min(feasible)
        return {"feasible_count": len(feasible), "selected_stiffness_N_per_mm": stiffness,
                "selected_offset_yield_force_N": yield_force, "selected_displacement_mm": force / stiffness,
                "selected_yield_margin": yield_force / (factor * force) - 1}
    if cid == "LAT-27":
        row = records[d["record_id"]]
        n = _integer(d["target_cells_per_axis"], "target_cells_per_axis")
        _, area = _dimensions(row, n)
        stiffness, yield_force = _mechanics(row, n)
        force = _number(d["service_force_N"], "service_force_N", nonnegative=True)
        band = _number(d["sensitivity_fraction"], "sensitivity_fraction", nonnegative=True)
        if band >= 1:
            raise ValueError("Sensitivity fraction must be less than one")
        refs = _asset(c, d["reference_asset"])["references"]
        topology = next(r for r in refs if r["topology"] == row["topology"])
        values = {r["n"]: r["features"]["values"] for r in topology["reference_curves"]}
        relative = lambda field: abs(values[4][field] - values[5][field]) / _number(values[5][field], field, positive=True)
        bcc = next(r for r in refs if r["topology"] == "BCC")
        direct = sum(r["n"] == 5 and r.get("source_kind") == "reference" and r.get("method") == "reference_fea" for r in bcc["reference_curves"])
        return {"target_cell_count": n ** 3, "nominal_area_mm2": area,
                "proxy_stiffness_N_per_mm": stiffness, "proxy_yield_force_N": yield_force,
                "sensitivity_low_allowable_N": (1 - band) * yield_force / _safety(d),
                "sensitivity_high_displacement_mm": force / ((1 - band) * stiffness),
                "reference_E_relative_change": relative("modulus_mpa"),
                "reference_yield_relative_change": relative("yield_stress_mpa"), "bcc_direct_n5_count": direct}
    if cid == "LAT-28":
        factor = _safety(d)
        left, right = records[d["left_record_id"]], records[d["right_record_id"]]
        kl, kr, allowable = _parallel(left, right, factor)
        force = _number(d["total_force_N"], "total_force_N", positive=True)
        result = {"initial_displacement_mm": force / (kl + kr), "initial_left_force_N": force * kl / (kl + kr),
                  "initial_allowable_N": allowable}
        final, turn = _final_inputs(c)
        if turn == 1:
            return result
        force = _number(final["total_force_N"], "total_force_N", positive=True)
        new_kl, new_kr, new_allowable = _parallel(records[final["replacement_left_record_id"]], right, _safety(final))
        result.update(upgraded_original_left_force_N=force * kl / (kl + kr),
                      upgraded_original_margin=allowable / force - 1,
                      revised_displacement_mm=force / (new_kl + new_kr),
                      revised_allowable_N=new_allowable, revised_margin=new_allowable / force - 1)
        return result
    if cid == "LAT-29":
        row = records[d["record_id"]]
        height, area = _dimensions(row)
        strength = _number(row["yield_stress_mpa"], "yield_stress_mpa", positive=True)
        force = _number(d["force_N"], "force_N", positive=True)
        eccentricity = _number(d["eccentricity_mm"], "eccentricity_mm", nonnegative=True)
        secondary = _number(d["secondary_eccentricity_mm"], "secondary_eccentricity_mm", nonnegative=True)
        section = height ** 3 / 6
        stress = force / area
        peak = stress + force * eccentricity / section
        factor = _safety(d)
        return {"section_modulus_mm3": section, "nominal_stress_MPa": stress, "max_edge_stress_MPa": peak,
                "min_edge_stress_MPa": stress - force * eccentricity / section,
                "screening_allowable_N": strength / (factor * (1 / area + eccentricity / section)),
                "yield_margin": strength / (factor * peak) - 1, "kern_limit_mm": height / 6,
                "secondary_min_edge_stress_MPa": stress - force * secondary / section}
    if cid == "LAT-30":
        rows = _radius_table([records[rid] for rid in d["radius_records"]])
        nominal = _number(d["nominal_radius_mm"], "nominal_radius_mm", positive=True)
        tolerance = _number(d["radius_tolerance_mm"], "radius_tolerance_mm", nonnegative=True)
        force = _number(d["service_force_N"], "service_force_N", positive=True)
        factor = _safety(d)
        height, area = _dimensions(rows[0])
        low, high = nominal - tolerance, nominal + tolerance
        strength = lambda r: _interpolate(rows, r, "yield_stress_mpa")
        required = factor * force / area
        if required <= rows[0]["yield_stress_mpa"]:
            radius = rows[0]["radius"]
        elif required > rows[-1]["yield_stress_mpa"]:
            raise ValueError("Required yield strength is outside the radius records")
        else:
            lo, hi = next((lo, hi) for lo, hi in zip(rows, rows[1:]) if lo["yield_stress_mpa"] <= required <= hi["yield_stress_mpa"])
            radius = lo["radius"] + (required - lo["yield_stress_mpa"]) * (hi["radius"] - lo["radius"]) / (hi["yield_stress_mpa"] - lo["yield_stress_mpa"])
        required_nominal = radius + tolerance
        # Both ends of the recommended tolerance interval must be supported.
        strength(required_nominal + tolerance)
        return {"nominal_yield_margin": strength(nominal) * area / (factor * force) - 1,
                "low_radius_mm": low, "high_radius_mm": high,
                "low_stiffness_N_per_mm": _interpolate(rows, low, "modulus_mpa") * area / height,
                "low_offset_yield_force_N": strength(low) * area,
                "worst_yield_margin": strength(low) * area / (factor * force) - 1,
                "best_yield_margin": strength(high) * area / (factor * force) - 1,
                "required_nominal_radius_mm": required_nominal}
    if cid == "LAT-31":
        row = records[d["record_id"]]
        source = _number(d["assumed_source_solid_E_MPa"], "source modulus", positive=True)
        target = _number(d["target_solid_E_MPa"], "target modulus", positive=True)
        modulus = _number(row["modulus_mpa"], "effective modulus", positive=True)
        height, area = _dimensions(row)
        ratio = target / source
        stiffness = modulus * ratio * area / height
        density_ratio = _number(d["target_density_g_cm3"], "target density", positive=True) / _number(d["assumed_source_density_g_cm3"], "source density", positive=True)
        return {"normalized_modulus": modulus / source, "elastic_scale_factor": ratio,
                "target_effective_modulus_MPa": modulus * ratio, "target_stiffness_N_per_mm": stiffness,
                "elastic_displacement_mm": _number(d["force_N"], "force_N", nonnegative=True) / stiffness,
                "mass_ratio_for_identical_geometry": density_ratio}
    # LAT-32: never recover audited metrics from display-downsampled curves.
    calibration = _asset(c, d["calibration_asset"])["group"]["metrics"]["sigma20"]
    n4 = _number(records[d["simulation_n4_record_id"]]["stress20_mpa"], "N4 sigma20", positive=True)
    n5 = _number(records[d["simulation_n5_record_id"]]["stress20_mpa"], "N5 sigma20", positive=True)
    factor = _number(calibration["mean"], "calibration sigma20", positive=True) / n4
    predicted = factor * n5
    result = {"calibration_factor": factor, "predicted_n5_sigma20_MPa": predicted,
              "calibration_specimen_count": _integer(calibration["n"], "calibration specimen count")}
    final, turn = _final_inputs(c)
    if "validation_asset" not in final:
        return result
    observed = _asset(c, final["validation_asset"], turn)["group"]["metrics"]["sigma20"]
    mean = _number(observed["mean"], "validation sigma20", positive=True)
    result.update(observed_n5_sigma20_MPa=mean, validation_relative_error=abs(predicted - mean) / mean,
                  validation_bias_MPa=predicted - mean,
                  observed_n5_sample_sd_MPa=_number(observed["sd"], "sample SD", nonnegative=True),
                  validation_specimen_count=_integer(observed["n"], "validation specimen count"))
    return result
