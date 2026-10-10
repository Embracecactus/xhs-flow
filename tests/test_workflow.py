import csv
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

spec=importlib.util.spec_from_file_location('xhs',Path(__file__).resolve().parents[1]/'scripts/xhs.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def csv(self,change=None):
        rows=list(csv.DictReader((x.REPO/'examples/metrics-test.csv').read_text().splitlines()))
        if change:change(rows)
        p=self.root/'data.csv'
        with p.open('w') as f:
            w=csv.DictWriter(f,fieldnames=x.FIELDS);w.writeheader();w.writerows(rows)
        return p
    def test_init_and_new_preserve_edits(self):
        p=x.create(self.root,'draft',True);(p/'copy.md').write_text('作者修改')
        x.create(self.root,'draft',False);x.init(self.root)
        self.assertEqual((p/'copy.md').read_text(),'作者修改')
        self.assertTrue(json.loads((p/'state.json').read_text())['demo'])
    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):x.create(self.root,'../escape')
    def test_demo_cannot_be_approved(self):
        x.create(self.root,'demo',True)
        with self.assertRaises(ValueError):x.approve(self.root,'demo','审核')
    def test_unapproved_cannot_be_published(self):
        x.create(self.root,'draft')
        with self.assertRaises(ValueError):x.published(self.root,'draft','','用户确认')
    def test_unpublished_cannot_be_reviewed(self):
        x.create(self.root,'draft')
        with self.assertRaises(ValueError):x.reviewed(self.root,'draft',self.root/'report.md','test')
    def test_test_report_cannot_close_real_post(self):
        p=x.create(self.root,'draft')
        x.save(p/'state.json',{'status':'已发布'})
        report=self.root/'reviews/test/a.md';report.parent.mkdir(parents=True,exist_ok=True);report.write_text('TEST')
        with self.assertRaises(ValueError):x.reviewed(self.root,'draft',report,'test')
    def test_missing_not_zero_or_likes(self):
        d=x.analyze(self.csv(),self.root,'test')
        rows=json.loads((d/'normalized.json').read_text())['rows']
        self.assertEqual(rows[0]['save_read_ratio'],.1)
        self.assertIsNone(rows[1]['follow_read_ratio'])
        self.assertIsNone(rows[2]['save_read_ratio'])
        self.assertIsNone(rows[2]['reads'])
        self.assertNotIn('ctr',rows[3])
    def test_zero_denominator(self):
        d=x.analyze(self.csv(lambda r:r[0].update(reads='0')),self.root,'test')
        self.assertIsNone(json.loads((d/'normalized.json').read_text())['rows'][0]['save_read_ratio'])
    def test_incompatible_unit(self):
        d=x.analyze(self.csv(lambda r:r[0].update(unit='people')),self.root,'test')
        self.assertIsNone(json.loads((d/'normalized.json').read_text())['rows'][0]['save_read_ratio'])
    def test_wrong_window_rejected(self):
        with self.assertRaises(ValueError):x.analyze(self.csv(lambda r:r[0].update(window_hours='48')),self.root,'test')
    def test_invalid_number_rejected(self):
        with self.assertRaises(ValueError):x.analyze(self.csv(lambda r:r[0].update(reads='NaN')),self.root,'test')
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):x.analyze(self.csv(lambda r:r.append(r[0].copy())),self.root,'test')
    def test_repeat_does_not_overwrite_review(self):
        p=self.csv();d=x.analyze(p,self.root,'test');(d/'review.md').write_text('作者批注')
        self.assertEqual(x.analyze(p,self.root,'test'),d)
        self.assertEqual((d/'review.md').read_text(),'作者批注')
    def test_test_real_isolation(self):
        p=self.csv();x.analyze(p,self.root,'test')
        with self.assertRaises(ValueError):x.analyze(p,self.root,'real')
        self.assertFalse((self.root/'metrics/real').exists())

    def render_fixture(self):
        p=x.create(self.root,'draft')
        (p/'editable/index.html').write_text('<section>fixture</section>')
        return p

    @staticmethod
    def fake_browser(cmd,check):
        (Path(cmd[-1])/'01.png').write_bytes(b'test-render-output')

    def test_export_interrupted_after_rename_recovers_state_without_render(self):
        p=self.render_fixture()
        save=x.save
        def fail_state(path,value):
            if path==p/'state.json':raise OSError('simulated interruption after rename')
            save(path,value)
        with patch.object(x.subprocess,'run',side_effect=self.fake_browser), patch.object(x,'save',side_effect=fail_state):
            with self.assertRaises(OSError):x.render(self.root,'draft','test')
        target=p/'publish/v001'
        before={str(f):x.digest(f) for f in target.rglob('*') if f.is_file()}
        self.assertEqual(json.loads((p/'state.json').read_text())['status'],'制作中')
        with patch.object(x.subprocess,'run',side_effect=AssertionError('must not rerender')):
            self.assertEqual(x.render(self.root,'draft','retry'),target)
        s=json.loads((p/'state.json').read_text())
        self.assertEqual((s['status'],s['version']),('待审核','v001'))
        self.assertEqual(before,{str(f):x.digest(f) for f in target.rglob('*') if f.is_file()})

    def test_recovery_clears_old_approval_and_preserves_later_source_edits(self):
        p=self.render_fixture()
        with patch.object(x.subprocess,'run',side_effect=self.fake_browser):
            x.render(self.root,'draft','first')
            x.approve(self.root,'draft','TEST simulated approval')
            (p/'copy.md').write_text('second draft')
            save=x.save
            def fail_state(path,value):
                if path==p/'state.json':raise OSError('interrupt')
                save(path,value)
            with patch.object(x,'save',side_effect=fail_state):
                with self.assertRaises(OSError):x.render(self.root,'draft','second')
        (p/'copy.md').write_text('author edit after interruption')
        with patch.object(x.subprocess,'run',side_effect=OSError('browser unavailable')):
            with self.assertRaises(OSError):x.render(self.root,'draft','retry')
        s=json.loads((p/'state.json').read_text())
        self.assertEqual(s['version'],'v002')
        self.assertIsNone(s['approval'])
        self.assertEqual((p/'copy.md').read_text(),'author edit after interruption')
        self.assertEqual(len(list((p/'publish').glob('v*'))),2)

    def test_conflicting_publication_is_not_reset_by_recovery(self):
        p=self.render_fixture()
        with patch.object(x.subprocess,'run',side_effect=self.fake_browser):x.render(self.root,'draft','test')
        s=json.loads((p/'state.json').read_text());s.update(status='已发布',version='v000')
        x.save(p/'state.json',s)
        before=(p/'state.json').read_bytes()
        with self.assertRaises(ValueError):x.render(self.root,'draft','retry')
        self.assertEqual((p/'state.json').read_bytes(),before)

    def test_import_interrupted_after_rename_recovers_reports(self):
        source=self.csv()
        with patch.object(x,'complete_import_reports',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):x.analyze(source,self.root,'test')
        dest=next((self.root/'metrics/test').iterdir())
        before={f.name:f.read_bytes() for f in dest.iterdir()}
        self.assertEqual(x.analyze(source,self.root,'test'),dest)
        for name,raw in before.items():self.assertEqual((dest/name).read_bytes(),raw)
        self.assertTrue((dest/'calculations.md').is_file())
        self.assertTrue((self.root/'reviews/test'/f'{dest.name}.md').is_file())

    def test_import_retry_preserves_notes_and_fills_missing_canonical_report(self):
        source=self.csv();new_file=x.new_file
        def fail_report(path,text):
            if path.parent==self.root/'reviews/test':raise OSError('report write interrupted')
            new_file(path,text)
        with patch.object(x,'new_file',side_effect=fail_report):
            with self.assertRaises(OSError):x.analyze(source,self.root,'test')
        dest=next((self.root/'metrics/test').iterdir())
        draft=(dest/'review-template.md').read_text()+'\n作者在模板中的批注\n'
        (dest/'review-template.md').write_text(draft)
        x.analyze(source,self.root,'test')
        report=self.root/'reviews/test'/f'{dest.name}.md'
        self.assertIn('分析状态：待分析',report.read_text())
        self.assertIn('作者在模板中的批注',report.read_text())
        self.assertEqual((dest/'review-template.md').read_text(),draft)
        report.write_text('作者正式报告批注')
        x.analyze(source,self.root,'test')
        self.assertEqual(report.read_text(),'作者正式报告批注')

    def test_interrupted_new_file_does_not_leave_partial_destination(self):
        p=self.root/'report.md'
        with patch.object(x.os,'link',side_effect=OSError('interrupt')):
            with self.assertRaises(OSError):x.new_file(p,'complete report')
        self.assertFalse(p.exists())
        x.new_file(p,'complete report')
        self.assertEqual(p.read_text(),'complete report')

    def test_legacy_import_recovery_keeps_old_notes_but_not_completion_claim(self):
        source=self.csv()
        with patch.object(x,'complete_import_reports',side_effect=OSError('interrupt')):
            with self.assertRaises(OSError):x.analyze(source,self.root,'test')
        dest=next((self.root/'metrics/test').iterdir())
        (dest/'review.md').write_text('旧报告中的作者批注')
        x.analyze(source,self.root,'test')
        report=self.root/'reviews/test'/f'{dest.name}.md'
        self.assertIn('旧报告中的作者批注',report.read_text())
        self.assertIn('分析状态：待分析',report.read_text())
        self.assertEqual((dest/'review.md').read_text(),'旧报告中的作者批注')

    def test_calculations_and_template_do_not_invent_explanation(self):
        d=x.analyze(self.csv(),self.root,'test')
        calculations=(d/'calculations.md').read_text()
        template=(d/'review-template.md').read_text()
        self.assertIn('10.00%',calculations)
        self.assertNotIn('步骤的可复用程度',calculations+template)
        self.assertNotIn('仅改变末页',calculations+template)
        self.assertIn('分析状态：待分析',template)
        self.assertNotIn('分析状态：已完成',template)

    def test_real_template_cannot_be_marked_reviewed(self):
        source=self.csv(lambda rows:[r.update(dataset_kind='real') for r in rows])
        d=x.analyze(source,self.root,'real')  # isolated synthetic fixture only
        p=x.create(self.root,'test-01');x.save(p/'state.json',{'status':'已发布'})
        report=self.root/'reviews/real'/f'{d.name}.md'
        with self.assertRaisesRegex(ValueError,'待分析模板'):x.reviewed(self.root,'test-01',report,'test')

if __name__=='__main__':unittest.main()
