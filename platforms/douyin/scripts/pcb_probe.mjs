import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill} from '@remotion/renderer';
const v=path.resolve(process.argv[2]);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const repo=path.resolve(root,'../..');
const out=path.join(v,'evidence',process.argv[3]||'pcb-probe');fs.mkdirSync(out,{recursive:true});
const inputProps=JSON.parse(fs.readFileSync(path.join(v,'project/props.json')));
const browserExecutable=JSON.parse(fs.readFileSync(path.join(repo,'.cache/browser.json'))).executablePath;
const serveUrl=await bundle({entryPoint:path.join(root,'templates/composition.jsx'),publicDir:path.join(v,'assets'),outDir:path.join(out,'bundle')});
const chromiumOptions={gl:'swangle'};
const browser=await openBrowser('chrome',{browserExecutable,chromiumOptions});
try {
 const composition=await selectComposition({serveUrl,id:'DouyinVideo',inputProps,browserExecutable,puppeteerInstance:browser,chromiumOptions,timeoutInMilliseconds:180000});
 for(const t of (process.argv.slice(4).length?process.argv.slice(4).map(Number):[4,19,30,41,52,62,70,77,86])) {
  const output=path.join(out,`frame-${t.toFixed(1)}.png`);
  console.log('rendering',t);
  await renderStill({serveUrl,composition,inputProps,browserExecutable,puppeteerInstance:browser,chromiumOptions,timeoutInMilliseconds:180000,frame:Math.round(t*30),output,imageFormat:'png',overwrite:true,onBrowserLog:log=>{if(log.type==='error')console.error(log.text);}});
  console.log('wrote',output);
 }
} finally {await browser.close({silent:true});}
