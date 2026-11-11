"""CPU regression checks on synthetic fixtures and saved pilot; never runs a model."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/countgdpp"))
from offline_text_v2 import decode, sha, transform
from select_offline_v2 import evaluate, fit_threshold, select_d9
from bundle_offline_v2 import build


class OfflineChecks(unittest.TestCase):
    def test_fallback_preserves_b0_exactly(self):
        raw = dict(input_ids=np.array([101,2111,1012,102]), scores=np.array([[.01,.6,.01,.01]]),
                   normalized_cxcywh=np.array([[.5,.5,.2,.2]]))
        _, boxes, scores, _ = decode(raw,100,100)
        row = dict(query_id="q",execution_status="ok",box_format="xyxy_pixels",no_pseudo=True,stage2_executed=False,
                   final_count=1,final_boxes=boxes.tolist(),final_scores=scores.tolist(),image_width=100,image_height=100)
        with tempfile.TemporaryDirectory() as temp:
            job=Path(temp)/"q";job.mkdir()
            np.savez(job/"stage1_raw.npz",**raw)
            result,_=transform([row],temp)
        self.assertEqual(result[0]["final_boxes"],row["final_boxes"])
        self.assertEqual(result[0]["final_scores"],row["final_scores"])
        self.assertFalse(result[0]["text_only_applied"])

    def test_cli_refuses_draft_and_test_split(self):
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp)
            meta=temp/"meta.json"; man=temp/"manifest.csv"
            for status,split in (("DRAFT_NOT_LOCKED","dev_v2"),("LOCKED","test_v2")):
                meta.write_text(json.dumps(dict(status=status)),encoding="utf-8")
                man.write_text("query_id,image_id,split,verified_by,presence_status,gt_count\nq,i,"+split+",synthetic,present,1\n",encoding="utf-8")
                cp=subprocess.run([sys.executable,str(ROOT/"experiments/countgdpp/select_offline_v2.py"),
                                   "--bundle",str(temp/"unused.json"),"--manifest",str(man),"--selection-meta",str(meta),
                                   "--out",str(temp/"out")],capture_output=True,text=True)
                self.assertNotEqual(cp.returncode,0)
                self.assertIn("locked dev" if status.startswith("DRAFT") else "never test",cp.stderr)
                self.assertFalse((temp/"out").exists())

    def test_text_ignores_visual_and_special_tokens(self):
        raw = dict(input_ids=np.array([101, 2111, 1008, 1012, 102]),
                   scores=np.array([[.01, .1, .99, .01, .01], [.99, .1, .01, .01, .01], [.01, .5, .9, .01, .1], [.01, .5, .9, .01, .6], [.01, .23, .9, .01, .1]]),
                   normalized_cxcywh=np.tile([.5, .5, .2, .2], (5, 1)))
        keep, boxes, scores, tokens = decode(raw, 100, 200, True)
        self.assertEqual(keep.tolist(), [2])
        self.assertEqual(tokens, [1])
        self.assertEqual(scores.tolist(), [.5])
        np.testing.assert_allclose(boxes, [[40, 80, 60, 120]])

    def test_threshold_rule_matches_brute_force(self):
        rng = np.random.default_rng(331)
        for _ in range(30):
            scores = {str(i): rng.choice([.1, .2, .3, .7], size=int(rng.integers(0, 7))).tolist() for i in range(5)}
            gt = {str(i): int(rng.integers(0, 7)) for i in range(5)}
            vals = sorted({v for s in scores.values() for v in s})
            candidates = [vals[0]-1e-6] + [(a+b)/2 for a,b in zip(vals, vals[1:])] + [vals[-1]+1e-6]
            def key(t):
                errors = [abs(sum(v >= t for v in s)-gt[q]) for q,s in scores.items()]
                return sum(errors), sum(e*e for e in errors), t
            self.assertEqual(fit_threshold(scores, gt), min(candidates, key=key))

    def test_d9_rejects_present_tradeoff_and_handles_ties(self):
        def m(a,p,f):
            return dict(all=dict(MAE=a), present=dict(MAE=p), absent=dict(FPR_absent=f))
        table = dict(B0=m(4,3,.5), bad=m(2,4,0), good=m(3,2,.5))
        self.assertEqual(select_d9(table)["selected"], "good")
        table["other"] = m(3,2,.5)
        self.assertEqual(select_d9(table)["status"], "TIE_REQUIRES_DECISION")
        self.assertEqual(select_d9(dict(B0=m(4,3,.5), bad=m(2,4,0)))["selected"], "B0")
        self.assertEqual(select_d9(dict(B0=m(4,3,.5), bad=m(2,2,1)))["selected"], "B0")

    def test_uncertain_excluded_from_fit_and_bounds(self):
        man = [dict(query_id=q,image_id=q,presence_status=s,gt_count=g) for q,s,g in [("p","present",1),("a","absent",0),("u","uncertain",999)]]
        rows = [dict(query_id=q,image_id=q,boxes=[[0,0,1,1]],scores=[s],clip=[s]) for q,s in [("p",.8),("a",.2),("u",1.)]]
        result = evaluate(dict(sources=dict(B0=rows)), man)
        self.assertEqual(result["parameters"]["B0"]["bounds"]["countgd"], [.2,.8])
        self.assertEqual(result["uncertain_excluded"], ["u"])
        self.assertEqual(result["summary"]["B0+S"]["all"]["MAE"], 0)
        with self.assertRaises(ValueError):
            evaluate(dict(sources=dict(B0=rows[:-1])), man)

    def test_empty_boxes(self):
        man = [dict(query_id=q,image_id=q,presence_status=s,gt_count=g) for q,s,g in [("p","present",1),("a","absent",0)]]
        rows = [dict(query_id=q,image_id=q,boxes=[],scores=[],clip=[]) for q in ["p","a"]]
        result = evaluate(dict(sources=dict(B0=rows)), man)
        self.assertEqual(result["d9"]["selected"], "B0")
        self.assertEqual(result["summary"]["B0+F"]["all"]["MAE"], .5)

    def test_saved_pilot_bundle_matches_original_counts(self):
        ctrl = ROOT / "results/countgdpp/p1_pilot_colab_20261103_1519_controls"
        bundle = build(ctrl, [])
        with (ctrl / "per_query_counts.csv").open(encoding="utf-8") as f:
            old = {r["query_id"]:r for r in csv.DictReader(f)}
        for source, rows in bundle["sources"].items():
            for r in rows:
                self.assertEqual(len(r["boxes"]), int(old[r["query_id"]][source]))

    def test_text_bundle_reuses_exact_clip_ranks_and_checks_hash(self):
        ctrl = ROOT / "results/countgdpp/p1_pilot_colab_20261103_1519_controls"
        base = build(ctrl, [])
        cfg = json.loads((ctrl/"run_config.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            temp=Path(temp); path=temp/"predictions.jsonl"
            rows=[]
            for b in base["sources"]["B2"]:
                ranks=[len(b["boxes"])] if b["boxes"] else []
                rows.append(dict(query_id=b["query_id"],image_id=b["image_id"],original_ranks=ranks,
                                 final_boxes=b["boxes"][-1:],final_scores=[.5] if ranks else [],final_count=len(ranks)))
            path.write_text("".join(json.dumps(r)+"\n" for r in rows),encoding="utf-8")
            (temp/"run_config.json").write_text(json.dumps(dict(tool="offline_text_v2.py",original_replay_verified=True,
                source_sha256=cfg["prediction_sha256"]["predictions_B2.jsonl"],predictions_sha256=sha(path))),encoding="utf-8")
            result=build(ctrl,[("T","B2",path)])
            original={r["query_id"]:r for r in base["sources"]["B2"]}
            for r in result["sources"]["T"]:
                self.assertEqual(r["clip"],original[r["query_id"]]["clip"][-1:])
            path.write_text(path.read_text(encoding="utf-8")+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                build(ctrl,[("T","B2",path)])

    def test_evaluator_regression_pilot_and_uncertain_absent(self):
        ctrl = ROOT / "results/countgdpp/p1_pilot_colab_20261103_1519_controls"
        mp = ROOT / "experiments/countgdpp/m4_inputs/manifest.csv"
        with mp.open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        with (ctrl / "per_query_counts.csv").open(encoding="utf-8") as f:
            counts = {r["query_id"]:r for r in csv.DictReader(f)}
        rows = [r for r in rows if r["query_id"] in counts]
        protected = [mp, ROOT / "evaluation/evaluate_research.py", ctrl / "per_query_counts.csv"]
        before = {str(p):sha(p) for p in protected}
        with tempfile.TemporaryDirectory(prefix="offline_v2_check_", dir=ROOT / "results/countgdpp") as temp:
            temp = Path(temp)
            for case in ("original", "uncertain_absent", "all_uncertain"):
                modified = [dict(r) for r in rows]
                if case == "uncertain_absent":
                    modified[0].update(presence_status="uncertain", gt_count="")
                    modified[1].update(presence_status="absent", gt_count="0")
                if case == "all_uncertain":
                    for r in modified:
                        r.update(presence_status="uncertain", gt_count="")
                path = temp / (case + ".csv")
                with path.open("w",encoding="utf-8",newline="") as f:
                    w=csv.DictWriter(f,fieldnames=list(modified[0]));w.writeheader();w.writerows(modified)
                # Nested unique output keeps the evaluator's own no-overwrite protection.
                run_id = temp.name + "_" + case
                output = ROOT / "results/countgdpp" / run_id
                cp = subprocess.run([sys.executable, str(ROOT / "evaluation/evaluate_research.py"), "--controls", str(ctrl),
                                     "--manifest", str(path), "--run-id", run_id], capture_output=True, text=True)
                if case == "all_uncertain":
                    self.assertNotEqual(cp.returncode,0)
                    self.assertIn("nothing to score", cp.stderr)
                    continue
                self.assertEqual(cp.returncode,0,cp.stderr)
                result = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
                # Move generated check output into the temp directory for cleanup.
                output.rename(temp / case)
                valid = [r for r in modified if r["presence_status"] != "uncertain"]
                self.assertEqual(result["uncertain_excluded"], [modified[0]["query_id"]] if case != "original" else [])
                for method, summary in result["summary"].items():
                    errors=[abs(int(counts[r["query_id"]][method])-int(r["gt_count"])) for r in valid]
                    self.assertAlmostEqual(summary["all"]["MAE"],sum(errors)/len(errors))
                    if case == "uncertain_absent":
                        self.assertEqual(summary["absent"]["FPR_absent"], float(int(counts[modified[1]["query_id"]][method]) > 0))
        self.assertEqual(before, {str(p):sha(p) for p in protected})


if __name__ == "__main__":
    unittest.main(verbosity=2)
