import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


lookup = load_module("buscar_simbolos", "buscar_simbolos.py")
journal = load_module("registro", "registro.py")


class LookupTests(unittest.TestCase):
    def test_dreambible_extracts_exact_heading_definition_not_header(self):
        source = """<html><title>Dream Bible - Dream Interpretation of snake</title>
        <p><b>Mamba Snake</b></p><p>Mamba definition.</p>
        <p><b>Snakes</b></p><p>A long snake definition with change and feelings.</p>
        <p><b>Snake Skin</b></p><p>Skin definition.</p></html>"""
        result = lookup._extract_dreambible("snake", source)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["excerpt"], "A long snake definition with change and feelings.")
        self.assertIn("search.php?q=snake", result["url"])

    def test_dreambible_unknown_symbol_is_not_found(self):
        result = lookup._extract_dreambible("moon", "<html><p><b>Sun</b></p><p>Some meaning.</p></html>")
        self.assertEqual(result["status"], "not_found")

    def test_auntyflo_requires_matching_article_heading_and_extracts_content(self):
        source = """<html><li>Snake in navigation</li><h1>Snake Dream Meaning</h1>
        <p>This is a substantial passage about the meaning of snakes and their symbolism within a dream.</p>
        <p>Another paragraph explores transformation, inner change, and emotion in dreams.</p>
        <p>LEGAL DISCLAIMER: not an article passage but long enough to exclude.</p></html>"""
        result = lookup._extract_auntyflo("snake", source, "https://www.auntyflo.com/dream-dictionary/snake")
        self.assertEqual(result["status"], "ok")
        self.assertIn("substantial passage", result["excerpt"])
        self.assertNotIn("LEGAL DISCLAIMER", result["excerpt"])

    def test_auntyflo_does_not_accept_navigation_mention_without_h1_match(self):
        source = "<html><li>Snake</li><h1>Water Dream Meaning</h1><p>Article body long enough to be considered readable.</p></html>"
        result = lookup._extract_auntyflo("snake", source, "https://www.auntyflo.com/dream-dictionary/water")
        self.assertEqual(result["status"], "not_found")

    def test_lookup_uses_cached_success_only_and_does_not_fetch_dreambook(self):
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.json"
            with patch.object(lookup, "CACHE_FILE", cache_path), patch.object(lookup, "_fetch") as fetch:
                fetch.side_effect = [
                    (200, "<p><b>Snakes</b></p><p>A valid definition from the Dream Bible source.</p>", "https://www.dreambible.com/search.php?q=snake"),
                    (200, "<h1>Snake Dream Meaning</h1><p>A sufficiently long and valid article excerpt about how snakes can carry different symbolic associations within a dream story.</p>", "https://www.auntyflo.com/dream-dictionary/snake"),
                ]
                result = lookup.run(["snake"], now=1000)
                self.assertEqual(result["simbolos"]["snake"]["Dream Bible"]["status"], "ok")
                self.assertTrue(result["simbolos"]["snake"]["Dream Bible"]["excerpt"])
                self.assertEqual(result["simbolos"]["snake"]["Dream Book"]["status"], "unavailable")
                self.assertEqual(fetch.call_count, 2)
                cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
                self.assertEqual(len(cache_data), 2)
                self.assertTrue(all(item["data"]["excerpt"].strip() for item in cache_data.values()))
                self.assertEqual(cache_path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(cache_path.parent.stat().st_mode & 0o777, 0o700)

    def test_success_cache_is_reused_but_not_empty_or_failed_results(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(lookup, "CACHE_FILE", Path(temp) / "cache.json"), patch.object(lookup, "_fetch") as fetch:
                fetch.side_effect = [
                    (200, "<p><b>Water</b></p><p>A substantial definition of water in dreams and symbols.</p>", "https://www.dreambible.com/search.php?q=water"),
                    (200, "<html><p>No matching entry.</p></html>", "https://www.auntyflo.com/dream-dictionary/water"),
                    (200, "<html><p>No matching entry.</p></html>", "https://www.auntyflo.com/dream-dictionary/water"),
                ]
                first = lookup.run(["water"], now=1000)
                second = lookup.run(["water"], now=1001)
                self.assertEqual(first["simbolos"]["water"]["Dream Bible"]["status"], "ok")
                self.assertTrue(second["simbolos"]["water"]["Dream Bible"]["cached"])
                self.assertEqual(second["simbolos"]["water"]["AuntyFlo"]["status"], "not_found")
                # Dream Bible success is reused; AuntyFlo's not_found is not cached.
                self.assertEqual(fetch.call_count, 3)


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "journal.json"
        self.override = patch.object(journal, "REGISTRO_FILE", self.path)
        self.override.start()

    def tearDown(self):
        self.override.stop()
        self.temp.cleanup()

    def test_refuses_write_without_explicit_consent(self):
        with self.assertRaisesRegex(ValueError, "explicit_consent_required"):
            journal.add_entry("test", "snake", "propio", False)
        self.assertFalse(self.path.exists())

    def test_add_stores_only_title_symbols_type_date_and_private_permissions(self):
        result = journal.add_entry("  La casa   y el agua ", "Snake, water, snake", "propio", True)
        self.assertEqual(result["status"], "success")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0]), {"fecha", "titulo", "simbolos", "tipo"})
        self.assertEqual(data[0]["titulo"], "La casa y el agua")
        self.assertEqual(data[0]["simbolos"], ["snake", "water"])
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.path.parent.stat().st_mode & 0o777, 0o700)

    def test_trends_count_symbol_once_per_dream_and_exclude_third_party(self):
        journal.add_entry("Uno", "snake,snake,water", "propio", True)
        journal.add_entry("Dos", "snake", "parcial", True)
        journal.add_entry("Tercero", "snake", "tercero", True)
        result = journal.trends()
        self.assertEqual(result["total_suenos_registrados"], 2)
        self.assertEqual(result["simbolos_recurrentes"], {"snake": 2})
        self.assertTrue(result["umbral_cumplido"])


if __name__ == "__main__":
    unittest.main()
