import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/refresh_public_sources.py'


def load():
    spec=importlib.util.spec_from_file_location('refresh_public_sources',SCRIPT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicRefresh(unittest.TestCase):
    def test_managed_workspace_does_not_chase_its_own_catalogue_commit(self):
        module=load()
        prior={'name':'eBLLM','pushed_at':'old','commit':'a'*40}
        repo={'full_name':'creelie/eBLLM','pushed_at':'new'}
        with patch.object(module,'api') as api:
            result=module.read_source(repo,prior)
        api.assert_not_called()
        self.assertEqual(result['commit'],prior['commit'])
        self.assertIn('refresh loop',result['monitoring_note'])

    def test_new_release_without_code_push_is_detected_and_flagged(self):
        module=load()
        prior={'name':'sample','pushed_at':'unchanged','commit':'a'*40,'latest_release':None}
        repo={'full_name':'creelie/sample','pushed_at':'unchanged','description':'sample','archived':False}
        release={'tag_name':'v2','html_url':'https://github.com/creelie/sample/releases/tag/v2','published_at':'today','body':'A new reported result'}
        with patch.object(module,'api',return_value=release):
            result=module.read_source(repo,prior)
        self.assertEqual(result['latest_release']['tag'],'v2')
        self.assertTrue(result['scope_note_requires_review'])
