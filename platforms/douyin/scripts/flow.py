#!/usr/bin/env python3
"""Local video tasks. No network, platform account, publishing or scheduler API."""
import argparse
import hashlib
import html
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
WORKSPACE = REPO / 'workspace/douyin'
STATES = ['idea','script','shooting','editing','review','ready_publish','published','reviewed']
TYPES = {'A':'真人口播', 'B':'技术动画解释', 'C':'实拍素材剪辑'}
REQUIRED = ['script.md','shotlist.yaml','subtitle.srt','thumbnail.png','project','final.mp4','publish.json']


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    tmp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def task(root, slug):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', slug):
        raise ValueError('任务名只允许小写英文、数字、连字符')
    p = root/slug
    if p.is_symlink():
        raise ValueError('不接受符号链接任务')
    return p


def current(p):
    s = json.loads((p/'state.json').read_text())
    return s, p/s['version']


def create(root, slug, kind, title, demo=False):
    p = task(root, slug)
    if p.exists() or kind not in TYPES or not title.strip():
        raise ValueError('任务已存在，类型或标题无效')
    v = p/'v001'
    (v/'assets').mkdir(parents=True)
    (v/'project').mkdir()
    (v/'script.md').write_text(f'# {title}\n\n'+('测试作品；标题和终稿未获正式确认。\n\n' if demo else '待作者确认。\n\n')+'## Hook（0–3 秒）\n待填写\n\n## 完整口播\n待填写\n\n## 事实与来源\n待填写\n')
    template = yaml.safe_load((ROOT/'templates'/f'{kind}.yaml').read_text())
    template.update(title=title, kind=kind)
    (v/'shotlist.yaml').write_text(yaml.safe_dump(template,allow_unicode=True,sort_keys=False))
    (v/'sources.md').write_text('# 来源与权利\n\n逐条记录论断、原始链接、读取时间和素材许可。\n')
    save(v/'assets.json', [])
    save(p/'state.json',dict(slug=slug,kind=kind,demo=demo,status='idea',version='v001',review=None,author_approval=None,publication=None,history=[dict(status='idea',time=now())]))
    return p


def inputs(v):
    paths = [v/'script.md',v/'shotlist.yaml',v/'sources.md',v/'assets.json']
    paths += sorted((v/'assets').rglob('*'))
    result = {}
    for f in paths:
        if f.is_symlink():
            raise ValueError('源文件不接受符号链接')
        if f.is_file():
            result[str(f.relative_to(v))] = digest(f)
    return result


def validate_cues(cues, duration):
    last = 0
    for c in cues:
        a,b,text = c['start'],c['end'],c['text']
        if not 0 <= last <= a < b <= duration or b-a < .6:
            raise ValueError('字幕时间重叠、越界或闪烁')
        lines = text.splitlines()
        if not text.strip() or len(lines)>2 or any(len(x)>20 for x in lines):
            raise ValueError('字幕最多两行，每行最多20字符（项目审核阈值）')
        if len(text.replace('\n',''))/(b-a)>9:
            raise ValueError('字幕阅读速度超过9字符/秒')
        last = b


def plan(v):
    d = yaml.safe_load((v/'shotlist.yaml').read_text())
    if d.get('production_hold'):
        raise ValueError('制作准备尚未完成：'+str(d['production_hold']))
    if '逐条记录论断' in (v/'sources.md').read_text():
        raise ValueError('先记录技术来源或原创/实拍素材依据，不能保留来源模板')
    if d['kind'] not in TYPES or not 1<=d['duration']<=300:
        raise ValueError('视频类型或时长无效')
    if (d.get('width',1080),d.get('height',1920)) not in [(1920,1080),(1080,1920)]:
        raise ValueError('支持1920×1080横屏或1080×1920竖屏')
    if d.get('style')=='qemu-cinematic' and (d.get('width')!=1920 or d.get('height')!=1080 or d['duration']!=60 or [(s['start'],s['end']) for s in d['scenes']]!=[(0,6),(6,13),(13,20),(20,27),(27,34),(34,43),(43,51),(51,60)]):
        raise ValueError('QEMU专用动画需保持60秒横屏及已冻结的8镜时间线；改镜须同时修改动画代码')
    validate_cues(d['cues'],d['duration'])
    if not d['cues'] or d['cues'][0]['start']>0.3 or d['cues'][0]['end']>3:
        raise ValueError('必须在前3秒配置Hook字幕')
    last = 0
    for scene in d['scenes']:
        if abs(scene['start']-last)>.001 or scene['end']<=scene['start']:
            raise ValueError('镜头必须顺序连续覆盖时间线')
        if d['kind'] in 'AC' and not scene.get('asset'):
            raise ValueError('真人口播/实拍剪辑需真实授权原片')
        if scene.get('asset'):
            f = (v/scene['asset']).resolve()
            if not f.is_relative_to((v/'assets').resolve()) or not f.is_file():
                raise ValueError('原片必须先导入本版本assets目录')
            registered = json.loads((v/'assets.json').read_text())
            if not any(x['path']==scene['asset'] and x['sha256']==digest(f) and x['rights'].strip() for x in registered):
                raise ValueError('素材未登记权利或哈希不一致')
            available=float(probe(f)['format']['duration'])
            if scene.get('source_start',0)+scene['end']-scene['start']>available+.04:
                raise ValueError('所选原片不足以覆盖镜头，不能静默截断')
            if d['voice']=='source':
                validate_cut(v,scene)
        last = scene['end']
    if abs(last-d['duration'])>.001:
        raise ValueError('镜头未覆盖完整时长')
    return d


