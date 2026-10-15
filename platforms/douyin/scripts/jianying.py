#!/usr/bin/env python3
"""Use the pinned JyProject API, write isolated drafts with Windows asset paths."""
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
import yaml

REPO=Path(__file__).resolve().parents[3]
skill=Path(os.environ.get('JY_SKILL_ROOT',REPO/'skills/jianying-editor-skill'))
if not (skill/'scripts/jy_wrapper.py').is_file():
    raise ImportError('未找到固定版本jianying-editor-skill')
sys.path.insert(0,str(skill/'scripts'))
sys.path.insert(0,str(skill/'scripts/vendor'))
from jy_wrapper import JyProject
import pyJianYingDraft as draft


def windows_path(p):
    return subprocess.check_output(['wslpath','-w',str(p.resolve())],text=True).strip()


def build(v):
    plan=yaml.safe_load((v/'shotlist.yaml').read_text())
    root=v/'project/jianying'; root.mkdir(exist_ok=True)
    name='Douyin-'+v.parent.name+'-'+v.name
    target=root/name
    if target.exists():
        if not (v/'project/jianying.json').exists():
            raise ValueError('剪映草稿制作中断；保留现场，使用revise')
        return
    width,height=plan.get('width',1080),plan.get('height',1920)
    project=JyProject(name,width=width,height=height,drafts_root=str(root),overwrite=False)
    for scene in plan['scenes']:
        project.add_clip(str(v/'project/base.mp4'),f"{scene['start']}s",f"{scene['end']-scene['start']}s",f"{scene['start']}s",track_name='动画与原片')
    project.add_media_safe(str(v/'project/voice.wav'),start_time='0s',duration=f"{plan['duration']}s",track_name='原创配乐与音效' if plan.get('voice')=='synth_score' else '旁白')
    for c in plan['cues']:
        project.add_text_simple(c['text'],start_time=f"{c['start']}s",duration=f"{c['end']-c['start']}s",track_name='字幕',style=draft.TextStyle(size=8.0,color=(1,1,1)),clip_settings=draft.ClipSettings(transform_y=-.72 if width>height else -.63))
    project.save()
    content=target/'draft_info.json'
    data=json.loads(content.read_text())
    tracks=data['tracks']
    counts={kind:sum(len(t['segments']) for t in tracks if t['type']==kind) for kind in ['video','audio','text']}
    if counts!={'video':len(plan['scenes']),'audio':1,'text':len(plan['cues'])} or data['duration']!=round(plan['duration']*1000000):
        raise ValueError('剪映工程轨道数量或时长校验失败')
    # Modify only our newly generated artifact. Exported Windows draft must use
    # Windows paths; leave upstream source and existing user drafts untouched.
    def convert(x):
        if isinstance(x,dict):return {k:convert(val) for k,val in x.items()}
        if isinstance(x,list):return [convert(val) for val in x]
        if isinstance(x,str) and x.startswith(str(v.resolve())+'/'):return windows_path(Path(x))
        return x
    content.write_text(json.dumps(convert(data),ensure_ascii=False,indent=2))
    meta=target/'draft_meta_info.json'; m=json.loads(meta.read_text())
    m.update(draft_id=str(uuid.uuid4()).upper(),draft_name=name,tm_duration=data['duration'],draft_fold_path=windows_path(target),draft_root_path=windows_path(root))
    meta.write_text(json.dumps(m,ensure_ascii=False,indent=2))
    report=dict(skill_commit='32c56928ded4f9e2c2b80e099dc7abb793d2c30b',draft=str(target.relative_to(v)),windows_draft_path=windows_path(target),duration_us=data['duration'],tracks=counts,sdk_save=True,windows_open_verified=False,windows_export_verified=False)
    (v/'project/jianying.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__': build(Path(sys.argv[1]).resolve())
