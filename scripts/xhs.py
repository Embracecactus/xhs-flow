#!/usr/bin/env python3
"""Small local file workflow. No credentials, platform API or scheduler."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATES = ['候选', '制作中', '待审核', '待发布', '已发布', '已复盘']

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(data)
    tmp.replace(path)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def new_file(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text)

def init(root):
    for name in ['sources', 'posts', 'metrics/raw', 'metrics/test', 'metrics/real', 'reviews/test', 'reviews/real']:
        (root/name).mkdir(parents=True, exist_ok=True)
    new_file(root/'account.md', '''# 单账号档案

账号阶段：待确认（新号 / 已有号）
受众：待确认
定位：待确认，不从职业推定
当前目标：待确认
可用素材及权利：待确认；演示仅使用公开项目文档与原创排版
语气偏好：待确认
禁止公开的信息：待确认；默认不公开个人、客户、凭据信息
商业合作：待确认
平台：小红书；图文优先；人工发布
正式内容方向 / 标题 / 风格 / 终稿：待作者确认

默认关闭：账号连接、发布、互动、付费、广告与定时任务。
成本：无新增付费依赖；模型额度、设备、电力、人工成本待记录。
''')
    new_file(root/'topics.csv', 'id,topic,status,source_url,published_at,observed_at,audience_question,original_evidence,duplicate_check,risk\n')

def post_dir(root, name):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', name):
        raise ValueError('post-id 只允许小写字母、数字、连字符')
    p = root/'posts'/name
    if p.is_symlink():
        raise ValueError('不接受符号链接笔记目录')
    return p

def create(root, name, demo=False):
    init(root)
    p=post_dir(root,name)
    if p.exists():
        return p  # never regenerate or reset an existing post
    p.mkdir()
    (p/'editable').mkdir()
    (p/'publish').mkdir()
    for f, body in {'brief.md':'# 简报\n\n方向、受众、证据、读者收益：待确认\n',
                    'copy.md':'# 标题待确认\n\n正文待制作\n',
                    'sources.md':'# 来源\n\n记录链接、作者、发布时间、观察时间、权利及对应论断。\n',
                    'review.md':'# 实质审核\n\n事实、版权、隐私、标题承诺、AI 标识、商业披露、手机可读性：待审核\n'}.items():
        (p/f).write_text(body)
    save(p/'state.json', {'status':'制作中','demo':demo,'approval':None,'publication':None})
    return p

def inputs(p):
    files = [p/x for x in ['brief.md','copy.md','sources.md']]
    files += sorted((p/'editable').rglob('*'))
    result={}
    for f in files:
        if f.is_symlink():
            raise ValueError('源文件不能为符号链接')
        if f.is_file():
            if not f.stat().st_size:
                raise ValueError('空文件: '+f.name)
            result[str(f.relative_to(p))]=digest(f)
    if 'editable/index.html' not in result:
        raise ValueError('缺少 editable/index.html')
    return result

def fingerprint(files):
    return hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()

def verify_package(v):
    m=json.loads((v/'manifest.json').read_text())
    for name, h in m['outputs'].items():
        if not (v/name).is_file() or digest(v/name)!=h:
            raise ValueError('导出被修改或丢失: '+name+'；保留现场，手动恢复旧文件或创建新版本')
    return m

def render(root,name,note):
    p=post_dir(root,name)
    original=inputs(p)
    key=fingerprint(original)
    state=json.loads((p/'state.json').read_text())
    versions=sorted((p/'publish').glob('v[0-9][0-9][0-9]'))
    if versions:
        latest=verify_package(versions[-1])
        if latest['input_hash']==key:
            return versions[-1]
    if state['status'] in ['已发布','已复盘']:
        raise ValueError('已发布内容须另建修订笔记，不覆盖发布记录')
    version=f'v{len(versions)+1:03d}'
    staging=Path(tempfile.mkdtemp(prefix='.render-',dir=p))
    try:
        shutil.copytree(p/'editable',staging/'editable')
        for f in ['brief.md','copy.md','sources.md','review.md']:
            shutil.copy2(p/f,staging/f)
        subprocess.run(['node',str(REPO/'scripts/render.mjs'),str(staging/'editable/index.html'),str(staging)],check=True)
        if inputs(p)!=original:
            raise ValueError('导出期间源文件发生变化，请重试')
        outputs={str(f.relative_to(staging)):digest(f) for f in sorted(staging.rglob('*')) if f.is_file()}
        save(staging/'manifest.json',{'version':version,'created_at':now(),'note':note,
             'input_hash':key,'inputs':original,'outputs':outputs,'demo':state['demo']})
        target=p/'publish'/version
        staging.rename(target)
        state.update(status='待审核',approval=None,version=version,input_hash=key)
        save(p/'state.json',state)
        return target
    finally:
        if staging.exists(): shutil.rmtree(staging)

def approve(root,name,note):
    p=post_dir(root,name)
    s=json.loads((p/'state.json').read_text())
    if s['demo']:
        raise ValueError('演示包不能批准为正式发布稿；确认账号后另建正式笔记')
    if s['status']!='待审核' or not note.strip():
        raise ValueError('需要待审核版本及作者实质审核记录')
    m=verify_package(p/'publish'/s['version'])
    if fingerprint(inputs(p))!=m['input_hash']:
        raise ValueError('源文件已修改，须重新导出和审核')
    s.update(status='待发布',approval={'note':note,'time':now(),'input_hash':m['input_hash']})
    save(p/'state.json',s)

def published(root,name,url,confirmation):
    p=post_dir(root,name)
    s=json.loads((p/'state.json').read_text())
    if s['status']!='待发布' or not s.get('approval'):
        raise ValueError('尚未完成实质审核')
    verify_package(p/'publish'/s['version'])
    if s['approval']['input_hash']!=fingerprint(inputs(p)):
        raise ValueError('审核后源文件已变更')
    if not confirmation.strip() and not re.fullmatch(r'https://(?:www\.)?(?:xiaohongshu\.com|xhslink\.com)/[^\s]+',url):
        raise ValueError('需要真实发布链接或用户明确发布确认')
    s.update(status='已发布',publication={'url':url,'confirmation':confirmation,'time':now()})
    save(p/'state.json',s)

def reviewed(root,name,report,note):
    p=post_dir(root,name)
    s=json.loads((p/'state.json').read_text())
    report=report.resolve()
    if s['status']!='已发布' or not note.strip():
        raise ValueError('只有已发布内容可完成实质复盘，需填写复盘说明')
    if report.parent!=(root/'reviews/real').resolve() or not report.is_file():
        raise ValueError('需要本工作区真实数据复盘报告')
    data=json.loads((root/'metrics/real'/report.stem/'normalized.json').read_text())
    if data['kind']!='real' or not any(r['post_id']==name for r in data['rows']):
        raise ValueError('复盘数据未包含该笔记')
    s.update(status='已复盘',review={'path':str(report.relative_to(root)),'sha256':digest(report),'note':note,'time':now()})
    save(p/'state.json',s)

FIELDS=['dataset_kind','post_id','account_id','platform','content_type','published_at','observed_at','exported_at','window_hours','paid','commercial','source','unit','basis','reads','saves','followers','impressions','likes']

def date(s):
    d=datetime.fromisoformat(s)
    if d.tzinfo is None: raise ValueError('时间必须含时区')
    return d

def analyze(source,root,kind):
    raw=source.read_bytes()
    rows=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    if not rows: raise ValueError('空数据')
    if set(rows[0])!=set(FIELDS): raise ValueError('CSV 字段不匹配；参见 examples/metrics-test.csv')
    seen=set(); normalized=[]
    for r in rows:
        if r['dataset_kind']!=kind:
            raise ValueError('数据集 test/real 标记与导入目标不一致')
        for field in FIELDS[:-5]:
            if not r[field].strip(): raise ValueError('缺少口径字段: '+field)
        if r['paid'] not in ['yes','no','unknown'] or r['commercial'] not in ['yes','no','unknown']:
            raise ValueError('paid/commercial 必须为 yes/no/unknown')
        window=float(r['window_hours'])
        if not (0 < window < 100000): raise ValueError('观察窗口异常')
        if abs((date(r['observed_at'])-date(r['published_at'])).total_seconds()/3600-window)>0.01:
            raise ValueError('实际观察时间与发布后窗口不符')
        if date(r['exported_at'])<date(r['observed_at']): raise ValueError('导出时间早于观察时间')
        identity=(r['account_id'],r['post_id'],r['window_hours'])
        if identity in seen: raise ValueError('同篇同窗口重复数据')
        seen.add(identity)
        for f in FIELDS[-5:]:
            if r[f]=='': r[f]=None
            elif not re.fullmatch(r'\d+',r[f]): raise ValueError('指标必须为非负整数或空白: '+f)
            else: r[f]=int(r[f])
        compatible=r['unit']=='count' and r['basis']=='same-post-window'
        for numerator,label in [('saves','save_read_ratio'),('followers','follow_read_ratio')]:
            r[label]=r[numerator]/r['reads'] if compatible and r['reads'] and r[numerator] is not None else None
        # No CTR: raw reads are not necessarily clicks.
        normalized.append(r)
    key=hashlib.sha256(raw).hexdigest()[:16]
    dest=root/'metrics'/kind/key
    if dest.exists():
        if (dest/'raw.csv').read_bytes()!=raw: raise ValueError('导入摘要冲突')
        return dest
    dest.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.import-',dir=dest.parent))
    try:
        (stage/'raw.csv').write_bytes(raw)
        save(stage/'normalized.json',{'kind':kind,'source_sha256':hashlib.sha256(raw).hexdigest(),'rows':normalized})
        groups={}
        for r in normalized:
            g=tuple(r[f] for f in ['account_id','platform','content_type','window_hours','paid','commercial','unit','basis'])
            groups.setdefault(g,[]).append(r)
        lines=['# '+('测试样例，非账号经营结果' if kind=='test' else '真实数据复盘（依赖导入口径的人工确认）'),'',
               '## 观察事实','缺失值为 null；未计算点击率。仅同账号、平台、类型、窗口、推广、商单及口径同组比较。','']
        for g,rs in groups.items():
            lines+=['### '+' / '.join(g),f'样本数：{len(rs)}','']
            for r in rs:
                fmt=lambda v:'缺失/口径不兼容' if v is None else f'{v:.2%}'
                lines.append(f"- {r['post_id']}：阅读={r['reads']}；收藏/阅读={fmt(r['save_read_ratio'])}；涨粉/阅读={fmt(r['follow_read_ratio'])}")
        lines+=['','## 可能解释','收藏比例差异可能与步骤的可复用程度有关；目前仅为待验证解释。',
                '','## 其他解释','推荐流量、发布时间、账号阶段、付费推广及读者构成均可能影响结果。缺失字段也影响比较。',
                '','## 下一轮一个实验','待作者选择正式方向后，仅改变末页是否增加可执行清单；保持同栏目与相同发布后窗口。记录实际阅读和收藏；无兼容分母不比较。成功标准是获得可比记录，不预设增长承诺。',
                '','样本不足，只作方向性信号，不宣称因果，不自动更改账号策略或生成已批准内容。']
        (stage/'review.md').write_text('\n'.join(lines)+'\n')
        stage.rename(dest)
    finally:
        if stage.exists(): shutil.rmtree(stage)
    new_file(root/'reviews'/kind/(key+'.md'),(dest/'review.md').read_text())
    return dest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,default=REPO/'xhs-workspace')
    sub=parser.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init')
    for c in ['new','render','approve','published','reviewed']:
        p=sub.add_parser(c);p.add_argument('post_id')
        if c=='new':p.add_argument('--demo',action='store_true')
        if c in ['render','approve','reviewed']:p.add_argument('--note',required=True)
        if c=='reviewed':p.add_argument('--report',type=Path,required=True)
        if c=='published':
            p.add_argument('--url',default='');p.add_argument('--confirmation',default='')
    p=sub.add_parser('metrics');p.add_argument('csv',type=Path);p.add_argument('--kind',choices=['test','real'],required=True)
    a=parser.parse_args();root=a.workspace.resolve()
    try:
        if a.cmd=='init':init(root);result=root
        elif a.cmd=='new':result=create(root,a.post_id,a.demo)
        elif a.cmd=='render':result=render(root,a.post_id,a.note)
        elif a.cmd=='approve':result=approve(root,a.post_id,a.note)
        elif a.cmd=='published':result=published(root,a.post_id,a.url,a.confirmation)
        elif a.cmd=='reviewed':result=reviewed(root,a.post_id,a.report,a.note)
        else:result=analyze(a.csv,root,a.kind)
        print(result or '已记录；未执行平台操作')
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        parser.exit(1,str(e)+'\n')

if __name__=='__main__': main()
