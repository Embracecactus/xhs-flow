#!/usr/bin/env python3
"""Source audio or local Windows SAPI narration; no cloud or cloning."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import yaml
import numpy as np
import wave

ROOT=Path(__file__).resolve().parent


def run(args):
    subprocess.run([str(a) for a in args],check=True)


def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)]))


def win(path):
    return subprocess.check_output(['wslpath','-w',str(path.resolve())],text=True).strip()


def main(v):
    d=yaml.safe_load((v/'shotlist.yaml').read_text())
    if d['voice']=='synth_score':
        from synth_score import compose
        compose(v/'project',d['duration'],d['scenes'])
        return
    project=v/'project'; raw=project/'voice-raw'; raw.mkdir(exist_ok=True)
    items=[]; cues=d['cues']; hz=48000
    samples=np.zeros(round(d['duration']*hz),dtype=np.int16)
    metrics=[]
    if d['voice']=='windows_sapi':
        for c in cues:
            text=c.get('spoken',c['text']).replace('\n','')
            key=hashlib.sha256(('Huihui-rate1:'+text).encode()).hexdigest()[:20]
            items.append(dict(text=text,output=win(raw/f'{key}.wav'),local=raw/f'{key}.wav'))
        config=project/'voice-config.json'
        config.write_text(json.dumps([{k:x[k] for k in ['text','output']} for x in items],ensure_ascii=False))
        run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','RemoteSigned','-File',win(ROOT/'windows_voice.ps1'),'-Config',win(config)])
        for i,(c,item) in enumerate(zip(cues,items)):
            available=c['end']-c['start']; original=duration(item['local'])
            # Complete utterances only. Allow small timing fit, never crop speech.
            speed=max(0.9,original/max(.1,available-.18))
            if speed>1.35:
                raise ValueError(f'第{i+1}句过长：{original:.2f}s / {available:.2f}s，请改稿，不截断词')
            target=raw/f'fit-{i:03}.wav'
            speech=original/speed
            filters=f'atempo={speed:.6f},afade=t=in:d=0.03,afade=t=out:st={max(0,speech-.03):.6f}:d=0.03'
            run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',item['local'],'-af',filters,'-ar',hz,'-ac','1','-c:a','pcm_s16le',target])
            with wave.open(str(target),'rb') as w: pcm=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
            start=round(c['start']*hz)
            if start+len(pcm)>round(c['end']*hz): raise ValueError('配音越过字幕边界')
            samples[start:start+len(pcm)]=pcm
            metrics.append(dict(start=c['start'],end=c['end'],text=item['text'],source_seconds=original,tempo=speed,speech_seconds=len(pcm)/hz,fade_ms=30))
    elif d['voice']=='source':
        for i,scene in enumerate(d['scenes']):
            if not scene.get('cut_evidence'): raise ValueError('剪原片前必须记录逐词边界或无对白证据')
            length=scene['end']-scene['start']; target=raw/f'source-{i:03}.wav'
            run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',scene.get('source_start',0),'-i',v/scene['asset'],'-t',length,'-af',f'afade=t=in:d=0.03,afade=t=out:st={length-.03}:d=0.03','-ar',hz,'-ac','1','-c:a','pcm_s16le',target])
            with wave.open(str(target),'rb') as w: pcm=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
            start=round(scene['start']*hz); samples[start:start+len(pcm)]=pcm
            metrics.append(dict(start=scene['start'],end=scene['end'],cut_evidence=scene['cut_evidence'],fade_ms=30))
    else: raise ValueError('voice必须为source或windows_sapi')
    mixed=project/'voice-mix.wav'
    with wave.open(str(mixed),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(hz);w.writeframes(samples.tobytes())
    proc=subprocess.run(['ffmpeg','-hide_banner','-i',str(mixed),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
    norm=json.loads(proc.stderr[proc.stderr.rfind('{'):])
    if not np.any(samples): raise ValueError('音轨无有效声音')
    filt='loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}'.format(**norm)
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mixed,'-af',filt,'-ar',hz,'-ac','1','-c:a','pcm_s16le',project/'voice.wav'])
    (project/'narration.json').write_text(json.dumps(dict(provider=d['voice'],cloning=False,cues=metrics,normalization=norm),ensure_ascii=False,indent=2))


if __name__=='__main__': main(Path(sys.argv[1]).resolve())
