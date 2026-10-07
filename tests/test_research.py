import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from export_case import build_packet
from input_assets import checked_asset,export_assets
from mesh_audit import load_obj,audit
from validate import load_suite,validate
ROOT=Path(__file__).resolve().parents[1]

def workspace_temporary_directory():
    base=(ROOT/"exports").resolve()
    if not base.is_relative_to(ROOT.resolve()): raise ValueError("Test temporary root escapes repository")
    base.mkdir(parents=True,exist_ok=True)
    return tempfile.TemporaryDirectory(dir=base,prefix="test-assets-")

class ResearchChallengeTests(unittest.TestCase):
    def test_tracks_preserve_original_weighting(self):
        cases,refs,rubrics,sources,manifest=load_suite()
        self.assertEqual(len(manifest["tracks"]["core"]["case_ids"]),20)
        self.assertEqual(len(manifest["tracks"]["research_challenge"]["case_ids"]),4)
        self.assertFalse(manifest["combined_score_defined"])
        changed=copy.deepcopy(manifest)
        changed["tracks"]["research_challenge"]["case_ids"].append("LAT-01")
        errors,_=validate(cases,refs,rubrics,sources,changed)
        self.assertIn("track membership mismatch",errors)

    def test_damaged_input_has_actual_multiple_defects(self):
        report=audit(*load_obj(ROOT/"fixtures/LAT-24/damaged_lattice.obj"),1000)
        for field in ("boundary_edges","nonmanifold_edges","duplicate_triangles","degenerate_triangles","inconsistent_winding_edges"):
            self.assertGreater(report[field],0,field)
        self.assertEqual(report["face_edge_components"],2)
        self.assertGreater(report["bbox_size_mm"][0],12)
        self.assertFalse(report["volume_usable_for_closed_oriented_mesh_only"])
        self.assertFalse(report["self_intersection_checked"])

    def test_fixture_packet_copies_only_manifest_inputs(self):
        packet=build_packet("LAT-24")
        self.assertNotIn("reference",packet["case"])
        self.assertNotIn("input_diagnostics",packet["case"])
        assets=packet["case"]["input_assets"]
        with workspace_temporary_directory() as folder:
            output=Path(folder)
            published=export_assets(assets,output)
            actual={str(p.relative_to(output).as_posix()) for p in output.rglob("*") if p.is_file()}
            self.assertEqual(actual,{"assets/damaged_lattice.obj","assets/input_metadata.json"})
            for item in published:
                self.assertEqual(hashlib.sha256((output/item["path"]).read_bytes()).hexdigest(),item["sha256"])

    def test_bad_hash_and_nonfixture_paths_are_rejected(self):
        asset=copy.deepcopy(build_packet("LAT-24")["case"]["input_assets"][0])
        asset["sha256"]="0"*64
        with self.assertRaises(ValueError): checked_asset(asset)
        for name in ("../reference_answers.json","fixtures/../reference_answers.json","/etc/passwd","C:/private.txt","reference_answers.json","fixtures\\LAT-24\\damaged_lattice.obj"):
            asset["path"]=name
            with self.assertRaises(ValueError): checked_asset(asset)

    def test_partial_export_cannot_happen_on_later_bad_hash(self):
        assets=copy.deepcopy(build_packet("LAT-24")["case"]["input_assets"])
        assets[-1]["sha256"]="0"*64
        with workspace_temporary_directory() as folder:
            with self.assertRaises(ValueError): export_assets(assets,Path(folder))
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_correct_mesh_audit_on_unit_tetrahedron(self):
        vertices=[(0,0,0),(1,0,0),(0,1,0),(0,0,1)]
        faces=[(0,2,1),(0,1,3),(0,3,2),(1,2,3)]
        report=audit(vertices,faces)
        self.assertTrue(report["volume_usable_for_closed_oriented_mesh_only"])
        self.assertAlmostEqual(report["signed_volume_mm3"],1/6)
        self.assertEqual(report["euler_characteristic"],2)
        self.assertEqual(report["face_edge_components"],1)

    def test_empty_numeric_references_are_not_valid_challenges(self):
        cases,refs,rubrics,sources,manifest=load_suite()
        refs["LAT-21"]["numeric"]={}
        errors,_=validate(cases,refs,rubrics,sources,manifest)
        self.assertTrue(any("LAT-21: missing independent numeric anchors" in e for e in errors))

    def test_derived_mass_answer_is_not_in_candidate_packet(self):
        packet=build_packet("LAT-23")
        rendered=json.dumps(packet,ensure_ascii=False)
        self.assertNotIn("4.35",rendered)
        self.assertNotIn("1.200462",rendered)
        self.assertNotIn("reference",packet["case"])

if __name__=="__main__":unittest.main()
