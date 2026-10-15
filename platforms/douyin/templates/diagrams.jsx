import React from 'react';
import {Easing, interpolate} from 'remotion';

export const palette = {
  dark: '#08111f', cyan: '#67e8dc', blue: '#589bff', amber: '#ffc86d',
  red: '#ff7d82', white: '#f3f7fd', muted: '#9cb0ca', panel: '#10223a',
};

const {dark, cyan, blue, amber, red, white, muted, panel} = palette;
const ease = (frame, from, to) => interpolate(frame, [from, to], [0, 1], {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
});
const enter = (frame, at, children) => <g opacity={ease(frame, at, at + 14)} transform={`translate(0 ${(1 - ease(frame, at, at + 14)) * 16})`}>{children}</g>;

const Label = ({x, y, children, color = muted, size = 30, anchor = 'start', weight = 400}) => (
  <text x={x} y={y} fill={color} fontSize={size} fontWeight={weight} textAnchor={anchor} fontFamily="Arial, 'Microsoft YaHei', sans-serif">{children}</text>
);

const Card = ({x, y, w, h, title, detail, color = cyan, icon, opacity = 1}) => (
  <g opacity={opacity}>
    <rect x={x} y={y} width={w} height={h} rx="22" fill={panel} stroke={color} strokeWidth="3"/>
    {icon}
    <Label x={x + w / 2} y={y + 60} size={34} color={white} weight={700} anchor="middle">{title}</Label>
    <Label x={x + w / 2} y={y + h - 26} size={28} color={color} anchor="middle">{detail}</Label>
  </g>
);

const Camera = ({x, y, color = cyan}) => <g transform={`translate(${x} ${y})`}><rect x="0" y="20" width="94" height="60" rx="12" fill="#17324e" stroke={color} strokeWidth="3"/><rect x="18" y="0" width="56" height="20" rx="5" fill="#1e4263"/><circle cx="47" cy="50" r="17" fill={dark} stroke={color} strokeWidth="3"/><circle cx="47" cy="50" r="7" fill={color}/><path d="M94 38h25l14 12v18L119 80H94z" fill="#1e4263" stroke={color} strokeWidth="3"/></g>;
const Nic = ({x, y, color = blue}) => <g transform={`translate(${x} ${y})`}><rect width="104" height="68" rx="12" fill="#17324e" stroke={color} strokeWidth="3"/><path d="M26 15v38M48 15v38M70 15v38" stroke={color} strokeWidth="4"/><path d="M14 54h76" stroke={color} strokeWidth="4"/></g>;
const Server = ({x, y, color = blue}) => <g transform={`translate(${x} ${y})`}><rect width="110" height="88" rx="14" fill="#17324e" stroke={color} strokeWidth="3"/><path d="M16 29h78M16 58h78" stroke={color} strokeWidth="3"/><circle cx="24" cy="20" r="5" fill={color}/><circle cx="24" cy="49" r="5" fill={color}/></g>;
const Arrow = ({x1, y1, x2, y2, color = cyan, opacity = 1, dash}) => <g opacity={opacity}><path d={`M${x1} ${y1} H${x2 - 16}`} stroke={color} strokeWidth="5" strokeDasharray={dash} fill="none"/><path d={`M${x2 - 20} ${y2 - 10} L${x2} ${y2} L${x2 - 20} ${y2 + 10}`} fill="none" stroke={color} strokeWidth="5"/></g>;

function Link({frame}) {
  const pulse = 250 + (frame % 90) * 4.6;
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="相机到主机的图像链路图">
    <Camera x={90} y={230}/><Server x={690} y={220}/><Arrow x1={235} y1={270} x2={680} y2={270}/>
    <circle cx={pulse} cy="270" r="12" fill={cyan}/><Label x={135} y={390} size={32} color={cyan} anchor="middle">相机</Label><Label x={745} y={390} size={32} color={blue} anchor="middle">主机</Label>
    {enter(frame, 12, <><rect x="155" y="450" width="590" height="80" rx="18" fill={panel}/><Label x="450" y="502" size={34} color={white} anchor="middle">画面停住，先描述看到的现象</Label></>)}
  </svg>;
}

function Three({frame}) {
  const rows = [['断链', '设备或控制连接丢失', red], ['丢帧', '设备仍在，图像不完整', cyan], ['等触发', '设备仍在，尚未出帧', amber]];
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="三种不同故障现象分类">
    {rows.map(([title, detail, color], i) => enter(frame, i * 16, <g key={title}><rect x="55" y={65 + i * 160} width="790" height="120" rx="22" fill={panel} stroke={color} strokeWidth="2"/><Label x="95" y={137 + i * 160} size={42} color={color} weight={700}>{title}</Label><Label x="285" y={137 + i * 160} size={31} color={white}>{detail}</Label><path d={`M95 ${160 + i * 160} H${95 + ease(frame, i * 16 + 8, i * 16 + 38) * 680}`} stroke={color} strokeWidth="4"/></g>))}
  </svg>;
}

function Checklist({frame}) {
  const rows = ['同一时刻：设备还在吗？', '链路事件：有没有断开？', '帧统计：丢包还是无触发？'];
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="按同一时刻对照的三步检查表">
    {rows.map((text, i) => enter(frame, i * 22, <g key={text}><circle cx="92" cy={105 + i * 155} r="28" fill={i === 0 ? cyan : blue}/><Label x="92" y={116 + i * 155} size={29} color={dark} weight={700} anchor="middle">{i + 1}</Label><rect x="145" y={62 + i * 155} width="655" height="86" rx="18" fill={panel}/><Label x="180" y={118 + i * 155} size={32} color={white}>{text}</Label></g>))}
  </svg>;
}

