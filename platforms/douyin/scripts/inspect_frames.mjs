import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderStill} from '@remotion/renderer';

const version=path.resolve(process.argv[2]);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const props=JSON.parse(fs.readFileSync(path.join(version,'project/props.json')));
const repo=path.resolve(root,'../..');
const browserExecutable=JSON.parse(fs.readFileSync(path.join(repo,'.cache/browser.json'))).executablePath;
const out=path.join(version,'evidence',process.argv[3]||'preflight');
fs.mkdirSync(out,{recursive:true});
const serveUrl=await bundle({entryPoint:path.join(root,'templates/composition.jsx'),publicDir:path.join(version,'assets'),outDir:path.join(out,'bundle')});
const composition=await selectComposition({serveUrl,id:'DouyinVideo',inputProps:props,browserExecutable});
const browser=await openBrowser('chrome',{browserExecutable});
const samples=[];
try {
  for(const [i,scene] of props.scenes.entries()) {
    for(const [stage,t] of [['start',scene.start+.75],['mid',(scene.start+scene.end)/2],['end',scene.end-.35]]) {
      const file=`scene-${String(i+1).padStart(2,'0')}-${stage}.png`;
      await renderStill({composition,serveUrl,inputProps:props,browserExecutable,puppeteerInstance:browser,frame:Math.round(t*composition.fps),output:path.join(out,file),imageFormat:'png',overwrite:false});
      samples.push({scene:i+1,stage,time:t,file});
    }
    console.log(`Beat ${i+1} / ${props.scenes.length}`);
  }
} finally {await browser.close({silent:true});}
fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify(samples,null,2));
