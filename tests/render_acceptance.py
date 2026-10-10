"""Run manually with browser available; all mutations isolated to a temp workspace."""
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('xhs',Path(__file__).resolve().parents[1]/'scripts/xhs.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
with tempfile.TemporaryDirectory(prefix='xhs-acceptance-') as tmp:
    root=Path(tmp)
    p=x.create(root,'fixture')
    source=x.REPO/'examples/demo-source-notes'
    for f in source.iterdir():
        if f.is_dir():shutil.copytree(f,p/f.name,dirs_exist_ok=True)
        else:shutil.copy2(f,p/f.name)
    first=x.render(root,'fixture','测试隔离：初版')
    h=x.digest(first/'01.png')
    x.approve(root,'fixture','TEST ONLY: simulated approval, not a user confirmation')
    assert x.render(root,'fixture','重复运行')==first
    assert json.loads((p/'state.json').read_text())['status']=='待发布'
    (p/'copy.md').write_text((p/'copy.md').read_text()+'\n测试修改，不是用户反馈。\n')
    try:x.published(root,'fixture','','测试确认')
    except ValueError:pass
    else:raise AssertionError('stale approval accepted')
    html=p/'editable/index.html'
    html.write_text(html.read_text().replace('收藏资料<br>','整理资料<br>'))
    second=x.render(root,'fixture','测试隔离：修改源文件后重导出')
    assert second!=first and x.digest(first/'01.png')==h
    assert x.digest(second/'01.png')!=h
    assert json.loads((p/'state.json').read_text())['approval'] is None
    assert x.render(root,'fixture','重复重导出')==second
    (second/'01.png').write_bytes(b'corruption test')
    try:x.render(root,'fixture','损坏后禁止覆盖')
    except ValueError:pass
    else:raise AssertionError('modified export overwritten')
print('PASS: approval binding, repeat-run preservation, actual HTML revision and PNG change, old version retained, corruption detected. TEST ONLY, not author feedback acceptance.')