def validate_cut(v,scene):
    if scene.get('speech') is False and scene.get('cut_evidence','').strip():
        return  # Explicit non-speech shot; source is still retained and hashed.
    if scene.get('speech') is not True or not scene.get('transcript'):
        raise ValueError('有对白原片必须保留逐词时间文件；无对白须明确speech:false与证据')
    path=(v/scene['transcript']).resolve()
    if not path.is_relative_to((v/'assets').resolve()) or not path.is_file():
        raise ValueError('逐词时间文件必须在assets内')
    tr=json.loads(path.read_text())
    if tr.get('source_sha256')!=digest(v/scene['asset']) or not tr.get('words'):
        raise ValueError('逐词时间必须绑定原片哈希且包含words')
    start=scene.get('source_start',0); end=start+scene['end']-scene['start']
    words=tr['words']; previous=0
    for w in words:
        if not previous<=w['start']<w['end'] or not w.get('text','').strip():
            raise ValueError('逐词时间顺序或内容无效')
        previous=w['end']
        if any(w['start']<edge<w['end'] for edge in [start,end]):
            raise ValueError('剪辑边界切入词内')
    kept=[w for w in words if start<=w['start'] and w['end']<=end]
    if kept and (kept[0]['start']-start<.03 or end-kept[-1]['end']<.03):
        raise ValueError('对白剪辑边缘需至少30ms留白')


def transition(p, target):
    s,v = current(p)
    if target not in STATES or STATES.index(target)!=STATES.index(s['status'])+1:
        raise ValueError('状态只能逐步推进；改稿使用revise')
    if target in ['script','shooting','editing']:
        plan(v)
        if '待填写' in (v/'script.md').read_text():
            raise ValueError('先完成脚本')
    if target=='review' and not (v/'manifest.json').exists():
        raise ValueError('先生成成片')
    if target=='ready_publish':
        verify(v)
        verify_review(s,v)
        if not s['demo'] and not s.get('author_approval'):
            raise ValueError('正式内容需作者确认')
    if target in ['published','reviewed']:
        raise ValueError('本阶段不登记发布或复盘；保留状态定义，不提供发布接口')
    s['status']=target
    s['history'].append(dict(status=target,time=now()))
    save(p/'state.json',s)


def revise(p):
    s,v = current(p)
    name=f"v{int(s['version'][1:])+1:03d}"
    new=p/name
    if new.exists():
        raise ValueError('新版本已存在，保留现场')
    new.mkdir()
    for f in ['script.md','shotlist.yaml','sources.md','assets.json']:
        shutil.copy2(v/f,new/f)
    shutil.copytree(v/'assets',new/'assets')
    (new/'project').mkdir()
    s.update(status='script',version=name,review=None,author_approval=None,publication=None)
    s['history'].append(dict(status='script',version=name,time=now(),reason='revision'))
    save(p/'state.json',s)
    return new


def asset(p, source, rights):
    s,v=current(p)
    if (v/'manifest.json').exists() or not rights.strip():
        raise ValueError('导出后需新建版本，且必须记录合法素材权利')
    src=Path(source).resolve()
    if not src.is_file():
        raise ValueError('素材不存在')
    target=v/'assets'/src.name
    if target.exists():
        raise ValueError('素材同名冲突，不覆盖')
    before=digest(src)
    shutil.copy2(src,target)
    if digest(target)!=before:
        raise ValueError('复制哈希不一致')
    records=json.loads((v/'assets.json').read_text())
    records.append(dict(path=str(target.relative_to(v)),sha256=before,rights=rights,imported_at=now()))
    save(v/'assets.json',records)


