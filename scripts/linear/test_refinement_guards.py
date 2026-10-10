"""Offline failure-injection checks for irreversible import mistakes.

Run after all proposal shards are complete. These tests never call Linear,
change preserved source files or execute product/provider workloads.
"""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_imprana_refinement as builder


class RefinementGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = [json.loads((builder.FOLDER / name).read_text()) for name in builder.SHARDS]
        builder.build()

    def rejected(self, change, message):
        documents = copy.deepcopy(self.original)
        change(documents)
        with tempfile.TemporaryDirectory(prefix="imprana-refinement-guards-") as folder:
            for name, data in zip(builder.SHARDS, documents, strict=True):
                (Path(folder) / name).write_text(json.dumps(data))
            with patch.object(builder, "FOLDER", Path(folder)):
                with self.assertRaisesRegex(ValueError, message):
                    builder.build()

    def test_missing_story_cannot_be_imported_as_complete(self):
        self.rejected(lambda d: d[2]["stories"].pop(), "incomplete/duplicate coverage")

    def test_dropping_original_rejection_is_detected(self):
        def change(documents):
            story = documents[0]["stories"][0]
            story["test_plan"] = story["test_plan"][:-1]

        self.rejected(change, "incomplete original scenario coverage")

    def test_historical_task_edit_is_detected(self):
        def change(documents):
            story = next(s for s in documents[0]["stories"] if s["story_id"] == "US-DX-01a")
            story["tasks"][0]["description"] += " Unauthorized historical rewrite."

        self.rejected(change, "original 24-task core changed")

    def test_cross_story_hard_dependency_is_not_invented(self):
        def change(documents):
            task = documents[2]["stories"][0]["tasks"][0]
            task["depends_on"] = ["TASK-US-DX-01a-01"]

        self.rejected(change, "dependency outside own reviewed task slice")

    def test_cycle_or_forward_dependency_blocks_creation(self):
        def change(documents):
            tasks = documents[2]["stories"][0]["tasks"]
            tasks[0]["depends_on"] = [tasks[-1]["id"]]

        self.rejected(change, "prerequisite must precede")

    def test_private_or_outside_anchor_is_not_published(self):
        def change(documents):
            documents[0]["stories"][0]["current_code"][0]["path"] = "../../../../etc/passwd"

        self.rejected(change, "Missing/outside/private code anchor")


if __name__ == "__main__":
    unittest.main()
