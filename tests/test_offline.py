import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from check_numeric import check
from export_case import build_packet
from validate import load_suite,validate

class OfflineContractTests(unittest.TestCase):
    def test_actual_suite(self):
        suite=load_suite();errors,count=validate(*suite)
        self.assertEqual(errors,[])
        self.assertEqual(count,156)
        self.assertEqual(sum(len(suite[1][cid]["numeric"]) for cid in suite[4]["tracks"]["core"]["case_ids"]),126)

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

if __name__=="__main__": unittest.main()