def run(args, cwd=None):
    subprocess.run([str(x) for x in args],check=True,cwd=cwd)


def probe(f):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]))


def stamp(t):
    ms=round(t*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def cover(v,d,demo):
    if d.get('style') in ['qemu-cinematic','pcb-lab']:
        run(['ffmpeg','-hide_banner','-loglevel','error','-n','-ss','4.8','-i',v/'project/base.mp4','-frames:v','1',v/'thumbnail.png'])
        return
    width,height=d.get('width',1080),d.get('height',1920)
    im=Image.new('RGB',(width,height),'#0b1424')
    draw=ImageDraw.Draw(im)
    font='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
    def text(x,y,t,size,color):
        draw.text((x,y),t,font=ImageFont.truetype(font,size),fill=color)
    if width>height:
        draw.rounded_rectangle((1120,170,1820,900),radius=38,fill='#14263e',outline='#295375',width=2)
        text(100,115,d.get('cover_kicker',TYPES[d['kind']]),34,'#67e8dc')
        lines=d.get('cover_lines',[d['title'][i:i+8] for i in range(0,len(d['title']),8)])
        for i,t in enumerate(lines):text(100,290+i*142,t,108,'#f3f7fd')
        text(100,675,d.get('cover_payoff','一个判断，完整解释'),44,'#a0b5cd')
        for i,t in enumerate(d.get('cover_categories',['核心判断','过程证据','执行步骤'])):
            y=290+i*190
            draw.rounded_rectangle((1190,y,1750,y+130),radius=22,fill='#1a334d')
            draw.ellipse((1225,y+44,1265,y+84),fill=['#ff7d82','#67e8dc','#ffc86d'][i%3])
            text(1300,y+34,t,48,'#f3f7fd')
        if demo:text(100,930,'原创动画测试作品 · 系统合成配音 · 待作者确认',28,'#7f99b6')
        im.save(v/'thumbnail.png');return
    text(80,200,d.get('cover_kicker',TYPES[d['kind']]),38,'#66d9ef')
    lines=d.get('cover_lines',[d['title'][i:i+9] for i in range(0,len(d['title']),9)])
    for i,t in enumerate(lines):
        text(80,440+i*130,t,88,'#ffffff')
    draw.rounded_rectangle((80,950,920,1230),radius=32,fill='#162b43')
    text(120,995,d.get('cover_summary','一条视频，一个核心判断'),46,'#66d9ef')
    text(120,1110,d.get('cover_payoff','完整解释与可执行步骤'),42,'#ffffff')
    if demo:
        text(80,1450,'技术动画测试作品 · 待作者确认',32,'#a0b5cd')
    im.save(v/'thumbnail.png')


def build(p):
    s,v=current(p)
    if (v/'manifest.json').exists():
        verify(v)
        if s['status']=='editing':transition(p,'review')
        if s['status']=='ready_publish':verify_review(s,v)
        return v
    d=plan(v); original=inputs(v)
    progress=v/'project/build-inputs.json'
    if progress.exists() and json.loads(progress.read_text())!=original:
        raise ValueError('未完成制作的源文件已变；请revise保留现场')
    save(progress,original)
    if s['status']=='idea': transition(p,'script')
    if current(p)[0]['status']=='script': transition(p,'shooting')
    if current(p)[0]['status']=='shooting': transition(p,'editing')
    project=v/'project'; project.mkdir(exist_ok=True)
    (v/'subtitle.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(d['cues']))+'\n')
    def ass_time(t):
        return f'{int(t)//3600}:{int(t)//60%60:02}:{int(t)%60:02}.{round(t%1*100):02}'
    ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,WenQuanYi Zen Hei,52,&H00FFFFFF,&H00FFFFFF,&H00101420,&H00101420,0,0,0,0,100,100,0,0,1,3,0,2,100,140,350,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    width,height=d.get('width',1080),d.get('height',1920)
    ass=ass.replace('PlayResX: 1080',f'PlayResX: {width}').replace('PlayResY: 1920',f'PlayResY: {height}')
    if width>height:ass=ass.replace('100,140,350,1','100,140,120,1')
    for c in d['cues']:
        line=c['text'].replace('{','').replace('}','').replace('\n',r'\N')
        ass+=f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Default,,0,0,0,,{line}\n"
    (project/'subtitle.ass').write_text(ass)
    props={**d,'demo':s['demo']}
    save(project/'props.json',props)
    shutil.copy2(ROOT/'templates/composition.jsx',project/'composition.jsx')
    shutil.copy2(ROOT/'templates/diagrams.jsx',project/'diagrams.jsx')
    shutil.copy2(ROOT/'templates/QemuExplainer.jsx',project/'QemuExplainer.jsx')
    shutil.copy2(ROOT/'templates/SpatialChip.jsx',project/'SpatialChip.jsx')
    shutil.copy2(ROOT/'templates/PcbFilm.jsx',project/'PcbFilm.jsx')
    shutil.copy2(ROOT/'templates/pcb-scene.js',project/'pcb-scene.js')
    run([sys.executable,ROOT/'scripts/narrate.py',v])
    if not (project/'base.mp4').exists():
        run(['node',ROOT/'scripts/render.mjs',v])
    # Caption filter is the last visual transform; base has all animations.
    if not (v/'final.mp4').exists():
        run(['ffmpeg','-hide_banner','-loglevel','error','-n','-i',project/'base.mp4','-i',project/'voice.wav','-vf','subtitles=project/subtitle.ass','-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-t',str(d['duration']),'-movflags','+faststart',v/'final.mp4'],cwd=v)
    cover(v,d,s['demo'])
    run([sys.executable,ROOT/'scripts/jianying.py',v])
    save(v/'publish.json',dict(platform='douyin',title=d['title'],description=d.get('description',''),hashtags=d.get('hashtags',[]),video='final.mp4',cover='thumbnail.png',subtitles='subtitle.srt',demo=s['demo'],author_confirmed=False,publish_authorized=False,auto_publish=False,publication=None,ai_disclosure=('程序动画与原创合成配乐，无人声；含授权开源板卡模型，教学实验不作工程验收；发布时核对平台AI声明' if d.get('voice')=='synth_score' else '原创程序动画、Windows系统合成配音；发布时核对平台AI声明'),commercial_relationship='待作者确认',sources='sources.md',version=s['version']))
    if inputs(v)!=original:
        raise ValueError('制作期间源文件变化；保留结果并新建版本')
    outputs={str(f.relative_to(v)):digest(f) for f in v.rglob('*') if f.is_file() and f.name not in ['manifest.json'] and not f.relative_to(v).parts[0]=='assets'}
    save(v/'manifest.json',dict(created_at=now(),inputs=original,outputs=outputs,engine='Remotion 4.0.534 + FFmpeg',version=s['version']))
    transition(p,'review')
    return v


def verify(v):
    m=json.loads((v/'manifest.json').read_text())
    if inputs(v)!=m['inputs']:
        raise ValueError('源文件已变，旧审核失效；请revise后制作')
    for name,h in m['outputs'].items():
        if not (v/name).is_file() or digest(v/name)!=h:
            raise ValueError('导出被修改或缺失：'+name)
    for name in REQUIRED:
        f=v/name
        if not f.exists() or f.is_file() and f.stat().st_size==0:
            raise ValueError('交付缺失：'+name)
    return m


def verify_review(s,v):
    q=json.loads((v/'quality.json').read_text());r=s.get('review')
    if not q.get('pass') or not all(q.get('checks',{}).values()) or not r or r.get('inputs')!=inputs(v) or q.get('inputs')!=inputs(v):
        raise ValueError('需要本版本自动检查及实质审核通过')
    if r.get('quality_hash')!=digest(v/'quality.json') or r.get('manifest_hash')!=digest(v/'manifest.json'):
        raise ValueError('质量记录或交付清单已变化；旧审核失效')
    return q


def caption_edge_ink(im, reference=None):
    width,height=im.size
    top=height-(120 if width>height else 350)-90
    bottom=height-(120 if width>height else 350)+30
    for box in [(0,top,80,bottom),(width-120,top,width,bottom)]:
        pixels=im.crop(box).convert('RGB').getdata()
        if reference is None:
            if any(min(pixel)>220 for pixel in pixels):return True
        else:
            base=reference.crop(box).convert('RGB').getdata()
            if any(min(pixel)>220 and max(abs(a-b) for a,b in zip(pixel,original))>=24 for pixel,original in zip(pixels,base)):
                return True
    return False


def audit(p):
    s,v=current(p); verify(v)
    if s['status']=='ready_publish':
        return verify_review(s,v)
    d=plan(v)
    evidence=v/'evidence'; evidence.mkdir(exist_ok=True)
    info=probe(v/'final.mp4'); save(evidence/'ffprobe.json',info)
    proc=subprocess.run(['ffmpeg','-hide_banner','-i',str(v/'final.mp4'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    audio=json.loads(proc.stderr[proc.stderr.rfind('{'):])
    save(evidence/'audio.json',audio)
    video=next(x for x in info['streams'] if x['codec_type']=='video')
    width,height=d.get('width',1080),d.get('height',1920)
    frames=[]; caption_overflow=[]; background_candidates=[]
    sample_times=sorted(set([0.5,2.5,d['duration']-1]+[c['start']+.6 for c in d['scenes']]+[max(0,c['start']-.05) for c in d['scenes'][1:]]+[c['start']+.5 for c in d['cues']]))
    for i,t in enumerate(sample_times):
        target=evidence/f'frame-{i:02}.png'
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',v/'final.mp4','-frames:v','1',target])
        im=Image.open(target).convert('RGB')
        # Compare suspect bright pixels against the exact subtitle-free base.
        # A light background alone is not caption ink. Source footage still
        # needs the independent line-width check and substantive review.
        if d['kind']=='B' and caption_edge_ink(im):
            png=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(v/'project/base.mp4'),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
            base=Image.open(io.BytesIO(png)).convert('RGB')
            if caption_edge_ink(im,base):caption_overflow.append(t)
            else:background_candidates.append(t)
        thumb=(480,270) if width>height else (270,480)
        im.thumbnail(thumb); frames.append((t,im.copy()))
    tw,th=thumb
    sheet=Image.new('RGB',(tw*4,(th+30)*((len(frames)+3)//4)),'#ddd')
    draw=ImageDraw.Draw(sheet)
    for i,(t,im) in enumerate(frames):
        x,y=i%4*tw,i//4*(th+30); sheet.paste(im,(x,y)); draw.text((x+8,y+th),f'{t:.2f}s',fill='black')
    sheet.save(evidence/'contact-sheet.png')
    cues=d['cues']; sizes=[c['end']-c['start'] for c in d['scenes']]
    checks={
        'duration':abs(float(info['format']['duration'])-d['duration'])<=.1,
        'format':video['width']==width and video['height']==height and video['codec_name']=='h264' and video['pix_fmt']=='yuv420p' and video['r_frame_rate']=='30/1',
        'hook':cues[0]['start']<=.3 and cues[0]['end']<=3,
        'subtitle_readability':not caption_overflow and all(ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',52).getlength(line)<=width-240 for c in cues for line in c['text'].splitlines()),
        'audio':-19<=float(audio['input_i'])<=-13 and float(audio['input_tp'])<=-1,
        'pace':all(1<=x<=12 for x in sizes),
        'cover':Image.open(v/'thumbnail.png').size==(width,height),
        'title':0<len(d['title'])<=40,
        'information_density':3<=len(d['scenes'])<=20,
    }
    q=dict(pass_=all(checks.values()),checks=checks,measurements=dict(duration=info['format']['duration'],audio=audio,scene_seconds=sizes,subtitle_font_px=52,caption_overflow_times=caption_overflow,caption_background_candidates=background_candidates,subtitle_max_cps=max(len(c['text'].replace('\n',''))/(c['end']-c['start']) for c in cues)),inputs=inputs(v),limits=['信息密度、Hook和标题语义需要实质审核','音频听感未由机器测量证明；需作者试听','阈值为项目标准，不声称平台规则'])
    q['pass']=q.pop('pass_'); save(v/'quality.json',q)
    (v/'preview.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Douyin 测试片审核</title><style>body{background:#0b1424;color:white;font:18px sans-serif;max-width:1100px;margin:auto;padding:24px}video{width:100%;max-width:100%}img{max-width:100%}a{color:#66d9ef}</style><h1>'+html.escape(d['title'])+'</h1><p>测试作品 · 无发布授权 · 请按正常速度试听</p><video controls src="final.mp4" poster="thumbnail.png"></video><p><a href="script.md">脚本</a> · <a href="publish.json">发布字段</a> · <a href="quality.json">实测质量</a></p><img src="evidence/contact-sheet.png" alt="实际成片采样">')
    return q


def review(p, document, author_note=None):
    s,v=current(p); verify(v)
    if s['status']!='review':
        raise ValueError('仅review状态可提交本版本审核')
    q=json.loads((v/'quality.json').read_text())
    if not q['pass'] or q['inputs']!=inputs(v):
        raise ValueError('当前版本自动检查未通过')
    fields=['hook','information_density','subtitle_readability','audio','pace','cover','title','facts','rights']
    r=json.loads(Path(document).read_text())
    if any(r.get(f,{}).get('verdict')!='pass' or len(r[f].get('evidence',''))<12 for f in fields):
        raise ValueError('七项质量及事实、权利必须有实质审核结论和证据')
    s['review']=dict(inputs=inputs(v),quality_hash=digest(v/'quality.json'),manifest_hash=digest(v/'manifest.json'),time=now(),reviewer=r.get('reviewer','agent'),checks=r)
    if author_note:
        s['author_approval']=dict(note=author_note,time=now(),inputs=inputs(v))
    save(v/'review.json',r); save(p/'state.json',s)
    transition(p,'ready_publish')


def package(p):
    s,v=current(p);m=verify(v)
    if s['status']!='ready_publish':raise ValueError('先完成本版本制作审核')
    verify_review(s,v)
    target=p/f"publish-{s['version']}.zip"
    if target.exists():raise ValueError('发布包已存在，保留已交付文件')
    names=set(m['outputs'])|set(m['inputs'])|{'manifest.json','review.json','quality.json','preview.html'}
    names.update(str(f.relative_to(v)) for f in (v/'evidence').glob('frame-*.png'))
    names.update({'evidence/ffprobe.json','evidence/audio.json','evidence/contact-sheet.png'})
    names.update({'evidence/windows-import.json','evidence/windows-cli-check.json'})
    files=sorted(name for name in names if (v/name).is_file() and '.private' not in Path(name).parts)
    tmp=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for name in files:
            if (v/name).is_symlink():raise ValueError('发布包拒绝符号链接')
            z.write(v/name,f'{v.name}/{name}')
        z.writestr('README.txt','横屏技术动画测试发布包。final.mp4为成片，thumbnail.png为封面，subtitle.srt为字幕，project/为可编辑工程与重建源。未授权发布；作者需正常速度试听并确认终稿。清单哈希在manifest.json，QA与实质审核分别在quality.json和review.json。剪映SDK工程已生成；Windows应用打开/导出结果以独立证据为准。\n')
        if m.get('engine'):
            for report in ['opus55-research.md','opus55-visual-study-20261012.md']:
                if (ROOT/'docs'/report).exists():z.write(ROOT/'docs'/report,'docs/'+report)
        z.write(p/'state.json','state.json')
    with zipfile.ZipFile(tmp) as z:
        if z.testzip():raise ValueError('发布包压缩校验失败')
        for name in m['outputs']:
            if '.private' in Path(name).parts:continue
            if hashlib.sha256(z.read(f'{v.name}/{name}')).hexdigest()!=m['outputs'][name]:raise ValueError('发布包与成片清单不符')
    tmp.replace(target)
    save(p/f"package-{s['version']}.json",dict(path=target.name,sha256=digest(target),files=len(files),version=s['version'],demo=s['demo'],publish_authorized=False))
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=WORKSPACE)
    sub=parser.add_subparsers(dest='command',required=True)
    c=sub.add_parser('new'); c.add_argument('slug'); c.add_argument('--kind',choices=TYPES,required=True); c.add_argument('--title',required=True); c.add_argument('--demo',action='store_true')
    c=sub.add_parser('asset'); c.add_argument('slug'); c.add_argument('source'); c.add_argument('--rights',required=True)
    for cmd in ['build','audit','revise','status','package']:
        sub.add_parser(cmd).add_argument('slug')
    c=sub.add_parser('review'); c.add_argument('slug'); c.add_argument('document'); c.add_argument('--author-note')
    args=parser.parse_args()
    if args.command=='new': result=create(args.root,args.slug,args.kind,args.title,args.demo)
    else:
        p=task(args.root,args.slug)
        if args.command=='asset': result=asset(p,args.source,args.rights)
        elif args.command=='review': result=review(p,args.document,args.author_note)
        elif args.command=='status':
            result=current(p)[0]
            v=current(p)[1]
            if (v/'manifest.json').exists(): verify(v)
            if result['status']=='ready_publish':verify_review(result,v)
        else: result=globals()[args.command](p)
    print(json.dumps(result,ensure_ascii=False,indent=2) if isinstance(result,dict) else str(result or 'ok'))


if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,FileNotFoundError) as exc:
        print(str(exc),file=sys.stderr); sys.exit(1)
