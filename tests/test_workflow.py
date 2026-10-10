import csv
import importlib.util
import json
import tempfile
import unittest
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

if __name__=='__main__':unittest.main()
