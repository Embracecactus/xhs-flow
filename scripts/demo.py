#!/usr/bin/env python3
"""Install the public demo only once. Never overwrite user edits."""
import shutil
from xhs import REPO, init, save
root=REPO/'xhs-workspace'
init(root)
target=root/'posts/demo-source-notes'
if target.exists():
    print('已有演示，保持全部文件不变：',target)
else:
    shutil.copytree(REPO/'examples/demo-source-notes',target)
    (target/'publish').mkdir()
    save(target/'state.json',{'status':'制作中','demo':True,'approval':None,'publication':None})
    print(target)
