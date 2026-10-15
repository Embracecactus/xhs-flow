import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {AbsoluteFill,useCurrentFrame,useVideoConfig,staticFile,delayRender,continueRender,cancelRender} from 'remotion';
import {createPcbScene,clamp,ease} from './pcb-scene.js';

const titles=[
 [0,7,'14 层，藏在这里。','01 / 先看成品'],
 [7,14,'把它拆开，再长回来。','02 / 分配任务'],
 [14,25,'每个器件，各就各位。','03 / 逐件装配'],
 [25,35,'走线，开始显形。','04 / 铜线重绘'],
 [35,47,'往里看，还有十三层。','05 / 叠层展开'],
 [47,57,'线路也会“换楼层”。','06 / 跨层连接'],
 [57,67,'热，怎样扩散出去？','07 / 数值小实验'],
 [67,74,'把看不见的运动放大。','08 / 振型示意'],
 [74,81,'漂亮之外，还要核对。','09 / 工程边界'],
 [81,90,'合起来，才这么薄。','10 / 回到成品'],
];
const palette=['#f0b568','#78c9c2','#95b2f0','#d99bc2','#b8cb79','#df9677','#99c1d7','#c7adf0'];
const Pill=({children,color='#c2d0df',style={}})=><span style={{display:'inline-block',padding:'9px 16px',border:'1px solid #8392a244',borderRadius:8,background:'#101924de',fontSize:24,color,...style}}>{children}</span>;

