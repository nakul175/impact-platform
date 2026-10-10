"""Offline regressions for incomplete or stale native refinement payloads.

Run after the three author shards and master proposal/plan/payload are built.
The genuine, complete 446-issue readback stays outside the repository; set
IMPRANA_REFINEMENT_BEFORE_SNAPSHOT to its path when using another machine.
These checks never call Linear or write proposal, checkpoint or source files.
Only the verifier's payload read is replaced. Its proposal builder and native
renderer run unchanged, so a matching hash stamp cannot bless omitted work.
"""

import copy
import hashlib
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_imprana_refinement as verifier


class RefinementVerifierGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        snapshot_path = Path(
            os.environ.get(
                "IMPRANA_REFINEMENT_BEFORE_SNAPSHOT",
                "/private/tmp/imprana-refinement-pre-complete.json",
            )
        )
        required = [
            snapshot_path,
            verifier.FOLDER / "backlog-refinement.json",
            verifier.FOLDER / "native-task-plan.json",
            verifier.FOLDER / "native-payloads.json",
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise unittest.SkipTest("Recorded baseline/master inputs are unavailable: " + ", ".join(missing))

        snapshot_bytes = snapshot_path.read_bytes()
        cls.snapshot_hash = hashlib.sha256(snapshot_bytes).hexdigest()
        cls.before = json.loads(snapshot_bytes)
        # The earlier complete export stores full native task relations in a
        # separate map. Join that recorded evidence without inventing relations.
        for issue in cls.before["issues"]:
            recorded = cls.before.get("task_relations", {}).get(verifier.canonical(issue))
            if recorded:
                issue["relations"] = copy.deepcopy(recorded["relations"])
        cls.before["task_relations"] = {
            verifier.canonical(issue): issue
            for issue in cls.before["issues"]
            if verifier.canonical(issue).startswith("TASK-") and "relations" in issue
        }
        if cls.before.get("pagination_complete") is not True:
            raise AssertionError("The recorded baseline must confirm complete native pagination")

        base_plan, base_hash = verifier.read_json(verifier.ROOT / "docs/product/linear/import-plan.json")
        checkpoint, checkpoint_hash = verifier.read_json(
            verifier.ROOT / "docs/product/linear/checkpoint.json"
        )
        baseline = verifier.verify(
            cls.before, cls.snapshot_hash, base_plan, base_hash, checkpoint, checkpoint_hash
        )
        if baseline["failures"]:
            raise AssertionError(
                "Recorded before snapshot is not the genuine verified baseline: " + str(baseline["failures"])
            )
        if len(cls.before["issues"]) != 446:
            raise AssertionError("These regressions require the complete original 446 native issues")
        if any("<!-- imprana:refinement:v1:" in issue["description"] for issue in cls.before["issues"]):
            raise AssertionError("The before snapshot must predate refinement appends")

        # A real regeneration supplies the fixture; it is never mocked as the
        # expected result inside run(). Each test changes only the stored input.
        cls.payload = verifier.render_payload()
        if not cls.payload["new_tasks"] or len(cls.payload["story_appends"]) != 368:
            raise AssertionError("Regenerated payload must cover the complete refinement proposal")

    def rejected_payload(self, change, expected_codes):
        payload = copy.deepcopy(self.payload)
        refinement_stamp = payload["refinement_sha256"]
        change(payload)
        self.assertEqual(payload["refinement_sha256"], refinement_stamp)
        genuine_read = verifier.read_json

        def read_payload_only(path):
            if Path(path) == verifier.FOLDER / "native-payloads.json":
                body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
                return payload, hashlib.sha256(body).hexdigest()
            return genuine_read(path)

        with patch.object(verifier, "read_json", side_effect=read_payload_only):
            report = verifier.run(
                copy.deepcopy(self.before),
                self.snapshot_hash,
                copy.deepcopy(self.before),
                self.snapshot_hash,
            )
        self.assertEqual(report["result"], "FAIL")
        self.assertFalse(report["baseline_report"]["failures"])
        self.assertEqual(report["counts"]["native_issues"], 446)
        codes = {failure["code"] for failure in report["failures"]}
        self.assertTrue(set(expected_codes) <= codes, sorted(codes))

    def test_empty_payload_with_matching_refinement_stamp_is_rejected(self):
        def change(payload):
            payload["new_tasks"] = []
            payload["story_appends"] = []

        self.rejected_payload(
            change,
            {"payload_matches_regeneration", "payload_full_new_task_set", "payload_full_story_set"},
        )

    def test_empty_task_list_with_matching_refinement_stamp_is_rejected(self):
        self.rejected_payload(
            lambda payload: payload.update(new_tasks=[]),
            {"payload_matches_regeneration", "payload_full_new_task_set"},
        )

    def test_empty_story_appends_with_matching_refinement_stamp_are_rejected(self):
        self.rejected_payload(
            lambda payload: payload.update(story_appends=[]),
            {"payload_matches_regeneration", "payload_full_story_set"},
        )

    def test_omitting_one_task_cannot_shrink_the_expected_scope(self):
        self.rejected_payload(
            lambda payload: payload["new_tasks"].pop(),
            {"payload_matches_regeneration", "payload_full_new_task_set"},
        )

    def test_omitting_one_story_append_cannot_shrink_the_expected_scope(self):
        self.rejected_payload(
            lambda payload: payload["story_appends"].pop(),
            {"payload_matches_regeneration", "payload_full_story_set"},
        )

    def test_stale_native_plan_hash_is_rejected_despite_matching_refinement_stamp(self):
        self.rejected_payload(
            lambda payload: payload.update(native_plan_sha256="0" * 64),
            {"payload_matches_regeneration", "payload_current_native_plan_hash"},
        )


if __name__ == "__main__":
    unittest.main()
