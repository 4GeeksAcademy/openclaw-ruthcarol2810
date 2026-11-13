import importlib.util
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "get_progress_summary.py"
spec = importlib.util.spec_from_file_location("get_progress_summary", SCRIPT)
helper = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(helper)


class ProgressSummaryTests(unittest.TestCase):
    @patch.object(helper, "_get_json")
    @patch.object(helper, "load_auth_helper")
    def test_authentication_precedes_task_calls(self, load_auth, get_json):
        auth = Mock()
        auth._token.return_value = "test-token"
        auth.check_auth.return_value = ("authenticated", None)
        load_auth.return_value = auth
        get_json.return_value = {
            "count": 2,
            "results": [
                {"task_status": "APPROVED", "task_type": "PROJECT", "cohort": {"name": "AI"}},
                {"task_status": "PENDING", "task_type": "EXERCISE", "cohort": {"name": "AI"}},
            ],
            "next": None,
        }
        result = helper.run()
        auth.check_auth.assert_called_once_with("test-token")
        get_json.assert_called_once_with(0, "test-token")
        self.assertEqual(result["total_assignments"], 2)
        self.assertEqual(result["counts_by_task_status"], {"APPROVED": 1, "PENDING": 1})
        self.assertEqual(result["counts_by_type"], {"EXERCISE": 1, "PROJECT": 1})
        self.assertEqual(result["counts_by_cohort"]["AI"], {"APPROVED": 1, "PENDING": 1})
        self.assertIn("no es el porcentaje oficial", result["metric_note"])

    @patch.object(helper, "_get_json")
    @patch.object(helper, "load_auth_helper")
    def test_rejected_auth_blocks_all_other_requests(self, load_auth, get_json):
        auth = Mock()
        auth._token.return_value = "test-token"
        auth.check_auth.return_value = ("rejected", "unauthorized")
        load_auth.return_value = auth
        with self.assertRaisesRegex(RuntimeError, "authentication_rejected"):
            helper.run()
        get_json.assert_not_called()

    @patch.object(helper, "_get_json")
    def test_task_pagination_advances_and_counts_every_page(self, get_json):
        get_json.side_effect = [
            {"count": 2, "results": [{"task_status": "DONE"}],
             "next": "https://breathecode.herokuapp.com/v1/assignment/user/me/task?limit=100&offset=1"},
            {"count": 2, "results": [{"task_status": "APPROVED"}], "next": None},
        ]
        rows = helper._fetch_tasks("test-token")
        self.assertEqual(get_json.call_args_list, [unittest.mock.call(0, "test-token"), unittest.mock.call(1, "test-token")])
        self.assertEqual(helper.summarize(rows)["total_assignments"], 2)

    def test_next_page_rejects_external_host_wrong_path_or_bad_offset(self):
        url = "https://breathecode.herokuapp.com/v1/assignment/user/me/task?limit=100&offset=2"
        self.assertEqual(helper._next_offset(url, 0, 2), 2)
        for bad in (
            url.replace("breathecode.herokuapp.com", "example.com"),
            url.replace("/v1/assignment/user/me/task", "/v1/other"),
            url.replace("offset=2", "offset=1"),
            url + "&token=secret",
        ):
            with self.assertRaisesRegex(RuntimeError, "invalid_pagination"):
                helper._next_offset(bad, 0, 2)

    def test_unknown_status_is_preserved_and_types_tallied(self):
        summary = helper.summarize([
            {"task_status": "PENDING", "task_type": "EXERCISE"},
            {"task_status": "FUTURE_STATUS", "task_type": "QUIZ"},
            {},
        ])
        self.assertEqual(summary["counts_by_task_status"], {"FUTURE_STATUS": 1, "PENDING": 1, "UNKNOWN": 1})
        self.assertEqual(summary["counts_by_type"], {"EXERCISE": 1, "QUIZ": 1, "UNKNOWN": 1})
        self.assertEqual(summary["total_assignments"], 3)

    @patch.object(helper, "_get_json")
    def test_incomplete_pagination_rejected(self, get_json):
        get_json.return_value = {"count": 2, "results": [{"task_status": "DONE"}], "next": None}
        with self.assertRaisesRegex(RuntimeError, "incomplete_pagination"):
            helper._fetch_tasks("test-token")

    @patch.object(helper, "_get_json")
    def test_zero_tasks_are_a_valid_summary(self, get_json):
        get_json.return_value = {"count": 0, "results": [], "next": None}
        rows = helper._fetch_tasks("test-token")
        self.assertEqual(helper.summarize(rows)["total_assignments"], 0)


if __name__ == "__main__":
    unittest.main()
