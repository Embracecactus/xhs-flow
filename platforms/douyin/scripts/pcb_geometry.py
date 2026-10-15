#!/usr/bin/env python3
"""Read-only KiCad geometry extraction + bounded numerical teaching experiment.
Not KiCad DRC, autorouting, electromagnetic simulation or board validation.
Derived texture/source data retains Antmicro Apache-2.0 provenance.
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def blocks(s, tag, level=1):
    indent='\t'*level
    return re.findall(r'(?ms)^'+indent+r'\('+tag+r'\b.*?^'+indent+r'\)',s)


def nums(s,key,default=None):
    m=re.search(r'\('+re.escape(key)+r' ([^()]+)\)',s)
    return [float(x) for x in m[1].split()] if m else default


def make(v):
    a=v/'assets';raw=(a/'board/polarfire-som.kicad_pcb').read_text();out=a/'derived';out.mkdir(exist_ok=True)
    layer_names=['F.Cu']+[f'In{i}.Cu' for i in range(1,13)]+['B.Cu']
    origin=[174.517,115.836];width,height=55.,40.
    layers=[[] for _ in layer_names];via=[];pads=[];polys=[[] for _ in layer_names]
    def xy(p):return [round(p[0]-origin[0]-width/2,5),round(p[1]-origin[1]-height/2,5)]
    for b in blocks(raw,'segment'):
        name=re.search(r'\(layer "([^"]+)"\)',b)[1]
        if name not in layer_names:continue
        layers[layer_names.index(name)].append([*xy(nums(b,'start')),*xy(nums(b,'end')),nums(b,'width')[0],int(nums(b,'net')[0])])
    for b in blocks(raw,'via'):
        via.append([*xy(nums(b,'at')),nums(b,'size')[0],nums(b,'drill')[0]])
    fp=blocks(raw,'footprint')
    for b in fp:
        at=nums(b,'at');angle=math.radians(at[2] if len(at)>2 else 0);c=math.cos(angle);s=math.sin(angle)
        for p in blocks(b,'pad',2):
            atp=nums(p,'at',[0,0]);size=nums(p,'size',[.3,.3]);lay=re.search(r'\(layers ([^)]+)\)',p)
            if not lay:continue
            lay=lay[1];ls=([0,13] if '*.Cu' in lay else [0] if 'F.Cu' in lay else [13] if 'B.Cu' in lay else [])
            q=xy([at[0]+atp[0]*c+atp[1]*s,at[1]-atp[0]*s+atp[1]*c])
            for layer in ls:pads.append([*q,min(size),max(size),layer])
    for b in blocks(raw,'zone'):
        for f in blocks(b,'filled_polygon',2):
            m=re.search(r'\(layer "([^"]+)"\)',f)
            if not m or m[1] not in layer_names:continue
            pts=[xy([float(x),float(y)]) for x,y in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)',f)]
            if len(pts)>2:polys[layer_names.index(m[1])].append(pts)
    colors=['#ebb85b','#63a9bf','#dc809b','#73bca7','#de985d','#839bcb','#be9acb','#7fbec9','#cfbd73','#a4bb7b','#e39392','#99b1da','#a4c3bb','#e4bc75']
    scale=40;W,H=round(width*scale),round(height*scale)
    def pix(p):return ((p[0]+width/2)*scale,(p[1]+height/2)*scale)
    for n,name in enumerate(layer_names):
        im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
        for poly in polys[n]:d.polygon([pix(p) for p in poly],fill=colors[n]+'aa')
        for x,y,ex,ey,w,net in layers[n]:d.line([pix((x,y)),pix((ex,ey))],fill=colors[n],width=max(2,round(w*scale)))
        for x,y,small,large,layer in pads:
            if layer!=n:continue
            px,py=pix((x,y));r=small*scale/2;d.ellipse((px-r,py-r,px+r,py+r),fill='#f3cf88')
        for x,y,size,drill in via:
            px,py=pix((x,y));r=size*scale/2;d.ellipse((px-r,py-r,px+r,py+r),fill='#e9d8ac')
            r=drill*scale/2;d.ellipse((px-r,py-r,px+r,py+r),fill=(0,0,0,0))
        im.save(out/f'layer-{n:02}.png')
    # A real, small finite-difference calculation with EXPLICIT artificial inputs.
    # Dimensionless diffusion du/dt = Laplacian(u) + source, zero-temperature edges.
    # No material identification, watts, degrees or physical elapsed time is claimed.
    nx,ny=111,81;y,x=np.mgrid[0:ny,0:nx];u=np.zeros((ny,nx));source=np.exp(-((x-47)**2+(y-35)**2)/42)*.02
    frames=[];alpha=.2
    for i in range(720):
        u[1:-1,1:-1]+=alpha*(u[2:,1:-1]+u[:-2,1:-1]+u[1:-1,2:]+u[1:-1,:-2]-4*u[1:-1,1:-1])+source[1:-1,1:-1]
        if i%12==0:frames.append(u.copy())
    maximum=float(u.max());normalized=[np.round(f/maximum,4).flatten().tolist() for f in frames]
    thermal={'width':nx,'height':ny,'frames':normalized,'method':'dimensionless 2D explicit finite difference','alpha':alpha,'steps':720,'boundary':'u=0 at all four edges','source':'artificial Gaussian; no board power data','stability_bound':.25,'max_unscaled':maximum,'physical_prediction':False,'scope':'教学热扩散实验；归一化，无温度/时间单位，非该板温升预测'}
    (out/'thermal.json').write_text(json.dumps(thermal,separators=(',',':')))
    nets={int(i):name for i,name in re.findall(r'^\t\(net (\d+) "([^"]+)"\)',raw,re.M)}
    pnp=json.loads((a/'board/pnp.json').read_text());count=sum(not k.startswith('_') for k in pnp)
    data={'width':width,'height':height,'origin':origin,'layer_names':layer_names,'layers':layers,'vias':via,'colors':colors,'nets':nets,'source_counts':{'copper_layers':14,'footprints':len(fp),'placed_models':count,'track_segments':sum(map(len,layers)),'vias':len(via),'filled_polygons':sum(map(len,polys))},'scope':'Existing routed design revealed progressively, not new autorouting; source geometry only; not DRC.'}
    (out/'pcb.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False))
    notice='Derived from Antmicro polarfire-som @ 1c787f6b8bb91cfc65c87a11866b2d13cb3f11a0 (Apache-2.0). Changed: extracted track/via/pad/polygon coordinates; rasterized and recolored copper for animation; exploded layer spacing is illustrative. Original CAD remains unmodified. Thermal data is an independent dimensionless teaching experiment, not board validation.\n'
    (out/'NOTICE.txt').write_text(notice)
    registry=json.loads((v/'assets.json').read_text());registry=[r for r in registry if not r['path'].startswith('assets/derived/')]
    for p in sorted(out.iterdir()):registry.append(dict(path=str(p.relative_to(v)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rights=notice.strip()))
    (v/'assets.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    evidence=v/'evidence';evidence.mkdir(exist_ok=True)
    (evidence/'source-geometry.json').write_text(json.dumps({'source_sha256':hashlib.sha256((a/'board/polarfire-som.kicad_pcb').read_bytes()).hexdigest(),**data['source_counts'],'drc_run':False,'manufacturing_validation':False,'thermal_solver_finite':bool(np.isfinite(u).all()),'thermal_stable_parameter':alpha<=.25,'thermal_peak_zero_boundary':float(np.max(np.r_[u[0],u[-1],u[:,0],u[:,-1]]))},indent=2)+'\n')
    print(data['source_counts'])

if __name__=='__main__':make(Path(sys.argv[1]).resolve())
