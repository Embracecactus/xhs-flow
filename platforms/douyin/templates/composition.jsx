import React from 'react';
import {AbsoluteFill, Composition, Easing, OffthreadVideo, Sequence, interpolate, registerRoot, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Diagram} from './diagrams.jsx';
import {QemuExplainer} from './QemuExplainer.jsx';
import {PcbFilm} from './PcbFilm.jsx';

const colors={cyan:'#67e8dc',white:'#f3f7fd',muted:'#9cb0ca'};
const ease=(f,a=0,b=18)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.out(Easing.cubic)});

function Scene({scene,index,total,wide}) {
  const f=useCurrentFrame();const {fps}=useVideoConfig();const e=ease(f);
  if(scene.asset) return <AbsoluteFill>
    <OffthreadVideo src={staticFile(scene.asset.replace(/^assets\//,''))} muted trimBefore={Math.round((scene.source_start||0)*fps)} style={{width:'100%',height:'100%',objectFit:'cover'}}/>
    <div style={{position:'absolute',left:90,top:130,fontSize:50,color:colors.white,textShadow:'0 3px 10px black'}}>{scene.heading}</div>
  </AbsoluteFill>;
  return <AbsoluteFill style={{opacity:e,transform:`translateY(${(1-e)*24}px)`}}>
    <div style={{position:'absolute',left:wide?92:100,top:wide?173:255,fontSize:wide?28:35,color:colors.cyan,letterSpacing:3}}>{String(index+1).padStart(2,'0')} / {String(total).padStart(2,'0')} <span style={{color:colors.muted,marginLeft:24}}>{scene.chapter||'观察 → 验证'}</span></div>
    <div style={{position:'absolute',left:wide?88:100,top:wide?253:345,width:wide?805:850,fontSize:wide?84:74,lineHeight:1.22,fontWeight:700,whiteSpace:'pre-line',letterSpacing:1}}>{scene.heading}</div>
    <div style={{position:'absolute',left:wide?94:100,top:wide?540:1340,width:wide?750:830,fontSize:wide?30:34,lineHeight:1.6,color:colors.muted}}><span style={{display:'inline-block',height:4,width:44,background:colors.cyan,verticalAlign:'middle',marginRight:18}}/>{scene.note}</div>
    <div style={{position:'absolute',left:wide?955:90,top:wide?170:650,width:900,height:600}}><Diagram scene={scene} frame={f} fps={fps}/></div>
  </AbsoluteFill>;
}

const Video=(props)=>{
  const frame=useCurrentFrame();const {fps,width,height}=useVideoConfig();const wide=width>height;
  if(props.style==='qemu-cinematic')return <QemuExplainer props={props}/>;
  if(props.style==='pcb-lab')return <PcbFilm props={props}/>;
  const active=props.scenes.findIndex(s=>frame>=s.start*fps&&frame<s.end*fps);
  return <AbsoluteFill style={{background:'#08111f',color:colors.white,fontFamily:'"WenQuanYi Zen Hei",sans-serif'}}>
    <AbsoluteFill style={{background:'radial-gradient(ellipse at 75% 40%, #102b46 0%, transparent 65%)'}}/>
    <AbsoluteFill style={{backgroundImage:'linear-gradient(#18304a33 1px,transparent 1px),linear-gradient(90deg,#18304a33 1px,transparent 1px)',backgroundSize:'52px 52px',opacity:.5}}/>
    <div style={{position:'absolute',left:90,right:90,top:wide?57:125,display:'flex',justifyContent:'space-between',fontSize:wide?25:30,color:colors.muted,letterSpacing:2}}><span>{props.kicker||'Douyin Flow / 技术说明'}</span><span>{wide?`TECH NOTES  /  ${props.duration}s`:''}</span></div>
    {props.scenes.map((s,i)=><Sequence key={i} from={Math.round(s.start*fps)} durationInFrames={Math.round((s.end-s.start)*fps)}><Scene scene={s} index={i} total={props.scenes.length} wide={wide}/></Sequence>)}
    <div style={{position:'absolute',left:90,right:90,top:wide?785:1770,display:'flex',gap:7}}>{props.scenes.map((s,i)=><div key={i} style={{flex:s.end-s.start,height:wide?5:4,background:i<active?colors.cyan:i===active?'#41777e':'#23354c'}}><div style={{height:'100%',background:colors.cyan,width:i===active?`${100*(frame/fps-s.start)/(s.end-s.start)}%`:0}}/></div>)}</div>
    {wide?<div style={{position:'absolute',left:90,top:805,right:90,display:'flex',justifyContent:'space-between',fontSize:20,color:colors.muted}}>{props.scenes.map((s,i)=><span key={i} style={{color:i===active?colors.cyan:colors.muted}}>{s.chapter||String(i+1).padStart(2,'0')}</span>)}</div>:null}
    {props.demo?<div style={{position:'absolute',left:90,top:height-44,fontSize:wide?20:23,color:'#6f8aa8'}}>原创概念动画 / 系统合成配音 / 测试作品待作者确认</div>:null}
  </AbsoluteFill>;
};
registerRoot(()=> <Composition id="DouyinVideo" component={Video} fps={30} width={1920} height={1080} durationInFrames={1800} defaultProps={{duration:60,width:1920,height:1080,scenes:[]}} calculateMetadata={({props})=>({durationInFrames:Math.round(props.duration*30),width:props.width||1080,height:props.height||1920})}/>);
