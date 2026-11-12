import importlib.util
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "get_pending_work.py"
spec = importlib.util.spec_from_file_location("get_pending_work", SCRIPT)
helper = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(helper)


class PendingWorkTests(unittest.TestCase):
    @patch.object(helper, "fetch_page")
    @patch.object(helper, "load_auth_helper")
    def test_authentication_happens_before_task_fetch(self, load_auth, fetch):
        auth = Mock()
        auth._token.return_value = "test-token"
        auth.check_auth.return_value = ("authenticated", None)
        load_auth.return_value = auth
        fetch.side_effect = [
            {"count": 1, "results": [{"task_status": "PENDING", "task_type": "EXERCISE", "title": "T"}], "next": None},
            {"count": 1, "results": [{"task_status": "REJECTED", "task_type": "PROJECT", "title": "R"}], "next": None},
        ]
        count, tasks = helper.run()
        load_auth.assert_called_once()
        auth.check_auth.assert_called_once_with("test-token")
        self.assertEqual(fetch.call_args_list[0].args, ("test-token", 0, "PENDING"))
        self.assertEqual(fetch.call_args_list[1].args, ("test-token", 0, "REJECTED"))
        self.assertEqual(count, 2)
        self.assertEqual([task["title"] for task in tasks], ["T", "R"])

    @patch.object(helper, "fetch_page")
    @patch.object(helper, "load_auth_helper")
    def test_failed_auth_prevents_task_request(self, load_auth, fetch):
        auth = Mock()
        auth._token.return_value = "test-token"
        auth.check_auth.return_value = ("rejected", "unauthorized")
        load_auth.return_value = auth
        with self.assertRaisesRegex(RuntimeError, "authentication_rejected"):
            helper.run()
        fetch.assert_not_called()

    @patch.object(helper, "fetch_page")
    @patch.object(helper, "load_auth_helper")
    def test_record_not_matching_current_status_is_rejected(self, load_auth, fetch):
        auth = Mock()
        auth._token.return_value = "test-token"
        auth.check_auth.return_value = ("authenticated", None)
        load_auth.return_value = auth
        fetch.side_effect = [
            {"count": 1, "results": [{"task_status": "DONE", "task_type": "PROJECT"}], "next": None},
        ]
        with self.assertRaisesRegex(RuntimeError, "unexpected_task_record"):
            helper.run()

    @patch.object(helper, "fetch_page")
    @patch.object(helper, "load_auth_helper")
    def test_rejected_query_rejects_wrong_status_records(self, load_auth, fetch):
        auth = Mock()
        auth._token.return_value = "test-token"
        auth.check_auth.return_value = ("authenticated", None)
        load_auth.return_value = auth
        fetch.side_effect = [
            {"count": 0, "results": [], "next": None},
            {"count": 1, "results": [{"task_status": "PENDING", "task_type": "PROJECT"}], "next": None},
        ]
        with self.assertRaisesRegex(RuntimeError, "unexpected_task_record"):
            helper.run()
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(fetch.call_args_list[1].args, ("test-token", 0, "REJECTED"))

    def test_next_page_url_is_bound_to_filter_and_page_progress(self):
        url = "https://breathecode.herokuapp.com/v1/assignment/user/me/task?task_status=PENDING&limit=100&offset=3"
        self.assertEqual(helper._next_page_offset(url, 0, 3, "PENDING"), 3)
        rejected_url = url.replace("task_status=PENDING", "task_status=REJECTED")
        self.assertEqual(helper._next_page_offset(rejected_url, 0, 3, "REJECTED"), 3)
        with self.assertRaisesRegex(RuntimeError, "invalid_pagination"):
            helper._next_page_offset(url.replace("task_status=PENDING", "task_status=DONE"), 0, 3, "PENDING")
        with self.assertRaisesRegex(RuntimeError, "invalid_pagination"):
            helper._next_page_offset(url.replace("breathecode.herokuapp.com", "example.com"), 0, 3, "PENDING")
        with self.assertRaisesRegex(RuntimeError, "invalid_pagination"):
            helper._next_page_offset(url.replace("offset=3", "offset=2"), 0, 3, "PENDING")

    def test_task_projection_preserves_only_available_fields(self):
        actual = helper._task({
            "id": 5,
            "title": "Pendiente",
            "task_type": "LESSON",
            "task_status": "PENDING",
            "cohort": {"name": "Cohorte A"},
            "created_at": "2026-11-12T00:00:00Z",
        })
        self.assertEqual(actual["task_id"], 5)
        self.assertEqual(actual["cohort"], "Cohorte A")
        self.assertEqual(actual["task_type"], "LESSON")
        self.assertNotIn("due_date", actual)


if __name__ == "__main__":
    unittest.main()
