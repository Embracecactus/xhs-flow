// Original animation of licensed Antmicro geometry, not CAD/solver UI automation.
import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {KTX2Loader} from 'three/examples/jsm/loaders/KTX2Loader.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';

export const clamp=x=>Math.max(0,Math.min(1,x));
export const ease=x=>{x=clamp(x);return x*x*(3-2*x);};
const lerp=(a,b,t)=>a+(b-a)*t;
const phase=(t,a,b)=>ease((t-a)/(b-a));
const v3=(x,y,z)=>new THREE.Vector3(x,y,z);
const C=['#f0b568','#78c9c2','#95b2f0','#d99bc2','#b8cb79','#df9677','#99c1d7','#c7adf0'];

function bot(color) {
  const root=new THREE.Group();
  const ceramic=new THREE.MeshStandardMaterial({color:'#e4e5e0',metalness:.25,roughness:.35});
  const accent=new THREE.MeshStandardMaterial({color,metalness:.35,roughness:.3});
  const dark=new THREE.MeshStandardMaterial({color:'#111922',metalness:.5,roughness:.3});
  const eye=new THREE.MeshStandardMaterial({color:'#c7f5f1',emissive:'#49c4c4',emissiveIntensity:1.6});
  const torso=new THREE.Mesh(new THREE.CapsuleGeometry(.62,.62,4,10),ceramic);torso.position.y=1.25;root.add(torso);
  const lid=new THREE.Mesh(new THREE.SphereGeometry(.7,16,8,0,Math.PI*2,0,Math.PI/2),accent);lid.position.y=1.68;root.add(lid);
  const visor=new THREE.Mesh(new THREE.BoxGeometry(1.05,.45,.17),dark);visor.position.set(0,1.35,.53);root.add(visor);
  for(const x of [-.25,.25]){const e=new THREE.Mesh(new THREE.BoxGeometry(.14,.15,.08),eye);e.position.set(x,1.36,.65);root.add(e);}
  const armL=new THREE.Group(),armR=new THREE.Group();
  for(const [arm,x] of [[armL,-.85],[armR,.85]]){const m=new THREE.Mesh(new THREE.CapsuleGeometry(.12,.48,3,6),accent);m.position.y=-.2;arm.add(m);arm.position.set(x,1.4,0);root.add(arm);}
  for(const x of [-.37,.37]){const foot=new THREE.Mesh(new THREE.BoxGeometry(.4,.22,.65),dark);foot.position.set(x,.25,.1);root.add(foot);}
  root.userData.arms=[armL,armR];return root;
}

