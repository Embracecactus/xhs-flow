import React from 'react';

// Deliberately schematic: this is a spatial teaching prop, not a BK7258 floorplan.
const clamp=(v)=>Math.max(0,Math.min(1,v));
const mix=(a,b,t)=>a+(b-a)*clamp(t);

function Poly({points,fill,stroke='#315260',width=2,opacity=1,dash}){
  return <polygon points={points} fill={fill} stroke={stroke} strokeWidth={width} opacity={opacity} strokeDasharray={dash}/>;
}

function Trace({d,active=false,wire=0}){
  return <path d={d} fill="none" stroke={active?'#54ecd2':'#2c5965'} strokeWidth={active?3:2}
    strokeDasharray={wire>.65?'7 6':undefined} opacity={active ? .94 : .64}/>;
}

/**
 * A deterministic pseudo-3D IC. The viewBox is the 1920 x 870 safe picture area;
 * x/y are its visual centre, while scale is based on an approximately 700 x 500 prop.
 */
export function SpatialChip({t=0,x=960,y=480,scale=1,rotate=0,explode=0,coverage=0,wire=0,labels=true,id='chip'}){
  const e=clamp(explode), w=clamp(wire), c=clamp(coverage);
  // rotate is radians. CSS applies a real perspective projection after the
  // isometric drawing, so the same chip can turn toward either camera side.
  const yaw=rotate, pitch=-.16+Math.sin(rotate*.5)*.08;
  const lidLift=190*e, dieLift=48*e;
  const lidOpacity=Math.max(.12,1-.84*Math.max(e,w));
  const shimmer=(Math.sin(t*1.45)+1)/2;
  const metal=`url(#metal-${id})`, board=`url(#board-${id})`, hatch=`url(#hatch-${id})`;
  const stroke=w>.5?'#54ecd2':'#426976';
  const pins=[];
  for(let i=0;i<9;i++){
    const topX=-250+i*58, sideY=-118+i*29;
    pins.push(<g key={`p${i}`} fill="url(#gold-${id})" stroke="#9b6940" strokeWidth="1">
      <Poly points={`${topX},-180 ${topX+27},-188 ${topX+32},-162 ${topX+4},-155`} fill={`url(#gold-${id})`}/>
      <Poly points={`${topX},145 ${topX+29},151 ${topX+34},177 ${topX+5},170`} fill={`url(#gold-${id})`}/>
      {i<7&&<><Poly points={`-308,${sideY} -282,${sideY+6} -272,${sideY+28} -299,${sideY+22}`} fill={`url(#gold-${id})`}/><Poly points={`280,${sideY+20} 306,${sideY+26} 316,${sideY+48} 289,${sideY+42}`} fill={`url(#gold-${id})`}/></>}
    </g>);
  }
  const modules=[
    ['CPU',-116,-42,115,76,'#54ecd2'],['RAM',22,-56,102,55,'#8ca8ff'],
    ['UART',48,29,92,57,'#fb9b66'],['TIMER',-112,52,111,48,'#80cfab']
  ];
  return <svg width="1920" height="870" viewBox="0 0 1920 870" style={{position:'absolute',left:0,top:0,overflow:'visible',pointerEvents:'none',transform:`perspective(1260px) rotateX(${pitch*180/Math.PI}deg) rotateY(${yaw*180/Math.PI}deg)`,transformOrigin:`${x}px ${y}px`,transformStyle:'preserve-3d'}} aria-label="Conceptual spatial chip">
    <defs>
      <linearGradient id={`metal-${id}`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#d6e2e7"/><stop offset=".18" stopColor="#5d7b86"/><stop offset=".53" stopColor="#182b37"/><stop offset=".78" stopColor="#75929a"/><stop offset="1" stopColor="#16222c"/></linearGradient>
      <linearGradient id={`board-${id}`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#193e4a"/><stop offset=".48" stopColor="#09202b"/><stop offset="1" stopColor="#07131d"/></linearGradient>
      <linearGradient id={`die-${id}`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#213b4a"/><stop offset=".55" stopColor="#07121d"/><stop offset="1" stopColor="#1e555b"/></linearGradient>
      <linearGradient id={`gold-${id}`} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#ffd494"/><stop offset="1" stopColor="#a9653d"/></linearGradient>
      <pattern id={`hatch-${id}`} width="11" height="11" patternUnits="userSpaceOnUse" patternTransform="rotate(36)"><path d="M0 0V12" stroke="#fb9b66" strokeWidth="3"/></pattern>
    </defs>
    <g transform={`translate(${x} ${y}) scale(${scale})`}>
      <ellipse cx="0" cy="232" rx="342" ry="50" fill="#02060b" opacity=".72"/>
      {pins}

      {/* substrate: top, front thickness, and left thickness */}
      <g transform={`translate(0 ${dieLift})`}>
        <Poly points="-292,-167 248,-135 298,145 -238,174" fill={board} stroke={stroke} width={3}/>
        <Poly points="-238,174 298,145 298,174 -238,203" fill="#0a1823" stroke={stroke}/>
        <Poly points="-292,-167 -238,174 -238,203 -292,-138" fill="#142f3a" stroke={stroke}/>
        <Poly points="-263,-143 224,-113 267,126 -216,153" fill="#0b1d28" stroke="#54ecd2" width={1.4} opacity=".92" dash={w>.5?'8 6':undefined}/>
        <Trace wire={w} d="M-236 -97 L-155 -81 L-123 -40 L-25 -33" active/>
        <Trace wire={w} d="M-218 67 L-144 75 L-77 113 L36 104"/>
        <Trace wire={w} d="M126 -82 L169 -31 L236 -21" active={w>.25}/>
        <Trace wire={w} d="M143 100 L195 60 L235 65"/>
        <Trace wire={w} d="M-16 -6 L18 32 L105 38" active={w>.55}/>
        {Array.from({length:16},(_,i)=><circle key={`via${i}`} cx={-214+(i%8)*57} cy={-117+Math.floor(i/8)*211} r="4" fill={i%3===0?'#54ecd2':'#597d83'} opacity=".9"/>) }
      </g>

      {/* bare die and its sidewall form the second physical layer */}
      <g transform={`translate(0 ${-dieLift})`}>
        <Poly points="-185,-111 159,-90 191,96 -151,117" fill={`url(#die-${id})`} stroke={w>.4?'#54ecd2':'#52717d'} width={3}/>
        <Poly points="-151,117 191,96 191,118 -151,140" fill="#061019" stroke="#3c6772"/>
        {modules.map(([name,mx,my,mw,mh,color])=>{
          return <g key={name} transform={`translate(${mx} ${my}) skewY(4)`}>
            <rect width={mw} height={mh} rx="7" fill={w>.55?'#071118':`${color}20`} stroke={color} strokeWidth={w>.55?3:2}/>
            {labels&&<text x={mw/2} y={mh/2+9} textAnchor="middle" fill={color} fontSize="24" fontWeight="700" fontFamily={'"WenQuanYi Zen Hei",sans-serif'}>{name}</text>}
          </g>;
        })}
        {c>0&&<g opacity={c}><Poly points="-28,-7 24,-3 33,36 -20,40" fill={hatch} stroke="#fb9b66" width={2}/>{labels&&<text x="2" y="22" textAnchor="middle" fill="#fb9b66" fontSize="14" fontWeight="700" fontFamily={'"WenQuanYi Zen Hei",sans-serif'}>?</text>}</g>}
        <Trace wire={w} d="M-158 -65 L-72 -58 L-44 -39" active/><Trace wire={w} d="M18 -8 L-2 33 L-62 53"/><Trace wire={w} d="M129 2 L105 29 L93 51" active={w>.6}/>
      </g>

      {/* lifted heat spreader: the third solid layer, with a deep visible rim */}
      <g transform={`translate(0 ${-lidLift})`} opacity={lidOpacity}>
        <Poly points="-229,-154 202,-128 240,96 -187,122" fill={metal} stroke={w>.5?'#54ecd2':'#7d9da5'} width={3}/>
        <Poly points="-187,122 240,96 240,125 -187,151" fill="#263f4a" stroke="#7d9da5" width={2}/>
        <Poly points="-229,-154 -187,122 -187,151 -229,-125" fill="#46626c" stroke="#7d9da5" width={2}/>
        <Poly points="-195,-126 168,-104 191,45 -169,67" fill="#162a35" stroke="#a5c5ca" width={2} opacity={w>.7?.3:.8}/>
        <path d="M-173 -112 L157 -92" stroke="#e4f5ef" strokeWidth={3+shimmer*2} opacity=".46"/>
        {labels&&<><text x="4" y="-10" textAnchor="middle" fill="#eaf5f6" fontSize="38" fontWeight="700" fontFamily={'"WenQuanYi Zen Hei",sans-serif'}>QEMU</text><text x="4" y="25" textAnchor="middle" fill="#54ecd2" fontSize="26" fontWeight="700" letterSpacing="3" fontFamily={'"WenQuanYi Zen Hei",sans-serif'}>CONCEPT</text></>}
      </g>

    </g>
  </svg>;
}
