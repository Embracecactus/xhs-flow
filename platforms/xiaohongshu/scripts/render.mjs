// Local-only renderer: no account connection or external network requests.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import {chromium,executablePath} from './browser.mjs';

const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('usage: node platforms/xiaohongshu/scripts/render.mjs index.html output-dir');
await fs.mkdir(output, {recursive:true});
const browser = await chromium.launch({headless:true, executablePath});
try {
  const page = await browser.newPage({viewport:{width:1200,height:1600},deviceScaleFactor:1});
  await page.route(/https?:\/\//, route => route.abort());
  await page.goto(pathToFileURL(path.resolve(input)).href);
  await page.evaluate(() => document.fonts.ready);
  const frames = page.locator('section.poster');
  const count = await frames.count();
  if (!count) throw new Error('No poster frames');
  const checks = [];
  for (let i=0;i<count;i++) {
    const frame=frames.nth(i);
    const check=await frame.evaluate(el=>{
      const r=el.getBoundingClientRect();
      const bad=[...el.querySelectorAll('*')].filter(n=>{
        const b=n.getBoundingClientRect();
        return b.width && b.height && (b.left<r.left-1 || b.right>r.right+1 || b.top<r.top-1 || b.bottom>r.bottom+1);
      }).map(n=>n.tagName+'.'+n.className);
      return {width:r.width,height:r.height,overflow:bad};
    });
    checks.push(check);
    if(check.width!==1080 || check.height!==1440 || check.overflow.length) throw new Error(JSON.stringify(check));
    await frame.screenshot({path:path.join(output,`${String(i+1).padStart(2,'0')}.png`)});
  }
  const thumbs=Array.from({length:count},(_,i)=>`<img alt="第 ${i+1} 张" src="${String(i+1).padStart(2,'0')}.png">`).join('');
  await fs.writeFile(path.join(output,'preview.html'),`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>待作者审核 · 手机预览</title><style>body{margin:0;background:#ddd;font:16px sans-serif}p{padding:12px}main{display:flex;flex-wrap:wrap;gap:16px}img{width:360px;max-width:100%;height:auto}</style><p>待作者审核 · 每张 360px 宽预览 · 按 01 至 ${count} 顺序</p><main>${thumbs}</main></html>`);
  await page.setViewportSize({width:1120,height:1100});
  await page.goto(pathToFileURL(path.resolve(output,'preview.html')).href);
  await page.screenshot({path:path.join(output,'contact-sheet.png'),fullPage:true});
  await fs.writeFile(path.join(output,'layout-check.json'),JSON.stringify({count,checks,network:'blocked',browser:browser.version()},null,2));
} finally {await browser.close();}
