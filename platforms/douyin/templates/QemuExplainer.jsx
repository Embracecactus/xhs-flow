import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {SpatialChip} from './SpatialChip.jsx';

const C={bg:'#090c12',ink:'#f2f1eb',muted:'#9ba7b7',teal:'#54ecd2',orange:'#fb9b66',line:'#293344',red:'#f28e9b',paper:'#eeeae1'};
const edges=[0,6,13,20,27,34,43,51,60];
const chapters=['没有开发板','指令与内存','寄存器访问','输出与中断','能力边界','项目证据','实机验收','先逻辑，后硬件'];
const p=(t,a,b)=>interpolate(t,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const lerp=(a,b,q)=>a+(b-a)*q;
const Text=({x=0,y=0,size=34,color=C.ink,weight=400,children,width,align='left',style={}})=><div style={{position:'absolute',left:x,top:y,width,fontSize:size,color,fontWeight:weight,lineHeight:1.18,textAlign:align,whiteSpace:'pre-line',...style}}>{children}</div>;
function Reveal({t,at,x,y,size=94,children,color=C.ink,width=1100}) {
 const q=p(t,at,at+.48);
 return <div style={{position:'absolute',left:x,top:y,width,height:size*1.3,overflow:'hidden'}}><Text size={size} color={color} weight={700} style={{transform:`translateY(${(1-q)*105}%)`,letterSpacing:-2}}>{children}</Text></div>;
}
const Label=({x,y,children,color=C.teal})=><div style={{position:'absolute',left:x,top:y,fontSize:29,color,borderLeft:`3px solid ${color}`,padding:'5px 0 5px 17px',letterSpacing:1}}>{children}</div>;
function Rail({x1,y1,x2,y2,q,color=C.teal,curve=0,ghost=true}) {
 const c1=[x1+(x2-x1)*.38,y1+curve],c2=[x1+(x2-x1)*.65,y2+curve];
 const d=`M${x1} ${y1} C${c1[0]} ${c1[1]},${c2[0]} ${c2[1]},${x2} ${y2}`;
 const k=Math.max(0,Math.min(1,q)),u=1-k;
 const px=u*u*u*x1+3*u*u*k*c1[0]+3*u*k*k*c2[0]+k*k*k*x2;
 const py=u*u*u*y1+3*u*u*k*c1[1]+3*u*k*k*c2[1]+k*k*k*y2;
 return <svg width="1920" height="865" style={{position:'absolute',left:0,top:0,pointerEvents:'none'}}>{ghost&&<path d={d} stroke={C.line} strokeWidth="3" fill="none"/>}<path d={d} stroke={color} strokeWidth="4" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-k}/><circle cx={px} cy={py} r="17" fill={color} opacity=".12"/><circle cx={px} cy={py} r="7" fill={color}/></svg>;
}
function Panel({x,y,w=315,h=172,title,detail,active=0,color=C.teal,tilt=0}) {
 return <div style={{position:'absolute',left:x,top:y,width:w,height:h,border:`1px solid ${active>.3?color+'99':'#374050'}`,borderRadius:15,background:`linear-gradient(130deg,${active>.3?color+'1c':'#1d2433'},#10141f)`,boxShadow:'0 17px 0 #050810,0 28px 35px #0006',transform:`perspective(1000px) rotateY(${tilt}deg)`,transformOrigin:'center'}}><div style={{position:'absolute',left:25,top:28,width:5,height:h-55,background:color,opacity:.3+active*.7}}/><Text x={51} y={25} size={49} weight={700}>{title}</Text><Text x={53} y={99} size={27} color={active>.3?color:C.muted}>{detail}</Text></div>;
}
function Background({t,light=false}) {
 return <><AbsoluteFill style={{background:light?C.paper:C.bg}}/><AbsoluteFill style={{background:light?'none':'radial-gradient(ellipse at 70% 53%,#172b3560,transparent 61%)'}}/><svg width="1920" height="870" style={{position:'absolute',opacity:light?.16:.45}}>{Array.from({length:17},(_,j)=><path key={j} d={`M${-350+j*125} 850 L${780+j*20} 305`} stroke={light?'#91978f':'#263144'} strokeWidth="1"/>)}{Array.from({length:8},(_,j)=><path key={j} d={`M0 ${385+j*j*9} H1920`} stroke={light?'#aaa99f':'#243040'} strokeWidth="1"/>)}</svg><div style={{position:'absolute',left:1200,top:150,width:530,height:530,border:`1px solid ${light?'#aeb5ac44':'#5da5a71a'}`,borderRadius:'50%',transform:`scale(${1+Math.sin(t*.3)*.025})`}}/></>;
}
// One geometric object stays in the same world while its camera framing changes.
const poses=[
 [0,1370,500,1.1,-.08,0,0,0],
 [2.7,1370,500,1.1,-.08,0,0,0],
 [4.5,1370,495,1.1,.05,.65,1,0],
 [6.7,1440,620,.70,.18,.38,1,0],
 [12.1,1410,620,.72,.18,.38,1,0],
 [13.8,455,600,.86,-.25,.9,1,0],
 [19.4,455,600,.86,-.14,.9,1,0],
 [20.7,400,575,.77,.03,.35,1,0],
 [26.4,400,575,.77,.11,.35,1,0],
 [27.7,495,590,.87,-.18,.5,0,.25],
 [33.4,495,590,.87,.12,.5,0,1],
 [34.8,550,560,.91,.21,.45,.25,.3],
 [42.4,550,560,.91,-.16,.45,.25,1],
 [43.8,460,580,.66,-.07,0,1,0],
 [50.4,460,580,.66,.10,0,1,0],
 [52,1410,490,1.12,.03,.15,1,0],
 [58,1410,490,1.12,-.04,0,1,0],
 [60,1410,490,1.12,-.04,0,1,0],
];
function pose(t){const k=Math.max(0,poses.findIndex((a,i)=>t>=a[0]&&t<(poses[i+1]?.[0]??61)));const a=poses[k],b=poses[Math.min(k+1,poses.length-1)],q=p(t,a[0],b[0]);return a.slice(1).map((v,i)=>lerp(v,b[i+1],q));}
function Hook({t}) {
 return <><Reveal t={t} at={0} x={105} y={183} size={109}>没插开发板，</Reveal><Reveal t={t} at={.16} x={105} y={327} size={119}>固件也能跑？</Reveal><Label x={112} y={603}>{t<2.7?'QEMU · 60秒看懂':'用软件，模拟硬件'}</Label><Text x={115} y={693} size={31} color={C.muted}>CPU / 内存 / 外设模型</Text><div style={{opacity:p(t,2.7,3.3)}}><Text x={1145} y={752} size={28} color={C.teal}>软件模型 / 概念结构</Text></div></>;
}
function Cpu({t}) {
 const a=p(t,6.5,7.7),b=p(t,7.7,9.4),m=p(t,9.6,12.4);
 return <><Reveal t={t} at={6.1} x={110} y={165} size={91}>先让指令</Reveal><Reveal t={t} at={6.2} x={110} y={278} size={91}>执行起来</Reveal><Label x={115} y={466}>CPU + 内存</Label><Text x={115} y={537} size={29} color={C.muted}>翻译指令，再按地址取数据</Text><Panel x={705} y={195} w={270} title="ARM" detail="固件指令" active={1} color={C.orange} tilt={-7}/><Panel x={1093} y={195} w={270} title="TCG" detail="指令翻译" active={a}/><Panel x={1480} y={195} w={270} title="HOST" detail="宿主执行" active={b} tilt={7}/><Rail x1={980} y1={280} x2={1075} y2={280} q={a} color={C.orange}/><Rail x1={1370} y1={280} x2={1462} y2={280} q={b}/><div style={{position:'absolute',left:780,top:477,display:'flex',gap:10,transform:'perspective(800px) rotateY(-9deg)'}}>{Array.from({length:8},(_,i)=><div key={i} style={{width:68,height:73,border:`1px solid ${m>(i+.1)/8?C.teal:'#3b4554'}`,borderRadius:7,background:m>(i+.1)/8?'#164c43':'#141b29',display:'grid',placeItems:'center',fontSize:23,color:m>(i+.1)/8?C.teal:C.muted}}>{i.toString(16).padStart(2,'0')}</div>)}</div><Text x={789} y={577} size={26} color={C.muted}>按地址提供内存 / 原理示意</Text></>;
}
function Bus({t}) {
 const a=p(t,13.6,15.8),b=p(t,16.2,17.7),r=p(t,17.8,19.4);
 return <><Reveal t={t} at={13.08} x={110} y={155} size={88}>写一个地址</Reveal><Text x={115} y={285} size={33} color={C.muted}>寄存器访问，交给外设模型</Text><Panel x={900} y={358} w={350} title="MMIO" detail="按地址路由" active={a} tilt={-6}/><Panel x={1442} y={358} w={350} title="外设模型" detail={b>.8?'寄存器已响应':'等待访问'} active={b} tilt={6}/><Rail x1={640} y1={520} x2={874} y2={444} q={a} color={C.orange} curve={-60}/><Rail x1={1265} y1={444} x2={1425} y2={444} q={b}/>{t>=17.8&&<Rail x1={1580} y1={590} x2={730} y2={735} q={r} curve={115}/>}<Label x={925} y={710}>{r>.5?'状态返回程序':'MMIO / 内存映射输入输出'}</Label></>;
}
function Response({t}) {
 const a=p(t,20.4,21.6),b=p(t,21.6,22.8),timer=p(t,23.4,25.6),irq=p(t,25.6,26.8);
 return <><Reveal t={t} at={20.08} x={110} y={145} size={88}>让外设，给出响应</Reveal><Panel x={825} y={346} w={330} title="UART" detail="写入字符 A" active={a}/><Rail x1={575} y1={480} x2={800} y2={432} q={a} color={C.orange} curve={-35}/><Rail x1={1170} y1={432} x2={1380} y2={432} q={b}/><div style={{position:'absolute',left:1402,top:322,width:385,height:228,border:'1px solid #434c58',borderRadius:12,background:'#03070c',boxShadow:'0 20px 0 #050810'}}><Text x={30} y={25} size={26} color={C.muted}>终端 / 原理示意</Text><Text x={35} y={79} size={102} color={C.teal} weight={700}>{b>.92?'A':'_'}</Text></div>{t>=23.4&&<><Text x={810} y={651} size={31} color={C.muted}>TIMER</Text><div style={{position:'absolute',left:950,top:654,width:540,height:24,border:'1px solid #9f7658',borderRadius:5,padding:3}}><div style={{height:16,width:`${timer*100}%`,background:C.orange}}/></div><Text x={1535} y={635} size={43} color={timer>.97?C.teal:C.muted} weight={700}>{timer>.97?'IRQ':'计数中'}</Text>{t>=25.6&&<Rail x1={1620} y1={707} x2={600} y2={750} q={irq} curve={85}/>}</>}</>;
}
function Boundary({t}) {
 const q=p(t,30.3,31.2);
 return <><Reveal t={t} at={27.1} x={105} y={139} size={106} color="#15222c">局部通过</Reveal><Text x={105} y={283} size={36} color="#536674">不等于整芯片支持</Text><div style={{position:'absolute',left:1000,top:368,width:670}}><Text size={71} color="#114b44" weight={700}>一条诊断路径</Text><Text y={111} size={31} color="#536674">CPU → 内存 → 已实现外设</Text><div style={{opacity:q,transform:`translateY(${(1-q)*30}px)`}}><Text y={254} size={65} color="#934f34" weight={700}>覆盖之外，仍待实现</Text><Text y={351} size={29} color="#536674">斜线只是概念标记，不代表实际比例</Text></div></div></>;
}
function Inventory({t}) {
 const ready=p(t,37.7,38.8),missing=p(t,40.3,41.3);
 return <><Reveal t={t} at={34.1} x={110} y={141} size={80}>公开项目，明确边界</Reveal><Label x={115} y={267}>qemu-bk7258 · 7057f17</Label><div style={{position:'absolute',left:1040,top:364,width:730}}><Text size={58} color={ready>.1?C.teal:C.ink} weight={700}>部分 CPU / 内存 / 外设</Text><Text y={103} size={31} color={C.muted}>用于诊断的模型子集</Text><div style={{opacity:missing,transform:`translateY(${(1-missing)*28}px)`}}><div style={{position:'absolute',left:0,top:208,width:650,height:2,background:'#65444b'}}/><Text y={243} size={57} color={C.red} weight={700}>Wi-Fi / BT / 音视频</Text><Text y={337} size={34} color={C.muted}>仍未支持</Text></div></div></>;
}
function Hil({t}) {
 const a=p(t,43.5,46.7),wave=p(t,47,50.6);
 return <><Reveal t={t} at={43.05} x={110} y={134} size={79}>两种验证，各有证据</Reveal><div style={{position:'absolute',left:959,top:328,width:1,height:450,background:C.line}}/><Label x={112} y={323}>模拟器 / 逻辑</Label><Text x={130} y={764} size={30} color={C.muted}>寄存器 · 中断 · 模型输出</Text><Rail x1={235} y1={760} x2={775} y2={760} q={a}/><Label x={1070} y={323} color={C.orange}>实机验收 / 概念图</Label><svg width="680" height="310" style={{position:'absolute',left:1090,top:437}}><defs><pattern id="scope-grid" width="60" height="55" patternUnits="userSpaceOnUse"><path d="M60 0 H0 V55" stroke="#303948" fill="none" strokeWidth="1"/></pattern></defs><rect width="680" height="310" fill="url(#scope-grid)"/><path d="M0 180 H130 V55 H255 V220 H405 V85 H550 V180 H680" stroke={C.orange} strokeWidth="6" fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-wave}/><circle cx={wave*670} cy="279" r="6" fill={C.orange}/></svg><Text x={1080} y={775} size={30} color={C.muted}>电压 · 波形 · 实际时序，仍需测量</Text></>;
}
function Closing({t}) {
 return <><Reveal t={t} at={51.1} x={105} y={178} size={107}>先验证逻辑</Reveal><Reveal t={t} at={51.3} x={105} y={318} size={107}>再验证硬件</Reveal><div style={{opacity:p(t,54,54.5)}}><Text x={112} y={553} size={36} color={C.muted}>在模型范围内，先查清逻辑问题</Text></div><div style={{opacity:p(t,57.2,57.6)}}><Label x={114} y={678} color={C.orange}>实机验收，仍然不能省</Label></div></>;
}
export function QemuExplainer(){
 const t=useCurrentFrame()/30,index=Math.max(0,edges.findIndex((e,i)=>t>=e&&t<edges[i+1])),light=index===4;
 const [x,y,scale,rotate,explode,wire,coverage]=pose(t);
 const Scenes=[Hook,Cpu,Bus,Response,Boundary,Inventory,Hil,Closing],Scene=Scenes[index];
 const start=edges[index],end=edges[index+1],alpha=p(t,start,start+.14)*(index===7?1:1-p(t,end-.12,end));
 return <AbsoluteFill style={{background:C.bg,color:C.ink,fontFamily:'"WenQuanYi Zen Hei",sans-serif',overflow:'hidden'}}>
 <Background t={t} light={light}/>
 <SpatialChip t={t} x={x} y={y} scale={scale} rotate={rotate} explode={explode} coverage={coverage} wire={wire} labels={index!==6} id="hero"/>
 <div style={{position:'absolute',inset:0,opacity:alpha}}><Scene t={t}/></div>
 <Text x={110} y={55} size={25} color={light?'#526371':C.muted} style={{letterSpacing:2}}>QEMU / 原理动画</Text><Text x={1560} y={53} size={27} color={light?'#3b766a':C.teal}>{String(index+1).padStart(2,'0')} / 08</Text>
 <div style={{position:'absolute',left:106,top:1003,width:1710,display:'flex',gap:8}}>{chapters.map((name,i)=><div key={name} style={{flex:edges[i+1]-edges[i],fontSize:20,color:i===index?C.teal:C.muted,borderTop:`3px solid ${i<=index?C.teal:C.line}`,paddingTop:10}}>{name}</div>)}</div>
 <Text x={110} y={1056} size={20} color={C.muted}>原创概念动画 · 系统合成配音 · 测试作品待作者确认</Text>
 </AbsoluteFill>;
}
