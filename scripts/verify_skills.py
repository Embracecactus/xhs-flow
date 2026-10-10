#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'skills.lock.json').read_text())
count=0
for component in lock['components']:
    for name,expected in component['files'].items():
        path=root/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise SystemExit('固定版本文件不匹配：'+name)
        count+=1
print(f'已核对 {count} 个固定版本文件')
