js = r"""
<script>
// ====================================================
// MATH CORE
// ====================================================
let rng;
function seedRng(s){rng=()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};}
function rn(){let u=0,v=0;while(!u)u=rng();while(!v)v=rng();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function cm(r,c,sc=0.35){return Array.from({length:r},()=>Array.from({length:c},()=>+(rn()*sc).toFixed(3)));}
function mm(A,B){const r=A.length,k=B.length,c=B[0].length;return Array.from({length:r},(_,i)=>Array.from({length:c},(__,j)=>A[i].reduce((s,v,l)=>s+v*B[l][j],0)));}
function smx(v,t=1){const s=v.map(x=>x/t),mx=Math.max(...s),ex=s.map(x=>Math.exp(x-mx)),sm=ex.reduce((a,b)=>a+b,0);return ex.map(x=>+(x/sm).toFixed(4));}
function pe(pos,d){return Array.from({length:d},(_,i)=>i%2===0?Math.sin(pos/Math.pow(10000,i/d)):Math.cos(pos/Math.pow(10000,(i-1)/d)));}
function hashStr(s){return s.split('').reduce((a,c)=>a+c.charCodeAt(0),0);}
function toks(s){return s.trim().split(/\s+/).filter(Boolean).slice(0,8);}
function embed(tList,d){seedRng(hashStr(tList.join('')));return tList.map((_,i)=>{const e=Array.from({length:d},()=>+(rn()*0.5).toFixed(3));const p=pe(i,d);return e.map((v,j)=>+(v+p[j]*0.1).toFixed(3));});}
function selfAttn(tkns,d,temp=1){
  const emb=embed(tkns,d);
  const Wq=cm(d,d),Wk=cm(d,d),Wv=cm(d,d);
  const Q=mm(emb,Wq).map(r=>r.map(v=>+v.toFixed(3)));
  const K=mm(emb,Wk).map(r=>r.map(v=>+v.toFixed(3)));
  const V=mm(emb,Wv).map(r=>r.map(v=>+v.toFixed(3)));
  const KT=K[0].map((_,j)=>K.map(r=>r[j]));
  const raw=mm(Q,KT).map(r=>r.map(v=>+(v/Math.sqrt(d)).toFixed(3)));
  const attn=raw.map(r=>smx(r,temp));
  const out=mm(attn,V).map(r=>r.map(v=>+v.toFixed(3)));
  return{emb,Q,K,V,raw,attn,out};
}

// ====================================================
// MATRIX TABLE RENDERER
// ====================================================
function matHtml(mat,rowLabels,colLabels,color='var(--ac)'){
  const maxCols=Math.min(mat[0].length,6);
  let h=`<table class="mat"><thead><tr><th></th>`;
  for(let j=0;j<maxCols;j++)h+=`<th>${colLabels?colLabels[j]:'d'+j}</th>`;
  if(mat[0].length>maxCols)h+=`<th>…</th>`;
  h+=`</tr></thead><tbody>`;
  mat.forEach((row,i)=>{
    h+=`<tr><td style="color:${color};font-weight:700;white-space:nowrap">${rowLabels?rowLabels[i]:'r'+i}</td>`;
    row.slice(0,maxCols).forEach(v=>{
      const a=Math.min(Math.abs(v)/0.8,1);
      const bg=v>0?`rgba(124,111,255,${a*0.3})`:`rgba(244,63,94,${a*0.25})`;
      h+=`<td style="background:${bg}">${v.toFixed(2)}</td>`;
    });
    if(row.length>maxCols)h+=`<td style="color:var(--mt)">…</td>`;
    h+=`</tr>`;
  });
  return h+`</tbody></table>`;
}

// ====================================================
// HEATMAP RENDERER
// ====================================================
function heatHtml(mat,rowL,colL,cellPx=42,onClickRow=null){
  const n=mat.length,m=mat[0].length;
  const px=Math.min(cellPx,Math.floor(300/m));
  let h=``;
  mat.forEach((row,i)=>{
    row.forEach((v,j)=>{
      const a=Math.pow(v<0?0:v,0.55);
      const r=Math.round(70+185*a),g=Math.round(70+25*a),b=Math.round(110+145*(1-a));
      const txt=v<0?'✗':v.toFixed(2);
      h+=`<div class="hcell" style="width:${px}px;height:${px}px;background:rgba(${r},${g},${b},${0.25+a*0.75});color:${v>0.3?'#fff':'rgba(255,255,255,.45)'};"
        data-r="${i}" data-c="${j}" data-v="${v}"
        onmouseenter="showTip(event,'${rowL?rowL[i]:'r'+i} → ${colL?colL[j]:'c'+j}: ${v<0?'masked':v.toFixed(3)}')"
        onmouseleave="hideTip()"
        ${onClickRow?`onclick="${onClickRow}(${i})"`:''}>
        <span style="font-size:${px<36?'.52rem':'.62rem'}">${txt}</span></div>`;
    });
  });
  return h;
}
function setHmap(id,mat,rowL,colL,cellPx=42,onClickRow=null){
  const el=document.getElementById(id);
  if(!el)return;
  el.style.gridTemplateColumns=`repeat(${mat[0].length},${Math.min(cellPx,Math.floor(300/mat[0].length))}px)`;
  el.innerHTML=heatHtml(mat,rowL,colL,cellPx,onClickRow);
}

// ====================================================
// SCORE BARS
// ====================================================
function sbarsHtml(weights,labels){
  const mx=Math.max(...weights)||1;
  return weights.map((w,i)=>`
    <div class="sbar-row sl"><span class="sbar-tok">${labels[i]}</span>
    <div class="sbar-wrap"><div class="sbar-fill" style="width:${(w/mx*100).toFixed(1)}%"></div></div>
    <span class="sbar-v">${w.toFixed(3)}</span></div>`).join('');
}

// ====================================================
// TOOLTIP
// ====================================================
function showTip(e,txt){const t=document.getElementById('tip');t.textContent=txt;t.style.left=(e.clientX+12)+'px';t.style.top=(e.clientY-30)+'px';t.style.opacity='1';}
function hideTip(){document.getElementById('tip').style.opacity='0';}

// ====================================================
// NAV
// ====================================================
const SECTIONS=['overview','embed','sdpa','single','multi','masked','cross','ffn','encoder','decoder','train'];
function goto(id){
  SECTIONS.forEach(s=>{
    document.getElementById('s-'+s).classList.toggle('active',s===id);
  });
  document.querySelectorAll('.nav-item').forEach(el=>{
    const onclick=el.getAttribute('onclick')||'';
    el.classList.toggle('active',onclick.includes("'"+id+"'"));
  });
  // Trigger render for that section
  const fn={embed:renderPE,sdpa:renderSDPA,single:runSH,multi:runMH,masked:runMasked,cross:runCross,ffn:runFFN,encoder:runEncoder,decoder:runDecoder,train:renderTrain};
  if(fn[id])fn[id]();
}

// ====================================================
// TABS HELPER
// ====================================================
function activateTab(tabClass,panelClass,name){
  document.querySelectorAll('.'+tabClass).forEach(t=>{t.classList.toggle('on',t.textContent.trim()===name||t.dataset.tab===name);});
  document.querySelectorAll('.'+panelClass).forEach(p=>{p.classList.toggle('on',p.dataset.panel===name);});
}
function shTab(n){
  document.querySelectorAll('#s-single .tab').forEach((t,i)=>t.classList.toggle('on',['q','k','v'][i]===n));
  ['q','k','v'].forEach(x=>document.getElementById('sh-tp'+x).classList.toggle('on',x===n));
}
function maskTab(n){
  document.querySelectorAll('#s-train .tab').forEach((t,i)=>t.classList.toggle('on',['pad','causal'][i]===n));
  ['pad','causal'].forEach(x=>document.getElementById('mask-'+x).classList.toggle('on',x===n));
}

// ====================================================
// SECTION: EMBEDDINGS + PE
// ====================================================
function renderPE(){
  const sent=document.getElementById('pe-sent').value;
  const d=parseInt(document.getElementById('pe-dm').value);
  const tkns=toks(sent);
  seedRng(hashStr(tkns.join('')));
  const emb=Array.from({length:tkns.length},()=>Array.from({length:d},()=>+(rn()*0.5).toFixed(3)));
  const pos=tkns.map((_,i)=>pe(i,d).map(v=>+v.toFixed(3)));
  const final=emb.map((row,i)=>row.map((v,j)=>+(v+pos[i][j]).toFixed(3)));
  document.getElementById('pe-emb-tbl').innerHTML=matHtml(emb,tkns,null,'var(--q)');
  document.getElementById('pe-pos-tbl').innerHTML=matHtml(pos,tkns,null,'var(--k)');
  document.getElementById('pe-final-tbl').innerHTML=matHtml(final,tkns,null,'var(--ac2)');
  drawPECanvas(tkns.length,d);
}
function drawPECanvas(n,d){
  const cv=document.getElementById('pe-canvas');if(!cv)return;
  cv.width=cv.offsetWidth||500;cv.height=140;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
  ctx.clearRect(0,0,W,H);
  const cw=W/Math.min(d,20),ch=H/Math.min(n,8);
  for(let i=0;i<Math.min(n,8);i++){
    for(let j=0;j<Math.min(d,20);j++){
      const v=pe(i,Math.min(d,20)*2)[j];
      const a=(v+1)/2;
      const r=Math.round(80+175*a),g=Math.round(80+25*a),b=Math.round(110+145*(1-a));
      ctx.fillStyle=`rgb(${r},${g},${b})`;
      ctx.fillRect(j*cw,i*ch,cw-1,ch-1);
    }
  }
}

// ====================================================
// SECTION: SDPA
// ====================================================
function renderSDPA(){
  const sent=document.getElementById('sdpa-sent').value;
  const dk=parseInt(document.getElementById('sdpa-dk').value);
  const temp=parseFloat(document.getElementById('sdpa-t').value);
  const tkns=toks(sent);
  const{raw,attn}=selfAttn(tkns,dk,temp);
  document.getElementById('sdpa-raw-tbl').innerHTML=matHtml(raw,tkns,tkns,'var(--q)');
  document.getElementById('sdpa-attn-tbl').innerHTML=matHtml(attn,tkns,tkns,'var(--ac2)');
  setHmap('sdpa-hmap',attn,tkns,tkns,44);
  // Animate steps
  const steps=document.querySelectorAll('#sdpa-steps .sitem');
  let idx=0;
  clearInterval(window._sdpaTimer);
  window._sdpaTimer=setInterval(()=>{steps.forEach(s=>s.classList.remove('on'));steps[idx].classList.add('on');idx=(idx+1)%steps.length;},1800);
}

// ====================================================
// SECTION: SINGLE-HEAD
// ====================================================
let shState={},shSel=0,shAnim=null;
const shSentences=['The cat sat on mat','Attention is all you need','I love deep learning','Neural nets learn features','BERT reads both ways'];
function shRandom(){document.getElementById('sh-sent').value=shSentences[Math.floor(Math.random()*shSentences.length)];runSH();}
function runSH(){
  const sent=document.getElementById('sh-sent').value;
  const d=parseInt(document.getElementById('sh-dm').value);
  const temp=parseFloat(document.getElementById('sh-t').value);
  const tkns=toks(sent);
  shState=selfAttn(tkns,d,temp);shState.tkns=tkns;shState.d=d;
  shSel=Math.min(shSel,tkns.length-1);
  renderShTokens(tkns);
  document.getElementById('sh-tpq').innerHTML=matHtml(shState.Q,tkns,null,'var(--q)');
  document.getElementById('sh-tpk').innerHTML=matHtml(shState.K,tkns,null,'var(--k)');
  document.getElementById('sh-tpv').innerHTML=matHtml(shState.V,tkns,null,'var(--v)');
  setHmap('sh-hmap',shState.attn,tkns,tkns,44,'shSelectTok');
  renderShSel(shSel);
  drawFlowCanvas('sh-canvas',shState.attn,tkns,shSel);
  renderShOutput();
}
function renderShTokens(tkns){
  document.getElementById('sh-tokens').innerHTML=tkns.map((t,i)=>`<div class="tok${i===shSel?' on':''}" onclick="shSelectTok(${i})"><span style="color:var(--mt);font-size:.65rem">[${i}]</span> ${t}</div>`).join('');
}
function shSelectTok(i){shSel=i;renderShTokens(shState.tkns);renderShSel(i);drawFlowCanvas('sh-canvas',shState.attn,shState.tkns,i);highlightHmapRow('sh-hmap',i,shState.tkns[0].length||5);}
function renderShSel(i){
  if(!shState.attn)return;
  document.getElementById('sh-sel-lbl').textContent=`"${shState.tkns[i]}" pos ${i}`;
  document.getElementById('sh-sbars').innerHTML=sbarsHtml(shState.attn[i],shState.tkns);
}
function highlightHmapRow(id,rowIdx){
  document.querySelectorAll('#'+id+' .hcell').forEach(c=>{c.style.outline=parseInt(c.dataset.r)===rowIdx?'2px solid var(--ac)':'none';});
}
function renderShOutput(){
  const el=document.getElementById('sh-output');if(!el)return;
  el.innerHTML=shState.tkns.map((t,i)=>{
    const top=shState.attn[i].indexOf(Math.max(...shState.attn[i]));
    return`<div style="margin-bottom:10px"><div style="font-size:.75rem;margin-bottom:3px"><span style="color:var(--v);font-weight:700">${t}</span><span style="color:var(--mt);font-size:.67rem"> → attends to "${shState.tkns[top]}"</span></div>
    <div class="ovec">${shState.out[i].slice(0,8).map(v=>`<div class="odim" style="background:rgba(251,191,36,${Math.min(Math.abs(v)/0.6,0.3)})">${v.toFixed(2)}</div>`).join('')}</div></div>`;
  }).join('');
}

// ====================================================
// FLOW CANVAS (shared)
// ====================================================
let _flowAfId=null,_flowParts=[];
function drawFlowCanvas(canvasId,attn,tkns,focusIdx){
  const cv=document.getElementById(canvasId);if(!cv)return;
  cv.width=cv.offsetWidth||600;cv.height=280;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
  const n=tkns.length,pad=50,xSt=(W-pad*2)/(n-1||1);
  const nodes=tkns.map((t,i)=>({x:pad+i*xSt,label:t.substring(0,5),idx:i}));
  const yT=55,yB=225;
  if(_flowAfId)cancelAnimationFrame(_flowAfId);
  _flowParts=[];
  for(let i=0;i<n;i++){
    if(focusIdx!==undefined&&i!==focusIdx)continue;
    for(let j=0;j<n;j++){
      const w=attn[i][j];
      if(w>0.07)_flowParts.push({from:i,to:j,w,progress:Math.random()});
    }
  }
  function frame(){
    ctx.clearRect(0,0,W,H);
    // Draw arcs
    for(let i=0;i<n;i++){
      if(focusIdx!==undefined&&i!==focusIdx)continue;
      for(let j=0;j<n;j++){
        const w=attn[i][j];if(w<0.02)continue;
        const al=Math.pow(w,0.55);
        ctx.beginPath();ctx.moveTo(nodes[i].x,yT+18);
        const cx=(nodes[i].x+nodes[j].x)/2,cy=(yT+yB)/2-38*Math.sign(j-i)*(i===j?0:1);
        ctx.quadraticCurveTo(cx,cy,nodes[j].x,yB-18);
        const g=ctx.createLinearGradient(nodes[i].x,yT,nodes[j].x,yB);
        g.addColorStop(0,`rgba(124,111,255,${al})`);g.addColorStop(1,`rgba(56,217,169,${al})`);
        ctx.strokeStyle=g;ctx.lineWidth=Math.max(0.4,w*4.5);ctx.stroke();
      }
    }
    // Particles
    _flowParts.forEach(p=>{
      p.progress+=0.009;if(p.progress>1)p.progress=0;
      const fn=nodes[p.from],tn=nodes[p.to],t=p.progress;
      const cx=(fn.x+tn.x)/2,cy=(yT+yB)/2-38*Math.sign(p.to-p.from)*(p.from===p.to?0:1);
      const px=(1-t)*(1-t)*fn.x+2*(1-t)*t*cx+t*t*tn.x;
      const py=(1-t)*(1-t)*(yT+18)+2*(1-t)*t*cy+t*t*(yB-18);
      ctx.beginPath();ctx.arc(px,py,2+p.w*3,0,Math.PI*2);
      ctx.fillStyle=`rgba(255,255,255,${p.w*0.85})`;ctx.fill();
    });
    // Query nodes (top)
    nodes.forEach((nd,i)=>{
      const sel=focusIdx===undefined||i===focusIdx;
      const g=ctx.createRadialGradient(nd.x,yT,2,nd.x,yT,17);
      g.addColorStop(0,sel?'#a78bfa':'#2a2d45');g.addColorStop(1,sel?'#5b4fcf':'#1a1c30');
      ctx.beginPath();ctx.arc(nd.x,yT,17,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
      if(sel){ctx.strokeStyle='#a78bfa';ctx.lineWidth=2;ctx.stroke();}
      ctx.fillStyle='#fff';ctx.font='600 9px Inter';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(nd.label,nd.x,yT);
      ctx.fillStyle='rgba(160,160,200,.5)';ctx.font='8px Inter';ctx.fillText('Q',nd.x,yT-26);
    });
    // Key/Value nodes (bottom)
    nodes.forEach((nd,i)=>{
      const av=focusIdx!==undefined?attn[focusIdx][i]:attn.reduce((s,r)=>s+r[i],0)/n;
      const g=ctx.createRadialGradient(nd.x,yB,2,nd.x,yB,17);
      g.addColorStop(0,`rgba(52,211,153,${0.4+av*0.6})`);g.addColorStop(1,`rgba(16,80,55,${0.4+av*0.6})`);
      ctx.beginPath();ctx.arc(nd.x,yB,17,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
      ctx.strokeStyle=`rgba(52,211,153,${0.3+av*0.65})`;ctx.lineWidth=2;ctx.stroke();
      ctx.fillStyle='#fff';ctx.font='600 9px Inter';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(nd.label,nd.x,yB);
      ctx.fillStyle='rgba(160,200,160,.5)';ctx.font='8px Inter';ctx.fillText('K/V',nd.x,yB+26);
    });
    _flowAfId=requestAnimationFrame(frame);
  }
  frame();
}

// ====================================================
// SECTION: MULTI-HEAD
// ====================================================
let mhState={},mhSelHead=0;
function runMH(){
  const sent=document.getElementById('mh-sent').value;
  const d=parseInt(document.getElementById('mh-dm').value);
  const h=parseInt(document.getElementById('mh-h').value);
  const temp=parseFloat(document.getElementById('mh-t').value);
  const tkns=toks(sent);
  const dk=Math.max(2,Math.floor(d/h));
  // Compute h heads each with dk dimensions
  const heads=Array.from({length:h},(_,hi)=>{
    seedRng(hashStr(tkns.join(''))+hi*137);
    const emb=embed(tkns,dk);
    const Wq=cm(dk,dk),Wk=cm(dk,dk),Wv=cm(dk,dk);
    const Q=mm(emb,Wq),K=mm(emb,Wk),V=mm(emb,Wv);
    const KT=K[0].map((_,j)=>K.map(r=>r[j]));
    const raw=mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(dk)));
    const attn=raw.map(r=>smx(r,temp));
    const out=mm(attn,V);
    return{Q,K,V,attn,out};
  });
  // Final projection
  const concat=tkns.map((_,i)=>heads.flatMap(hd=>hd.out[i]));
  seedRng(hashStr('proj'));
  const Wo=cm(h*dk,d);
  const final=mm(concat,Wo).map(r=>r.map(v=>+v.toFixed(3)));
  mhState={tkns,heads,final,d,h,dk};
  renderMHTokens(tkns);
  renderMHHeads();
  mhSelectHead(mhSelHead<h?mhSelHead:0);
  renderMHOutput(final,tkns);
}
function renderMHTokens(tkns){
  document.getElementById('mh-tokens').innerHTML=tkns.map(t=>`<div class="tok">${t}</div>`).join('');
}
function renderMHHeads(){
  const{heads,tkns,h}=mhState;
  const wrap=document.getElementById('mh-heads');
  wrap.innerHTML=heads.map((hd,hi)=>{
    const cellPx=Math.min(32,Math.floor(160/tkns.length));
    const cells=hd.attn.map(row=>row.map(v=>{
      const a=Math.pow(v,0.55),r=Math.round(70+185*a),g=Math.round(70+25*a),b=Math.round(110+145*(1-a));
      return`<div class="hmc" style="background:rgba(${r},${g},${b},${0.3+a*0.7});width:${cellPx}px"></div>`;
    }).join('')).join('');
    return`<div class="head-box${hi===mhSelHead?' active':''}" onclick="mhSelectHead(${hi})">
      <div class="head-title">Head ${hi}</div>
      <div class="head-mini" style="grid-template-columns:repeat(${tkns.length},${cellPx}px)">${cells}</div>
      <div style="font-size:.62rem;color:var(--mt);margin-top:4px">d_k=${mhState.dk}</div>
    </div>`;
  }).join('');
}
function mhSelectHead(i){
  mhSelHead=i;
  document.querySelectorAll('.head-box').forEach((b,j)=>b.classList.toggle('active',j===i));
  document.getElementById('mh-sel-h').textContent='Head '+i;
  const{heads,tkns}=mhState;
  setHmap('mh-detail-hmap',heads[i].attn,tkns,tkns,44);
  document.getElementById('mh-detail-sbars').innerHTML=sbarsHtml(heads[i].attn[0],tkns);
}
function renderMHOutput(final,tkns){
  const el=document.getElementById('mh-output');if(!el)return;
  el.innerHTML=`<div style="font-size:.72rem;color:var(--mt);margin-bottom:8px">Final output after W_O projection (${final[0].length} dims):</div>`;
  el.innerHTML+=tkns.map((t,i)=>`<div style="margin-bottom:8px"><div style="font-size:.72rem;color:var(--v);font-weight:700;margin-bottom:3px">${t}</div>
    <div class="ovec">${final[i].slice(0,8).map(v=>`<div class="odim">${v.toFixed(2)}</div>`).join('')}</div></div>`).join('');
}

// ====================================================
// SECTION: MASKED ATTENTION
// ====================================================
function runMasked(){
  const sent=document.getElementById('mk-sent').value;
  const d=parseInt(document.getElementById('mk-dm').value);
  const tkns=toks(sent);
  const{raw,attn:unmasked}=selfAttn(tkns,d);
  // Apply causal mask
  const maskedRaw=raw.map((row,i)=>row.map((v,j)=>j>i?-Infinity:v));
  const maskedAttn=maskedRaw.map(row=>{
    const finite=row.map(v=>isFinite(v)?v:-1e9);
    return smx(finite);
  }).map((row,i)=>row.map((v,j)=>j>i?0:v)); // zero out for display
  // Display matrices
  const rawDisp=maskedRaw.map(row=>row.map(v=>isFinite(v)?v:-9.99));
  document.getElementById('mk-raw').innerHTML=matHtml(rawDisp,tkns,tkns,'var(--r)');
  document.getElementById('mk-attn').innerHTML=matHtml(maskedAttn,tkns,tkns,'var(--ac2)');
  setHmap('mk-hmap',maskedAttn,tkns,tkns,46);
}

// ====================================================
// SECTION: CROSS-ATTENTION
// ====================================================
function runCross(){
  const encSent=document.getElementById('ca-enc').value;
  const decSent=document.getElementById('ca-dec').value;
  const d=parseInt(document.getElementById('ca-dm').value);
  const encToks=toks(encSent),decToks=toks(decSent);
  seedRng(hashStr(encSent+decSent));
  const encEmb=embed(encToks,d),decEmb=embed(decToks,d);
  const Wq=cm(d,d),Wk=cm(d,d),Wv=cm(d,d);
  const Q=mm(decEmb,Wq),K=mm(encEmb,Wk),V=mm(encEmb,Wv);
  const KT=K[0].map((_,j)=>K.map(r=>r[j]));
  const raw =mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(d)));
  const attn=raw.map(r=>smx(r));
  // Token bars
  document.getElementById('ca-dec-toks').innerHTML=decToks.map(t=>`<div class="tok">${t}</div>`).join('');
  document.getElementById('ca-enc-toks').innerHTML=encToks.map(t=>`<div class="tok" style="color:var(--k)">${t}</div>`).join('');
  // Heatmap: rows=dec tokens, cols=enc tokens
  const el=document.getElementById('ca-hmap');
  const cellPx=Math.min(44,Math.floor(560/Math.max(encToks.length,1)));
  el.style.gridTemplateColumns=`repeat(${encToks.length},${cellPx}px)`;
  el.innerHTML=heatHtml(attn,decToks,encToks,cellPx);
  document.getElementById('ca-sbars').innerHTML=`<div class="card-title"><div class="dot" style="background:var(--ac2)"></div>Cross-Attention weights (decoder token 0 → encoder)</div>`+sbarsHtml(attn[0],encToks);
}

// ====================================================
// SECTION: FFN
// ====================================================
function runFFN(){
  const d=parseInt(document.getElementById('ffn-dm').value);
  const ff=parseInt(document.getElementById('ffn-ff').value);
  const el=document.getElementById('ffn-vis');
  const x=Array.from({length:d},()=>+(rn()*0.5).toFixed(3));
  const W1=Array.from({length:d},()=>Array.from({length:ff},()=>+(rn()*0.3).toFixed(3)));
  const b1=Array.from({length:ff},()=>+(rn()*0.1).toFixed(3));
  const h1=x.map==undefined?[]:Array.from({length:ff},(_,j)=>Math.max(0,x.reduce((s,v,i)=>s+v*W1[i][j],0)+b1[j]));
  const W2=Array.from({length:ff},()=>Array.from({length:d},()=>+(rn()*0.3).toFixed(3)));
  const b2=Array.from({length:d},()=>+(rn()*0.1).toFixed(3));
  const out=Array.from({length:d},(_,j)=>h1.reduce((s,v,i)=>s+v*W2[i][j],0)+b2[j]);
  const res=x.map((v,i)=>+(v+out[i]).toFixed(3));
  const mean=res.reduce((a,b)=>a+b,0)/res.length;
  const std=Math.sqrt(res.reduce((s,v)=>s+(v-mean)**2,0)/res.length)||1;
  const ln=res.map(v=>+((v-mean)/std).toFixed(3));
  el.innerHTML=`
    <div style="font-size:.72rem;color:var(--mt);margin-bottom:6px">Input x (${d} dims):</div>
    <div class="ovec">${x.map(v=>`<div class="odim" style="color:var(--q)">${v.toFixed(2)}</div>`).join('')}</div>
    <div style="font-size:.72rem;color:var(--mt);margin:6px 0 4px">After FFN (${ff}→${d}):</div>
    <div class="ovec">${out.map(v=>`<div class="odim" style="color:var(--ac3)">${v.toFixed(2)}</div>`).join('')}</div>`;
  document.getElementById('ffn-ln-vis').innerHTML=`
    <div style="font-size:.72rem;color:var(--mt);margin-bottom:6px">Residual x + FFN(x):</div>
    <div class="ovec">${res.map(v=>`<div class="odim" style="color:var(--ac)">${v.toFixed(2)}</div>`).join('')}</div>
    <div style="font-size:.72rem;color:var(--mt);margin:6px 0 4px">After LayerNorm (μ=${mean.toFixed(2)}, σ=${std.toFixed(2)}):</div>
    <div class="ovec">${ln.map(v=>`<div class="odim" style="color:var(--ac2)">${v.toFixed(2)}</div>`).join('')}</div>`;
}

// ====================================================
// SECTION: ENCODER
// ====================================================
function runEncoder(){
  const sent=document.getElementById('enc-sent').value;
  const nLayers=parseInt(document.getElementById('enc-l').value);
  const nHeads=parseInt(document.getElementById('enc-h').value);
  const d=8,temp=1;
  const tkns=toks(sent);
  const vis=document.getElementById('enc-layer-vis');
  const norms=[];
  let repr=embed(tkns,d);
  let html='';
  for(let l=0;l<nLayers;l++){
    seedRng(hashStr(tkns.join(''))+l*211);
    const dk=Math.max(2,Math.floor(d/nHeads));
    const heads=Array.from({length:nHeads},(_,hi)=>{
      seedRng(hashStr(tkns.join(''))+l*211+hi*37);
      const Wq=cm(d,dk),Wk=cm(d,dk),Wv=cm(d,dk);
      const Q=mm(repr,Wq),K=mm(repr,Wk),V=mm(repr,Wv);
      const KT=K[0].map((_,j)=>K.map(r=>r[j]));
      const raw=mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(dk)));
      const attn=raw.map(r=>smx(r,temp));
      return{attn,out:mm(attn,V)};
    });
    // Avg attention for display
    const attnAvg=tkns.map((_,i)=>tkns.map((_,j)=>+(heads.reduce((s,h)=>s+h.attn[i][j],0)/nHeads).toFixed(3)));
    const norm=repr.map(r=>{const m=r.reduce((a,b)=>a+b,0)/r.length;const s=Math.sqrt(r.reduce((a,v)=>a+(v-m)**2,0)/r.length)||1;return r.map(v=>+((v-m)/s).toFixed(3));});
    repr=norm;
    const avgNorm=norm.reduce((s,r)=>s+r.reduce((a,b)=>a+Math.abs(b),0)/r.length,0)/norm.length;
    norms.push(avgNorm);
    html+=`<div style="margin-bottom:14px">
      <div style="font-size:.72rem;color:var(--ac);font-weight:700;margin-bottom:6px">Layer ${l+1} — Avg attention (${nHeads} head${nHeads>1?'s':''})</div>
      <div class="hmap" style="grid-template-columns:repeat(${tkns.length},40px)">${heatHtml(attnAvg,tkns,tkns,40)}</div>
    </div>`;
  }
  vis.innerHTML=html;
  drawNormCanvas(norms);
}
function drawNormCanvas(norms){
  const cv=document.getElementById('enc-canvas');if(!cv)return;
  cv.width=cv.offsetWidth||600;cv.height=180;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height,n=norms.length;
  ctx.clearRect(0,0,W,H);
  const mx=Math.max(...norms)*1.1||1;
  const xs=Array.from({length:n},(_,i)=>60+i*(W-80)/(n-1||1));
  ctx.beginPath();ctx.strokeStyle='var(--bd)';
  for(let i=0;i<=4;i++){const y=H-20-(H-40)*i/4;ctx.moveTo(40,y);ctx.lineTo(W-10,y);}
  ctx.stroke();
  ctx.beginPath();ctx.strokeStyle='rgba(124,111,255,.8)';ctx.lineWidth=2;
  xs.forEach((x,i)=>{const y=H-20-(H-40)*(norms[i]/mx);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
  ctx.stroke();
  xs.forEach((x,i)=>{
    const y=H-20-(H-40)*(norms[i]/mx);
    ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.fillStyle='var(--ac)';ctx.fill();
    ctx.fillStyle='var(--tx)';ctx.font='10px Inter';ctx.textAlign='center';
    ctx.fillText('L'+(i+1),x,H-5);ctx.fillText(norms[i].toFixed(2),x,y-10);
  });
}

// ====================================================
// SECTION: DECODER
// ====================================================
function runDecoder(){
  const encSent=document.getElementById('dec-enc').value;
  const decSent=document.getElementById('dec-dec').value;
  const d=8,temp=1;
  const encToks=toks(encSent),decToks=toks(decSent);
  // 1. Masked self-attention
  const{attn:selfAttnW}=selfAttn(decToks,d);
  const masked=selfAttnW.map((row,i)=>row.map((v,j)=>j>i?0:v));
  // 2. Cross-attention
  seedRng(hashStr(encSent+decSent));
  const encEmb=embed(encToks,d),decEmb=embed(decToks,d);
  const Wq=cm(d,d),Wk=cm(d,d),Wv=cm(d,d);
  const Q=mm(decEmb,Wq),K=mm(encEmb,Wk),V=mm(encEmb,Wv);
  const KT=K[0].map((_,j)=>K.map(r=>r[j]));
  const crossRaw=mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(d)));
  const crossAttn=crossRaw.map(r=>smx(r));
  // 3. FFN output
  const out=crossAttn.map((row,i)=>{
    const v=V.map(r=>r[i]);
    return row.reduce((s,w,j)=>s.map((x,k)=>x+w*V[j][k]),Array(d).fill(0)).map(x=>+x.toFixed(3));
  });
  setHmap('dec-masked-hmap',masked,decToks,decToks,44);
  const el=document.getElementById('dec-cross-hmap');
  const cellPx=Math.min(44,Math.floor(300/Math.max(encToks.length,1)));
  el.style.gridTemplateColumns=`repeat(${encToks.length},${cellPx}px)`;
  el.innerHTML=heatHtml(crossAttn,decToks,encToks,cellPx);
  const fEl=document.getElementById('dec-ffn-out');
  fEl.innerHTML=decToks.map((t,i)=>`<div style="margin-bottom:8px"><div style="font-size:.72rem;color:var(--ac2);font-weight:700">${t}</div>
    <div class="ovec">${out[i].slice(0,6).map(v=>`<div class="odim">${v.toFixed(2)}</div>`).join('')}</div></div>`).join('');
}

// ====================================================
// SECTION: TRAINING
// ====================================================
function renderTrain(){
  renderLoss();
  renderPadMask();
  renderCausalMask();
  renderTrainConcepts();
}
function renderLoss(){
  const conf=parseFloat(document.getElementById('tr-conf').value);
  const cv=document.getElementById('loss-canvas');if(!cv)return;
  cv.width=cv.offsetWidth||500;cv.height=160;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
  ctx.clearRect(0,0,W,H);
  const xs=Array.from({length:100},(_,i)=>0.01+i*0.0098);
  const ys=xs.map(x=>-Math.log(x));
  const mx=Math.max(...ys.slice(0,50));
  // Grid
  ctx.strokeStyle='rgba(255,255,255,.06)';ctx.lineWidth=1;
  for(let i=0;i<=4;i++){ctx.beginPath();ctx.moveTo(40,10+i*(H-20)/4);ctx.lineTo(W-10,10+i*(H-20)/4);ctx.stroke();}
  // Curve
  ctx.beginPath();ctx.strokeStyle='rgba(124,111,255,.7)';ctx.lineWidth=2.5;
  xs.forEach((x,i)=>{const px=40+i*(W-50)/99,py=H-10-(H-20)*Math.min(ys[i]/mx,1);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py);});
  ctx.stroke();
  // Current point
  const curX=40+(conf-0.01)/(0.99-0.01)*(W-50);
  const curY=H-10-(H-20)*Math.min(-Math.log(conf)/mx,1);
  ctx.beginPath();ctx.arc(curX,curY,6,0,Math.PI*2);ctx.fillStyle='var(--ac3)';ctx.fill();
  ctx.fillStyle='var(--tx)';ctx.font='11px Inter';ctx.textAlign='center';ctx.fillText(`conf=${conf.toFixed(2)} → loss=${(-Math.log(conf)).toFixed(3)}`,curX,curY-14);
  ctx.fillStyle='rgba(124,111,255,.15)';ctx.fillRect(40,curY,curX-40,H-10-curY);
}
function renderPadMask(){
  const n=5,padIdx=4;
  const mat=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>j===padIdx?-1:1));
  const el=document.getElementById('pad-hmap');
  el.style.gridTemplateColumns=`repeat(${n},44px)`;
  const labels=['The','cat','sat','on','[PAD]'];
  el.innerHTML=mat.map((row,i)=>row.map((v,j)=>{
    const c=v<0?'rgba(244,63,94,.7)':'rgba(52,211,153,.5)';
    return`<div class="hcell" style="width:44px;height:44px;background:${c};color:#fff">${v<0?'×':'✓'}</div>`;
  }).join('')).join('');
}
function renderCausalMask(){
  const n=5;
  const mat=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>j<=i?1:-1));
  const el=document.getElementById('causal-hmap');
  el.style.gridTemplateColumns=`repeat(${n},44px)`;
  el.innerHTML=mat.map(row=>row.map(v=>`<div class="hcell" style="width:44px;height:44px;background:${v>0?'rgba(124,111,255,.6)':'rgba(244,63,94,.4)'};color:#fff">${v>0?'✓':'×'}</div>`).join('')).join('');
}
function renderTrainConcepts(){
  const el=document.getElementById('train-concepts');if(!el)return;
  const items=[
    {icon:'📉',name:'Learning Rate',desc:'~1e-4 with warmup + decay'},
    {icon:'🎲',name:'Dropout',desc:'0.1 on attention & FFN'},
    {icon:'🔢',name:'Batch Size',desc:'Tokens per batch ~4096'},
    {icon:'🔥',name:'Warmup Steps',desc:'4000 steps linear ramp'},
    {icon:'⚖️',name:'Weight Decay',desc:'L2 regularisation 0.01'},
    {icon:'✂️',name:'Gradient Clip',desc:'Max norm 1.0'},
  ];
  el.innerHTML=items.map(it=>`<div class="concept-card"><div class="icon">${it.icon}</div><h4>${it.name}</h4><p>${it.desc}</p></div>`).join('');
}

// ====================================================
// OVERVIEW CONCEPTS
// ====================================================
function renderOverviewConcepts(){
  const el=document.getElementById('concept-grid');if(!el)return;
  const items=[
    {icon:'🔤',name:'Embeddings + PE',desc:'Position-aware token vectors',sec:'embed'},
    {icon:'🎯',name:'Scaled Dot-Product',desc:'QKᵀ/√dk attention',sec:'sdpa'},
    {icon:'👁️',name:'Single-Head',desc:'One attention pattern',sec:'single'},
    {icon:'🧠',name:'Multi-Head',desc:'h parallel attention heads',sec:'multi'},
    {icon:'🔒',name:'Masked Attention',desc:'Causal, no future peek',sec:'masked'},
    {icon:'🔗',name:'Cross-Attention',desc:'Encoder→Decoder bridge',sec:'cross'},
    {icon:'⚙️',name:'FFN + LayerNorm',desc:'Per-token MLP + residual',sec:'ffn'},
    {icon:'📥',name:'Encoder',desc:'Bidirectional context',sec:'encoder'},
    {icon:'📤',name:'Decoder',desc:'Autoregressive generation',sec:'decoder'},
    {icon:'📈',name:'Training',desc:'Loss, masking, teacher forcing',sec:'train'},
  ];
  el.innerHTML=items.map(it=>`<div class="concept-card" onclick="goto('${it.sec}')"><div class="icon">${it.icon}</div><h4>${it.name}</h4><p>${it.desc}</p></div>`).join('');
}

// ====================================================
// INIT
// ====================================================
window.addEventListener('resize',()=>{
  if(document.getElementById('s-single').classList.contains('active'))drawFlowCanvas('sh-canvas',shState.attn,shState.tkns,shSel);
  if(document.getElementById('s-embed').classList.contains('active'))renderPE();
  if(document.getElementById('s-train').classList.contains('active'))renderLoss();
  if(document.getElementById('s-encoder').classList.contains('active'))drawNormCanvas&&runEncoder();
});
renderOverviewConcepts();
renderPE();
renderSDPA();
runSH();
runMH();
runMasked();
runCross();
runFFN();
renderTrain();
</script>
</body>
</html>
"""

with open('transformer_complete.html', 'ab') as f:
    f.write(js.encode('utf-8'))
print('done, total:', len(open('transformer_complete.html','rb').read()), 'bytes')