export function PcbFilm({props}){
 const f=useCurrentFrame();const {fps,width,height}=useVideoConfig();const t=f/fps;const canvas=useRef();const runtime=useRef();const [stats,setStats]=useState(null);const [hold]=useState(()=>delayRender('Loading licensed PCB geometry',{timeoutInMilliseconds:180000}));
 useEffect(()=>{
  let alive=true;
  createPcbScene(canvas.current,staticFile,width,height).then(r=>{if(!alive){r.dispose();return;}runtime.current=r;r.draw(t);setStats(r.stats);window.__pcbStats=r.stats;continueRender(hold);}).catch(cancelRender);
  return()=>{alive=false;runtime.current?.dispose();};
 },[]);
 useLayoutEffect(()=>{runtime.current?.draw(Math.min(t,88));},[t]);
 const shot=titles.find(([a,b])=>t>=a&&t<b)||titles.at(-1);const p=ease((t-shot[0])/.65);
 const progress=Math.round(100*ease((t-14.2)/7.6));
 return <AbsoluteFill style={{background:'#080b12',fontFamily:'"WenQuanYi Zen Hei",sans-serif',color:'#eaece8'}}>
  <AbsoluteFill style={{background:'radial-gradient(ellipse at 53% 45%,#25303a 0%,#10151e 44%,#06080e 85%)'}}/>
  <canvas ref={canvas} width={width} height={height} style={{position:'absolute',width,height,clipPath:t>=14&&t<25?'inset(220px 0 200px 0)':undefined}}/>
  <div style={{position:'absolute',left:84,top:42,color:'#a9b8c6',fontSize:21,letterSpacing:3}}>BOARD LAB <span style={{color:'#64727f',margin:'0 17px'}}> / </span> 开源工程 · 动画实验</div>
  <div style={{position:'absolute',left:82,top:92,opacity:p,transform:`translateY(${12*(1-p)}px)`}}>
   <div style={{fontSize:58,fontWeight:700,letterSpacing:1,textShadow:'0 3px 16px #0008'}}>{shot[2]}</div>
   <div style={{fontSize:23,color:'#9bb0bc',marginTop:15,letterSpacing:2}}>{shot[3]}</div>
  </div>
  <div style={{position:'absolute',right:82,top:48,display:'flex',gap:12}}><Pill color='#ecc384'>14 铜层</Pill><Pill>55 × 40 mm</Pill></div>
  {t<7&&<div style={{position:'absolute',right:92,top:780,fontSize:29,color:'#b9c3c9'}}>PolarFire SoM <span style={{color:'#748797'}}> / Antmicro</span></div>}
  {t>=7&&t<14&&<div style={{position:'absolute',left:90,top:302,width:590}}>
   <div style={{color:'#f0b568',fontSize:27,marginBottom:20}}>一项任务 / 八个动画小助手</div>
   <div style={{background:'#e2e8e2',color:'#17222a',borderRadius:'22px 22px 22px 3px',padding:'23px 28px',fontSize:36,width:475}}>今天，把这块板拆给你看。</div>
   {t>9&&<div style={{marginTop:24,marginLeft:80,background:'#293747',border:'1px solid #526575',borderRadius:'22px 22px 3px 22px',padding:'24px 28px',fontSize:36}}>这么薄，能藏十四层？</div>}
   {t>11&&<div style={{fontSize:28,color:'#8bc8bf',marginTop:30}}>负责摆件、走线、分层和检查。<br/><span style={{fontSize:22,color:'#8193a2'}}>角色分工是动画设定，不是真实多 Agent 记录。</span></div>}
  </div>}
  {t>=14&&t<25&&<div style={{position:'absolute',right:90,top:238,width:260}}>
   <div style={{fontSize:25,color:'#a8bac6'}}>贴装位置重建</div><div style={{fontSize:56,margin:'12px 0',fontFamily:'monospace'}}>406<span style={{fontSize:29,color:'#8298a5'}}> 个模型</span></div>
   <div style={{height:5,background:'#3c4b55'}}><div style={{height:5,width:`${progress}%`,background:'#9ccbbd'}}/></div>
   <div style={{fontSize:23,color:'#96a3ad',marginTop:17}}>采用原工程贴装位置<br/>动画进度 {progress}%<br/>非生产录像</div>
  </div>}
  {t>=25&&t<35&&<div style={{position:'absolute',right:86,top:220,width:265}}>
   <Pill color='#e6bc74'>已有布线 · 渐进重绘</Pill>
   <div style={{fontSize:28,marginTop:22,color:'#c5cdd3'}}>11,271 条线段</div>
   <div style={{fontSize:23,marginTop:12,color:'#91a4b3'}}>来自 PCB 源文件<br/>不是本轮自动布线结果</div>
  </div>}
  {t>=35&&t<47&&<div style={{position:'absolute',right:82,top:218,width:202}}>
    <div style={{fontSize:22,color:'#a6b7bd',marginBottom:12}}>铜层 / 间距示意放大</div>
    {Array.from({length:14},(_,i)=><div key={i} style={{height:37,display:'flex',alignItems:'center',gap:14,fontSize:23,color:'#c9d1d3'}}><span style={{width:31,height:4,background:palette[i%8]}}/>{i===0?'F.Cu':i===13?'B.Cu':`In${i}.Cu`}</div>)}
  </div>}
  {t>=47&&t<57&&<div style={{position:'absolute',right:86,top:242,width:300}}><Pill color='#eec676'>1,565 个过孔</Pill><div style={{fontSize:29,marginTop:22,lineHeight:1.65,color:'#c1cbd2'}}>一条路线，<br/>不必挤在同一层。</div><div style={{fontSize:23,marginTop:20,color:'#8fa3b1'}}>四层截取 · 孔径/间距放大<br/>光点只强调几何连接<br/>不是电流或时序仿真</div></div>}
  {t>=57&&t<74&&<div style={{position:'absolute',right:88,top:226,width:358}}>
   <Pill color='#f1ba79'>{t<67?'教学热扩散实验':'解析振型演示'}</Pill>
   <div style={{fontSize:27,lineHeight:1.65,marginTop:24,color:'#cdd4d6'}}>{t<67?<>二维有限差分<br/>假设热源 · 固定边界</>:<>正弦振型 · 归一化位移<br/>不计算该板固有频率</>}</div>
   <div style={{height:13,background:'linear-gradient(90deg,#234aa9,#3cbbad,#e4df56,#e66043)',borderRadius:5,marginTop:28}}/>
   <div style={{display:'flex',justifyContent:'space-between',fontSize:23,marginTop:8,color:'#a6b7bf'}}><span>{t<67?'0':'−1'}</span><span>{t<67?'归一化量':'位移示意'}</span><span>1</span></div>
   <div style={{fontSize:27,color:'#efbc8b',marginTop:28,lineHeight:1.6}}>非本板工程仿真结果<br/>不作为设计验收依据</div>
  </div>}
  {t>=74&&t<81&&<div style={{position:'absolute',right:86,top:242,width:510,padding:28,background:'#121c26ed',border:'1px solid #53616d',borderRadius:15}}>
   <div style={{fontSize:31,marginBottom:22}}>本次实际完成的核对</div>
   {[['14 铜层 / 源文件一致',true],['473 个 PCB 封装 / 已统计',true],['406 个贴装模型 / 已重建',true],['DRC / 未运行',false],['实板电热、模态验收 / 未进行',false]].map(([x,ok],i)=><div key={x} style={{fontSize:26,padding:'14px 0',borderTop:'1px solid #3c4955',color:ok?'#acd4c4':'#e6b68a',opacity:t>74.6+i*.45?1:.15}}>{ok?'✓':'—'}　{x}</div>)}
  </div>}
  {t>=84&&<div style={{position:'absolute',left:88,top:714,color:'#c7d1d3',fontSize:26,lineHeight:1.7,textShadow:'0 2px 10px #000'}}>
   <span style={{color:'#ecc786'}}>设计与模型：Antmicro · Apache-2.0</span><br/>本片：原创镜头、角色与合成配乐<br/><span style={{fontSize:23,color:'#91a5b3'}}>可视化改编 / 非从零设计、制造或验收记录</span>
  </div>}
  <div style={{position:'absolute',bottom:55,left:84,right:84,height:3,background:'#40505b44'}}><div style={{height:3,width:`${Math.min(100,t/90*100)}%`,background:'#98bdb9'}}/></div>
  <div style={{position:'absolute',bottom:20,left:84,right:84,fontSize:20,color:'#93a2ad',display:'flex',justifyContent:'space-between'}}><span>DEMO · 无口播 · 开源工程可视化改编</span><span>{t>=57&&t<74?'教学实验 / 非工程验收':'Antmicro PolarFire SoM · Apache-2.0'}</span></div>
 </AbsoluteFill>;
}