export async function createPcbScene(canvas,asset,width=1920,height=1080) {
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
  renderer.setSize(width,height);renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.35;renderer.localClippingEnabled=true;
  const scene=new THREE.Scene();
  const pmrem=new THREE.PMREMGenerator(renderer);const room=new RoomEnvironment();const env=pmrem.fromScene(room,.04);scene.environment=env.texture;room.dispose();
  scene.add(new THREE.HemisphereLight('#e1efff','#575263',2.3));
  const light=new THREE.DirectionalLight('#fff1db',3.5);light.position.set(-35,60,35);scene.add(light);
  const rim=new THREE.DirectionalLight('#91bbff',2.2);rim.position.set(40,25,-45);scene.add(rim);
  const camera=new THREE.OrthographicCamera(-48,48,27,-27,.1,500);
  const world=new THREE.Group();scene.add(world);
  const ktx=new KTX2Loader().setTranscoderPath(asset('basis/')).setWorkerLimit(2).detectSupport(renderer);
  const loader=new GLTFLoader().setKTX2Loader(ktx);
  const [board,index,pnp,pcb,thermal]=await Promise.all([
    loader.loadAsync(asset('board/polarfire-som.gltf')),
    fetch(asset('model-index.json')).then(r=>r.json()),fetch(asset('board/pnp.json')).then(r=>r.json()),
    fetch(asset('derived/pcb.json')).then(r=>r.json()),fetch(asset('derived/thermal.json')).then(r=>r.json()),
  ]);
  const boardRoot=board.scene;world.add(boardRoot);
  boardRoot.traverse(o=>{if(o.isMesh){o.material.roughness=Math.min(o.material.roughness,.85);}});
  const partsRoot=new THREE.Group();world.add(partsRoot);
  const unique=[...new Set(Object.values(index.models))];const libs={};
  // Bound loader concurrency and share all geometries/textures across instances.
  for(let i=0;i<unique.length;i+=4){await Promise.all(unique.slice(i,i+4).map(async p=>{libs[p]=(await loader.loadAsync(asset(p))).scene;}));}
  const partEntries=Object.entries(pnp).filter(([k])=>!k.startsWith('_'));
  const instanceGroups=[];const temp=new THREE.Object3D();let triangleEstimate=0;
  for(const path of unique) {
    const entries=partEntries.filter(([,p])=>index.models[p.ahid]===path);const lib=libs[path];lib.updateMatrixWorld(true);
    lib.traverse(o=>{
      if(!o.isMesh)return;
      const mesh=new THREE.InstancedMesh(o.geometry,o.material,entries.length);mesh.frustumCulled=false;
      triangleEstimate+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3*entries.length;
      partsRoot.add(mesh);const local=o.matrixWorld.clone();
      const bases=entries.map(([ref,p])=>{
        const top=p.side==='top';const x=Math.abs(+p.posx)-27.5;const z=20-(+p.posy);
        temp.position.set(x,top?1.6:0,z);temp.rotation.set(top?0:Math.PI,(top?1:-1)*(+p.rot)*Math.PI/180,0);temp.scale.set(1,1,1);temp.updateMatrix();
        return {ref,top,x,z,base:temp.matrix.clone().multiply(local),order:(partEntries.findIndex(([r])=>r===ref)*.61803398875)%1};
      });
      instanceGroups.push({mesh,bases});
    });
  }
  const traceRoot=new THREE.Group();world.add(traceRoot);
  const traceLines=[];
  pcb.layers.forEach((items,i)=>{
    const arr=[];for(const [x,z,x2,z2] of items)arr.push(x,1.85+i*.015,z,x2,1.85+i*.015,z2);
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));
    const mat=new THREE.LineBasicMaterial({color:pcb.colors[i],transparent:true,opacity:.92});
    const lines=new THREE.LineSegments(g,mat);traceRoot.add(lines);traceLines.push(lines);
  });
  const layerRoot=new THREE.Group();world.add(layerRoot);const textureLoader=new THREE.TextureLoader();
  const copperLayers=[];
  // Shape is schematic only at the rounded corners; copper textures are parsed source geometry.
  const shape=new THREE.Shape();const w=27.5,h=20,r=3.5;
  shape.moveTo(-w+r,-h);shape.lineTo(w-r,-h);shape.quadraticCurveTo(w,-h,w,-h+r);shape.lineTo(w,h-r);shape.quadraticCurveTo(w,h,w-r,h);shape.lineTo(-w+r,h);shape.quadraticCurveTo(-w,h,-w,h-r);shape.lineTo(-w,-h+r);shape.quadraticCurveTo(-w,-h,-w+r,-h);
  for(const x of [-24,24])for(const y of [-16.5,16.5]){const hole=new THREE.Path();hole.absarc(x,y,1.4,0,Math.PI*2,true);shape.holes.push(hole);}
  const sheetGeom=new THREE.ShapeGeometry(shape,10);sheetGeom.rotateX(-Math.PI/2);
  const uv=sheetGeom.attributes.uv,pos=sheetGeom.attributes.position;
  for(let i=0;i<uv.count;i++)uv.setXY(i,(pos.getX(i)+w)/(w*2),1-(pos.getZ(i)+h)/(h*2));uv.needsUpdate=true;
  for(let i=0;i<14;i++){
    const group=new THREE.Group();layerRoot.add(group);
    const base=new THREE.Mesh(sheetGeom,new THREE.MeshBasicMaterial({color:new THREE.Color(pcb.colors[i]).multiplyScalar(.23),side:THREE.DoubleSide,depthWrite:true}));group.add(base);
    const map=await textureLoader.loadAsync(asset(`derived/layer-${String(i).padStart(2,'0')}.png`));map.colorSpace=THREE.SRGBColorSpace;map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
    const copper=new THREE.Mesh(sheetGeom,new THREE.MeshBasicMaterial({map,transparent:true,side:THREE.DoubleSide,depthWrite:true,alphaTest:.08}));copper.position.y=.035;group.add(copper);copperLayers.push(group);
  }
  const bots=new THREE.Group();world.add(bots);const workers=C.map(c=>bot(c));workers.forEach(b=>bots.add(b));
  // A source-derived route packet is a *routing highlight*, not an electric field or timing result.
  const sparksRoot=new THREE.Group();world.add(sparksRoot);const sparks=[];
  for(let i=0;i<48;i++){const m=new THREE.Mesh(new THREE.SphereGeometry(.12,5,4),new THREE.MeshBasicMaterial({color: C[i%8]}));sparksRoot.add(m);sparks.push(m);}
  // v002 cutaway: source via coordinates, with explicitly exaggerated diameter/spacing.
  // Source inspection confirmed all 1,565 vias connect F.Cu to B.Cu.
  const viaRoot=new THREE.Group();world.add(viaRoot);const viaColumns=[];
  const candidates=pcb.vias.filter(v=>v[0]>6&&v[0]<22&&Math.abs(v[1])<15);
  const viaMetal=new THREE.MeshStandardMaterial({color:'#d7a44f',metalness:.7,roughness:.25,side:THREE.DoubleSide});
  for(let i=0;i<12;i++){
    const v=candidates[Math.floor(i*(candidates.length-1)/11)],g=new THREE.Group();g.position.set(v[0],0,v[1]);viaRoot.add(g);
    const radius=Math.max(.24,v[2]*1.1),tube=new THREE.Mesh(new THREE.CylinderGeometry(radius,radius,1,16,1,true),viaMetal);g.add(tube);
    const rings=[0,3,7,13].map((layer,j)=>{const m=new THREE.Mesh(new THREE.TorusGeometry(radius+.10,.095,5,16),new THREE.MeshBasicMaterial({color:C[j]}));m.rotation.x=Math.PI/2;g.add(m);return {m,layer};});
    const packet=new THREE.Mesh(new THREE.TorusGeometry(radius+.13,.15,6,18),new THREE.MeshBasicMaterial({color:'#5bffda',toneMapped:false}));packet.rotation.x=Math.PI/2;g.add(packet);viaColumns.push({tube,rings,packet});
  }
  const cutPlane=new THREE.Plane(v3(-1,0,0),5);
  const heatRoot=new THREE.Group();world.add(heatRoot);
  const heatGeom=new THREE.PlaneGeometry(55,40,110,80);heatGeom.rotateX(-Math.PI/2);
  const heatPos=heatGeom.attributes.position;const baseHeat=new Float32Array(heatPos.array);const heatColors=new Float32Array(heatPos.count*3);heatGeom.setAttribute('color',new THREE.BufferAttribute(heatColors,3));
  const heatMaterial=new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,toneMapped:false});
  const heat=new THREE.Mesh(heatGeom,heatMaterial);heatRoot.add(heat);
  const wire=new THREE.Mesh(heatGeom,new THREE.MeshBasicMaterial({color:'#e2eefa',wireframe:true,transparent:true,opacity:.065}));wire.position.y=.03;heatRoot.add(wire);
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=256;shadowCanvas.height=256;const ctx=shadowCanvas.getContext('2d');const grad=ctx.createRadialGradient(128,128,15,128,128,128);grad.addColorStop(0,'rgba(0,0,0,.65)');grad.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=grad;ctx.fillRect(0,0,256,256);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(100,80),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));floor.rotation.x=-Math.PI/2;floor.position.y=-5;world.add(floor);
  const matrix=new THREE.Matrix4();const trans=new THREE.Matrix4();const color=new THREE.Color();
  function draw(t) {
    let eye=v3(49,62,65),look=v3(0,1,0),zoom=1.02,orbit=0;
    boardRoot.visible=true;partsRoot.visible=true;traceRoot.visible=false;layerRoot.visible=false;heatRoot.visible=false;sparksRoot.visible=false;bots.visible=false;floor.visible=true;viaRoot.visible=t>=47&&t<57;
    world.position.set(0,2,0);world.rotation.set(0,0,0);world.scale.setScalar(.83);
    if(t<7){orbit=-.34+t*.048;zoom=1.07+phase(t,0,5)*.08;bots.visible=t>3;}
    else if(t<14){orbit=.1;zoom=.82;world.position.x=11;eye=v3(25,78,60);bots.visible=true;}
    else if(t<25){orbit=.08;zoom=1;eye=v3(20,85,56);world.position.x=-4;bots.visible=true;}
    else if(t<35){eye=v3(0,110,.02);zoom=1.16;traceRoot.visible=true;partsRoot.visible=false;boardRoot.visible=false;layerRoot.visible=true;bots.visible=true;sparksRoot.visible=true;}
    else if(t<47){orbit=-.18+phase(t,35,47)*.45;eye=v3(48,38,68);look=v3(0,9,0);zoom=.86;world.position.x=-5;world.position.y=-4;layerRoot.visible=true;partsRoot.visible=false;boardRoot.visible=false;floor.visible=false;}
    else if(t<57){eye=v3(55,33,64);look=v3(0,5,0);zoom=.96+phase(t,47,56)*.05;orbit=-.22+phase(t,47,57)*.46;world.position.x=-9;world.position.y=-1.5;partsRoot.visible=false;boardRoot.visible=false;layerRoot.visible=true;floor.visible=false;}
    else if(t<67){eye=v3(45,58,65);zoom=1.02;world.position.x=-7;partsRoot.visible=false;boardRoot.visible=false;heatRoot.visible=true;orbit=(t-57)*.025;}
    else if(t<74){eye=v3(45,48,65);zoom=1.04;world.position.x=-7;partsRoot.visible=false;boardRoot.visible=false;heatRoot.visible=true;orbit=(t-67)*.025;}
    else if(t<81){eye=v3(36,76,65);zoom=.83;world.position.x=-12;world.position.y=-2;orbit=-.15;bots.visible=true;}
    else {eye=v3(48,52,65);zoom=1.1;orbit=.3-phase(t,81,89)*.5;bots.visible=true;}
    world.rotation.y=orbit;
    camera.position.copy(eye);camera.lookAt(look);camera.zoom=zoom;camera.updateProjectionMatrix();
    const assembly=t>=14&&t<25;const assemblyP=phase(t,14.2,21.8);
    for(const {mesh,bases} of instanceGroups){
      for(let i=0;i<bases.length;i++){
        const b=bases[i];const land=assembly?ease((assemblyP-b.order*.72)/.28):1;
        trans.makeTranslation(0,(b.top?1:-1)*(1-land)*36,0);matrix.multiplyMatrices(trans,b.base);
        if(assembly&&land<=.001)matrix.scale(v3(.001,.001,.001));mesh.setMatrixAt(i,matrix);
      }mesh.instanceMatrix.needsUpdate=true;
    }
    traceLines.forEach((m,i)=>{const n=m.geometry.attributes.position.count;const p=phase(t,25+i*.25,32+i*.16);m.geometry.setDrawRange(0,Math.floor(n*p/2)*2);});
    const cross=t>=47&&t<57,spacing=.22+phase(t,47,49)*.68;
    world.updateMatrixWorld(true);cutPlane.set(v3(-1,0,0),5).applyMatrix4(world.matrixWorld);
    copperLayers.forEach((g,i)=>{
      const explode=t>=35&&t<47?phase(t,35.4,39.5)*(1-phase(t,45,47)):0;
      g.position.y=.2+i*.095+(13-i)*2.2*explode;g.position.x=0;
      g.visible=t>=35&&t<47||t>=25&&t<35&&i===0||t>=47&&t<57&&(i===0||i===3||i===7||i===13);
      if(cross)g.position.y=(13-i)*spacing;
      g.children[0].visible=!(t>=25&&t<35);
      const baseMaterial=g.children[0].material,copperMaterial=g.children[1].material;
      baseMaterial.transparent=cross;baseMaterial.opacity=cross?.18:1;baseMaterial.depthWrite=!cross;
      copperMaterial.opacity=cross?.48:t>=25&&t<35?.16:1;copperMaterial.depthWrite=!cross;
      for(const m of [baseMaterial,copperMaterial]){m.clippingPlanes=cross?[cutPlane]:null;}
    });
    if(cross)viaColumns.forEach(({tube,rings,packet},i)=>{
      const height=13*spacing;tube.scale.y=height;tube.position.y=height/2;
      rings.forEach(({m,layer})=>{m.position.y=(13-layer)*spacing;});
      packet.position.y=height*(1-((t-47)*.52+i/12)%1);
    });
    workers.forEach((b,i)=>{
      b.visible=t>=7&&t<35||i===0||t>=74;
      const s=t>=7&&t<14?2.05:1.8;b.scale.setScalar(s);
      let x=-24+(i%4)*15,z=-16+Math.floor(i/4)*32,y=2;
      if(t>=7&&t<14){x=-31+(i%4)*8;z=18+Math.floor(i/4)*6;y=1;}
      else if(t>=14&&t<35){x+=Math.sin(t*.65+i)*2.3;z+=Math.cos(t*.6+i*1.6)*2;y=2.6+Math.abs(Math.sin(t*3+i))*.3;}
      else if(t>=47&&t<57){x=23;z=15;y=5;b.visible=i===0;}
      else if(t>=74&&t<81){x=28;z=-8+i*3.7;y=1.7;b.visible=i<6;}
      else{x=23;z=14;y=2;b.visible=i===0;}
      b.position.set(x,y,z);b.rotation.set(0,.3+Math.sin(t*.5+i)*.14,0);
      b.userData.arms[0].rotation.z=Math.sin(t*3+i)*.6;b.userData.arms[1].rotation.z=-.5+Math.cos(t*2.5+i)*.6;
    });
    for(let i=0;i<sparks.length;i++){
      const list=pcb.layers[i%14];const seg=list.length?list[(i*191+Math.floor(t*1.8))%list.length]:[0,0,1,1];const p=(t*.8+i*.137)%1;
      sparks[i].position.set(lerp(seg[0],seg[2],p),3.2+(i%14)*.13,lerp(seg[1],seg[3],p));
    }
    if(heatRoot.visible){
      const mode=t>=67;const frame=thermal.frames[Math.min(thermal.frames.length-1,Math.floor(phase(t,57,65)*(thermal.frames.length-1)))];
      for(let i=0;i<heatPos.count;i++){
        const x=baseHeat[i*3],z=baseHeat[i*3+2];const u=mode?(Math.sin((x+27.5)/55*Math.PI*2)*Math.sin((z+20)/40*Math.PI)*Math.cos((t-67)*2.7)):frame[i];
        heatPos.setY(i,mode?u*6:u*4.4);
        const f=mode?(u+1)/2:u;color.setHSL((1-clamp(f))*.62,.68,.36+clamp(f)*.2);heatColors[i*3]=color.r;heatColors[i*3+1]=color.g;heatColors[i*3+2]=color.b;
      }heatPos.needsUpdate=true;heatGeom.attributes.color.needsUpdate=true;heatGeom.computeVertexNormals();
    }
    renderer.render(scene,camera);
  }
  return {draw,stats:{models:partEntries.length,uniqueModels:unique.length,triangleEstimate,...pcb.source_counts,substitutions:index.substitutions},dispose(){ktx.dispose();env.dispose();pmrem.dispose();renderer.dispose();}};
}