function Packets({frame, fps}) {
  const second = frame / fps;
  const stage = second < 3 ? 0 : second < 6 ? 1 : 2;
  const packets = [0, 1, 2, 3, 4, 5];
  const active = ease(frame, 6, 24);
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="网络数据包丢失、链路检查和降载观察示意">
    <Camera x={55} y={105}/><Nic x={700} y={100}/><Arrow x1={205} y1={145} x2={690} y2={145}/>
    {packets.map((i) => { const x = 230 + i * 70; const lost = i === 3; return <rect key={i} x={x} y="126" width="34" height="38" rx="7" fill={lost ? red : cyan} opacity={lost ? .55 + active * .45 : 1}/>; })}
    {stage === 0 && enter(frame, 10, <><Label x="450" y="278" size={39} color={red} anchor="middle" weight={700}>少了数据包：一帧图像可能失败</Label><Label x="450" y="332" size={30} color={muted} anchor="middle">设备仍在，不等于图像完整</Label></>)}
    {stage >= 1 && <g opacity={stage === 1 ? 1 : 1 - ease(frame, 180, 196)}><Label x="450" y="276" size={34} color={white} anchor="middle">按链路逐项排查</Label>{['网线', '交换机', '网卡'].map((x, i) => <g key={x}>{enter(frame, 90 + i * 18, <><rect x={90 + i * 250} y="320" width="210" height="100" rx="18" fill={panel} stroke={blue} strokeWidth="2"/><Label x={195 + i * 250} y="382" size={32} color={white} anchor="middle">{x}</Label></>)}</g>)}</g>}
    {stage === 2 && <g opacity={ease(frame, 180, 198)}><rect x="95" y="455" width="710" height="80" rx="18" fill="#17324e"/><Label x="450" y="507" size={31} color={amber} anchor="middle">降低帧率 / 重传 / 观察失败帧变化</Label></g>}
  </svg>;
}

function Heartbeat({frame, fps}) {
  const second = frame / fps;
  const paused = second >= 3 && second < 6;
  const timeout = second >= 6;
  const dotX = timeout ? 675 : 230 + ((frame % 48) / 48) * 430;
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="控制连接心跳、暂停和超时示意">
    <Camera x={72} y={155}/><Server x={700} y={145}/><path d="M220 195H690" stroke={timeout ? red : cyan} strokeWidth="5" strokeDasharray="12 12"/>
    {!paused && <circle cx={dotX} cy="195" r="13" fill={timeout ? red : cyan}/>} {enter(frame, 8, <Label x="450" y="285" size={34} color={second < 3 ? cyan : timeout ? red : amber} anchor="middle">{second < 3 ? '正常：程序定期发送心跳' : paused ? '暂停：心跳没有继续发送' : '超时：相机可能关闭控制连接'}</Label>)}
    {enter(frame, 35, <><rect x="115" y="365" width="670" height="105" rx="20" fill={timeout ? '#422638' : panel}/><Label x="450" y="430" size={31} color={white} anchor="middle">调试暂停是一个已知例子；超时值依设备而定</Label></>)}
  </svg>;
}

function Usb({frame, fps}) {
  const second = frame / fps;
  const level = second < 3 ? 0.38 : second < 6 ? 0.82 : 0.48;
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="两个USB相机共享控制器与带宽对照示意">
    <Camera x={90} y={65}/><Camera x={660} y={65}/><path d="M145 165V270H450M715 165V270H450V310" fill="none" stroke={cyan} strokeWidth="5"/>
    <Card x={300} y={310} w={300} h={120} title="同一控制器" detail="带宽可能共用" color={red}/>
    {enter(frame, 12, <><Label x="450" y="500" size={32} color={white} anchor="middle">先观察，再做带宽对照</Label><rect x="170" y="535" width="560" height="22" rx="11" fill="#19314b"/><rect x="170" y="535" width={560 * level} height="22" rx="11" fill={level > .7 ? red : amber}/></>)}
    {second >= 6 && <Label x="450" y="590" size={28} color={cyan} anchor="middle">概念演示：降低带宽后比较帧统计</Label>}
  </svg>;
}

function Fallback({scene, frame}) {
  const rows = scene.bullets || [scene.note || '记录现象，再核对证据'];
  return <svg viewBox="0 0 900 600" width="900" height="600" role="img" aria-label="信息要点图">
    {rows.slice(0, 3).map((text, i) => enter(frame, i * 18, <g key={text}><rect x="60" y={70 + i * 155} width="780" height="108" rx="20" fill={panel}/><Label x="105" y={137 + i * 155} size={34} color={i === 0 ? cyan : white}>{text}</Label></g>))}
  </svg>;
}

export function Diagram({scene, frame, fps = 30}) {
  const props = {frame, fps, scene};
  if (scene.diagram === 'link') return <Link {...props}/>;
  if (scene.diagram === 'three') return <Three {...props}/>;
  if (scene.diagram === 'checklist') return <Checklist {...props}/>;
  if (scene.diagram === 'packets') return <Packets {...props}/>;
  if (scene.diagram === 'heartbeat') return <Heartbeat {...props}/>;
  if (scene.diagram === 'usb') return <Usb {...props}/>;
  return <Fallback {...props}/>;
}
