'use strict';
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const token = $('meta[name="jarvis-token"]').content;
let state = {tasks: [], memories: [], messages: [], settings: {}}, busy = false, listening = false;
let alerts = [], toastTimer, currentView = 'home', connection = null;
async function api(path, data) {
  const response = await fetch('/api/' + path, {method: data === undefined ? 'GET' : 'POST', headers: {'X-Jarvis-Token': token, 'Content-Type': 'application/json'}, ...(data === undefined ? {} : {body: JSON.stringify(data)})});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Could not complete the request.');
  return result;
}
function toast(message) { $('#toast').textContent = message; $('#toast').hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => $('#toast').hidden = true, 6000); }
function el(tag, cls, text) { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; }
function button(text, cls, fn, label) { const b = el('button', cls, text); b.type = 'button'; if (label) b.setAttribute('aria-label', label); b.addEventListener('click', () => Promise.resolve().then(fn).catch(e => toast(e.message))); return b; }
function view(name) {
  currentView = name;
  $$('.page').forEach(n => n.hidden = n.id !== 'view-' + name);
  $$('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.view === name));
  $('#page-label').textContent = ({home: 'COMMAND CENTER', tasks: 'TASKS & REMINDERS', memory: 'MEMORY', settings: 'SETTINGS'})[name];
  if (name === 'settings') fillSettings();
}
function fillSettings() { const s = state.settings; $('#setting-name').value = s.name; $('#setting-model').value = s.model; $('#setting-language').value = s.language; $('#setting-speak').checked = s.speak; $('#data-path').textContent = state.data_dir; }
function updateClock() {
  const date = new Date(); $('#clock').textContent = date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
  $('#today-label').textContent = date.toLocaleDateString('en', {weekday:'long', month:'long', day:'numeric'}).toUpperCase() + ' / YOUR PERSONAL CO-PILOT';
  const hour = date.getHours(); const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  $('#greeting').replaceChildren(document.createTextNode(`${greeting}, ${state.settings.name || 'Prasanna'}`), el('span', '', '.'));
}
function renderMessages() {
  const box = $('#messages'); box.replaceChildren();
  const messages = state.messages.length ? state.messages : [{role: 'assistant', content: `Hello ${state.settings.name}. I’m JARVIS, your personal assistant.\nSet a reminder, save a thought, or let’s work through your day.`, created: Date.now()/1000}];
  messages.forEach(m => {
    const row = el('div', 'message ' + m.role); row.append(el('div', 'message-avatar', m.role === 'user' ? (state.settings.name || 'P')[0].toUpperCase() : '✦'));
    const body = el('div', 'message-content'); const name = el('div', 'message-name', m.role === 'user' ? state.settings.name : 'JARVIS');
    name.append(el('span', '', new Date(m.created*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})));
    body.append(name, el('div', 'message-text', m.content)); row.append(body); box.append(row);
  }); box.scrollTop = box.scrollHeight;
}
function taskRow(task, compact=false) {
  const row = el('div', 'task-row' + (task.done ? ' done' : ''));
  const check = button(task.done ? '✓' : '', 'task-check', async () => { await api('tasks/toggle', {id:task.id}); await refresh(false); }, (task.done ? 'Reopen ' : 'Complete ') + task.title);
  check.setAttribute('aria-pressed', String(!!task.done)); row.append(check);
  const details = el('div', 'task-details'); details.append(el('div', 'task-title', task.title));
  const overdue = task.due && task.due*1000 < Date.now() && !task.done;
  const dueText = task.due ? new Date(task.due*1000).toLocaleString([], {month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}) : 'Whenever you’re ready';
  details.append(el('span', 'task-time' + (overdue ? ' overdue' : ''), (overdue ? 'Due · ' : '') + dueText)); row.append(details);
  if (!compact) row.append(button('×', 'delete-button', async () => { await api('tasks/delete',{id:task.id}); await refresh(false); }, 'Delete ' + task.title));
  return row;
}
function empty(text) { const box = el('div','empty-state'); box.append(el('span','empty-symbol','◇'), document.createTextNode(text)); return box; }
function renderTasks() {
  const pending = state.tasks.filter(t=>!t.done); $('#task-count').textContent = pending.length; $('#pending-badge').textContent = pending.length + ' PENDING';
  $('#focus-tasks').replaceChildren(...(pending.length ? pending.slice(0,3).map(t=>taskRow(t,true)) : [empty('A little space to breathe. Add your first task below.')]));
  $('#all-tasks').replaceChildren(...(state.tasks.length ? state.tasks.map(t=>taskRow(t)) : [empty('No tasks yet. Start with one small next step.')]));
}
function renderMemories() {
  const rows = state.memories.map(m => { const row = el('div', 'memory-item'); row.append(el('span','','◇'), el('p','',m.content), button('×', 'delete-button', async()=>{await api('memories/delete',{id:m.id});await refresh(false);}, 'Delete memory')); return row; });
  $('#memory-list').replaceChildren(...(rows.length ? rows : [empty('Nothing saved yet. Add a preference or a useful detail.')]));
}
async function refresh(messages=true) {
  state = await api('state'); $('#profile-name').textContent = state.settings.name; $('.avatar').textContent = state.settings.name[0].toUpperCase();
  $('#voice-status').textContent = state.windows ? 'Windows push-to-talk' : 'Windows voice only';
  if (messages) renderMessages(); renderTasks(); renderMemories(); updateClock();
}
async function speak(text) { if (state.settings.speak && state.windows) { try { await api('voice/speak', {text}); } catch(e) { toast(e.message); } } }
async function send(text) {
  text = text.trim(); if (!text || busy) return;
  busy = true; $('#chat-input').value = ''; $('#thinking').hidden = false; $('.send-button').disabled = true; $('#mic').disabled = true; $('#orb').classList.add('busy'); $('#core-status').textContent = 'On it.';
  state.messages.push({role:'user',content:text,created:Date.now()/1000}); renderMessages();
  try { const result = await api('chat', {text}); await refresh(); speak(result.reply); }
  catch(e) { toast(e.message); await refresh().catch(()=>{}); }
  finally { busy=false; $('#thinking').hidden=true; $('.send-button').disabled=false; $('#mic').disabled=false; $('#orb').classList.remove('busy'); $('#core-status').textContent='Your day, assisted.'; $('#chat-input').focus(); }
}
function openTask() { $('#task-form').reset(); $('#task-dialog').showModal(); $('#task-title').focus(); }
async function checkModels() {
  $('#check-model').disabled=true; $('#model-result').textContent='Checking Ollama…';
  try {
    connection=await api('models'); const available=connection.connected && connection.models.includes(state.settings.model);
    $('#model-result').textContent = connection.connected ? (connection.models.length ? 'Installed: '+connection.models.join(', ') : 'Ollama is running. Download a local model first.') : connection.message;
    $('#model-list').replaceChildren(...connection.models.map(name=>{const n=el('option');n.value=name;return n;}));
    $('#connection-title').textContent=available?'Your AI is connected':'Connect your AI';
    $('#connection-detail').textContent=available?`Using ${state.settings.model} on this computer. Ready for questions, coding and conversation.`:'Add a local model to unlock conversation, coding help and bigger ideas.';
    $('#connect-link').textContent=available?'Manage AI ↗':'Set up AI ↗'; $('#chat-mode').textContent=available?'Local AI connected':'Local commands';
  } catch(e) { $('#model-result').textContent=e.message; }
  finally { $('#check-model').disabled=false; }
}
async function pollAlerts() {
  if ($('#alert-dialog').open || $('#task-dialog').open) return;
  try {
    const data=await api('alerts'); if (!data.alerts.length) return;
    alerts=data.alerts; $('#alert-list').replaceChildren(...alerts.map(a=>el('p','',a.title))); $('#alert-dialog').showModal();
    speak('Reminder. '+alerts.map(a=>a.title).join('. '));
  } catch(e) { /* Retry on the next poll; do not discard reminders. */ }
}
$$('.nav-item').forEach(n=>n.addEventListener('click',()=>view(n.dataset.view)));
$('.brand').addEventListener('click',e=>{e.preventDefault();view('home');});
$$('[data-command]').forEach(n=>n.addEventListener('click',()=>{view('home');send(n.dataset.command);}));
$('#chat-form').addEventListener('submit',e=>{e.preventDefault();send($('#chat-input').value);});
$('#chat-input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();send(e.target.value);}});
$('#clear-chat').addEventListener('click',async()=>{if(!state.messages.length)return;if(!confirm('Clear this conversation? Tasks and memories will stay.'))return;try{await api('chat/clear',{});await refresh();}catch(e){toast(e.message);}});
$('#mic').addEventListener('click',async()=>{
  if(listening||busy)return;listening=true;$('#mic').disabled=true;$('#mic').classList.add('listening');$('#orb').classList.add('listening');$('#core-status').textContent='I’m listening.';$('#core-detail').textContent='Speak in English. Review your words before sending.';
  try{const r=await api('voice/listen',{});if(r.text){$('#chat-input').value=r.text;$('#chat-input').focus();toast('Transcript ready. Review it, then press Enter to send.');}else{toast('No clear speech heard. Try again or type your message.');}}
  catch(e){toast(e.message);}finally{listening=false;$('#mic').disabled=busy;$('#mic').classList.remove('listening');$('#orb').classList.remove('listening');$('#core-status').textContent='Your day, assisted.';$('#core-detail').textContent='Think out loud. Make a plan. Take the next step.';}
});
['#new-reminder','#quick-add-task','#add-reminder-page'].forEach(s=>$(s).addEventListener('click',openTask));
$('#close-task').addEventListener('click',()=>$('#task-dialog').close());
$('#task-form').addEventListener('submit',async e=>{e.preventDefault();const submit=e.submitter;submit.disabled=true;try{const due=$('#task-due').value;await api('tasks/add',{title:$('#task-title').value,due:due?new Date(due).getTime()/1000:null});$('#task-dialog').close();await refresh(false);toast('Saved. Your next step is ready.');}catch(err){toast(err.message);}finally{submit.disabled=false;}});
$('#memory-form').addEventListener('submit',async e=>{e.preventDefault();e.submitter.disabled=true;try{await api('memories/add',{content:$('#memory-input').value});$('#memory-input').value='';await refresh(false);toast('Memory saved.');}catch(err){toast(err.message);}finally{e.submitter.disabled=false;}});
$('#settings-form').addEventListener('submit',async e=>{e.preventDefault();e.submitter.disabled=true;try{await api('settings',{name:$('#setting-name').value,model:$('#setting-model').value,language:$('#setting-language').value,speak:$('#setting-speak').checked});await refresh();toast('Settings saved.');checkModels();}catch(err){toast(err.message);}finally{e.submitter.disabled=false;}});
$('#check-model').addEventListener('click',checkModels);$('#connect-link').addEventListener('click',()=>{view('settings');checkModels();});
$('#dismiss-alerts').addEventListener('click',async()=>{try{for(const a of alerts)await api('tasks/ack',{id:a.id});$('#alert-dialog').close();alerts=[];await refresh(false);}catch(e){toast(e.message);}});
$('#alert-dialog').addEventListener('cancel',e=>e.preventDefault());
refresh().then(()=>{checkModels();pollAlerts();}).catch(e=>toast('Cannot connect to JARVIS. Restart the app. '+e.message));
setInterval(updateClock,30000);setInterval(pollAlerts,3000);
