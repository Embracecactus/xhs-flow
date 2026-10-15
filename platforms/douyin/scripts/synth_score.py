#!/usr/bin/env python3
"""Original deterministic instrumental score and sparse synchronized foley.
No samples, cloud service, voice cloning, reference audio or speech.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np


def compose(project, seconds, scenes):
    hz=48000;rng=np.random.default_rng(143406);audio=np.zeros((round(seconds*hz),2),dtype=np.float64)
    def add(start,sound,volume=.15,pan=0):
        a=round(start*hz);n=min(len(sound),len(audio)-a)
        if a<0 or n<=0:return
        # Equal-power pan, short smooth edges; no discontinuous cut transients.
        fade=min(round(.03*hz),n//2);env=np.ones(n)
        env[:fade]=np.sin(np.linspace(0,np.pi/2,fade))**2;env[-fade:]=np.cos(np.linspace(0,np.pi/2,fade))**2
        x=sound[:n]*env*volume
        audio[a:a+n,0]+=x*np.sqrt((1-pan)/2);audio[a:a+n,1]+=x*np.sqrt((1+pan)/2)
    def pluck(midi,duration=1.15):
        t=np.arange(round(duration*hz))/hz;f=440*2**((midi-69)/12)
        return (np.sin(2*np.pi*f*t)+.28*np.sin(2*np.pi*f*2*t)+.12*np.sin(2*np.pi*f*3*t))*np.exp(-t*4.7)
    bpm=104;beat=60/bpm;chords=[[57,60,64,67],[53,57,60,64],[48,55,60,64],[55,59,62,67]]
    for i,t0 in enumerate(np.arange(0,seconds-2,beat/2)):
        chord=chords[(i//32)%4];note=chord[[0,2,1,3,2,1,3,2][i%8]]+12
        quiet=.45 if 57<=t0<74 else 1
        if i%2==0 or 14<=t0<47:add(t0,pluck(note),.085*quiet,(-.35 if i%2 else .35))
        if i%8==0:
            t=np.arange(round(beat*3.5*hz))/hz;f=440*2**((chord[0]-12-69)/12)
            add(t0,np.sin(2*np.pi*f*t)*np.exp(-t*1.4),.12*quiet)
        if i%4==0 and 13<t0<81:
            t=np.arange(round(.24*hz))/hz;phase=2*np.pi*(49*t+58*.025*(1-np.exp(-t/.025)))
            add(t0,np.sin(phase)*np.exp(-t*21),.16*quiet)
        if i%4==2 and 14<t0<57:
            t=np.arange(round(.1*hz))/hz;noise=rng.normal(0,1,len(t));high=noise-np.r_[0,noise[:-1]]
            add(t0,high*np.exp(-t*55),.023,.13)
    events=[(7,'message'),(14.3,'assembly'),(25,'routing'),(35.5,'layers'),(47.1,'via'),(57,'experiment'),(74.6,'check'),(81,'reassemble')]
    for when,kind in events:
        if kind in ['message','check']:
            add(when,pluck(81,.38),.16);add(when+.14,pluck(88,.35),.11)
        else:
            t=np.arange(round(.6*hz))/hz;f=300+1800*t/.6
            sound=np.sin(2*np.pi*(300*t+1500*t*t))*.25+rng.normal(0,.09,len(t))
            sound*=np.sin(np.pi*np.minimum(t/.6,1))**2
            add(when-.15,sound,.1,-.25)
    for i in range(12):add(15+i*.57,pluck(69+(i%4)*3,.18),.09,(-.5+i/11))
    # Original closing harmony; all notes finish before the 2-second visual hold ends.
    for i,n in enumerate([57,64,69,72]):add(seconds-4+i*.13,pluck(n,2.5),.11,(-.3+i*.2))
    ramp=np.ones(len(audio));n=hz*2;ramp[-n:]=np.linspace(1,0,n)**2;audio*=ramp[:,None]
    audio*=min(1,.93/max(np.abs(audio).max(),1e-8));pcm=(audio*32767).astype('<i2')
    raw=project/'score-mix.wav'
    with wave.open(str(raw),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(hz);w.writeframes(pcm.tobytes())
    proc=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af','loudnorm=I=-17:TP=-1.5:LRA=9:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
    norm=json.loads(proc.stderr[proc.stderr.rfind('{'):]);filt='loudnorm=I=-17:TP=-1.5:LRA=9:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}'.format(**norm)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-af',filt,'-ar',str(hz),'-ac','2','-c:a','pcm_s16le',str(project/'voice.wav')],check=True)
    (project/'narration.json').write_text(json.dumps({'provider':'synth_score','role':'original instrumental score and sparse sound effects','speech':False,'cloning':False,'samples_used':False,'reference_audio_used':False,'seed':143406,'bpm':bpm,'events':events,'normalization':norm,'listening':'not performed; measurements do not establish listening quality'},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':compose(Path(sys.argv[1]),float(sys.argv[2]),[])
