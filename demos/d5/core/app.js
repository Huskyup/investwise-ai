/* Browser presentation only. No answer selection, model output or secrets originate here. */
'use strict';
const $ = id => document.getElementById(id);
let token = location.hash.slice(1) || sessionStorage.getItem('d5-token');
if (location.hash) { sessionStorage.setItem('d5-token', token); history.replaceState(null, '', '/'); }
let state, busy = false;
const labels = {D5_SALARY:'Salary or wages',D5_PENSION_PAYMENTS:'Pension payments',D5_WITHDRAWALS:'Savings / investment withdrawals (category)',D5_BENEFITS_SUPPORT:'Benefits / regular support (category)',D5_NO_REGULAR:'No regular source'};
function node(tag, text, cls) { const el=document.createElement(tag); el.textContent=text; if(cls) el.className=cls; return el; }
function message(who, text, cls) { const el=node('div','',`message ${cls}`); el.append(node('span',who,'who'),node('div',text)); return el; }
function lock(value) { busy=value; document.body.classList.toggle('busy',value); document.querySelectorAll('button,textarea').forEach(e=>e.disabled=value || !!state?.stopped); if(!value && state) { $('confirm').disabled=!state.can_confirm || state.stopped; $('next').disabled=!state.next_step || state.stopped; } }
function showError(text) { $('error').textContent=text; $('error').hidden=false; $('refresh').hidden=false; }
function render(data) {
 state=data; const live=data.mode==='live';
 $('mode').textContent=live?'LIVE · ML + GPT-6.1 Sol · low':'RECORDED OUTPUT REPLAY · GPT calls: 0'; $('mode').classList.toggle('live',live);
 $('notice').textContent=live?'Live free text. The existing interpreter runs only when you submit a reply. GPT requires your existing account access; a service failure stops this session.':'Offline reproduction using current local ML and previously saved GPT outputs. Only the fixed recorded sequence is available. This is not live interpretation of new text; no GPT or sign-in request is made.';
 $('notice').classList.toggle('live',live); $('reply-form').hidden=!live; $('controls').hidden=!live;
 $('history').textContent=`${data.history_count} interpreted replies in memory`;
 $('status').textContent=data.status; $('bucket').textContent=data.bucket || (data.model_uncertain?'Model uncertainty — not customer indecision':'No financial bucket selected');
 $('category').textContent=data.option_label?`Questionnaire category: ${data.option_label}`:'No accepted financial answer';
 $('ml-count').textContent=data.ml_calls; $('gpt-count').textContent=data.gpt_calls; $('replay-count').textContent=data.replayed_outputs;
 const transcript=$('transcript'); transcript.replaceChildren(message('INVESTWISE · D5',data.question,'assistant'));
 data.events.forEach(event=>{ transcript.append(message('YOU',event.input,'user')); const response=message('INVESTWISE',event.texts.join('\n\n'),'assistant'); if(event.bucket) response.prepend(node('span',event.bucket,'bucket-tag')); response.append(node('div',`${event.route} · ML ${event.ml_calls} · GPT ${event.gpt_calls} · recorded ${event.replayed_outputs}`,'audit')); transcript.append(response); });
 transcript.scrollTop=transcript.scrollHeight;
 $('facts').replaceChildren();
 data.facts.forEach(fact=>{ const el=node('div','','fact'); el.append(node('strong',labels[fact.source_category]||fact.source_category),node('p',`Living-cost use: ${fact.pays_living_costs} · Time: ${fact.time} · Owner: ${fact.owner}`),node('blockquote',fact.evidence)); $('facts').append(el); });
 $('step-title').textContent=live?'Optional guide · existing example':'Recorded walkthrough'; $('step-count').textContent=`${data.step} / ${data.steps_total} steps`;
 $('step-purpose').textContent=data.next_step?data.next_step.purpose:'Walkthrough complete. No new semantic accuracy is established by replay.'; $('step-text').textContent=data.next_step?.text||'';
 $('next').textContent=live?'Put this step in the answer box':'Run next recorded step';
 if(data.error) showError(data.error); lock(false);
}
async function request(path, options={}) { const response=await fetch(path,{...options,headers:{'X-D5-Token':token,'Content-Type':'application/json'},cache:'no-store'}); const data=await response.json(); if(!response.ok) throw new Error(data.error||'Local request failed'); return data; }
async function act(text) {
 if(busy || !state || state.stopped) return; lock(true); $('error').hidden=true; $('refresh').hidden=true;
 try { render(await request('/api/action',{method:'POST',body:JSON.stringify({version:state.version,text})})); $('reply').value=''; }
 catch(error) { showError(error.message+'. Do not resend: refresh state to see whether the action completed.'); /* keep actions locked until an explicit read-only refresh */ $('refresh').disabled=false; }
}
$('reply-form').addEventListener('submit',event=>{event.preventDefault(); const text=$('reply').value.trim(); if(text) act(text);});
document.querySelectorAll('[data-command]').forEach(button=>button.addEventListener('click',()=>act(button.dataset.command)));
$('next').addEventListener('click',()=>{ if(state.mode==='replay') act(null); else { $('reply').value=state.next_step.text; $('reply').focus(); } });
$('refresh').addEventListener('click',async()=>{ try { render(await request('/api/state')); $('refresh').hidden=true; $('error').hidden=!!state.error?false:true; } catch(error) { showError(error.message); $('refresh').disabled=false; } });
if(!token) { showError('Open the complete local URL printed by the demo command.'); lock(true); }
else request('/api/state').then(render).catch(error=>showError(error.message));
