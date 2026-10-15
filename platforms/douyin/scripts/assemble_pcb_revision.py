#!/usr/bin/env python3
"""Splice this PCB revision's verified 47–57s render into its registered old base.

This is a local, frame-exact editorial reuse helper, not a general account or
publishing interface. Refuses differing props, wrong frame counts or overwrites.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import flow


def assemble(v, previous):
    v,previous=Path(v).resolve(),Path(previous).resolve()
    props=json.loads((v/'project/props.json').read_text())
    old_props=json.loads((previous/'project/props.json').read_text())
    if props!=old_props or props.get('style')!='pcb-lab' or props['duration']!=90:
        raise ValueError('Reuse requires identical 90-second PCB timeline/props')
    source=v/'assets/base.mp4';patch=v/'project/patch-1410-1709.mp4';output=v/'project/base.mp4'
    if output.exists():raise ValueError('Keep the existing assembled base')
    records=json.loads((v/'assets.json').read_text())
    if not any(r['path']=='assets/base.mp4' and r['sha256']==flow.digest(source) and r.get('rights') for r in records):
        raise ValueError('Previous base must be hash-registered with rights')
    if flow.digest(source)!=flow.digest(previous/'project/base.mp4'):
        raise ValueError('Registered media is not the preserved previous base')
    for name in ['composition.jsx','diagrams.jsx','QemuExplainer.jsx','SpatialChip.jsx']:
        if flow.digest(v/'project'/name)!=flow.digest(previous/'project'/name):
            raise ValueError('Changed an unrelated composition: '+name)
    for media,count in [(source,2700),(patch,300)]:
        stream=next(s for s in flow.probe(media)['streams'] if s['codec_type']=='video')
        if (stream['width'],stream['height'],stream['r_frame_rate'],int(stream['nb_frames']))!=(1920,1080,'30/1',count):
            raise ValueError('Unexpected media geometry/timebase/frame count')
    command=['ffmpeg','-hide_banner','-loglevel','error','-n','-i',str(source),'-i',str(patch),
        '-filter_complex','[0:v]split=2[o1][o2];[o1]trim=start_frame=0:end_frame=1410,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[o2]trim=start_frame=1710:end_frame=2700,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]',
        '-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-r','30','-frames:v','2700','-movflags','+faststart',str(output)]
    subprocess.run(command,check=True)
    report={'method':'frame-index trim + concat + H.264 re-encode; no keyframe-seek approximation',
        'source_base':{'path':'assets/base.mp4','sha256':flow.digest(source),'previous_version':previous.name},
        'replacement':{'path':'project/patch-1410-1709.mp4','sha256':flow.digest(patch),'frames_inclusive':[1410,1709]},
        'reused_frames_inclusive':[[0,1409],[1710,2699]],'output_sha256':flow.digest(output),
        'frame_count':2700,'fps':30,'prior_review_reused':False,'command':command}
    flow.save(v/'project/assembly.json',report)
    flow.save(v/'project/render.json',{'engine':'Remotion 4.0.534 / FFmpeg frame-exact selective revision','durationInFrames':2700,'fps':30,'width':1920,'height':1080,'provenance':'assembly.json'})
    return report


if __name__=='__main__':assemble(sys.argv[1],sys.argv[2])
