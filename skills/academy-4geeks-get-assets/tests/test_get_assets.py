import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "get_assets.py"
spec = importlib.util.spec_from_file_location("get_assets", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class AssetsTests(unittest.TestCase):
    def test_technology_resolution_requires_unique_public_canonical_choice(self):
        class Opener:
            def __init__(self, pages): self.pages = list(pages); self.requests = []
            def open(self, request, timeout):
                self.requests.append(request.full_url)
                body = self.pages.pop(0)
                return response(body)
        exact = {"count": 2, "results": [
            {"slug": "python", "title": "Python", "visibility": "PUBLIC", "is_deprecated": False},
            {"slug": "python-extra", "title": "Python Extra", "visibility": "PUBLIC", "is_deprecated": False},
        ], "next": None}
        result = module.resolve_technology("python", opener=Opener([exact]))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["technology"]["slug"], "python")
        ambiguous = {"count": 2, "results": [
            {"slug": "reactjs", "title": "React.js", "visibility": "PUBLIC", "is_deprecated": False},
            {"slug": "react-native", "title": "React Native", "visibility": "PUBLIC", "is_deprecated": False},
        ], "next": None}
        result = module.resolve_technology("react", opener=Opener([ambiguous]))
        self.assertEqual(result["status"], "needs_selection")
        self.assertEqual(len(result["candidates"]), 2)

    def test_asset_projection_matches_canonical_slug_and_redacts_private_records(self):
        item = {
            "id": 10,
            "slug": "python-intro",
            "title": "Intro Python",
            "asset_type": "LESSON",
            "technologies": [{"slug": "python", "title": "Python"}, {"slug": "flask", "title": "Flask"}],
            "category": {"title": "Lessons", "slug": "lessons"},
            "description": "An intro",
            "author": {"email": "private@example.com"},
        }
        result = module._project_asset(item, "python")
        self.assertEqual(result["technologies"][0]["slug"], "python")
        self.assertNotIn("author", result)
        with self.assertRaisesRegex(RuntimeError, "technology_filter_mismatch"):
            module._project_asset(item, "reactjs")

    def test_pagination_fetches_every_page_and_checks_count(self):
        first = {"count": 2, "results": [asset("a")], "next": "https://breathecode.herokuapp.com/v1/registry/asset?technologies=python&limit=100&offset=1"}
        second = {"count": 2, "results": [asset("b")], "next": None}
        opener = QueueOpener([first, second])
        count, assets = module.fetch_assets("python", opener=opener)
        self.assertEqual(count, 2)
        self.assertEqual(len(assets), 2)
        self.assertEqual(len(opener.requests), 2)
        self.assertNotIn("Authorization", opener.requests[0].headers)

    def test_pagination_rejects_cross_host_and_incomplete_collection(self):
        first = {"count": 2, "results": [asset("a")], "next": "https://evil.example/v1/registry/asset?technologies=python&limit=100&offset=1"}
        with self.assertRaisesRegex(RuntimeError, "invalid_pagination"):
            module.fetch_assets("python", opener=QueueOpener([first]))
        incomplete = {"count": 2, "results": [asset("a")], "next": None}
        with self.assertRaisesRegex(RuntimeError, "incomplete_pagination"):
            module.fetch_assets("python", opener=QueueOpener([incomplete]))

    def test_empty_and_unexpected_technology_result(self):
        empty = {"count": 0, "results": [], "next": None}
        result = module.resolve_technology("not-real", opener=QueueOpener([empty]))
        self.assertEqual(result["status"], "not_found")
        with self.assertRaisesRegex(RuntimeError, "unexpected_collection_response"):
            module.resolve_technology("python", opener=QueueOpener([[{"slug": "python"}]]))


def asset(slug):
    return {"slug": slug, "title": slug, "asset_type": "LESSON", "technologies": ["python"]}


def response(payload):
    class Response:
        status = 200
        headers = {"Content-Type": "application/json"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, limit): return json.dumps(payload).encode()
    return Response()


class QueueOpener:
    def __init__(self, pages): self.pages = list(pages); self.requests = []
    def open(self, request, timeout):
        self.requests.append(request)
        return response(self.pages.pop(0))


if __name__ == "__main__":
    unittest.main()
