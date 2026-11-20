import importlib.util
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "get_events.py"
spec = importlib.util.spec_from_file_location("get_events", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class EventsTests(unittest.TestCase):
    def test_ai_detection_uses_explicit_terms(self):
        self.assertTrue(module.is_ai_related({"title": "Workshop de IA aplicada"}))
        self.assertTrue(module.is_ai_related({"title": "Build an AI assistant"}))
        self.assertTrue(module.is_ai_related({"event_type": {"slug": "coding-with-ai"}}))
        self.assertTrue(module.is_ai_related({"description": "Machine learning basics"}))
        self.assertTrue(module.is_ai_related({"tags": ["ai-all-programs", {"name": "Applied AI"}]}))
        self.assertFalse(module.is_ai_related({"tags": [{"name": "programming"}]}))
        self.assertFalse(module.is_ai_related({"title": "Networking para desarrolladores"}))
        self.assertFalse(module.is_ai_related({"title": "Said and done: a tech meetup"}))

    def test_projection_normalizes_dates_and_filters_public_fields(self):
        now = datetime(2026, 11, 20, 15, tzinfo=timezone.utc)
        raw = {
            "id": 5,
            "title": "Evento IA",
            "starting_at": "2026-11-29T18:00:00Z",
            "ending_at": "2026-11-29T19:00:00Z",
            "online_event": True,
            "event_type": {"name": "AI", "slug": "ai", "technologies": None},
            "venue": {"title": "Online", "city": "Miami"},
            "academy": {"name": "4Geeks.com", "slug": "4geeks-com"},
            "description": "Useful details",
            "host_user": {"email": "private@example.com"},
            "status": "ACTIVE",
        }
        projected = module.project_event(raw, now=now)
        self.assertEqual(projected["starting_at"], "2026-11-29T18:00:00Z")
        self.assertTrue(projected["upcoming"])
        self.assertTrue(projected["ai_related"])
        self.assertTrue(projected["has_valid_time_range"])
        self.assertTrue(projected["active"])
        self.assertEqual(projected["academy"]["name"], "4Geeks.com")
        self.assertNotIn("host_user", projected)

    def test_invalid_or_past_events_not_upcoming(self):
        now = datetime(2026, 11, 20, 15, tzinfo=timezone.utc)
        past = module.project_event({"title": "Evento pasado", "starting_at": "2026-11-19T10:00:00Z", "ending_at": "2026-11-19T11:00:00Z"}, now=now)
        missing_end = module.project_event({"title": "Falta fin", "starting_at": "2026-11-29T10:00:00Z"}, now=now)
        self.assertFalse(past["upcoming"])
        self.assertTrue(missing_end["upcoming"])
        self.assertFalse(missing_end["has_valid_time_range"])
        self.assertIsNone(missing_end["active"])
        with self.assertRaisesRegex(ValueError, "invalid_event_time_range"):
            module.project_event({"title": "Fechas invertidas", "starting_at": "2026-11-29T11:00:00Z", "ending_at": "2026-11-29T10:00:00Z"}, now=now)

    def test_fetch_requires_json_array_and_sanitizes_rows(self):
        payload = [{"id": 7, "title": "AI webinar", "starting_at": "2026-11-29T18:00:00Z", "ending_at": "2026-11-29T19:00:00Z", "status": "ACTIVE"}]
        class Response:
            status = 200
            headers = {"Content-Type": "application/json"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, limit): return json.dumps(payload).encode()
        class Opener:
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return Response()
        opener = Opener()
        result = module.fetch_events(opener=opener)
        self.assertEqual(result[0]["id"], 7)
        self.assertIn("upcoming=true", opener.request.full_url)
        self.assertNotIn("Authorization", opener.request.headers)

    def test_unknown_shape_inactive_and_missing_status_are_handled(self):
        class BadResponse:
            status = 200
            headers = {"Content-Type": "application/json"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, limit): return b'{"results": []}'
        class BadOpener:
            def open(self, request, timeout): return BadResponse()
        with self.assertRaisesRegex(RuntimeError, "unexpected_response_shape"):
            module.fetch_events(opener=BadOpener())
        inactive = module.project_event({"title": "AI cancelled", "starting_at": "2026-11-29T18:00:00Z", "ending_at": "2026-11-29T19:00:00Z", "status": "CANCELLED"})
        missing_status = module.project_event({"title": "AI status unknown", "starting_at": "2026-11-29T18:00:00Z", "ending_at": "2026-11-29T19:00:00Z"})
        self.assertEqual(inactive["status"], "CANCELLED")
        self.assertFalse(inactive["active"])
        self.assertIsNone(missing_status["active"])

    def test_full_result_page_fails_instead_of_claiming_exhaustive_list(self):
        payload = [
            {"id": i, "title": f"Event {i}", "starting_at": "2026-11-29T18:00:00Z", "ending_at": "2026-11-29T19:00:00Z"}
            for i in range(module.LIMIT)
        ]
        class Response:
            status = 200
            headers = {"Content-Type": "application/json"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, limit): return json.dumps(payload).encode()
        class Opener:
            def open(self, request, timeout): return Response()
        with self.assertRaisesRegex(RuntimeError, "possibly_truncated_at_api_limit"):
            module.fetch_events(opener=Opener())


if __name__ == "__main__":
    unittest.main()
