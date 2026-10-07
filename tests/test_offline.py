import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from check_numeric import check
from export_case import build_packet,main as export_main
from input_assets import export_assets
from validate import load_suite,validate

def workspace_temporary_directory():
    root=Path(__file__).resolve().parents[1]
    base=(root/"exports").resolve()
    if not base.is_relative_to(root): raise ValueError("Test temporary root escapes repository")
    base.mkdir(parents=True,exist_ok=True)
    return tempfile.TemporaryDirectory(dir=base,prefix="test-packet-")

class OfflineContractTests(unittest.TestCase):
    def test_actual_suite(self):
        suite=load_suite();errors,count=validate(*suite)
        self.assertEqual(errors,[])
        self.assertEqual(count,sum(len(ref["numeric"]) for ref in suite[1].values()))
        self.assertEqual(sum(len(suite[1][cid]["numeric"]) for cid in suite[4]["tracks"]["core"]["case_ids"]),126)
        self.assertEqual(sum(len(suite[1][cid]["numeric"]) for cid in suite[4]["tracks"]["research_challenge"]["case_ids"]),30)

    def test_wrong_reference_is_detected_independently(self):
        cases,refs,rubrics,sources,manifest=load_suite()
        refs["LAT-05"]["numeric"]["energy_B_J"]["value"]=15.5
        errors,_=validate(cases,refs,rubrics,sources,manifest)
        self.assertTrue(any("LAT-05/energy_B_J" in error for error in errors))

    def test_actual_input_change_invalidates_old_answer(self):
        cases,refs,rubrics,sources,manifest=load_suite()
        cases[4]["inputs"]["mass_g"]=16
        errors,_=validate(cases,refs,rubrics,sources,manifest)
        self.assertTrue(any("sea_A_kj_kg" in error for error in errors))

    def test_bool_nan_and_wrong_units_do_not_pass(self):
        ref={"x":{"value":1,"unit":"J","abs_tol":1e-6,"rel_tol":1e-5}}
        for item in ({"value":True,"unit":"J"},{"value":float("nan"),"unit":"J"},{"value":1,"unit":"mJ"},{}):
            self.assertFalse(check(ref,{"x":item})["x"]["pass"])
        self.assertFalse(check(ref,[])["_format"]["pass"])

    def test_rounding_accepted_but_magnitude_error_rejected(self):
        ref={"x":{"value":1483.3333333333333,"unit":"N","abs_tol":1e-6,"rel_tol":1e-5}}
        self.assertTrue(check(ref,{"x":{"value":1483.33,"unit":"N"}})["x"]["pass"])
        self.assertFalse(check(ref,{"x":{"value":1.48333,"unit":"N"}})["x"]["pass"])

    def test_initial_packet_cannot_reveal_future_state(self):
        packet=build_packet("LAT-15",1)
        case=packet["case"]
        self.assertNotIn("followup_turns",case)
        self.assertNotIn("reference",case)
        self.assertNotIn("rubric",case)
        self.assertNotIn("numeric_output_schema",case)
        self.assertEqual(case["inputs"]["target_angle_deg"],20)
        self.assertNotIn("material_A_density_g_cm3",case["inputs"])
        step2=build_packet("LAT-15",2)["case"]
        self.assertEqual(step2["inputs_update"]["target_angle_deg"],30)
        self.assertNotIn("material_A_density_g_cm3",step2["inputs_update"])
        self.assertIn("numeric_output_schema",build_packet("LAT-15",3)["case"])

    def test_numeric_schema_present_for_single_turn_case(self):
        case=build_packet("LAT-05")["case"]
        self.assertIn("energy_A_J",case["numeric_output_schema"])
        self.assertNotIn("value",case["numeric_output_schema"]["energy_A_J"])

    def test_unknown_case_or_turn_rejected(self):
        with self.assertRaises(ValueError): build_packet("LAT-00")
        for turn in (0,2):
            with self.assertRaises(ValueError): build_packet("LAT-05",turn)

    def test_followup_order_checked_outside_original_multiturn_stratum(self):
        cases,refs,rubrics,sources,manifest=load_suite()
        cases[4]["followup_turns"]=[{"turn":3,"prompt_zh":"Update the loading.","inputs_update":{"force_N":20}}]
        errors,_=validate(cases,refs,rubrics,sources,manifest)
        self.assertTrue(any("LAT-05: malformed scripted turn" in error for error in errors))

    def test_input_asset_release_cannot_point_beyond_final_turn(self):
        cases,refs,rubrics,sources,manifest=load_suite()
        case=next(c for c in cases if c["id"]=="LAT-24")
        case["input_assets"][0]["available_from_turn"]=2
        errors,_=validate(cases,refs,rubrics,sources,manifest)
        self.assertTrue(any("LAT-24: input asset has invalid available_from_turn" in error for error in errors))

    def test_engineering_packet_paths_work_with_direct_harness_export(self):
        for turn in (1,2):
            case=build_packet("LAT-32",turn)["case"]
            with workspace_temporary_directory() as directory:
                assets=export_assets(case["input_assets"],directory)
                exported={asset["path"] for asset in assets}
                fields=case.get("inputs",case.get("inputs_update",{}))
                for key,value in fields.items():
                    if key.endswith("_asset"):
                        self.assertIn(value,exported)
                        self.assertTrue((Path(directory)/value).is_file())
                self.assertTrue(all(asset["source_path"].startswith("fixtures/") for asset in assets))
                n5=Path(directory)/"assets"/"experiment_n5.json"
                self.assertEqual(n5.exists(),turn==2)
                if turn==1:
                    self.assertNotIn("numeric_output_schema",case)
                    self.assertNotIn("experiment_n5.json",json.dumps(case))

    def test_engineering_cli_exports_resolvable_asset_references(self):
        with workspace_temporary_directory() as directory:
            output=Path(directory)/"packet.json"
            with patch.object(sys,"argv",["export_case.py","LAT-25","--output",str(output)]),contextlib.redirect_stdout(io.StringIO()):
                export_main()
            case=json.loads(output.read_text(encoding="utf-8"))["case"]
            path=case["inputs"]["database_snapshot_asset"]
            self.assertEqual(path,"assets/atlas_records.json")
            self.assertTrue((output.parent/path).is_file())
            self.assertEqual(case["input_assets"][0]["source_path"],"fixtures/engineering/atlas_records.json")

if __name__=="__main__": unittest.main()
