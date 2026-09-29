async function api(url, options={}) {
  const res = await fetch(url, {credentials:'same-origin', ...options});
  let data = {};
  try { data = await res.json(); } catch {}
  if (!res.ok) throw new Error(data.detail || data.message || `Request failed (${res.status})`);
  return data;
}

function money(value, currency='INR') {
  return new Intl.NumberFormat('en-IN', {style:'currency', currency, maximumFractionDigits:0}).format(value || 0);
}
function showMsg(el, text, good=false) { if (!el) return; el.textContent=text; el.className=`msg ${good?'good':'bad'}`; }

async function submitPlanner(form) {
  const planner = form.dataset.planner;
  const msg = document.getElementById('formMsg');
  try {
    let response;
    if (planner === 'jewelry') {
      const fd = new FormData(form);
      response = await api('/api/generate-jewelry', {method:'POST', body:fd});
    } else {
      const data = Object.fromEntries(new FormData(form).entries());
      data.budget = Number(data.budget);
      if (planner === 'home') data.rooms = data.rooms.split(',').map(x=>x.trim()).filter(Boolean);
      if (planner === 'party') data.guests = Number(data.guests);
      response = await api(`/api/generate-${planner}`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    }
    showMsg(msg, 'Plan generated. Opening recommendations…', true);
    // Save the returned object temporarily; history contains the persistent id.
    const history = await api('/api/history');
    const latest = history[0];
    window.location.href = `/results/${latest.id}`;
  } catch (e) { showMsg(msg, e.message); }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('plannerForm');
  if (form) form.addEventListener('submit', e => { e.preventDefault(); submitPlanner(form); });

  const login = document.getElementById('loginForm');
  if (login) login.addEventListener('submit', async e => {
    e.preventDefault(); const msg=document.getElementById('formMsg');
    try { await api('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(login)))}); location.href='/dashboard'; }
    catch(err){showMsg(msg,err.message);}
  });
  const register = document.getElementById('registerForm');
  if (register) register.addEventListener('submit', async e => {
    e.preventDefault(); const msg=document.getElementById('formMsg'); const d=Object.fromEntries(new FormData(register));
    if(d.password!==d.confirm){showMsg(msg,'Passwords do not match');return;}
    try { await api('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:d.email,password:d.password})}); await api('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:d.email,password:d.password})}); location.href='/dashboard'; }
    catch(err){showMsg(msg,err.message);}
  });
  const logout=document.getElementById('logoutBtn'); if(logout) logout.addEventListener('click', async()=>{try{await api('/api/auth/logout',{method:'POST'});location.href='/';}catch{location.href='/';}});
});

async function loadDashboard(){
  try { const d=await api('/api/session-data'); document.getElementById('welcome').textContent=`Signed in as ${d.user.email}`; const stats=document.getElementById('stats'); stats.innerHTML=Object.entries({Home:d.recommendation_counts.home||0,Party:d.recommendation_counts.party||0,Jewelry:d.recommendation_counts.jewelry||0}).map(([k,v])=>`<article class="card stat"><small>${k} plans</small><strong>${v}</strong></article>`).join(''); }
  catch(e){location.href='/login';}
}

async function loadHistory(){
  const box=document.getElementById('history'); try{const rows=await api('/api/history'); if(!rows.length){box.innerHTML='<div class="card"><h2>No plans yet</h2><p>Create your first budget plan.</p></div>';return;} box.innerHTML=rows.map(r=>`<a class="card history-row" href="/results/${r.id}"><div><span class="pill">${r.planner_type}</span><h2>${r.result.title}</h2><p>${r.result.summary}</p></div><div><strong>${money(r.result.budget,r.result.currency)}</strong><small>${r.created_at}</small></div></a>`).join('');}catch(e){box.textContent=e.message;}}

async function loadResult(id){
  const box=document.getElementById('result'); try{const d=await api(`/api/recommendations-details/${id}`), r=d.result; box.innerHTML=`<div class="section-head"><div><span class="pill">${r.source_mode==='gemini'?'GEMINI':'OFFLINE FALLBACK'}</span><h1>${r.title}</h1><p>${r.summary}</p></div><strong class="total">${money(r.budget,r.currency)}</strong></div><div class="grid two"><div class="card"><h2>Budget allocation</h2><div class="bars">${Object.entries(r.budget_breakdown).map(([k,v])=>`<div><div class="barlabel"><span>${k}</span><b>${money(v,r.currency)}</b></div><div class="bar"><i style="width:${Math.min(100,(v/r.budget)*100)}%"></i></div></div>`).join('')}</div></div><div class="card"><h2>Tips</h2><ul>${r.tips.map(x=>`<li>${x}</li>`).join('')}</ul>${r.image_analysis?`<h3>Outfit image notes</h3><p>${r.image_analysis}</p>`:''}</div></div><div class="grid two recommendations">${r.items.map(i=>`<article class="card"><span class="pill">${i.category}</span><h2>${i.name}</h2><strong>${money(i.estimated_price,r.currency)}</strong><p>${i.reason}</p><small>Search suggestion on ${i.platform}</small><a class="btn secondary" target="_blank" rel="noopener" href="${i.search_url}">Open ${i.platform}</a></article>`).join('')}</div><p class="disclaimer">${r.disclaimer}</p>`; }catch(e){box.innerHTML=`<div class="card"><h2>Could not load this plan</h2><p>${e.message}</p></div>`;}
}
