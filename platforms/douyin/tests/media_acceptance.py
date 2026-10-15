#!/usr/bin/env python3
"""Real source-path integration using labelled synthetic fixtures, not people."""
import json
import subprocess
import sys
from pathlib import Path
import yaml

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from flow import ROOT, WORKSPACE, create, asset, build, audit, inputs, current, revise


def main():
    source=WORKSPACE/'fixture-source.mp4'
    if not source.exists():
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','lavfi','-i','testsrc2=size=720x1280:rate=30','-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','6','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac',str(source)],check=True)
    results=[]
    for kind in 'AC':
        slug='fixture-'+kind.lower()
        p=WORKSPACE/slug
        if not p.exists():
            create(WORKSPACE,slug,kind,'合成素材路径测试',demo=True)
            asset(p,source,'本地FFmpeg生成的测试条纹+正弦音；非真人/实拍验收')
            v=p/'v001'
            (v/'script.md').write_text('# 合成素材路径测试\n\n仅测试A/C素材导入、剪辑、音轨、字幕和草稿；无真人或实拍结论。\n')
            (v/'sources.md').write_text('# 来源\n\n自建FFmpeg testsrc2 + sine测试fixture，无外部素材；明确无对白。\n')
            d=dict(kind=kind,title='合成素材路径测试',duration=6,width=1920,height=1080,voice='source',cues=[dict(start=0,end=3,text='这是合成素材测试'),dict(start=3,end=6,text='验证素材剪辑路径')],scenes=[dict(start=0,end=3,heading='路径测试',asset='assets/fixture-source.mp4',source_start=0,speech=False,cut_evidence='正弦音测试素材，无对白，无词内裁切'),dict(start=3,end=6,heading='路径测试',asset='assets/fixture-source.mp4',source_start=3,speech=False,cut_evidence='正弦音测试素材，无对白，无词内裁切')])
            (v/'shotlist.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
        else:
            _,v=current(p);d=yaml.safe_load((v/'shotlist.yaml').read_text())
            if (d.get('width'),d.get('height'))!=(1920,1080):
                v=revise(p);d.update(width=1920,height=1080)
                (v/'shotlist.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
        v=build(p); before=inputs(v); quality=audit(p)
        # A short fixture checks media plumbing, not the density gate for a
        # finished editorial video (which intentionally needs >=3 scenes).
        required=['duration','format','subtitle_readability','audio']
        assert all(quality['checks'][k] for k in required), quality
        assert before==inputs(v)
        results.append(dict(kind=kind,version=str(v.relative_to(WORKSPACE)),checks={k:quality['checks'][k] for k in required},source_sha256=json.loads((v/'assets.json').read_text())[0]['sha256'],limitations='合成fixture；不证明真实人物裁切、对白ASR或实拍内容审核'))
    evidence=ROOT/'docs/media-acceptance.json'
    evidence.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False))


if __name__=='__main__':main()
