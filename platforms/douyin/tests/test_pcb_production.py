"""Local PCB film helpers: provenance, extraction scope and speech-free audio."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import wave

SCRIPTS=Path(__file__).parents[1]/'scripts'

def load(name):
    spec=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

geometry=load('pcb_geometry')
assets=load('prepare_pcb_assets')
score=load('synth_score')

class PcbProductionTests(unittest.TestCase):
    def test_git_blob_hash_uses_git_header(self):
        self.assertEqual(assets.git_hash(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
        self.assertNotEqual(assets.git_hash(b'unchanged'),assets.git_hash(b'changed'))

    def test_extract_only_top_level_segments_and_exact_numbers(self):
        source='(kicad_pcb\n\t(footprint "demo"\n\t\t(segment\n\t\t\t(start 1 2)\n\t\t)\n\t)\n\t(segment\n\t\t(start 3.5 -2)\n\t\t(end 8 9)\n\t)\n)\n'
        blocks=geometry.blocks(source,'segment')
        self.assertEqual(len(blocks),1)
        self.assertEqual(geometry.nums(blocks[0],'start'),[3.5,-2.])
        self.assertEqual(geometry.nums(blocks[0],'end'),[8.,9.])
        self.assertIsNone(geometry.nums(blocks[0],'drill'))

    @unittest.skipUnless(shutil.which('ffmpeg'),'requires existing FFmpeg')
    def test_score_is_real_stereo_without_speech_or_external_samples(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);score.compose(p,6,[])
            with wave.open(str(p/'score-mix.wav'),'rb') as w:
                self.assertEqual(w.getnchannels(),2)
                self.assertEqual(w.getframerate(),48000)
                self.assertEqual(w.getnframes(),288000)
                self.assertTrue(any(w.readframes(w.getnframes())))
            report=json.loads((p/'narration.json').read_text())
            self.assertEqual(report['provider'],'synth_score')
            for key in ['speech','cloning','samples_used','reference_audio_used']:
                self.assertIs(report[key],False)
            self.assertTrue((p/'voice.wav').stat().st_size>0)

if __name__=='__main__':unittest.main()
