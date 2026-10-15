"""Frozen behavior contracts: local video production, never platform writes."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('flow', Path(__file__).parents[1]/'scripts/flow.py')
flow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(flow)


class WorkflowContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_all_requested_states_and_types(self):
        self.assertEqual(flow.STATES, ['idea','script','shooting','editing','review','ready_publish','published','reviewed'])
        for kind in 'ABC':
            p = flow.create(self.root, f'video-{kind.lower()}', kind, '测试标题', demo=True)
            self.assertEqual(json.loads((p/'state.json').read_text())['status'], 'idea')
            self.assertTrue((p/'v001/script.md').is_file())
            self.assertTrue((p/'v001/shotlist.yaml').is_file())

    def test_new_task_never_overwrites(self):
        p = flow.create(self.root, 'test', 'B', '测试标题', demo=True)
        (p/'v001/script.md').write_text('作者修改')
        with self.assertRaises(ValueError):
            flow.create(self.root, 'test', 'B', '新标题', demo=True)
        self.assertEqual((p/'v001/script.md').read_text(), '作者修改')

    def test_state_cannot_skip_missing_shooting_assets(self):
        p = flow.create(self.root, 'talk', 'A', '口播', demo=True)
        with self.assertRaises(ValueError):
            flow.transition(p, 'editing')

    def test_no_publication_without_evidence(self):
        p = flow.create(self.root, 'test', 'B', '标题', demo=True)
        with self.assertRaises(ValueError):
            flow.transition(p, 'published')

    def test_revision_preserves_export_and_invalidates_review(self):
        p = flow.create(self.root, 'test', 'B', '标题', demo=True)
        (p/'v001/final.mp4').write_bytes(b'old export')
        state = json.loads((p/'state.json').read_text())
        state.update(status='ready_publish', author_approval={'note':'old'}, review={'pass':True})
        flow.save(p/'state.json', state)
        v = flow.revise(p)
        self.assertEqual(v.name, 'v002')
        self.assertEqual((p/'v001/final.mp4').read_bytes(), b'old export')
        self.assertFalse((v/'final.mp4').exists())
        current = json.loads((p/'state.json').read_text())
        self.assertEqual(current['status'], 'script')
        self.assertIsNone(current['review'])
        self.assertIsNone(current['author_approval'])

    def test_production_hold_stops_build_before_state_or_outputs_change(self):
        p = flow.create(self.root, 'recording', 'B', '等待真人录音', demo=True)
        v = p/'v001'
        # A real recording plan has timing estimates but is not render-ready.
        hold = '等待作者录音及新动画，不得用系统配音替代'
        (v/'shotlist.yaml').write_text('production_hold: '+hold+'\n')
        before = (p/'state.json').read_bytes()
        with self.assertRaisesRegex(ValueError, hold):
            flow.build(p)
        self.assertEqual((p/'state.json').read_bytes(), before)
        self.assertEqual(list((v/'project').iterdir()), [])
        self.assertFalse((v/'subtitle.srt').exists())
        self.assertFalse((v/'final.mp4').exists())

    def test_reject_path_escape(self):
        for slug in ['../escape','/tmp/out','bad/name']:
            with self.assertRaises(ValueError):
                flow.create(self.root, slug, 'B', '标题', demo=True)

    def test_subtitles_reject_overlap_or_overlong_lines(self):
        for segments in [
            [{'start':0,'end':3,'text':'一'},{'start':2,'end':4,'text':'二'}],
            [{'start':0,'end':3,'text':'字'*41}],
        ]:
            with self.assertRaises(ValueError):
                flow.validate_cues(segments, 60)

    def test_word_cut_rejects_inside_word_and_wrong_source(self):
        p = flow.create(self.root, 'words', 'A', '对白', demo=True)
        v=p/'v001'; (v/'assets/take.mp4').write_bytes(b'fixture')
        path=v/'assets/words.json'
        flow.save(path, {'source_sha256':flow.digest(v/'assets/take.mp4'),'words':[{'start':1,'end':2,'text':'整词'}]})
        scene={'asset':'assets/take.mp4','transcript':'assets/words.json','speech':True,'start':0,'end':1,'source_start':1.5}
        with self.assertRaises(ValueError):flow.validate_cut(v,scene)
        scene.update(source_start=.9,end=1.2)
        flow.validate_cut(v,scene)
        flow.save(path, {'source_sha256':'wrong','words':[{'start':1,'end':2,'text':'整词'}]})
        with self.assertRaises(ValueError):flow.validate_cut(v,scene)

    def rendered_fixture(self, status):
        p=flow.create(self.root,'rendered','B','标题',demo=True)
        v=p/'v001'
        for name in flow.REQUIRED:
            if name!='project':(v/name).write_bytes(b'fixture output')
        original=flow.inputs(v)
        flow.save(v/'manifest.json',{'inputs':original,'outputs':{name:flow.digest(v/name) for name in flow.REQUIRED if name!='project'}})
        flow.save(v/'quality.json',{'pass':True,'inputs':original,'checks':{'audio':True}})
        state=json.loads((p/'state.json').read_text())
        state.update(status=status,review={'inputs':original,'quality_hash':flow.digest(v/'quality.json'),'manifest_hash':flow.digest(v/'manifest.json')})
        flow.save(p/'state.json',state)
        return p,v

    def test_modified_qa_cannot_reuse_review(self):
        p,v=self.rendered_fixture('review')
        quality=json.loads((v/'quality.json').read_text())
        quality['measurements']={'audio_lufs':-12}
        flow.save(v/'quality.json',quality)
        with self.assertRaises(ValueError):flow.transition(p,'ready_publish')

    def test_completed_render_recovers_interrupted_state(self):
        p,v=self.rendered_fixture('editing')
        self.assertEqual(flow.build(p),v)
        self.assertEqual(flow.current(p)[0]['status'],'review')

    def test_bright_background_is_not_caption_ink(self):
        from PIL import Image
        background=Image.new('RGB',(640,360),(238,234,225))
        self.assertFalse(flow.caption_edge_ink(background,background.copy()))

    def test_caption_ink_outside_safe_area_is_detected(self):
        from PIL import Image
        reference=Image.new('RGB',(640,360),(238,234,225))
        frame=reference.copy();frame.putpixel((10,180),(255,255,255))
        self.assertTrue(flow.caption_edge_ink(frame,reference))
        centered=reference.copy();centered.putpixel((320,180),(255,255,255))
        self.assertFalse(flow.caption_edge_ink(centered,reference))

    def test_package_excludes_private_and_unregistered_files(self):
        p,v=self.rendered_fixture('ready_publish')
        (v/'project/.private').mkdir()
        (v/'project/.private/index-backup.json').write_text('other user drafts')
        (v/'unrelated.txt').write_text('not part of production')
        flow.save(v/'review.json',{'reviewer':'fixture'})
        archive=flow.package(p)
        with zipfile.ZipFile(archive) as z:
            self.assertFalse(any('.private' in n or 'unrelated' in n for n in z.namelist()))
            self.assertEqual(z.read('v001/final.mp4'),b'fixture output')
        with self.assertRaises(ValueError):flow.package(p)


if __name__ == '__main__':
    unittest.main()
