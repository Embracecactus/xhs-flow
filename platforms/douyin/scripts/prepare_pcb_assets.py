#!/usr/bin/env python3
"""Fetch only pinned Apache-2.0 assets needed for the PCB film; never account APIs.
Run after reviewing both upstream licenses. Research tree snapshots live in .cache.
"""
import concurrent.futures
import hashlib
import json
import posixpath
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

PLATFORM = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
CACHE = REPO/'.cache/pcb-reference'
BOARD_SHA = '1c787f6b8bb91cfc65c87a11866b2d13cb3f11a0'
COMP_SHA = 'b645af2b1aefe7b08b1a33d9fde1e4f9f1809349'


def git_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def prepare(v):
    assets = v/'assets'
    if (v/'manifest.json').exists():
        raise ValueError('Reviewed/exported version is immutable; revise first')
    board = {e['path']:e for e in json.loads((CACHE/'tree.json').read_text())['tree']}
    comps = {'gltf-models/'+e['path']:e for e in json.loads((CACHE/'gltf-models-tree.json').read_text())['tree']}
    records = {}
    def fetch(repo, sha, remote, local, tree):
        dst = assets/local
        url = f'https://raw.githubusercontent.com/antmicro/{repo}/{sha}/'+urllib.parse.quote(remote)
        expected = tree.get(remote, {}).get('sha')
        if dst.exists():
            data = dst.read_bytes()
        else:
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(url, timeout=100) as r:
                        data = r.read()
                    break
                except Exception:
                    if attempt == 2: raise
                    time.sleep(2)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
        if expected and git_hash(data) != expected:
            raise ValueError('Pinned Git blob mismatch: '+remote)
        records[str(Path(local))] = dict(path=str(Path('assets')/local), sha256=hashlib.sha256(data).hexdigest(), rights=f'Apache-2.0; Antmicro; source unmodified; license retained. {url}', source=url, git_blob=expected)
        return data
    jobs=[]
    for remote,e in board.items():
        if e['type']=='blob' and remote.startswith('assets/gltf/'):
            jobs.append(('polarfire-som',BOARD_SHA,remote,'board/'+Path(remote).name,board))
    for name in ['LICENSE','README.md','assets/stackup.csv']:
        jobs.append(('polarfire-som',BOARD_SHA,name,'licenses/board-'+Path(name).name,board))
    # The large CAD source was read-only fetched during research; pin it too.
    src=CACHE/'polarfire-som.kicad_pcb'; dst=assets/'board/polarfire-som.kicad_pcb';dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(src,dst)
    fetch('polarfire-som',BOARD_SHA,src.name,'board/'+src.name,board)
    jobs.append(('hardware-components',COMP_SHA,'LICENSE','licenses/components-LICENSE',{}))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda x:fetch(*x),jobs))
    selected=json.loads((CACHE/'model-selection.json').read_text())
    # These two legacy component IDs no longer exist in the pinned library.
    # Substitute an explicitly documented same-size visual package, NOT a BOM claim.
    selected['bourns-cr0402-fx-50r0glf']=selected['bourns-cr0402-fx-1003glf']
    selected['tdk-c1005x5r1e474m050bb']=selected['murata-grm155r61h104ke14d']
    model_paths=sorted(set(selected.values()))
    def get_model(remote):
        path='gltf-models/'+remote
        raw=fetch('hardware-components',COMP_SHA,path,'models/'+remote,comps)
        d=json.loads(raw)
        deps={x['uri'] for k in ['buffers','images'] for x in d.get(k,[]) if 'uri' in x and not x['uri'].startswith('data:')}
        for uri in sorted(deps):
            dep=posixpath.normpath(posixpath.join(posixpath.dirname(path),uri))
            if not dep.startswith('gltf-models/'):raise ValueError('Unexpected model dependency')
            fetch('hardware-components',COMP_SHA,dep,'models/'+dep.removeprefix('gltf-models/'),comps)
        return remote
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for i,p in enumerate(ex.map(get_model,model_paths),1):print(f'Model {i}/{len(model_paths)} {Path(p).name}',flush=True)
    mapping={'models':{a:'models/'+p for a,p in selected.items()},'substitutions':{'bourns-cr0402-fx-50r0glf':'bourns-cr0402-fx-1003glf visual package','tdk-c1005x5r1e474m050bb':'murata-grm155r61h104ke14d visual package'},'board_commit':BOARD_SHA,'components_commit':COMP_SHA}
    target=assets/'model-index.json';target.write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
    records['model-index.json']=dict(path='assets/model-index.json',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),rights='Original mapping; identifies two visual package substitutions; no electrical/BOM changes claimed.')
    # KTX2 transcoders are MIT-licensed three.js dependencies. They stay local.
    basis=PLATFORM/'node_modules/three/examples/jsm/libs/basis'
    for name in ['basis_transcoder.js','basis_transcoder.wasm']:
        target=assets/'basis'/name;target.parent.mkdir(exist_ok=True);shutil.copy2(basis/name,target)
        records['basis/'+name]=dict(path='assets/basis/'+name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),rights='Three.js r180 bundled Basis Universal transcoder; Apache-2.0, license header retained; see licenses/three-LICENSE.')
    target=assets/'licenses/three-LICENSE';shutil.copy2(PLATFORM/'node_modules/three/LICENSE',target)
    records['three-license']=dict(path='assets/licenses/three-LICENSE',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),rights='Three.js MIT license text, unmodified.')
    (v/'assets.json').write_text(json.dumps(sorted(records.values(),key=lambda r:r['path']),ensure_ascii=False,indent=2)+'\n')
    print(f'Registered {len(records)} files; {len(model_paths)} shared models; no reference-video media imported.')


if __name__=='__main__':prepare(Path(sys.argv[1]).resolve())
