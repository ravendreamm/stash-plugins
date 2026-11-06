import unittest

from planner import plan


class PlannerTest(unittest.TestCase):
    def test_unmatched_scene_still_organizes(self):
        self.assertEqual(plan({"tags": [], "organized": True}, True),
                         {"kind": "scene", "library": "/data/scenes", "action": "organize", "reason": "no_stashdb_id"})

    def test_movie_tag_is_whole_name_and_case_insensitive(self):
        self.assertEqual(plan({"tags": [" Movie "], "organized": True}, True)["kind"], "movie")
        self.assertEqual(plan({"tags": ["movie trailer"], "organized": True}, True)["kind"], "scene")

    def test_toggle_never_prevents_organization(self):
        result = plan({"tags": [], "organized": True, "stashdb_ids": ["test-id"]}, False)
        self.assertEqual((result["action"], result["reason"]), ("organize", "handoff_disabled"))

    def test_matched_scene_is_candidate_only(self):
        result = plan({"tags": [], "organized": True, "stashdb_ids": ["test-id"]}, True)
        self.assertEqual(result["action"], "organize_then_check_handoff")

    def test_ambiguous_ids_never_handoff(self):
        result = plan({"tags": [], "organized": True, "stashdb_ids": ["one", "two"]}, True)
        self.assertEqual((result["action"], result["reason"]), ("organize", "ambiguous_stashdb_ids"))

    def test_movie_handoff_requires_further_research(self):
        result = plan({"tags": ["movie"], "organized": True, "stashdb_ids": ["test-id"]}, True)
        self.assertEqual(result["reason"], "movie_handoff_unverified")

    def test_unorganized_item_has_no_action(self):
        self.assertEqual(plan({"tags": [], "organized": False}, True)["action"], "none")

    def test_reject_unknown_toggle_and_missing_organized(self):
        with self.assertRaises(ValueError):
            plan({"tags": [], "organized": True}, "false")
        with self.assertRaises(ValueError):
            plan({"tags": []}, True)


if __name__ == "__main__":
    unittest.main()
