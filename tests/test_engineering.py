"""Independent dimensional, staged-access and hand-calculated engineering checks."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import engineering_oracles as eng
from export_case import build_packet
from input_assets import checked_asset


def row(rid="kelvin", **updates):
    result = {"id": rid, "topology": "Kelvin", "n": 2, "cell_size_mm": 5,
              "radius": .4, "slider": 4, "mode": "StaCompre", "source_kind": "estimated",
              "modulus_mpa": 100, "yield_stress_mpa": 5, "yield_strain": .06,
              "stress20_mpa": 8,
              "curve": {"strain": [0, .02, .04, .06, .1, .2], "stress": [0, 2, 4, 5, 4, 8]}}
    result.update(updates)
    return result


class EngineeringOracleTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / "exports"
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base, prefix="test-engineering-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patcher = patch.object(eng, "ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.assets = []

    def asset(self, basename, data, turn=1):
        relative = "fixtures/engineering/" + basename
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        metadata = {"path": relative, "role": "candidate_input", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "available_from_turn": turn}
        self.assets.append(metadata)
        return relative

    def case(self, number, inputs, rows=None):
        snapshot = self.asset("atlas_records.json", {"records": rows or [row()]})
        return {"id": f"LAT-{number}", "inputs": {"database_snapshot_asset": snapshot, **inputs},
                "input_assets": self.assets, "followup_turns": []}

    def test_full_curve_first_load_attainment_and_truncated_energy(self):
        case = self.case(25, {"record_id": "kelvin", "load_levels_N": [100, 300, 500],
                              "safety_factor": 2, "energy_end_strain": .15})
        got = eng.oracle(case)
        self.assertEqual(got["effective_modulus_MPa"], 100)
        self.assertEqual(got["stiffness_N_per_mm"], 1000)
        self.assertEqual(got["offset_yield_force_N"], 500)
        self.assertEqual(got["screening_allowable_N"], 250)
        self.assertAlmostEqual(got["offset_yield_displacement_mm"], .6)
        self.assertAlmostEqual(got["displacement_load1_mm"], .1)
        self.assertAlmostEqual(got["displacement_load2_mm"], .3)
        self.assertAlmostEqual(got["displacement_load3_mm"], .6)
        # Hand-integrated trapezoids: .02 + .06 + .09 + .18 + .25 MPa.
        self.assertAlmostEqual(got["absorbed_energy_J"], .6)
        self.assertEqual(got["load3_yield_ratio"], 1)

    def test_loading_envelope_does_not_sort_unloading_or_choose_later_equal_stress(self):
        curve = {"strain": [0, .02, .01, .04, .06, .1], "stress": [0, 2, 90, 4, 3, 2]}
        points = eng._loading_envelope(curve)
        self.assertNotIn((.01, 90), points)
        self.assertAlmostEqual(eng._first_crossing(points, 2), .02)
        self.assertAlmostEqual(eng._first_crossing(points, 3), .03)
        with self.assertRaises(ValueError):
            eng._first_crossing(points, 5)
        with self.assertRaises(ValueError):
            eng._integral(points, .11)

    def test_offset_yield_is_first_saved_sample_not_interpolated_intersection(self):
        original = row()
        self.assertEqual(eng._offset_yield_sample(original), (.06, 5))
        # This piecewise curve intersects the offset line at strain .05, stress
        # 4.5. The database convention deliberately retains the .06 sample.
        interpolated = row(yield_strain=.05, yield_stress_mpa=4.5)
        with self.assertRaisesRegex(ValueError, "first 0.5% offset"):
            eng._offset_yield_sample(interpolated)
        endpoint = row(yield_strain=.2, yield_stress_mpa=8)
        with self.assertRaisesRegex(ValueError, "first 0.5% offset"):
            eng._offset_yield_sample(endpoint)
        no_yield = row(curve={"strain": [0, .1, .2], "stress": [0, 10, 20]})
        with self.assertRaisesRegex(ValueError, "endpoint fallback"):
            eng._offset_yield_sample(no_yield)

    def test_dimensional_scaling_distinguishes_area_stiffness_and_energy(self):
        inputs = {"record_id": "kelvin", "load_levels_N": [100, 200, 300],
                  "safety_factor": 1.5, "energy_end_strain": .15}
        original = eng.oracle(self.case(25, inputs))
        # Same effective stress-strain curve at twice the edge: A x4, k x2,
        # force at equal strain x4, displacement x2, absorbed energy x8.
        self.assets.clear()
        enlarged = eng.oracle(self.case(25, {**inputs, "load_levels_N": [400, 800, 1200]}, [row(n=4)]))
        self.assertEqual(enlarged["offset_yield_force_N"], 4 * original["offset_yield_force_N"])
        self.assertEqual(enlarged["stiffness_N_per_mm"], 2 * original["stiffness_N_per_mm"])
        self.assertAlmostEqual(enlarged["displacement_load2_mm"], 2 * original["displacement_load2_mm"])
        self.assertAlmostEqual(enlarged["absorbed_energy_J"], 8 * original["absorbed_energy_J"])

    def test_candidate_selection_applies_both_constraints_and_deterministic_tie(self):
        rows = [row("weak", modulus_mpa=50, yield_stress_mpa=4),
                row("A", yield_stress_mpa=6), row("Z", yield_stress_mpa=8),
                row("stiff", modulus_mpa=200, yield_stress_mpa=12)]
        case = self.case(26, {"candidate_ids": ["weak", "Z", "stiff", "A"], "service_force_N": 300,
                              "safety_factor": 1.5, "max_displacement_mm": .3}, rows)
        got = eng.oracle(case)
        self.assertEqual(got["feasible_count"], 3)
        self.assertEqual(got["selected_stiffness_N_per_mm"], 1000)
        self.assertEqual(got["selected_offset_yield_force_N"], 600)
        case["inputs"]["max_displacement_mm"] = .2
        self.assertEqual(eng.oracle(case)["feasible_count"], 1)
        self.assertEqual(eng.oracle(case)["selected_stiffness_N_per_mm"], 2000)
        case["inputs"]["service_force_N"] = 10000
        with self.assertRaises(ValueError):
            eng.oracle(case)

    def test_n5_proxy_uses_target_dimensions_and_reference_cohort(self):
        reference = self.asset("size_references.json", {"references": [
            {"topology": "Kelvin", "reference_curves": [
                {"n": 4, "features": {"values": {"modulus_mpa": 80, "yield_stress_mpa": 4}}},
                {"n": 5, "features": {"values": {"modulus_mpa": 100, "yield_stress_mpa": 5}}}]},
            {"topology": "BCC", "reference_curves": [
                {"n": 4, "source_kind": "reference", "method": "reference_fea"},
                {"n": 5, "source_kind": "estimated", "method": "interpolation"}]}]})
        case = self.case(27, {"record_id": "kelvin", "target_cells_per_axis": 8, "service_force_N": 600,
                              "safety_factor": 2, "sensitivity_fraction": .1, "reference_asset": reference})
        got = eng.oracle(case)
        self.assertEqual(got["target_cell_count"], 512)
        self.assertEqual(got["nominal_area_mm2"], 1600)
        self.assertEqual(got["proxy_stiffness_N_per_mm"], 4000)
        self.assertEqual(got["proxy_yield_force_N"], 8000)
        self.assertEqual(got["sensitivity_low_allowable_N"], 3600)
        self.assertAlmostEqual(got["sensitivity_high_displacement_mm"], 1 / 6)
        self.assertEqual(got["reference_E_relative_change"], .2)
        self.assertEqual(got["reference_yield_relative_change"], .2)
        self.assertEqual(got["bcc_direct_n5_count"], 0)
        case["inputs"]["sensitivity_fraction"] = 1
        with self.assertRaises(ValueError):
            eng.oracle(case)

    def test_parallel_load_sharing_first_yield_then_explicit_replacement(self):
        case = self.case(28, {"left_record_id": "kelvin", "right_record_id": "octet", "total_force_N": 600,
                              "safety_factor": 1.5}, [row(), row("octet", modulus_mpa=200, yield_stress_mpa=12)])
        initial = eng.oracle(case)
        self.assertEqual(set(initial), {"initial_displacement_mm", "initial_left_force_N", "initial_allowable_N"})
        self.assertEqual(initial["initial_displacement_mm"], .2)
        self.assertEqual(initial["initial_left_force_N"], 200)
        self.assertEqual(initial["initial_allowable_N"], 1000)
        case["followup_turns"] = [{"turn": 2, "inputs_update": {"total_force_N": 1500, "replacement_left_record_id": "octet"}}]
        final = eng.oracle(case)
        self.assertEqual(final["upgraded_original_left_force_N"], 500)
        self.assertAlmostEqual(final["upgraded_original_margin"], -1 / 3)
        self.assertEqual(final["revised_displacement_mm"], .375)
        self.assertEqual(final["revised_allowable_N"], 1600)
        self.assertAlmostEqual(final["revised_margin"], 1 / 15)
        self.assertEqual({k: final[k] for k in initial}, initial)

    def test_eccentric_screen_marks_tension_beyond_kern_without_contact_solver(self):
        case = self.case(29, {"record_id": "kelvin", "force_N": 100, "eccentricity_mm": 1,
                              "secondary_eccentricity_mm": 2, "safety_factor": 2})
        got = eng.oracle(case)
        self.assertAlmostEqual(got["section_modulus_mm3"], 1000 / 6)
        self.assertEqual(got["nominal_stress_MPa"], 1)
        self.assertAlmostEqual(got["max_edge_stress_MPa"], 1.6)
        self.assertAlmostEqual(got["min_edge_stress_MPa"], .4)
        self.assertAlmostEqual(got["screening_allowable_N"], 156.25)
        self.assertAlmostEqual(got["yield_margin"], .5625)
        self.assertAlmostEqual(got["secondary_min_edge_stress_MPa"], -.2)

    def test_radius_tolerance_inversion_and_bounds_are_conditional(self):
        rows = [row("lo", radius=.3, modulus_mpa=60, yield_stress_mpa=3), row(),
                row("hi", radius=.5, modulus_mpa=140, yield_stress_mpa=7)]
        case = self.case(30, {"radius_records": ["hi", "lo", "kelvin"], "nominal_radius_mm": .4,
                              "radius_tolerance_mm": .02, "service_force_N": 250, "safety_factor": 2}, rows)
        got = eng.oracle(case)
        self.assertAlmostEqual(got["nominal_yield_margin"], 0)
        self.assertAlmostEqual(got["low_stiffness_N_per_mm"], 920)
        self.assertAlmostEqual(got["low_offset_yield_force_N"], 460)
        self.assertAlmostEqual(got["worst_yield_margin"], -.08)
        self.assertAlmostEqual(got["best_yield_margin"], .08)
        self.assertAlmostEqual(got["required_nominal_radius_mm"], .42)
        case["inputs"]["radius_tolerance_mm"] = .11
        with self.assertRaises(ValueError):
            eng.oracle(case)
        self.assets.clear()
        rows[-1]["yield_stress_mpa"] = 4
        case = self.case(30, {**case["inputs"], "radius_tolerance_mm": .02}, rows)
        with self.assertRaisesRegex(ValueError, "increasing yield"):
            eng.oracle(case)

    def test_material_transfer_scales_elasticity_but_emits_no_yield_or_mass(self):
        case = self.case(31, {"record_id": "kelvin", "assumed_source_solid_E_MPa": 1000,
                              "target_solid_E_MPa": 2000, "assumed_source_density_g_cm3": 1,
                              "target_density_g_cm3": 1.2, "force_N": 200})
        got = eng.oracle(case)
        self.assertEqual(got["normalized_modulus"], .1)
        self.assertEqual(got["elastic_scale_factor"], 2)
        self.assertEqual(got["target_effective_modulus_MPa"], 200)
        self.assertEqual(got["target_stiffness_N_per_mm"], 2000)
        self.assertEqual(got["elastic_displacement_mm"], .1)
        self.assertEqual(got["mass_ratio_for_identical_geometry"], 1.2)
        self.assertFalse(any("yield" in key or key == "mass_g" for key in got))

    def test_holdout_asset_unread_until_reveal_and_prediction_stays_frozen(self):
        calibration = self.asset("experiment_n4.json", {"group": {"metrics": {"sigma20": {"mean": 6, "sd": .4, "n": 4}}},
                                                         "curve": {"strain": [0, .2], "stress": [0, 999]}})
        validation = self.asset("experiment_n5.json", {"group": {"metrics": {"sigma20": {"mean": 9, "sd": 2, "n": 3}}}}, turn=2)
        case = self.case(32, {"simulation_n4_record_id": "n4", "simulation_n5_record_id": "n5", "calibration_asset": calibration,
                              "validation_relative_error_limit": .1}, [row("n4", n=4, stress20_mpa=3), row("n5", n=5, stress20_mpa=4)])
        with patch.object(eng, "checked_asset", wraps=checked_asset) as loader:
            initial = eng.oracle(case)
        self.assertEqual(initial["calibration_factor"], 2)
        self.assertEqual(initial["predicted_n5_sigma20_MPa"], 8)
        self.assertEqual(initial["calibration_specimen_count"], 4)
        self.assertEqual(len(loader.call_args_list), 2)
        self.assertFalse(any(call.args[0]["path"] == validation for call in loader.call_args_list))
        # Merely inserting a future path into initial inputs cannot bypass turn metadata.
        premature = copy.deepcopy(case)
        premature["inputs"]["validation_asset"] = validation
        with self.assertRaisesRegex(ValueError, "not available"):
            eng.oracle(premature)
        case["followup_turns"] = [{"turn": 2, "inputs_update": {"validation_asset": validation}}]
        final = eng.oracle(case)
        self.assertEqual(final["predicted_n5_sigma20_MPa"], initial["predicted_n5_sigma20_MPa"])
        self.assertEqual(final["validation_bias_MPa"], -1)
        self.assertAlmostEqual(final["validation_relative_error"], 1 / 9)
        self.assertEqual(final["observed_n5_sample_sd_MPa"], 2)
        self.assertEqual(final["validation_specimen_count"], 3)

    def test_hash_mutation_and_undeclared_asset_are_rejected(self):
        case = self.case(31, {"record_id": "kelvin", "assumed_source_solid_E_MPa": 1000,
                              "target_solid_E_MPa": 2000, "assumed_source_density_g_cm3": 1,
                              "target_density_g_cm3": 1.2, "force_N": 200})
        path = self.root / case["inputs"]["database_snapshot_asset"]
        path.write_text(path.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            eng.oracle(case)
        case["inputs"]["database_snapshot_asset"] = "reference_answers.json"
        with self.assertRaisesRegex(ValueError, "declared input asset"):
            eng.oracle(case)

    def test_nonfinite_and_unphysical_values_are_not_silently_scored(self):
        case = self.case(25, {"record_id": "kelvin", "load_levels_N": [100, 200, 300],
                              "safety_factor": 1.5, "energy_end_strain": .15})
        for updates in ({"safety_factor": .5}, {"safety_factor": float("nan")},
                        {"load_levels_N": [-1, 200, 300]}, {"energy_end_strain": 1}):
            changed = copy.deepcopy(case)
            changed["inputs"].update(updates)
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                eng.oracle(changed)


class PublishedEngineeringPacketTests(unittest.TestCase):
    def setUp(self):
        self.cases = {c["id"]: c for c in (json.loads(line) for line in (ROOT / "cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
        if "LAT-32" not in self.cases:
            self.skipTest("Engineering cases have not been assembled yet")

    def test_initial_packets_hide_future_feedback_and_holdout_data(self):
        first28 = build_packet("LAT-28")
        text28 = json.dumps(first28, ensure_ascii=False)
        self.assertNotIn("replacement_left_record_id", text28)
        self.assertNotIn("upgraded_original_left_force_N", text28)
        self.assertNotIn("followup_turns", first28["case"])
        first32 = build_packet("LAT-32")
        assets = first32["case"]["input_assets"]
        self.assertFalse(any("experiment_n5.json" in asset["path"] for asset in assets))
        self.assertNotIn("validation_asset", json.dumps(first32, ensure_ascii=False))
        second32 = build_packet("LAT-32", turn=2)
        self.assertTrue(any("experiment_n5.json" in asset["path"] for asset in second32["case"]["input_assets"]))
        self.assertNotIn("reference_answers", json.dumps(second32, ensure_ascii=False).lower())

    def test_public_packets_preserve_mixed_origin_and_source_boundaries(self):
        for number in range(25, 33):
            with self.subTest(case=number):
                case = self.cases[f"LAT-{number}"]
                self.assertFalse(case["inputs"]["synthetic"])
                self.assertEqual(case["inputs"]["scenario_origin"], "synthetic")
                packet = build_packet(case["id"])
                self.assertNotIn("所有数值为合成输入", packet["instructions"])
                self.assertIn("哈希", packet["instructions"])
                self.assertEqual(set(eng.oracle(case)), set(case["numeric_output_schema"]))
        data = json.loads((ROOT / "fixtures/engineering/atlas_records.json").read_text(encoding="utf-8-sig"))
        self.assertFalse(data["source"]["live_site_fetched"])
        self.assertTrue(all(record["source_kind"] == "estimated" for record in data["records"] if record["n"] > 1))
        experiment = json.loads((ROOT / "fixtures/engineering/experiment_n5.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(experiment["data_origin"], "real_experiment_from_published_snapshot")
        self.assertEqual(experiment["group"]["material"], "unknown")


if __name__ == "__main__":
    unittest.main()
