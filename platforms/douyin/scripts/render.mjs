import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {selectComposition, renderMedia} from '@remotion/renderer';

const v=path.resolve(process.argv[2]);
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const inputProps=JSON.parse(fs.readFileSync(path.join(v,'project/props.json')));
const local=JSON.parse(fs.readFileSync(path.join(repo,'.cache/browser.json')));
const serveUrl=await bundle({entryPoint:path.join(v,'project/composition.jsx'),publicDir:path.join(v,'assets'),outDir:path.join(v,'project/remotion-bundle')});
const chromiumOptions=inputProps.style==='pcb-lab'?{gl:'swangle'}:{};
const composition=await selectComposition({serveUrl,id:'DouyinVideo',inputProps,browserExecutable:local.executablePath,chromiumOptions,timeoutInMilliseconds:180000});
const frameRange=process.argv[3]?process.argv[3].split(',').map(Number):undefined;
if(frameRange&&(frameRange.length!==2||frameRange.some(x=>!Number.isInteger(x))||frameRange[0]<0||frameRange[1]<frameRange[0]||frameRange[1]>=composition.durationInFrames))throw new Error('Invalid inclusive frame range');
const outputName=frameRange?`patch-${frameRange[0]}-${frameRange[1]}.mp4`:'base.mp4';
let last=-1;
await renderMedia({composition,serveUrl,frameRange,codec:'h264',outputLocation:path.join(v,'project',outputName),inputProps,browserExecutable:local.executablePath,chromiumOptions,timeoutInMilliseconds:180000,overwrite:false,concurrency:inputProps.style==='pcb-lab'?2:4,muted:true,crf:19,x264Preset:'fast',onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log(`Render ${p*10}%`);}}});
fs.writeFileSync(path.join(v,'project',frameRange?`render-${frameRange[0]}-${frameRange[1]}.json`:'render.json'),JSON.stringify({engine:'Remotion',version:'4.0.534',frameRange:frameRange??null,durationInFrames:frameRange?frameRange[1]-frameRange[0]+1:composition.durationInFrames,fps:composition.fps,width:composition.width,height:composition.height},null,2));
