'use strict';

// ── CONFIG ───────────────────────────────────────────────────────────────────
const API      = 'https://quiz-chaos-by-project-adnan.bdadnanboss.workers.dev';
const QBANK_URL= 'https://raw.githubusercontent.com/adnanXmacro/quiz-chaos/main/questions.json';
const CIRCUMFERENCE = 113.097;

// ── STATE ────────────────────────────────────────────────────────────────────
let user          = null;
let dailyData     = null;
let scoresData    = null;
let currentPage   = 'login';

// Quiz
let quizQuestions = [];
let quizAnswers   = {};
let quizIndex     = 0;
let isCatchup     = false;
let timerInterval = null;
let timerRemaining= 25;

// Practice
let practiceBank      = [];
let practiceQuestions = [];
let practiceAnswers   = {};
let practiceIndex     = 0;
let practiceConfig    = { subject:'all', count:10, timer:0, mode:'after' };
let practiceTimerInt  = null;
let practiceTimerSecs = 0;

// Vocab
let vocabBank     = [];
let vocabState    = null; // loaded from localStorage
let vocabSession  = [];
let vocabSessIdx  = 0;
let vocabFlipped  = false;

// Syllabus
let syllabusData  = null; // loaded from localStorage
let noteTarget    = null; // { subjectKey, chapterIndex }

// Admin
let adminUnlocked = false;
let editingFakeId = null;
let notifColor    = 'red';

// ── UTILS ────────────────────────────────────────────────────────────────────
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function getBDDate(offset=0) {
  return new Date(Date.now()+6*3600000+offset*86400000).toISOString().slice(0,10);
}
function formatNum(n){ return Number(n||0).toLocaleString(); }
function accuracy(c,t){ return t?Math.round(c/t*100)+'%':'0%'; }
function accuracyNum(c,t){ return t?Math.round(c/t*100):0; }
function grade(acc){
  if(acc>=90)return'S'; if(acc>=80)return'A+'; if(acc>=70)return'A';
  if(acc>=60)return'B'; if(acc>=50)return'C'; return'D';
}
function gradeColor(g){
  return{S:'var(--gold)',['A+']:'var(--green)',A:'#69f0ae',B:'#90caf9',C:'var(--yellow)',D:'var(--red-bright)'}[g]||'var(--text)';
}
function gradeClass(g){
  return{S:'grade-S',['A+']:'grade-Ap',A:'grade-A',B:'grade-B',C:'grade-C',D:'grade-D'}[g]||'grade-D';
}
function avatarUrl(id,av){
  if(!av||av==='null'||av==='undefined')return'';
  return`https://cdn.discordapp.com/avatars/${id}/${av}.png`;
}
function normalize(t){ return String(t).normalize('NFKC').toLowerCase().trim().replace(/\s+/g,' '); }
function randomSample(arr,n){
  const c=[...arr];
  for(let i=c.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[c[i],c[j]]=[c[j],c[i]];}
  return c.slice(0,Math.min(n,c.length));
}
function uuid(){ return Date.now().toString(36)+Math.random().toString(36).slice(2); }

// ── TOAST ────────────────────────────────────────────────────────────────────
function toast(msg,type=''){
  const c=document.getElementById('toast-container');
  const t=document.createElement('div');
  t.className='toast '+type; t.textContent=msg; c.appendChild(t);
  requestAnimationFrame(()=>requestAnimationFrame(()=>t.classList.add('show')));
  setTimeout(()=>{t.classList.remove('show');setTimeout(()=>t.remove(),300);},3200);
}

// ── API ───────────────────────────────────────────────────────────────────────
async function apiFetch(path,opts={}){
  const res=await fetch(API+path,opts);
  if(!res.ok)throw new Error('HTTP '+res.status);
  return res.json();
}
async function fetchScores(){ scoresData=await apiFetch('/scores'); return scoresData; }
async function fetchDaily(){ dailyData=await apiFetch('/daily'); return dailyData; }
async function fetchHistory(id){ const d=await apiFetch('/history?id='+encodeURIComponent(id)); return d.history||[]; }
async function fetchNotifications(){
  try{ return await apiFetch('/notifications'); }catch{ return []; }
}
async function workerPost(path,body){
  const res=await fetch(API+path,{method:'POST',headers:{'Content-Type':'application/json','X-Worker-Secret':'J111005376a'},body:JSON.stringify(body)});
  if(!res.ok)throw new Error('HTTP '+res.status);
  return res.json();
}

// ── AUTH ──────────────────────────────────────────────────────────────────────
function loadUser(){
  const p=new URLSearchParams(location.search);
  if(p.get('discord_id')){
    user={discord_id:p.get('discord_id'),username:p.get('username')||'Player',avatar:p.get('avatar')||''};
    localStorage.setItem('qc_user',JSON.stringify(user));
    history.replaceState({},'',location.pathname);
  } else {
    try{ const s=localStorage.getItem('qc_user'); if(s)user=JSON.parse(s); }catch{}
  }
}
function doLogin(){ location.href=API+'/login'; }
function logout(){
  localStorage.removeItem('qc_user');
  user=null; scoresData=null; dailyData=null; quizQuestions=[];
  showPage('login');
}

// ── NAV ───────────────────────────────────────────────────────────────────────
const NAV_MAP={dashboard:'home',quiz:'quiz',leaderboard:'ranks',profile:'profile'};

function navTap(btn,page){
  // Bounce animation
  btn.classList.add('tapped');
  setTimeout(()=>btn.classList.remove('tapped'),200);
  showPage(page);
}

function showPage(name){
  if(name==='quiz'&&quizQuestions.length===0){ toast('Enter the code to start the quiz','info'); name='dashboard'; }
  currentPage=name;
  clearTimer(); clearPracticeTimer();

  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));

  const isLogin=name==='login';
  document.body.classList.toggle('no-chrome',isLogin);
  document.getElementById('top-nav').classList.toggle('hidden',isLogin);
  document.getElementById('bot-nav').classList.toggle('hidden',isLogin);

  const pg=document.getElementById('pg-'+name);
  if(pg) pg.classList.add('active');

  const navId=NAV_MAP[name];
  if(navId) document.getElementById('nav-'+navId)?.classList.add('active');

  closeMoreMenu();

  if(name==='login')       loadLoginPage();
  if(name==='dashboard')   loadDashboard();
  if(name==='leaderboard') loadLeaderboard();
  if(name==='profile')     loadProfile();
  if(name==='syllabus')    loadSyllabus();
  if(name==='practice')    loadPracticePage();
  if(name==='vocabulary')  loadVocab();
  if(name==='history')     loadHistoryPage();
  if(name==='admin')       initAdminPage();
  if(name==='simulations') {} // static
}

// ── MORE MENU ─────────────────────────────────────────────────────────────────
function toggleMoreMenu(){
  const menu=document.getElementById('more-menu');
  const overlay=document.getElementById('more-overlay');
  const isHidden=menu.classList.contains('hidden');
  if(isHidden){ menu.classList.remove('hidden'); overlay.classList.remove('hidden'); }
  else closeMoreMenu();
}
function closeMoreMenu(){
  document.getElementById('more-menu').classList.add('hidden');
  document.getElementById('more-overlay').classList.add('hidden');
}
function moreNav(page){
  closeMoreMenu();
  setTimeout(()=>showPage(page),150);
}
function openSimulations(){ showPage('simulations'); }
function openSim(url,name){
  window.open(url,'_blank');
  toast(`Opening ${name} in a new tab — Quiz Chaos stays here`,'info');
}

// ── LOGIN ─────────────────────────────────────────────────────────────────────
async function loadLoginPage(){
  try{
    const data=await fetchScores();
    const ids=Object.keys(data.scores||{});
    document.getElementById('login-players').textContent=ids.length;
    document.getElementById('login-sessions').textContent=data.session_count||0;
    const sorted=ids.map(id=>({...data.scores[id],id})).sort((a,b)=>(b.points||0)-(a.points||0)).slice(0,5);
    const medals=['🥇','🥈','🥉'];
    document.getElementById('login-lb-list').innerHTML=sorted.length===0
      ?'<div class="empty-state">No players yet</div>'
      :sorted.map((p,i)=>`<div class="public-lb-row"><div class="lb-rank">${medals[i]||(i+1)}</div><div class="lb-name">${escHtml(p.username)}</div><div class="lb-pts">${formatNum(p.points)}</div></div>`).join('');
  }catch{
    document.getElementById('login-players').textContent='—';
    document.getElementById('login-sessions').textContent='—';
    document.getElementById('login-lb-list').innerHTML='<div class="empty-state">Could not load</div>';
  }
}

// ── DASHBOARD ─────────────────────────────────────────────────────────────────
const LEVELS=[{name:'Initiate',min:0,max:500},{name:'Scholar',min:500,max:1500},{name:'Expert',min:1500,max:3000},{name:'Master',min:3000,max:Infinity}];
function getLevelInfo(pts){
  const l=LEVELS.find((lv,i)=>pts<lv.max||i===LEVELS.length-1)||LEVELS[0];
  const pct=l.max===Infinity?100:Math.min(100,((pts-l.min)/(l.max-l.min)*100));
  const next=LEVELS[LEVELS.indexOf(l)+1];
  return{name:l.name,pct,nextName:next?.name||'Max',ptsLeft:next?next.min-pts:0};
}

async function loadDashboard(){
  if(!user)return;
  updateNavAvatar();
  const card=document.getElementById('quiz-status-card');
  card.innerHTML='<div class="center-spinner"><div class="spinner"></div></div>';
  try{
    const [scores,daily,history,notifs]=await Promise.all([
      fetchScores(),
      fetchDaily().catch(()=>null),
      fetchHistory(user.discord_id).catch(()=>[]),
      fetchNotifications().catch(()=>[]),
    ]);
    renderDashHero(scores);
    renderQuizStatus(daily,Array.isArray(history)?history:[]);
    renderDashHistory();
    renderNotifications(notifs);
  }catch(e){
    card.innerHTML='<div class="empty-state">Failed to load. Check your connection.</div>';
  }
}

function updateNavAvatar(){
  const av=avatarUrl(user.discord_id,user.avatar);
  const img=document.getElementById('nav-avatar');
  const ini=document.getElementById('nav-user-initial');
  if(av){ img.src=av; img.classList.remove('hidden'); ini.classList.add('hidden'); }
  else{ ini.textContent=(user.username||'P')[0].toUpperCase(); ini.classList.remove('hidden'); img.classList.add('hidden'); }
}

function renderDashHero(scores){
  const me=scores?.scores?.[user.discord_id];
  const myStreak=scores?.streaks?.[user.discord_id]?.streak||0;
  const pts=me?.points||0;
  const acc=accuracyNum(me?.correct||0,me?.total||0);
  const lvl=getLevelInfo(pts);

  const hr=new Date(Date.now()+6*3600000).getHours();
  const greet=hr<12?'Good morning':hr<17?'Good afternoon':'Good evening';
  document.getElementById('dash-greeting').textContent=greet;
  document.getElementById('dash-username').textContent=user.username;
  document.getElementById('dash-level-badge').textContent=lvl.name;
  document.getElementById('dash-pts-hero').textContent=formatNum(pts);
  document.getElementById('dash-streak-hero').textContent=myStreak;
  document.getElementById('dash-acc-hero').textContent=acc+'%';
  document.getElementById('level-fill').style.width=lvl.pct+'%';
  document.getElementById('level-current-label').textContent=formatNum(pts)+' pts';
  document.getElementById('level-next-label').textContent=lvl.nextName==='Max'?'Max Level':'Next: '+lvl.nextName+' ('+(lvl.ptsLeft)+' pts)';

  const owed=me?.catchup_owed||0;
  const sec=document.getElementById('catchup-section');
  if(owed>0){
    sec.classList.remove('hidden');
    document.getElementById('catchup-title').textContent=`${owed} Questions to Catch Up`;
    document.getElementById('catchup-sub').textContent='Complete them to earn back your points';
  } else sec.classList.add('hidden');
}

function renderQuizStatus(daily,history){
  const card=document.getElementById('quiz-status-card');
  const now=Date.now(), bdDate=getBDDate();
  const todayDone=history.includes(bdDate);
  if(!daily||!daily.date){
    card.innerHTML=`<div class="status-badge waiting"><span class="dot"></span>Waiting</div><div class="status-title">No Quiz Posted Yet</div><div class="status-sub">Check back after 5 AM Bangladesh time</div>`;return;
  }
  const isOpen=now>=daily.open_at&&now<daily.expires_at;
  const isExpired=now>=daily.expires_at;
  const notYet=now<daily.open_at;
  if(todayDone){
    card.innerHTML=`<div class="status-badge done"><span class="dot"></span>Completed</div><div class="status-title">Done for Today</div><div class="status-sub">Well done. See you tomorrow.</div>`;return;
  }
  if(notYet){
    const t=new Date(daily.open_at+6*3600000).toISOString().slice(11,16);
    card.innerHTML=`<div class="status-badge waiting"><span class="dot"></span>Scheduled</div><div class="status-title">Quiz Not Open Yet</div><div class="status-sub">Opens at ${escHtml(t)} BD</div>`;return;
  }
  if(isExpired){
    card.innerHTML=`<div class="status-badge expired"><span class="dot"></span>Expired</div><div class="status-title">Today's Quiz Closed</div><div class="status-sub">Closed at 3:00 AM BD · Opens again at 5:00 AM BD</div>`;return;
  }
  if(isOpen){
    if(Date.now()>=daily.expires_at){
      card.innerHTML=`<div class="status-badge expired"><span class="dot"></span>Expired</div><div class="status-title">Today's Quiz Closed</div><div class="status-sub">Opens again at 5:00 AM Bangladesh time</div>`;return;
    }
    const exp=new Date(daily.expires_at+6*3600000).toISOString().slice(11,16);
    card.innerHTML=`<div class="status-badge live"><span class="dot"></span>Live Now</div><div class="status-title">Quiz is Open</div><div class="status-sub">Closes at ${escHtml(exp)} BD · Enter code from Discord</div><div class="code-entry"><input class="code-input" id="code-field" placeholder="ENTER CODE" maxlength="6" autocomplete="off" spellcheck="false" oninput="this.value=this.value.toUpperCase()" onkeydown="if(event.key==='Enter')verifyCode()"/><button class="btn-primary" id="code-btn" onclick="verifyCode()">Go</button></div><div class="code-error" id="code-err"></div>`;
  }
}

function renderDashHistory(){
  const sessions=getExamHistory().slice(0,3);
  const el=document.getElementById('dash-history-list');
  if(!sessions.length){ el.innerHTML='<div class="empty-state" style="padding:20px;">No sessions yet — take a quiz!</div>'; return; }
  el.innerHTML=sessions.map(s=>{
    const g=grade(s.total?Math.round(s.correct/s.total*100):0);
    return`<div class="dash-history-card"><div class="dhc-grade" style="color:${gradeColor(g)}">${g}</div><div class="dhc-info"><div class="dhc-title">${escHtml(s.type==='daily'?'Daily Quiz':s.type==='catchup'?'Catch-Up':'Practice — '+s.subject)}</div><div class="dhc-meta">${escHtml(s.date)} · ${s.correct}/${s.total} correct</div></div><div class="dhc-pts">+${formatNum(s.points)}</div></div>`;
  }).join('');
}

function renderNotifications(notifs){
  const sec=document.getElementById('notif-section');
  const list=document.getElementById('notif-list');
  if(!notifs||!notifs.length){ sec.classList.add('hidden'); return; }
  sec.classList.remove('hidden');
  list.innerHTML=notifs.slice(0,3).map(n=>`<div class="notif-card color-${n.color||'red'}"><div class="notif-title">${escHtml(n.title)}</div><div class="notif-body">${escHtml(n.body)}</div><div class="notif-date">${escHtml(n.date)}</div></div>`).join('');
}

// ── CODE VERIFY ───────────────────────────────────────────────────────────────
async function verifyCode(){
  const field=document.getElementById('code-field');
  const btn=document.getElementById('code-btn');
  const errEl=document.getElementById('code-err');
  const code=field.value.trim().toUpperCase();
  if(code.length<3){ errEl.textContent='Enter the 6-character code from Discord'; return; }
  btn.disabled=true; btn.textContent='…'; errEl.textContent='';
  try{
    const res=await apiFetch('/verify-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})});
    if(res.valid){ toast('Code accepted','success'); await loadQuiz(false); }
    else{ const msgs={expired:'This code has expired.',not_open_yet:'The quiz is not open yet.'}; errEl.textContent=msgs[res.reason]||'Invalid code. Check the Discord channel.'; }
  }catch{ errEl.textContent='Connection error. Please try again.'; }
  finally{ btn.disabled=false; btn.textContent='Go'; }
}

// ── QUIZ ──────────────────────────────────────────────────────────────────────
async function loadQuiz(catchup){
  if(!dailyData){ try{ await fetchDaily(); }catch{ toast('Failed to load quiz','error'); return; } }
  if(!catchup){
    const now=Date.now();
    if(!dailyData.expires_at||now>=dailyData.expires_at){ toast('This quiz session has expired','error'); showPage('dashboard'); return; }
    if(!dailyData.open_at||now<dailyData.open_at){ toast('Quiz is not open yet','error'); showPage('dashboard'); return; }
  }
  isCatchup=catchup;
  quizQuestions=catchup?(dailyData.catchup_questions||[]):(dailyData.questions||[]);
  if(!quizQuestions.length){ toast(catchup?'No catch-up questions available':'No questions available','error'); return; }
  quizAnswers={}; quizIndex=0;
  showPage('quiz');
  renderQuestion();
}
function startCatchup(){ loadQuiz(true); }

function renderQuestion(){
  const q=quizQuestions[quizIndex], total=quizQuestions.length;
  const pct=((quizIndex+1)/total*100).toFixed(1);
  document.getElementById('q-counter').textContent=`Q ${quizIndex+1} / ${total}`;
  document.getElementById('q-subject').textContent=escHtml(q.subject||'');
  document.getElementById('q-progress').style.width=pct+'%';
  document.getElementById('q-text').innerHTML=escHtml(q.question);
  // Image
  const qCard=document.querySelector('#pg-quiz .question-card');
  const existImg=qCard?.querySelector('.q-image'); if(existImg)existImg.remove();
  if(q.image&&!q.image.startsWith('REPLACE')&&qCard){
    const img=document.createElement('img'); img.src=q.image; img.className='q-image'; img.alt='Question'; img.loading='lazy';
    qCard.insertBefore(img,qCard.querySelector('.question-text').nextSibling);
  }
  // Dots
  const dotsNav=document.getElementById('dots-nav'); dotsNav.innerHTML='';
  quizQuestions.forEach((qq,i)=>{
    const dot=document.createElement('div');
    let cls='dot-q'; if(quizAnswers[qq.id])cls+=' answered'; if(i===quizIndex)cls+=' current';
    dot.className=cls; dot.title='Q'+(i+1); dot.addEventListener('click',()=>jumpTo(i)); dotsNav.appendChild(dot);
  });
  // Options
  const optList=document.getElementById('options-list'); optList.innerHTML='';
  ['A','B','C','D'].forEach(k=>{
    const btn=document.createElement('button');
    btn.className='option-btn'+(quizAnswers[q.id]===k?' selected':'');
    btn.innerHTML=`<span class="option-key">${k}</span><span>${escHtml(q.options?.[k]??'')}</span>`;
    btn.addEventListener('click',()=>selectOption(k)); optList.appendChild(btn);
  });
  // Nav
  const isFirst=quizIndex===0, isLast=quizIndex===total-1;
  const allDone=quizQuestions.every(qq=>quizAnswers[qq.id]);
  document.getElementById('btn-prev').disabled=isFirst;
  document.getElementById('btn-next').classList.toggle('hidden',isLast);
  document.getElementById('btn-submit').classList.toggle('hidden',!isLast);
  document.getElementById('btn-submit').disabled=!allDone;
  startTimer();
}

function selectOption(key){
  clearTimer();
  quizAnswers[quizQuestions[quizIndex].id]=key;
  renderQuestion();
  if(quizIndex<quizQuestions.length-1) setTimeout(()=>{ quizIndex++; renderQuestion(); },300);
}
function jumpTo(i){ quizIndex=i; renderQuestion(); }
function quizNav(dir){ clearTimer(); quizIndex=Math.max(0,Math.min(quizQuestions.length-1,quizIndex+dir)); renderQuestion(); }

async function submitQuiz(){
  clearTimer();
  const allDone=quizQuestions.every(q=>quizAnswers[q.id]);
  if(!allDone){ toast('Answer all questions before submitting','error'); return; }
  const btn=document.getElementById('btn-submit'); btn.disabled=true; btn.textContent='Submitting…';
  try{
    const res=await apiFetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({discord_id:user.discord_id,username:user.username,answers:quizAnswers,date:getBDDate(),is_catchup:isCatchup})});
    if(res.success){
      saveExamHistory({date:getBDDate(),type:isCatchup?'catchup':'daily',subject:'All',correct:res.correct,total:res.total,points:res.points,grade:grade(res.total?Math.round(res.correct/res.total*100):0),results:res.results});
      renderResults(res); showPage('result');
    } else toast('Submission failed — try again','error');
  }catch{ toast('Network error — try again','error'); }
  finally{ btn.disabled=false; btn.textContent='Submit'; }
}

// ── TIMER ─────────────────────────────────────────────────────────────────────
const TIMER_SECONDS=25;
function startTimer(){
  clearTimer(); timerRemaining=TIMER_SECONDS; updateTimerUI(timerRemaining);
  timerInterval=setInterval(()=>{ timerRemaining--; updateTimerUI(timerRemaining); if(timerRemaining<=0){ clearTimer(); autoAdvance(); } },1000);
}
function clearTimer(){ if(timerInterval){ clearInterval(timerInterval); timerInterval=null; } }
function updateTimerUI(secs,prefix=''){
  const ring=document.getElementById(prefix+'timer-ring');
  const numEl=document.getElementById(prefix+'timer-num');
  const bar=document.getElementById(prefix+'timer-bar');
  if(!ring||!numEl||!bar)return;
  const total=prefix?practiceConfig.timer||25:TIMER_SECONDS;
  const pct=secs/total, offset=CIRCUMFERENCE*(1-pct);
  const isW=secs<=10&&secs>5, isD=secs<=5;
  const state=isD?'danger':isW?'warning':'';
  ring.style.strokeDashoffset=offset; ring.setAttribute('class','timer-ring'+(state?' '+state:''));
  numEl.textContent=secs; numEl.setAttribute('class','timer-num'+(state?' '+state:''));
  bar.style.width=(pct*100)+'%'; bar.setAttribute('class','timer-bar'+(state?' '+state:''));
}
function autoAdvance(){
  const card=document.querySelector('.question-card');
  if(card){ card.style.transition='border-color 0.2s'; card.style.borderColor='var(--red-glow)'; setTimeout(()=>card.style.borderColor='',400); }
  if(quizIndex<quizQuestions.length-1){ quizIndex++; renderQuestion(); }
  else{ renderQuestion(); toast('Time up! Review and submit.','error'); }
}

// ── RESULTS ───────────────────────────────────────────────────────────────────
function renderResults(res){
  const acc=res.total?Math.round(res.correct/res.total*100):0;
  const g=grade(acc);
  document.getElementById('res-grade').textContent=g;
  document.getElementById('res-grade').style.filter=`drop-shadow(0 0 20px ${gradeColor(g)}66)`;
  document.getElementById('res-frac').textContent=`${res.correct} / ${res.total}`;
  document.getElementById('res-pts').textContent=res.points;
  document.getElementById('res-type').textContent=isCatchup?'Catch-Up Session':'Daily Quiz';
  const resultMap={}; (res.results||[]).forEach(r=>{ resultMap[r.id]=r; });
  const prev=[...quizQuestions];
  document.getElementById('review-list').innerHTML=prev.map((q,i)=>{
    const r=resultMap[q.id]||{}, isC=!!r.correct, given=r.given||quizAnswers[q.id]||'—';
    return`<div class="review-item ${isC?'correct-item':'wrong-item'} fade-up" style="animation-delay:${(i*0.04).toFixed(2)}s">
      <div class="review-header"><div class="review-icon">${isC?'<svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2" style="width:14px;height:14px;"><polyline points="20 6 9 17 4 12"/></svg>':'<svg viewBox="0 0 24 24" fill="none" stroke="var(--red-bright)" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'}</div><div class="review-q">${escHtml(q.question)}</div></div>
      <div class="review-body"><div class="review-given-row"><span class="rev-label">Correct: </span><span class="rev-correct">${escHtml(q.answer)} — ${escHtml(q.options?.[q.answer]??'')}</span></div>${!isC?`<div class="review-given-row"><span class="rev-label">Your answer: </span><span class="rev-given-wrong">${escHtml(given)}</span></div>`:''} ${q.explanation?`<div class="review-explanation">${escHtml(q.explanation)}</div>`:''}</div>
    </div>`;
  }).join('');
  quizQuestions=[]; quizAnswers={};
}

// ── LEADERBOARD ───────────────────────────────────────────────────────────────
async function loadLeaderboard(){
  const list=document.getElementById('lb-list');
  list.innerHTML='<div class="center-spinner"><div class="spinner"></div></div>';
  try{
    const data=await fetchScores();
    const sorted=Object.keys(data.scores||{}).map(id=>({id,...data.scores[id],streak:data.streaks?.[id]?.streak||0})).sort((a,b)=>(b.points||0)-(a.points||0));
    if(!sorted.length){ list.innerHTML='<div class="empty-state">No players yet</div>'; return; }
    const medals=['🥇','🥈','🥉'];
    list.innerHTML=sorted.map((p,i)=>{
      const isMe=user&&p.id===user.discord_id;
      const acc=accuracy(p.correct||0,p.total||0);
      return`<div class="lb-item${isMe?' me':''}"> ${i<3?`<div class="rank-medal">${medals[i]}</div>`:`<div class="rank-num">${i+1}</div>`}<div class="lb-info"><div class="lb-username">${escHtml(p.username)}${isMe?' <span style="color:var(--red-bright);font-size:10px;font-weight:700;">you</span>':''}</div><div class="lb-meta">${acc} · ${p.streak} day streak</div></div><div class="lb-right"><div class="lb-pts-big">${formatNum(p.points)}</div><div class="lb-streak">${formatNum(p.correct||0)} correct</div></div></div>`;
    }).join('');
  }catch{ list.innerHTML='<div class="empty-state">Failed to load</div>'; }
}

// ── PROFILE ───────────────────────────────────────────────────────────────────
async function loadProfile(){
  if(!user)return;
  const av=avatarUrl(user.discord_id,user.avatar);
  const img=document.getElementById('prof-avatar'), fall=document.getElementById('prof-avatar-fallback');
  if(av){ img.src=av; img.classList.remove('hidden'); fall.classList.add('hidden'); }
  else{ fall.textContent=(user.username||'P')[0].toUpperCase(); fall.classList.remove('hidden'); img.classList.add('hidden'); }
  document.getElementById('prof-name').textContent=user.username;
  document.getElementById('prof-id').textContent='#'+user.discord_id;
  try{
    const [scores,history]=await Promise.all([fetchScores(),fetchHistory(user.discord_id).catch(()=>[])]);
    const me=scores?.scores?.[user.discord_id];
    const myStreak=scores?.streaks?.[user.discord_id]?.streak||0;
    const sorted=Object.keys(scores?.scores||{}).map(id=>({id,pts:scores.scores[id]?.points||0})).sort((a,b)=>b.pts-a.pts);
    const rank=sorted.findIndex(p=>p.id===user.discord_id)+1;
    document.getElementById('prof-rank').textContent=rank>0?`Rank #${rank}`:'Unranked';
    document.getElementById('prof-pts').textContent=formatNum(me?.points||0);
    document.getElementById('prof-streak').textContent=myStreak;
    document.getElementById('prof-correct').textContent=formatNum(me?.correct||0);
    document.getElementById('prof-acc').textContent=accuracy(me?.correct||0,me?.total||0);
    renderCalendar(Array.isArray(history)?history:[]);
    renderReportCard(me,scores);
    renderMissedQuestions(me?.wrong_questions||[]);
  }catch{ toast('Failed to load profile','error'); renderCalendar([]); renderReportCard(null,null); renderMissedQuestions([]); }
}

function renderCalendar(doneDates){
  const grid=document.getElementById('cal-grid'), today=getBDDate();
  const days=[];
  for(let i=29;i>=0;i--) days.push(new Date(Date.now()+6*3600000-i*86400000).toISOString().slice(0,10));
  grid.innerHTML=days.map(d=>{
    let cls='cal-day'; if(doneDates.includes(d))cls+=' done'; if(d===today)cls+=' today';
    return`<div class="${cls}" title="${d}"></div>`;
  }).join('');
}

function subjectGrade(acc){ if(acc>=90)return'S'; if(acc>=80)return'A+'; if(acc>=70)return'A'; if(acc>=60)return'B'; if(acc>=50)return'C'; return'D'; }

function renderReportCard(me,scores){
  const wrap=document.getElementById('report-card');
  const subjects=me?.subjects||{}, keys=Object.keys(subjects);
  if(!keys.length){ wrap.innerHTML='<div class="empty-state" style="padding:20px;">No quiz data yet</div>'; return; }
  const totalAcc=accuracyNum(me?.correct||0,me?.total||0);
  const og=subjectGrade(totalAcc);
  const sorted=keys.map(sub=>{ const s=subjects[sub]; const acc=accuracyNum(s.correct||0,s.total||0); return{sub,correct:s.correct||0,total:s.total||0,acc,g:subjectGrade(acc)}; }).sort((a,b)=>b.acc-a.acc);
  wrap.innerHTML=`<div class="rc-summary"><div class="rc-overall-grade">${og}</div><div class="rc-summary-info"><div class="rc-summary-title">Overall Performance</div><div class="rc-summary-sub">${me?.correct||0} / ${me?.total||0} correct · ${totalAcc}%</div></div><div class="rc-total-pts">${formatNum(me?.points||0)}<span>points</span></div></div>`
    +sorted.map((s,i)=>{ const gc=gradeClass(s.g); return`<div class="rc-subject-row fade-up" style="animation-delay:${(i*0.05).toFixed(2)}s"><div class="rc-subject-header"><div class="rc-subject-name">${escHtml(s.sub)}</div><div class="rc-grade-pill ${gc}">${escHtml(s.g)}</div></div><div class="rc-stats-row"><div class="rc-correct-total">${s.correct} / ${s.total}</div><div class="rc-bar-wrap"><div class="rc-bar ${gc}" style="width:0%" data-width="${s.acc}%"></div></div><div class="rc-acc-label">${s.acc}%</div></div></div>`; }).join('');
  requestAnimationFrame(()=>requestAnimationFrame(()=>{ wrap.querySelectorAll('.rc-bar[data-width]').forEach(b=>b.style.width=b.dataset.width); }));
}

// Missed questions
let missedOpen=false;
function toggleMissed(){
  missedOpen=!missedOpen;
  document.getElementById('missed-body').classList.toggle('open',missedOpen);
  document.getElementById('missed-chevron')?.classList.toggle('open',missedOpen);
}
function renderMissedQuestions(arr){
  const list=document.getElementById('missed-list');
  const badge=document.getElementById('missed-count');
  badge.textContent=arr.length;
  if(!arr.length){ list.innerHTML='<div class="missed-empty">No wrong answers yet</div>'; return; }
  const groups={};
  arr.forEach(q=>{ const s=q.subject||'General'; if(!groups[s])groups[s]=[]; groups[s].push(q); });
  list.innerHTML=Object.keys(groups).sort().map(sub=>{
    const qs=groups[sub];
    return`<div class="missed-subject-group"><div class="missed-subject-label">${escHtml(sub)} (${qs.length})</div>`+qs.map(q=>`<div class="missed-card"><div class="missed-q-text">${escHtml(q.question)}</div><div class="missed-answers"><div class="missed-ans-row"><div class="missed-ans-label">Your ans</div><div class="missed-ans-wrong">${escHtml(q.given||'—')} — ${escHtml(q.options?.[q.given]??'')}</div></div><div class="missed-ans-row"><div class="missed-ans-label">Correct</div><div class="missed-ans-correct">${escHtml(q.answer)} — ${escHtml(q.options?.[q.answer]??'')}</div></div></div>${q.explanation?`<div class="missed-explanation">${escHtml(q.explanation)}</div>`:''}</div>`).join('')+'</div>';
  }).join('');
}

// ── EXAM HISTORY ──────────────────────────────────────────────────────────────
function getExamHistory(){
  try{ return JSON.parse(localStorage.getItem('qc_history')||'[]'); }catch{ return[]; }
}
function saveExamHistory(session){
  const h=getExamHistory();
  h.unshift({...session,id:uuid()});
  if(h.length>50)h.length=50;
  localStorage.setItem('qc_history',JSON.stringify(h));
}
function loadHistoryPage(){
  const el=document.getElementById('history-full-list');
  const sessions=getExamHistory();
  if(!sessions.length){ el.innerHTML='<div class="empty-state" style="padding:40px;">No sessions recorded yet</div>'; return; }
  el.innerHTML=sessions.map(s=>{
    const acc=s.total?Math.round(s.correct/s.total*100):0;
    const g=s.grade||grade(acc);
    const typeLabel=s.type==='daily'?'Daily Quiz':s.type==='catchup'?'Catch-Up':'Practice'+(s.subject&&s.subject!=='All'?' — '+s.subject:'');
    return`<div class="history-item"><div class="hi-grade" style="color:${gradeColor(g)}">${g}</div><div class="hi-info"><div class="hi-title">${escHtml(typeLabel)}</div><div class="hi-meta">${escHtml(s.date)} · ${s.correct}/${s.total} correct</div></div><div class="hi-right"><div class="hi-pts">+${formatNum(s.points)}</div><div class="hi-acc">${acc}%</div></div></div>`;
  }).join('');
}

// ── PRACTICE ──────────────────────────────────────────────────────────────────
const PRACTICE_LIMIT=50;
function getPracticeData(){ try{ const d=JSON.parse(localStorage.getItem('qc_practice')||'{}'); return d.date===getBDDate()?d:{date:getBDDate(),used:0,asked:[]}; }catch{ return{date:getBDDate(),used:0,asked:[]}; } }
function savePracticeData(d){ localStorage.setItem('qc_practice',JSON.stringify(d)); }

async function loadPracticePage(){
  document.getElementById('practice-setup').classList.remove('hidden');
  document.getElementById('practice-quiz').classList.add('hidden');
  document.getElementById('practice-result').classList.add('hidden');
  updatePracticeLimitUI();
  if(!practiceBank.length){
    try{
      const res=await fetch(QBANK_URL);
      if(!res.ok)throw new Error('HTTP '+res.status);
      practiceBank=await res.json();
      practiceBank.forEach(q=>{ q.type=q.type||'mcq'; q.subject=q.subject||'General'; });
      buildSubjectChips();
    }catch(e){ document.getElementById('practice-setup-err').textContent='Failed to load question bank: '+e.message; }
  }
}
function updatePracticeLimitUI(){
  const d=getPracticeData(), used=d.used||0, pct=Math.min(used/PRACTICE_LIMIT*100,100);
  document.getElementById('practice-used').textContent=used;
  const fill=document.getElementById('practice-limit-fill');
  fill.style.width=pct+'%'; fill.className='plb-fill'+(used>=PRACTICE_LIMIT?' full':'');
}
function buildSubjectChips(){
  const subs=[...new Set(practiceBank.map(q=>q.subject))].sort();
  const grid=document.getElementById('practice-subject-grid');
  grid.innerHTML='<button class="subject-chip active" data-subject="all" onclick="selectSubject(this)">All Subjects</button>'+subs.map(s=>`<button class="subject-chip" data-subject="${escHtml(s)}" onclick="selectSubject(this)">${escHtml(s)}</button>`).join('');
}
function selectSubject(el){ document.querySelectorAll('.subject-chip').forEach(c=>c.classList.remove('active')); el.classList.add('active'); practiceConfig.subject=el.dataset.subject; }
function selectCount(el){ document.querySelectorAll('.count-chip[data-count]').forEach(c=>c.classList.remove('active')); el.classList.add('active'); practiceConfig.count=parseInt(el.dataset.count); }
function selectTimer(el){ document.querySelectorAll('.count-chip[data-timer]').forEach(c=>c.classList.remove('active')); el.classList.add('active'); practiceConfig.timer=parseInt(el.dataset.timer); }
function selectMode(el){ document.querySelectorAll('.count-chip[data-mode]').forEach(c=>c.classList.remove('active')); el.classList.add('active'); practiceConfig.mode=el.dataset.mode; }

function startPractice(){
  const errEl=document.getElementById('practice-setup-err'); errEl.textContent='';
  const d=getPracticeData(), remaining=PRACTICE_LIMIT-(d.used||0);
  if(remaining<=0){ errEl.textContent='Daily limit reached (50 questions). Come back tomorrow!'; return; }
  if(!practiceBank.length){ errEl.textContent='Question bank not loaded yet.'; return; }
  const count=Math.min(practiceConfig.count,remaining);
  let pool=practiceConfig.subject==='all'?[...practiceBank]:practiceBank.filter(q=>q.subject===practiceConfig.subject);
  if(!pool.length){ errEl.textContent='No questions found for this subject.'; return; }
  const seen=new Set(); pool=pool.filter(q=>{ const k=normalize(q.question); if(seen.has(k))return false; seen.add(k); return true; });
  const askedNorm=new Set((d.asked||[]).map(normalize));
  let fresh=pool.filter(q=>!askedNorm.has(normalize(q.question)));
  if(fresh.length<count){ fresh=pool; d.asked=[]; savePracticeData(d); }
  practiceQuestions=randomSample(fresh,count).map((q,i)=>({...q,id:'pq'+(i+1)}));
  practiceAnswers={}; practiceIndex=0;
  document.getElementById('practice-setup').classList.add('hidden');
  document.getElementById('practice-result').classList.add('hidden');
  document.getElementById('practice-quiz').classList.remove('hidden');
  document.getElementById('pq-timer-wrap').style.display=practiceConfig.timer>0?'flex':'none';
  renderPracticeQuestion();
}

function renderPracticeQuestion(){
  const q=practiceQuestions[practiceIndex], total=practiceQuestions.length;
  document.getElementById('pq-counter').textContent=`Q ${practiceIndex+1} / ${total}`;
  document.getElementById('pq-subject').textContent=escHtml(q.subject||'');
  document.getElementById('pq-progress').style.width=((practiceIndex+1)/total*100).toFixed(1)+'%';
  document.getElementById('pq-text').innerHTML=escHtml(q.question);
  document.getElementById('pq-feedback').classList.add('hidden');
  document.getElementById('pq-feedback').className='pq-feedback hidden';
  // Image
  const pqCard=document.querySelector('#practice-quiz .question-card');
  const existPqImg=pqCard?.querySelector('.q-image'); if(existPqImg)existPqImg.remove();
  if(q.image&&!q.image.startsWith('REPLACE')&&pqCard){ const img=document.createElement('img'); img.src=q.image; img.className='q-image'; img.alt=''; img.loading='lazy'; pqCard.insertBefore(img,pqCard.querySelector('.question-text').nextSibling); }
  // Dots
  const pqDots=document.getElementById('pq-dots'); pqDots.innerHTML='';
  practiceQuestions.forEach((qq,i)=>{ const dot=document.createElement('div'); let cls='dot-q'; if(practiceAnswers[qq.id])cls+=' answered'; if(i===practiceIndex)cls+=' current'; dot.className=cls; dot.addEventListener('click',()=>{ practiceIndex=i; renderPracticeQuestion(); }); pqDots.appendChild(dot); });
  // Options
  const pqOpts=document.getElementById('pq-options'); pqOpts.innerHTML='';
  const isRev=practiceConfig.mode==='immediately'&&practiceAnswers[q.id];
  ['A','B','C','D'].forEach(k=>{
    const btn=document.createElement('button');
    let cls='option-btn'; if(practiceAnswers[q.id]===k)cls+=' selected';
    if(isRev){ if(k===q.answer)cls+=' correct'; else if(practiceAnswers[q.id]===k)cls+=' wrong'; }
    btn.className=cls;
    btn.innerHTML=`<span class="option-key">${k}</span><span>${escHtml(q.options?.[k]??'')}</span>`;
    if(!isRev) btn.addEventListener('click',()=>selectPracticeOption(k)); else btn.disabled=true;
    pqOpts.appendChild(btn);
  });
  if(isRev) showPqFeedback(q,practiceAnswers[q.id]);
  // Nav
  const isLast=practiceIndex===total-1, allDone=practiceQuestions.every(qq=>practiceAnswers[qq.id]);
  document.getElementById('pq-prev').disabled=practiceIndex===0;
  document.getElementById('pq-next').classList.toggle('hidden',isLast);
  document.getElementById('pq-submit').classList.toggle('hidden',!isLast);
  document.getElementById('pq-submit').disabled=!allDone;
  if(practiceConfig.timer>0) startPracticeTimer();
}

function showPqFeedback(q,given){
  const isC=given===q.answer, fb=document.getElementById('pq-feedback');
  fb.className='pq-feedback '+(isC?'correct-fb':'wrong-fb'); fb.classList.remove('hidden');
  fb.innerHTML=`<div style="font-size:13px;font-weight:700;color:${isC?'var(--green)':'var(--red-bright)'};margin-bottom:6px;">${isC?'Correct':'Incorrect'}</div>${!isC?`<div style="font-size:12px;color:var(--text-dim);margin-bottom:6px;">Correct: <span style="color:var(--green);font-weight:600;">${escHtml(q.answer)} — ${escHtml(q.options?.[q.answer]??'')}</span></div>`:''} ${q.explanation?`<div style="font-size:12px;color:var(--muted);border-left:2px solid var(--red-mid);padding-left:10px;line-height:1.65;">${escHtml(q.explanation)}</div>`:''}`;
}

function selectPracticeOption(key){
  const q=practiceQuestions[practiceIndex]; practiceAnswers[q.id]=key; clearPracticeTimer();
  if(practiceConfig.mode==='immediately'){ renderPracticeQuestion(); if(practiceIndex<practiceQuestions.length-1) setTimeout(()=>{ practiceIndex++; renderPracticeQuestion(); },2000); }
  else{ renderPracticeQuestion(); if(practiceIndex<practiceQuestions.length-1) setTimeout(()=>{ practiceIndex++; renderPracticeQuestion(); },300); }
}
function practiceNav(dir){ clearPracticeTimer(); practiceIndex=Math.max(0,Math.min(practiceQuestions.length-1,practiceIndex+dir)); renderPracticeQuestion(); }

function startPracticeTimer(){
  clearPracticeTimer(); practiceTimerSecs=practiceConfig.timer; updateTimerUI(practiceTimerSecs,'pq-');
  practiceTimerInt=setInterval(()=>{ practiceTimerSecs--; updateTimerUI(practiceTimerSecs,'pq-'); if(practiceTimerSecs<=0){ clearPracticeTimer(); if(practiceIndex<practiceQuestions.length-1){ practiceIndex++; renderPracticeQuestion(); } else{ renderPracticeQuestion(); toast('Time up!','error'); } } },1000);
}
function clearPracticeTimer(){ if(practiceTimerInt){ clearInterval(practiceTimerInt); practiceTimerInt=null; } }

function submitPractice(){
  clearPracticeTimer();
  let correct=0;
  const results=practiceQuestions.map(q=>{ const given=practiceAnswers[q.id]; const isC=given===q.answer; if(isC)correct++; return{...q,given,isCorrect:isC}; });
  const total=practiceQuestions.length, acc=total?Math.round(correct/total*100):0, g=grade(acc);
  const d=getPracticeData(); d.used=(d.used||0)+total;
  const newAsked=[...new Set([...(d.asked||[]),...practiceQuestions.map(q=>q.question)])];
  d.asked=newAsked; savePracticeData(d);
  saveExamHistory({date:getBDDate(),type:'practice',subject:practiceConfig.subject==='all'?'All':practiceConfig.subject,correct,total,points:0,grade:g});
  document.getElementById('pr-grade').textContent=g;
  document.getElementById('pr-frac').textContent=`${correct} / ${total}`;
  document.getElementById('pr-subject-label').textContent=practiceConfig.subject==='all'?'All Subjects':practiceConfig.subject;
  document.getElementById('pr-review').innerHTML=results.map((q,i)=>{
    const delay=(i*0.04).toFixed(2);
    return`<div class="review-item ${q.isCorrect?'correct-item':'wrong-item'} fade-up" style="animation-delay:${delay}s"><div class="review-header"><div class="review-icon">${q.isCorrect?'<svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2" style="width:14px;height:14px;"><polyline points="20 6 9 17 4 12"/></svg>':'<svg viewBox="0 0 24 24" fill="none" stroke="var(--red-bright)" stroke-width="2" style="width:14px;height:14px;"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'}</div><div class="review-q">${escHtml(q.question)}</div></div><div class="review-body"><div class="review-given-row"><span class="rev-label">Correct: </span><span class="rev-correct">${escHtml(q.answer)} — ${escHtml(q.options?.[q.answer]??'')}</span></div>${!q.isCorrect?`<div class="review-given-row"><span class="rev-label">Your answer: </span><span class="rev-given-wrong">${escHtml(q.given||'—')}</span></div>`:''} ${q.explanation?`<div class="review-explanation">${escHtml(q.explanation)}</div>`:''}</div></div>`;
  }).join('');
  document.getElementById('practice-quiz').classList.add('hidden');
  document.getElementById('practice-result').classList.remove('hidden');
  updatePracticeLimitUI();
}
function resetPractice(){ practiceQuestions=[]; practiceAnswers={}; clearPracticeTimer(); document.getElementById('practice-result').classList.add('hidden'); document.getElementById('practice-setup').classList.remove('hidden'); updatePracticeLimitUI(); }

// ── SYLLABUS TRACKER ──────────────────────────────────────────────────────────
const SYLLABUS={
  physics:{label:'Physics',color:'#3c8cff',chapters:['ভৌত জগৎ ও পরিমাপ','ভেক্টর','গতিবিদ্যা','নিউটনিয়ান বলবিদ্যা','কাজ, শক্তি ও ক্ষমতা','মহাকর্ষ ও অভিকর্ষ','পদার্থের গাঠনিক ধর্ম','পর্যাবৃত্ত গতি','তরঙ্গ','আদর্শ গ্যাস ও গ্যাসের গতিতত্ত্ব','তাপগতিবিদ্যা','স্থির তড়িৎ','চল তড়িৎ','তড়িৎ প্রবাহের চৌম্বক ক্রিয়া ও চুম্বকত্ব','তাড়িতচৌম্বক আবেশ ও পরিবর্তী প্রবাহ','জ্যামিতিক আলোকবিজ্ঞান','ভৌত আলোকবিজ্ঞান','আধুনিক পদার্থবিজ্ঞানের সূচনা','পরমাণুর মডেল ও নিউক্লিয়ার পদার্থবিজ্ঞান','সেমিকন্ডাক্টর ও ইলেকট্রনিক্স']},
  chemistry:{label:'Chemistry',color:'#00c853',chapters:['ল্যাবরেটরির নিরাপত্তা ও রাসায়নিক পরিবেশ','গুণগত রসায়ন','মৌলের পর্যায়বৃত্ত ধর্ম ও রাসায়নিক বন্ধন','রাসায়নিক পরিবর্তন','কর্মমুখী রসায়ন','পরিবেশ রসায়ন','জৈব রসায়ন','পরিমাণগত রসায়ন','তড়িৎ রসায়ন','অর্থনৈতিক রসায়ন']},
  botany:{label:'Botany',color:'#69f0ae',chapters:['কোষ ও কোষীয় অঙ্গাণু','কোষ বিভাজন','জীবের শ্রেণিবিন্যাস','শৈবাল ও ছত্রাক','ব্রায়োফাইটা ও টেরিডোফাইটা','নগ্নবীজী ও আবৃতবীজী উদ্ভিদ','উদ্ভিদ শারীরতত্ত্ব','উদ্ভিদের প্রজনন','জীবপ্রযুক্তি','উদ্ভিদ ও পরিবেশ']},
  zoology:{label:'Zoology',color:'#ff8c1a',chapters:['প্রাণীর বিভিন্নতা ও শ্রেণিবিন্যাস','প্রাণীর পরিচিতি (হাইড্রা, ঘাসফড়িং, রুই মাছ, ব্যাঙ)','মানব শারীরতত্ত্ব — পরিপাক ও শোষণ','মানব শারীরতত্ত্ব — রক্ত ও সংবহন','মানব শারীরতত্ত্ব — শ্বসন','মানব শারীরতত্ত্ব — রেচন','মানব শারীরতত্ত্ব — চলন ও অঙ্গচালনা','মানব শারীরতত্ত্ব — স্নায়ুতন্ত্র ও অন্তঃক্ষরা গ্রন্থি','মানব জনন ও ভ্রূণতত্ত্ব','মানব রোগ ও স্বাস্থ্য']},
  english:{label:'English',color:'#c9a227',chapters:['Reading Comprehension','Vocabulary & Word Meaning','Grammar — Tense & Verb Forms','Grammar — Parts of Speech','Sentence Transformation','Fill in the Blanks','Preposition & Articles','Error Correction','Connectors & Linking Words','Paragraph / Passage Based Questions']},
  gk:{label:'General Knowledge',color:'#a032ff',chapters:['বাংলাদেশের ইতিহাস ও মুক্তিযুদ্ধ','বাংলাদেশের ভূগোল ও পরিবেশ','বাংলাদেশের রাষ্ট্রব্যবস্থা ও সংবিধান','আন্তর্জাতিক সংস্থা ও বিশ্বব্যবস্থা','বিজ্ঞান ও প্রযুক্তি','স্বাস্থ্য ও চিকিৎসা বিজ্ঞান','খেলাধুলা ও সংস্কৃতি','সাম্প্রতিক ঘটনা']},
};
const CIRC_RING=163; // 2π×26 for r=26

function getSyllabusData(){
  try{
    const d=JSON.parse(localStorage.getItem('qc_syllabus')||'null');
    if(d)return d;
  }catch{}
  const d={};
  Object.keys(SYLLABUS).forEach(k=>{ d[k]={chapters:SYLLABUS[k].chapters.map(()=>({pct:0,note:''}))}; });
  return d;
}
function saveSyllabusData(d){ localStorage.setItem('qc_syllabus',JSON.stringify(d)); }

function getSubjectPct(key){
  const data=getSyllabusData();
  const chs=data[key]?.chapters||[];
  if(!chs.length)return 0;
  return Math.round(chs.reduce((s,c)=>s+(c.pct||0),0)/chs.length);
}

function loadSyllabus(){
  const data=getSyllabusData();
  // Overview rings
  const ov=document.getElementById('syllabus-overview');
  ov.innerHTML=Object.keys(SYLLABUS).map(k=>{
    const s=SYLLABUS[k], pct=getSubjectPct(k);
    const offset=CIRC_RING*(1-pct/100);
    return`<div class="syl-ring-card" onclick="scrollToSubject('${k}')">
      <div class="syl-ring-wrap">
        <svg viewBox="0 0 56 56">
          <circle class="syl-ring-track" cx="28" cy="28" r="26"/>
          <circle class="syl-ring-fill" cx="28" cy="28" r="26" stroke="${s.color}" stroke-dashoffset="${offset}" style="transform-origin:center;transform:rotate(-90deg);"/>
        </svg>
        <div class="syl-ring-pct">${pct}%</div>
      </div>
      <div class="syl-ring-label">${s.label}</div>
    </div>`;
  }).join('');

  // Subject blocks
  const sb=document.getElementById('syllabus-subjects');
  sb.innerHTML=Object.keys(SYLLABUS).map(k=>{
    const s=SYLLABUS[k], pct=getSubjectPct(k), chs=data[k]?.chapters||[];
    return`<div class="syl-subject-block" id="syl-block-${k}">
      <div class="syl-subject-header" onclick="toggleSubject('${k}')">
        <div class="syl-subject-dot" style="background:${s.color}"></div>
        <div class="syl-subject-name">${s.label}</div>
        <div class="syl-subject-pct">${pct}%</div>
        <div class="syl-subject-chevron" id="syl-chev-${k}">▼</div>
      </div>
      <div class="syl-chapters" id="syl-chs-${k}">
        ${s.chapters.map((ch,i)=>{
          const chData=chs[i]||{pct:0,note:''};
          const hasNote=!!chData.note;
          return`<div class="syl-chapter-row" id="syl-ch-${k}-${i}">
            <div class="syl-chapter-top">
              <div class="syl-chapter-name">${escHtml(ch)}</div>
              <div class="syl-chapter-pct-label" id="syl-pct-${k}-${i}">${chData.pct||0}%</div>
              <button class="syl-chapter-note-btn${hasNote?' has-note':''}" id="syl-note-btn-${k}-${i}" onclick="openNoteModal('${k}',${i},'${escHtml(ch)}')">Note</button>
            </div>
            <input type="range" class="syl-chapter-slider" min="0" max="100" step="5" value="${chData.pct||0}" oninput="updateChapterPct('${k}',${i},this.value)"/>
            ${hasNote?`<div class="syl-chapter-note-preview visible" id="syl-note-prev-${k}-${i}">${escHtml(chData.note.slice(0,80))}${chData.note.length>80?'...':''}</div>`:`<div class="syl-chapter-note-preview" id="syl-note-prev-${k}-${i}"></div>`}
          </div>`;
        }).join('')}
      </div>
    </div>`;
  }).join('');
  scheduleReminderCheck();
}

function scrollToSubject(k){
  const el=document.getElementById('syl-block-'+k); if(!el)return;
  const chs=document.getElementById('syl-chs-'+k);
  if(chs.classList.contains('open')){ el.scrollIntoView({behavior:'smooth',block:'start'}); }
  else{ toggleSubject(k); setTimeout(()=>el.scrollIntoView({behavior:'smooth',block:'start'}),300); }
}

function toggleSubject(k){
  const chs=document.getElementById('syl-chs-'+k);
  const chev=document.getElementById('syl-chev-'+k);
  const open=chs.classList.toggle('open');
  if(chev)chev.classList.toggle('open',open);
}

function updateChapterPct(subKey,chIdx,val){
  const data=getSyllabusData();
  if(!data[subKey])data[subKey]={chapters:SYLLABUS[subKey].chapters.map(()=>({pct:0,note:''}))};
  while(data[subKey].chapters.length<=chIdx) data[subKey].chapters.push({pct:0,note:''});
  data[subKey].chapters[chIdx].pct=parseInt(val);
  saveSyllabusData(data);
  document.getElementById('syl-pct-'+subKey+'-'+chIdx).textContent=val+'%';
  // Update ring
  const pct=getSubjectPct(subKey);
  const offset=CIRC_RING*(1-pct/100);
  const ring=document.querySelector(`#syl-block-${subKey} .syl-ring-fill`);
  // Update overview without full reload
  loadSyllabusOverview();
}

function loadSyllabusOverview(){
  const ov=document.getElementById('syllabus-overview');
  if(!ov)return;
  Object.keys(SYLLABUS).forEach(k=>{
    const s=SYLLABUS[k], pct=getSubjectPct(k);
    const offset=CIRC_RING*(1-pct/100);
    const card=ov.querySelector(`.syl-ring-card:nth-child(${Object.keys(SYLLABUS).indexOf(k)+1})`);
    if(card){
      const fill=card.querySelector('.syl-ring-fill'); const pctEl=card.querySelector('.syl-ring-pct');
      if(fill)fill.style.strokeDashoffset=offset; if(pctEl)pctEl.textContent=pct+'%';
    }
    const subjPct=document.querySelector(`#syl-block-${k} .syl-subject-pct`);
    if(subjPct)subjPct.textContent=pct+'%';
  });
}

// Note modal
function openNoteModal(subKey,chIdx,chName){
  noteTarget={subKey,chIdx};
  const data=getSyllabusData();
  const note=data[subKey]?.chapters?.[chIdx]?.note||'';
  document.getElementById('note-modal-title').textContent=chName;
  document.getElementById('note-textarea').value=note;
  document.getElementById('note-modal-overlay').classList.remove('hidden');
  document.getElementById('note-modal').classList.remove('hidden');
  setTimeout(()=>document.getElementById('note-textarea').focus(),300);
}
function closeNoteModal(){
  document.getElementById('note-modal-overlay').classList.add('hidden');
  document.getElementById('note-modal').classList.add('hidden');
  noteTarget=null;
}
function saveChapterNote(){
  if(!noteTarget)return;
  const {subKey,chIdx}=noteTarget;
  const note=document.getElementById('note-textarea').value.trim();
  const data=getSyllabusData();
  if(!data[subKey])data[subKey]={chapters:SYLLABUS[subKey].chapters.map(()=>({pct:0,note:''}))};
  while(data[subKey].chapters.length<=chIdx) data[subKey].chapters.push({pct:0,note:''});
  data[subKey].chapters[chIdx].note=note;
  saveSyllabusData(data);
  // Update UI
  const prevEl=document.getElementById(`syl-note-prev-${subKey}-${chIdx}`);
  const noteBtn=document.getElementById(`syl-note-btn-${subKey}-${chIdx}`);
  if(prevEl){ if(note){ prevEl.textContent=note.slice(0,80)+(note.length>80?'...':''); prevEl.classList.add('visible'); } else{ prevEl.textContent=''; prevEl.classList.remove('visible'); } }
  if(noteBtn){ if(note)noteBtn.classList.add('has-note'); else noteBtn.classList.remove('has-note'); }
  closeNoteModal();
  toast('Note saved','success');
}

// Smart reminders
const TAG_CONFIG={
  '@goal:':{type:'goal',msg:(name,text)=>`Hey ${name}! Forgot about your goal — "${text}"?`},
  '@reminder:':{type:'reminder',msg:(name,text)=>`Hey ${name}! You set a reminder — "${text}"`},
  '@finish:':{type:'finish',msg:(name,text)=>`Hey ${name}! Did you finish — "${text}"?`},
  '@left:':{type:'left',msg:(name,text)=>`Hey ${name}! You left off at — "${text}"`},
};

function getAllTaggedNotes(){
  const data=getSyllabusData(), tagged=[];
  Object.keys(SYLLABUS).forEach(sk=>{
    const chs=data[sk]?.chapters||[];
    chs.forEach((ch,i)=>{
      if(!ch.note)return;
      Object.keys(TAG_CONFIG).forEach(tag=>{
        const lower=ch.note.toLowerCase();
        let idx=lower.indexOf(tag);
        while(idx!==-1){
          const rest=ch.note.slice(idx+tag.length).split('\n')[0].trim();
          if(rest) tagged.push({tag,text:rest,config:TAG_CONFIG[tag]});
          idx=lower.indexOf(tag,idx+1);
        }
      });
    });
  });
  return tagged;
}

let reminderTimeout=null;
function scheduleReminderCheck(){
  if(reminderTimeout)clearTimeout(reminderTimeout);
  const delay=Math.floor(Math.random()*(3600000-1800000))+1800000; // 30-60 min
  reminderTimeout=setTimeout(showRandomReminder,delay);
}
function showRandomReminder(){
  const notes=getAllTaggedNotes();
  if(!notes.length){ scheduleReminderCheck(); return; }
  const pick=notes[Math.floor(Math.random()*notes.length)];
  const name=user?.username||'Student';
  const msg=pick.config.msg(name,pick.text);
  document.getElementById('reminder-text').textContent=msg;
  const tagEl=document.getElementById('reminder-tag');
  tagEl.textContent=pick.config.type.charAt(0).toUpperCase()+pick.config.type.slice(1);
  tagEl.className='reminder-tag '+pick.config.type;
  document.getElementById('reminder-popup').classList.remove('hidden');
  scheduleReminderCheck();
}
function dismissReminder(){ document.getElementById('reminder-popup').classList.add('hidden'); }

// ── VOCABULARY ────────────────────────────────────────────────────────────────
const VOCAB_BANK=[
  {en:'Desiccation',bn:'শুষ্কীভবন / পানিশূন্যতা',ex:'Desiccation of cells leads to death.'},
  {en:'Osmosis',bn:'অভিস্রবণ',ex:'Water moves by osmosis across membranes.'},
  {en:'Mitogenic',bn:'কোষবিভাজন-উদ্দীপক',ex:'Mitogenic signals trigger cell division.'},
  {en:'Palliate',bn:'প্রশমিত করা',ex:'The drug palliates pain without curing.'},
  {en:'Turgor',bn:'কোষস্ফীতি',ex:'Turgor pressure keeps plant cells rigid.'},
  {en:'Diastole',bn:'হৃদ-প্রসারণ',ex:'Diastole is the relaxation phase of the heart.'},
  {en:'Exogenous',bn:'বহিরাগত / বাহ্যিক উৎস থেকে',ex:'Exogenous hormones are taken from outside.'},
  {en:'Cytolysis',bn:'কোষবিশ্লেষণ',ex:'Cytolysis destroys cells through osmotic pressure.'},
  {en:'Benign',bn:'নিরীহ / অক্ষতিকর',ex:'A benign tumour does not spread.'},
  {en:'Malignant',bn:'মারাত্মক / ক্যান্সারযুক্ত',ex:'Malignant cells invade other tissues.'},
  {en:'Prophylaxis',bn:'প্রতিরোধমূলক চিকিৎসা',ex:'Vaccination is a prophylaxis against disease.'},
  {en:'Aetiology',bn:'রোগের কারণবিদ্যা',ex:'The aetiology of the disease is unknown.'},
  {en:'Haemostasis',bn:'রক্তপাত বন্ধের প্রক্রিয়া',ex:'Haemostasis prevents excessive blood loss.'},
  {en:'Anabolism',bn:'সংশ্লেষণ বিপাক',ex:'Anabolism builds complex molecules from simpler ones.'},
  {en:'Catabolism',bn:'বিশ্লেষণ বিপাক',ex:'Catabolism breaks down molecules to release energy.'},
  {en:'Homeostasis',bn:'সমস্থিতি',ex:'The body maintains homeostasis for stable conditions.'},
  {en:'Turgid',bn:'স্ফীত / ফুলে ওঠা',ex:'A turgid cell is swollen with water.'},
  {en:'Plasmolysis',bn:'কোষরস নিষ্কাশন',ex:'Plasmolysis occurs when cells lose water.'},
  {en:'Apoptosis',bn:'কোষের পরিকল্পিত মৃত্যু',ex:'Apoptosis removes damaged cells safely.'},
  {en:'Phagocytosis',bn:'ভক্ষণকোষীয় পরিপাক',ex:'Phagocytosis engulfs bacteria.'},
  {en:'Endocytosis',bn:'এন্ডোসাইটোসিস / কোষে প্রবেশ প্রক্রিয়া',ex:'Endocytosis brings substances into the cell.'},
  {en:'Exocytosis',bn:'বহিঃক্ষরণ',ex:'Exocytosis expels materials from the cell.'},
  {en:'Symbiosis',bn:'মিথোজীবিতা',ex:'Lichen is a symbiosis of fungi and algae.'},
  {en:'Commensalism',bn:'সহভোজিতা',ex:'Barnacles on whales show commensalism.'},
  {en:'Mutualism',bn:'পারস্পরিক সহযোগিতা',ex:'Bees and flowers demonstrate mutualism.'},
  {en:'Parasitism',bn:'পরজীবিতা',ex:'A tapeworm shows parasitism in the gut.'},
  {en:'Pathogen',bn:'রোগজীবাণু',ex:'Bacteria are common pathogens.'},
  {en:'Antigen',bn:'অ্যান্টিজেন',ex:'An antigen triggers immune response.'},
  {en:'Antibody',bn:'অ্যান্টিবডি',ex:'Antibodies neutralise antigens.'},
  {en:'Vaccine',bn:'টিকা',ex:'A vaccine prevents infectious disease.'},
  {en:'Enzyme',bn:'উৎসেচক / এনজাইম',ex:'Enzymes speed up biochemical reactions.'},
  {en:'Substrate',bn:'ক্রিয়াধার',ex:'The substrate binds to the enzyme active site.'},
  {en:'Catalyst',bn:'অনুঘটক',ex:'A catalyst lowers activation energy.'},
  {en:'Inhibitor',bn:'বাধক / প্রতিরোধক',ex:'An inhibitor reduces enzyme activity.'},
  {en:'Coenzyme',bn:'সহ-উৎসেচক',ex:'Vitamins often act as coenzymes.'},
  {en:'Transpiration',bn:'বাষ্পমোচন',ex:'Transpiration pulls water up through xylem.'},
  {en:'Photosynthesis',bn:'সালোকসংশ্লেষণ',ex:'Photosynthesis converts light to glucose.'},
  {en:'Respiration',bn:'শ্বসন',ex:'Respiration releases energy from glucose.'},
  {en:'Fermentation',bn:'গাঁজন / গাঁজন প্রক্রিয়া',ex:'Fermentation produces ethanol from glucose.'},
  {en:'Diffusion',bn:'ব্যাপন',ex:'Oxygen enters cells by diffusion.'},
  {en:'Osmotic pressure',bn:'অভিস্রবণ চাপ',ex:'High osmotic pressure draws water in.'},
  {en:'Trophic level',bn:'পুষ্টিস্তর',ex:'Plants occupy the first trophic level.'},
  {en:'Biodiversity',bn:'জীববৈচিত্র্য',ex:'Biodiversity supports ecosystem stability.'},
  {en:'Deforestation',bn:'বনউজাড়',ex:'Deforestation reduces biodiversity.'},
  {en:'Mutation',bn:'মিউটেশন / জিন পরিবর্তন',ex:'A mutation in DNA may cause disease.'},
  {en:'Chromosome',bn:'ক্রোমোজোম',ex:'Humans have 46 chromosomes.'},
  {en:'Allele',bn:'অ্যালিল / জিনের রূপ',ex:'Dominant alleles mask recessive ones.'},
  {en:'Genotype',bn:'জিনোটাইপ',ex:'Genotype is the genetic make-up.'},
  {en:'Phenotype',bn:'ফিনোটাইপ',ex:'Phenotype is the observable trait.'},
  {en:'Meiosis',bn:'মিয়োসিস / হ্রাস বিভাজন',ex:'Meiosis produces gametes with half chromosomes.'},
  {en:'Mitosis',bn:'মাইটোসিস / সমবিভাজন',ex:'Mitosis produces identical daughter cells.'},
  {en:'Dominant',bn:'প্রকট',ex:'Brown eye colour is dominant over blue.'},
  {en:'Recessive',bn:'প্রচ্ছন্ন',ex:'Blue eyes result from a recessive allele.'},
  {en:'Heterozygous',bn:'বিষমযুগ্মক',ex:'A heterozygous individual has two different alleles.'},
  {en:'Homozygous',bn:'সমযুগ্মক',ex:'A homozygous individual has two identical alleles.'},
  {en:'Taxonomy',bn:'শ্রেণিবিন্যাস বিদ্যা',ex:'Taxonomy classifies living organisms.'},
  {en:'Phylogeny',bn:'বিবর্তনীয় সম্পর্ক',ex:'Phylogeny studies evolutionary relationships.'},
  {en:'Prokaryote',bn:'আদিকোষী জীব',ex:'Bacteria are prokaryotes without a nucleus.'},
  {en:'Eukaryote',bn:'প্রকৃতকোষী জীব',ex:'Animal cells are eukaryotes.'},
  {en:'Nucleus',bn:'কোষকেন্দ্র / নিউক্লিয়াস',ex:'The nucleus controls cell activities.'},
  {en:'Ribosome',bn:'রাইবোজোম',ex:'Ribosomes synthesise proteins.'},
  {en:'Mitochondria',bn:'মাইটোকন্ড্রিয়া',ex:'Mitochondria produce ATP energy.'},
  {en:'Chloroplast',bn:'ক্লোরোপ্লাস্ট',ex:'Chloroplasts carry out photosynthesis.'},
  {en:'Vacuole',bn:'গহ্বর / ভ্যাকুওল',ex:'The central vacuole stores water in plants.'},
  {en:'Cell wall',bn:'কোষ প্রাচীর',ex:'The cell wall gives plants their shape.'},
  {en:'Plasma membrane',bn:'কোষ ঝিল্লি',ex:'The plasma membrane controls what enters the cell.'},
  {en:'Cytoplasm',bn:'কোষরস / সাইটোপ্লাজম',ex:'Cytoplasm fills the cell outside the nucleus.'},
  {en:'ATP',bn:'অ্যাডিনোসিন ট্রাইফসফেট (শক্তির মুদ্রা)',ex:'ATP provides energy for cellular work.'},
  {en:'Haemoglobin',bn:'হিমোগ্লোবিন',ex:'Haemoglobin carries oxygen in red blood cells.'},
  {en:'Plasma',bn:'রক্তরস / প্লাজমা',ex:'Plasma is the liquid component of blood.'},
  {en:'Lymph',bn:'লসিকা',ex:'Lymph drains excess fluid from tissues.'},
  {en:'Neuron',bn:'স্নায়ুকোষ / নিউরন',ex:'Neurons transmit electrical signals.'},
  {en:'Synapse',bn:'সংযোগস্থল / সিন্যাপ্স',ex:'Signals cross the synapse via neurotransmitters.'},
  {en:'Reflex',bn:'প্রতিবর্ত ক্রিয়া',ex:'A reflex is an automatic response to stimulus.'},
  {en:'Hormone',bn:'হরমোন',ex:'Hormones regulate body processes.'},
  {en:'Insulin',bn:'ইনসুলিন',ex:'Insulin lowers blood glucose levels.'},
  {en:'Glucagon',bn:'গ্লুকাগন',ex:'Glucagon raises blood glucose levels.'},
  {en:'Nephron',bn:'নেফ্রন',ex:'Nephrons filter blood in the kidney.'},
  {en:'Glomerulus',bn:'গ্লোমেরুলাস',ex:'The glomerulus filters blood under pressure.'},
  {en:'Peristalsis',bn:'পেরিস্টালসিস / অন্ত্রের তরঙ্গ সংকোচন',ex:'Peristalsis moves food through the gut.'},
  {en:'Villi',bn:'অন্ত্রীয় রোম / ভিলাই',ex:'Villi increase surface area in the small intestine.'},
  {en:'Bile',bn:'পিত্ত',ex:'Bile emulsifies fats for digestion.'},
  {en:'Alveoli',bn:'বায়ুথলি / অ্যালভিওলাই',ex:'Alveoli are where gas exchange occurs in lungs.'},
  {en:'Diaphragm',bn:'মধ্যচ্ছদা',ex:'The diaphragm contracts during inhalation.'},
  {en:'Systole',bn:'হৃদ-সংকোচন',ex:'Systole pumps blood out of the heart.'},
  {en:'Capillary',bn:'কৈশিক নালি',ex:'Capillaries allow exchange of nutrients.'},
  {en:'Artery',bn:'ধমনি',ex:'Arteries carry blood away from the heart.'},
  {en:'Vein',bn:'শিরা',ex:'Veins return blood to the heart.'},
  {en:'Zygote',bn:'জাইগোট / নিষিক্ত ডিম্বাণু',ex:'A zygote forms after fertilisation.'},
  {en:'Embryo',bn:'ভ্রূণ',ex:'An embryo develops into a foetus.'},
  {en:'Placenta',bn:'অমরা / প্লাসেন্টা',ex:'The placenta nourishes the developing baby.'},
  {en:'Meiotic division',bn:'মিয়োটিক বিভাজন',ex:'Meiotic division halves the chromosome number.'},
  {en:'Germination',bn:'অঙ্কুরোদগম',ex:'Germination is the sprouting of a seed.'},
  {en:'Pollination',bn:'পরাগায়ন',ex:'Pollination transfers pollen to the stigma.'},
  {en:'Fertilisation',bn:'নিষেক',ex:'Fertilisation joins sperm and egg nuclei.'},
  {en:'Xylem',bn:'জাইলেম',ex:'Xylem transports water upward in plants.'},
  {en:'Phloem',bn:'ফ্লোয়েম',ex:'Phloem transports sugars through the plant.'},
  {en:'Stoma',bn:'পত্ররন্ধ্র',ex:'Stomata control gas exchange in leaves.'},
  {en:'Tropism',bn:'অনুবর্তন / ট্রপিজম',ex:'Phototropism bends plants towards light.'},
  {en:'Auxin',bn:'অক্সিন',ex:'Auxin promotes cell elongation.'},
  {en:'Biomass',bn:'জৈববস্তু',ex:'Biomass decreases at higher trophic levels.'},
  {en:'Decomposer',bn:'বিয়োজক',ex:'Decomposers break down dead organic matter.'},
  {en:'Ecology',bn:'বাস্তুবিদ্যা',ex:'Ecology studies organisms and their environment.'},
  {en:'Niche',bn:'বাস্তু-ভূমিকা',ex:'Each organism fills a specific ecological niche.'},
];

function getVocabState(){
  try{ const d=JSON.parse(localStorage.getItem('qc_vocab')||'null'); if(d)return d; }catch{}
  return{day:0,date:'',xp:0,streak:0,lastDate:'',words:VOCAB_BANK.map(()=>({mastery:0,correct:0})),todayDone:0};
}
function saveVocabState(d){ localStorage.setItem('qc_vocab',JSON.stringify(d)); }

const WORDS_PER_DAY=10;
function getTodayWords(state){
  const total=VOCAB_BANK.length, idx=(state.day*WORDS_PER_DAY)%total;
  const today=[]; for(let i=0;i<WORDS_PER_DAY&&i<total;i++) today.push({...VOCAB_BANK[(idx+i)%total],bankIdx:(idx+i)%total});
  return today;
}
function getYesterdayWords(state){
  if(state.day===0)return[];
  const total=VOCAB_BANK.length, idx=((state.day-1)*WORDS_PER_DAY)%total;
  const yest=[]; for(let i=0;i<WORDS_PER_DAY&&i<total;i++) yest.push({...VOCAB_BANK[(idx+i)%total],bankIdx:(idx+i)%total});
  return yest;
}

function loadVocab(){
  vocabState=getVocabState();
  const today=getBDDate();
  // New day check
  if(vocabState.date!==today){
    if(vocabState.date){ vocabState.day++; }
    vocabState.date=today; vocabState.todayDone=0;
    // Streak
    const yest=getBDDate(-1);
    if(vocabState.lastDate===yest) vocabState.streak=(vocabState.streak||0)+1;
    else if(vocabState.lastDate!==today) vocabState.streak=0;
    saveVocabState(vocabState);
  }
  updateVocabHeader();
  buildVocabSession();
}

function updateVocabHeader(){
  document.getElementById('vocab-streak-display').textContent=(vocabState.streak||0)+' day streak';
  document.getElementById('vocab-xp-display').textContent=(vocabState.xp||0)+' XP';
  const todayWords=getTodayWords(vocabState), yestWords=getYesterdayWords(vocabState);
  const total=(todayWords.length)+(yestWords.length); // quiz + learn
  const done=vocabState.todayDone||0;
  document.getElementById('vdp-label').textContent=done+'/'+total*2;
  const arc=document.getElementById('vdp-arc');
  const pct=total*2>0?done/(total*2):0;
  arc.style.strokeDashoffset=CIRCUMFERENCE*(1-pct);
}

function buildVocabSession(){
  const el=document.getElementById('vocab-loading');
  const learnEl=document.getElementById('vocab-learn');
  const quizEl=document.getElementById('vocab-quiz');
  const doneEl=document.getElementById('vocab-done');
  el.classList.remove('hidden'); learnEl.classList.add('hidden'); quizEl.classList.add('hidden'); doneEl.classList.add('hidden');

  const todayWords=getTodayWords(vocabState);
  const yestWords=getYesterdayWords(vocabState);

  // Session = quiz on yesterday's words (both directions) + learn today's words
  vocabSession=[];
  // Quiz yesterday's words — EN→BN then BN→EN
  yestWords.forEach(w=>{ vocabSession.push({...w,mode:'quiz-en'}); vocabSession.push({...w,mode:'quiz-bn'}); });
  // Learn today's words
  todayWords.forEach(w=>{ vocabSession.push({...w,mode:'learn'}); });

  vocabSessIdx=vocabState.todayDone||0;
  if(vocabSessIdx>=vocabSession.length){ showVocabDone(); el.classList.add('hidden'); return; }
  el.classList.add('hidden');
  renderVocabCard();
}

function renderVocabCard(){
  if(vocabSessIdx>=vocabSession.length){ showVocabDone(); return; }
  const item=vocabSession[vocabSessIdx];
  document.getElementById('vocab-learn').classList.add('hidden');
  document.getElementById('vocab-quiz').classList.add('hidden');
  if(item.mode==='learn') renderVocabLearn(item);
  else renderVocabQuiz(item);
}

function renderVocabLearn(item){
  vocabFlipped=false;
  const el=document.getElementById('vocab-learn');
  el.classList.remove('hidden');
  el.innerHTML=`<div class="vocab-card" onclick="flipVocabCard(this,'${escHtml(item.bn)}','${escHtml(item.ex||'')}')">
    <div class="vocab-card-lang">English</div>
    <div class="vocab-word">${escHtml(item.en)}</div>
    <div class="vocab-tap-hint" id="vocab-flip-hint">Tap to reveal meaning</div>
  </div>
  <div class="vocab-actions mt-12">
    <button class="vocab-btn-dontknow" onclick="vocabMarkLearn(false)">Didn't Know</button>
    <button class="vocab-btn-know" onclick="vocabMarkLearn(true)">Got It</button>
  </div>`;
}

function flipVocabCard(card,bn,ex){
  if(vocabFlipped)return;
  vocabFlipped=true;
  const hint=document.getElementById('vocab-flip-hint');
  if(hint)hint.textContent='';
  const meaning=document.createElement('div'); meaning.className='vocab-meaning'; meaning.textContent=bn;
  const example=ex?(() =>{ const d=document.createElement('div'); d.className='vocab-example'; d.textContent=ex; return d; })():null;
  card.appendChild(meaning); if(example)card.appendChild(example);
  card.style.borderColor='var(--border3)';
}

function vocabMarkLearn(knew){
  if(!vocabFlipped){ toast('Tap the card to reveal the meaning first','info'); return; }
  vocabState.xp=(vocabState.xp||0)+(knew?10:0);
  vocabState.todayDone=(vocabState.todayDone||0)+1;
  vocabState.lastDate=getBDDate();
  saveVocabState(vocabState);
  vocabSessIdx++;
  updateVocabHeader();
  renderVocabCard();
}

function renderVocabQuiz(item){
  const el=document.getElementById('vocab-quiz');
  el.classList.remove('hidden');
  const isEnToBn=item.mode==='quiz-en';
  const question=isEnToBn?item.en:item.bn;
  const correct=isEnToBn?item.bn:item.en;
  // Generate distractors
  const distractors=VOCAB_BANK.filter(w=>w.en!==item.en).sort(()=>Math.random()-0.5).slice(0,3).map(w=>isEnToBn?w.bn:w.en);
  const options=[correct,...distractors].sort(()=>Math.random()-0.5);
  el.innerHTML=`<div class="vocab-quiz-word"><span class="vocab-card-lang">${isEnToBn?'English':'বাংলা'}</span>${escHtml(question)}</div>
  <div class="section-title mt-4">Choose the correct ${isEnToBn?'meaning (বাংলা)':'meaning (English)'}</div>
  <div class="vocab-options">${options.map(o=>`<button class="vocab-option" onclick="checkVocabAnswer(this,'${escHtml(o)}','${escHtml(correct)}')">${escHtml(o)}</button>`).join('')}</div>`;
}

function checkVocabAnswer(btn,chosen,correct){
  document.querySelectorAll('.vocab-option').forEach(b=>b.onclick=null);
  const isC=chosen===correct;
  btn.classList.add(isC?'correct':'wrong');
  if(!isC) document.querySelectorAll('.vocab-option').forEach(b=>{ if(b.textContent===correct)b.classList.add('correct'); });
  vocabState.xp=(vocabState.xp||0)+(isC?10:0);
  vocabState.todayDone=(vocabState.todayDone||0)+1;
  const item=vocabSession[vocabSessIdx];
  if(item?.bankIdx!==undefined){
    if(!vocabState.words[item.bankIdx])vocabState.words[item.bankIdx]={mastery:0,correct:0};
    if(isC)vocabState.words[item.bankIdx].mastery=Math.min(4,vocabState.words[item.bankIdx].mastery+1);
    else vocabState.words[item.bankIdx].mastery=Math.max(0,vocabState.words[item.bankIdx].mastery-1);
  }
  vocabState.lastDate=getBDDate();
  saveVocabState(vocabState);
  setTimeout(()=>{ vocabSessIdx++; updateVocabHeader(); renderVocabCard(); },isC?700:1200);
}

function showVocabDone(){
  const el=document.getElementById('vocab-done');
  document.getElementById('vocab-learn').classList.add('hidden');
  document.getElementById('vocab-quiz').classList.add('hidden');
  el.classList.remove('hidden');
  el.innerHTML=`<div class="score-display fade-up" style="margin-top:16px;"><span class="grade-badge" style="-webkit-text-fill-color:var(--gold);color:var(--gold);font-size:48px;">Done</span><div class="score-frac">${vocabState.xp} XP</div><div class="score-pts">Streak: <span>${vocabState.streak} days</span></div></div><div class="section-title mt-12">Come back tomorrow for 10 new words</div>`;
}

// ── PARTICLE SYSTEM ───────────────────────────────────────────────────────────
function initParticles(){
  const canvas=document.getElementById('particle-canvas'); if(!canvas)return;
  const ctx=canvas.getContext('2d');
  let W,H,particles;
  function resize(){ W=canvas.width=window.innerWidth; H=canvas.height=window.innerHeight; }
  function createParticle(){ return{x:Math.random()*W,y:Math.random()*H,r:Math.random()*1.8+0.4,dx:(Math.random()-0.5)*0.3,dy:-(Math.random()*0.4+0.1),alpha:Math.random()*0.4+0.1,pulse:Math.random()*Math.PI*2}; }
  function init(){ resize(); particles=Array.from({length:55},createParticle); }
  function draw(){
    ctx.clearRect(0,0,W,H);
    for(const p of particles){
      p.pulse+=0.015; p.x+=p.dx; p.y+=p.dy;
      const alpha=p.alpha*(0.5+0.5*Math.sin(p.pulse));
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fillStyle=`rgba(139,0,0,${alpha})`; ctx.fill();
      if(p.r>1.4){ ctx.beginPath(); ctx.arc(p.x,p.y,p.r*0.35,0,Math.PI*2); ctx.fillStyle=`rgba(196,30,58,${alpha*0.8})`; ctx.fill(); }
      if(p.y<-10||p.x<-10||p.x>W+10){ Object.assign(p,createParticle()); p.y=H+10; p.x=Math.random()*W; }
    }
    for(let i=0;i<particles.length;i++) for(let j=i+1;j<particles.length;j++){
      const dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y, dist=Math.sqrt(dx*dx+dy*dy);
      if(dist<90){ ctx.beginPath(); ctx.moveTo(particles[i].x,particles[i].y); ctx.lineTo(particles[j].x,particles[j].y); ctx.strokeStyle=`rgba(107,0,0,${0.04*(1-dist/90)})`; ctx.lineWidth=0.4; ctx.stroke(); }
    }
    requestAnimationFrame(draw);
  }
  window.addEventListener('resize',resize); init(); draw();
}

// ── ADMIN ─────────────────────────────────────────────────────────────────────
function initAdminPage(){
  if(adminUnlocked){ document.getElementById('admin-lock').classList.add('hidden'); document.getElementById('admin-dash').classList.remove('hidden'); loadAdminData(); }
  else{ document.getElementById('admin-lock').classList.remove('hidden'); document.getElementById('admin-dash').classList.add('hidden'); document.getElementById('admin-pw').value=''; document.getElementById('admin-pw-err').textContent=''; }
}
function adminLogin(){
  const pw=document.getElementById('admin-pw').value;
  const errEl=document.getElementById('admin-pw-err');
  if(pw!=='J111005376a'){ errEl.textContent='Wrong password.'; document.getElementById('admin-pw').value=''; return; }
  adminUnlocked=true; errEl.textContent='';
  document.getElementById('admin-lock').classList.add('hidden');
  document.getElementById('admin-dash').classList.remove('hidden');
  loadAdminData();
}

async function loadAdminData(){
  try{
    const [scores,daily]=await Promise.all([fetchScores(),fetchDaily().catch(()=>null)]);
    const allScores=scores?.scores||{}, streaks=scores?.streaks||{};
    const realIds=Object.keys(allScores).filter(id=>!id.startsWith('700000000000000'));
    const bdDate=getBDDate();
    const histMap={};
    await Promise.all(realIds.map(async id=>{ try{ histMap[id]=await fetchHistory(id); }catch{ histMap[id]=[]; } }));
    const donePlayers=realIds.filter(id=>histMap[id]?.includes(bdDate));
    const missedPlayers=realIds.filter(id=>!histMap[id]?.includes(bdDate));
    const catchupPlayers=realIds.filter(id=>(allScores[id]?.catchup_owed||0)>0);
    document.getElementById('adm-total-players').textContent=realIds.length;
    document.getElementById('adm-today-done').textContent=donePlayers.length;
    document.getElementById('adm-catchup-pending').textContent=catchupPlayers.length;
    document.getElementById('adm-sessions').textContent=formatNum(scores?.session_count||0);
    // Quiz info
    const qc=document.getElementById('adm-quiz-info');
    if(!daily||!daily.date){ qc.innerHTML='<div class="empty-state" style="padding:20px;">No quiz posted yet</div>'; }
    else{
      const now=Date.now(), openBD=new Date(daily.open_at+6*3600000).toISOString().slice(11,16), expBD=new Date(daily.expires_at+6*3600000).toISOString().slice(11,16);
      const status=now>=daily.open_at&&now<daily.expires_at?'Live':now>=daily.expires_at?'Expired':'Scheduled';
      qc.innerHTML=`<div class="adm-quiz-row"><span class="adm-quiz-label">Date</span><span class="adm-quiz-val">${escHtml(daily.date)}</span></div><div class="adm-quiz-row"><span class="adm-quiz-label">Code</span><span class="adm-quiz-val" style="color:var(--red-main);letter-spacing:3px;">${escHtml(daily.code||'—')}</span></div><div class="adm-quiz-row"><span class="adm-quiz-label">Status</span><span class="adm-quiz-val">${status}</span></div><div class="adm-quiz-row"><span class="adm-quiz-label">Window</span><span class="adm-quiz-val">${openBD} → ${expBD} BD</span></div><div class="adm-quiz-row"><span class="adm-quiz-label">Completion</span><span class="adm-quiz-val">${donePlayers.length} / ${realIds.length}</span></div>`;
    }
    renderAdminList('adm-done-list',donePlayers,allScores,streaks,'done');
    renderAdminList('adm-missed-list',missedPlayers,allScores,streaks,'missed');
    // Catchup list
    const cuEl=document.getElementById('adm-catchup-list');
    const cuSorted=catchupPlayers.sort((a,b)=>(allScores[b]?.catchup_owed||0)-(allScores[a]?.catchup_owed||0));
    cuEl.innerHTML=cuSorted.length?cuSorted.map((id,i)=>{ const s=allScores[id]; return`<div class="adm-row"><div class="adm-rank">${i+1}</div><div class="adm-name">${escHtml(s.username)}</div><div class="adm-badge catchup">${s.catchup_owed} owed</div><div class="adm-meta">${formatNum(s.points)}pts</div></div>`; }).join(''):'<div class="empty-state" style="padding:20px;">All caught up</div>';
    // Fake list
    renderFakePlayerList(allScores,streaks);
    // All players
    const allSorted=realIds.map(id=>({id,...allScores[id],streak:streaks[id]?.streak||0})).sort((a,b)=>(b.points||0)-(a.points||0));
    document.getElementById('adm-all-players').innerHTML=allSorted.map((p,i)=>{ const doneT=histMap[p.id]?.includes(bdDate); const acc=p.total?Math.round(p.correct/p.total*100):0; return`<div class="adm-row"><div class="adm-rank">#${i+1}</div><div class="adm-name">${escHtml(p.username)}<div style="font-size:10px;color:var(--muted);font-family:'Space Mono',monospace;">${p.id}</div></div><div style="text-align:right;"><div class="adm-badge ${doneT?'done':'missed'}" style="margin-bottom:3px;">${doneT?'Done':'Missed'}</div><div class="adm-meta">${formatNum(p.points)}pts · ${acc}%${p.catchup_owed?` · <span style="color:var(--yellow);">${p.catchup_owed} owed</span>`:''}</div></div></div>`; }).join('');
  }catch(e){ toast('Failed to load admin data: '+e.message,'error'); }
}

function renderAdminList(elId,ids,allScores,streaks,type){
  const el=document.getElementById(elId);
  if(!ids.length){ el.innerHTML=`<div class="empty-state" style="padding:20px;">${type==='done'?'No completions yet':'All players done today'}</div>`; return; }
  el.innerHTML=ids.map((id,i)=>{ const p=allScores[id]; const acc=p.total?Math.round(p.correct/p.total*100):0; return`<div class="adm-row"><div class="adm-rank">${i+1}</div><div class="adm-name">${escHtml(p.username)}</div><div class="adm-meta">${formatNum(p.points)}pts · ${acc}%</div></div>`; }).join('');
}

// Notifications push
function selectNotifColor(btn){ document.querySelectorAll('.notif-color-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); notifColor=btn.dataset.color; }

async function pushNotification(){
  const title=document.getElementById('notif-title').value.trim();
  const body=document.getElementById('notif-body').value.trim();
  const errEl=document.getElementById('notif-err');
  if(!title||!body){ errEl.textContent='Title and body required'; return; }
  errEl.textContent='';
  try{
    await workerPost('/push-notification',{title,body,color:notifColor,date:getBDDate()});
    toast('Notification pushed!','success');
    document.getElementById('notif-title').value='';
    document.getElementById('notif-body').value='';
  }catch(e){ errEl.textContent='Failed: '+e.message; }
}

// Fake players
function showAddFakeForm(){ editingFakeId=null; document.getElementById('fake-form-title').textContent='Add Fake Player'; document.getElementById('fake-username').value=''; document.getElementById('fake-points').value=''; document.getElementById('fake-streak').value='5'; document.getElementById('fake-correct').value=''; document.getElementById('fake-total').value=''; document.getElementById('fake-form-err').textContent=''; document.getElementById('fake-form').classList.remove('hidden'); }
function showEditFakeForm(id,s,streak){ editingFakeId=id; document.getElementById('fake-form-title').textContent='Edit — '+s.username; document.getElementById('fake-username').value=s.username; document.getElementById('fake-points').value=s.points||0; document.getElementById('fake-streak').value=streak||5; document.getElementById('fake-correct').value=s.correct||0; document.getElementById('fake-total').value=s.total||0; document.getElementById('fake-form-err').textContent=''; document.getElementById('fake-form').classList.remove('hidden'); }
function hideFakeForm(){ document.getElementById('fake-form').classList.add('hidden'); editingFakeId=null; }
async function saveFakePlayer(){
  const btn=document.getElementById('fake-save-btn'), errEl=document.getElementById('fake-form-err');
  const username=document.getElementById('fake-username').value.trim();
  if(!username){ errEl.textContent='Username required'; return; }
  const data={username,points:document.getElementById('fake-points').value||0,streak:document.getElementById('fake-streak').value||5,correct:document.getElementById('fake-correct').value||0,total:document.getElementById('fake-total').value||0};
  btn.disabled=true; btn.textContent='…'; errEl.textContent='';
  try{ await workerPost('/manage-fake',editingFakeId?{action:'edit',id:editingFakeId,data}:{action:'add',data}); toast(editingFakeId?'Updated!':'Added!','success'); hideFakeForm(); await loadAdminData(); }
  catch(e){ errEl.textContent='Failed: '+e.message; }
  finally{ btn.disabled=false; btn.textContent='Save'; }
}
async function deleteFakePlayer(id,name){ if(!confirm(`Delete "${name}"?`))return; try{ await workerPost('/manage-fake',{action:'delete',id}); toast('Deleted','success'); await loadAdminData(); }catch(e){ toast('Failed: '+e.message,'error'); } }
async function simulateFake(id){ try{ await workerPost('/simulate-fakes',{ids:[id],date:getBDDate()}); toast('Simulated!','success'); await loadAdminData(); }catch(e){ toast('Failed: '+e.message,'error'); } }
async function bulkSimulateFakes(){
  const btn=event.target; btn.disabled=true; btn.textContent='Simulating...';
  try{ const res=await workerPost('/simulate-fakes',{date:getBDDate()}); toast(`Simulated ${res.simulated} players!`,'success'); await loadAdminData(); }
  catch(e){ toast('Failed: '+e.message,'error'); }
  finally{ btn.disabled=false; btn.textContent='Simulate All'; }
}
function renderFakePlayerList(allScores,streaks){
  const el=document.getElementById('adm-fake-list'); if(!el)return;
  const fakes=Object.keys(allScores).filter(id=>id.startsWith('700000000000000')).map(id=>({id,...allScores[id],streak:streaks[id]?.streak||0})).sort((a,b)=>(b.points||0)-(a.points||0));
  if(!fakes.length){ el.innerHTML='<div class="empty-state" style="padding:20px;">No fake players yet</div>'; return; }
  el.innerHTML=fakes.map(p=>{ const acc=p.total?Math.round(p.correct/p.total*100):0; return`<div class="fake-player-row"><div class="fake-player-info"><div class="fake-player-name">${escHtml(p.username)}</div><div class="fake-player-meta">${formatNum(p.points)} pts · ${acc}% · ${p.streak} streak</div></div><div class="fake-action-btns"><button class="fake-btn sim" onclick="simulateFake('${p.id}')">Sim</button><button class="fake-btn edit" onclick="showEditFakeForm('${p.id}',${JSON.stringify({username:p.username,points:p.points,correct:p.correct,total:p.total})},${p.streak})">Edit</button><button class="fake-btn del" onclick="deleteFakePlayer('${p.id}','${escHtml(p.username)}')">Del</button></div></div>`; }).join('');
}

// ── INIT ──────────────────────────────────────────────────────────────────────
function init(){
  initParticles();
  loadUser();
  if(location.hash==='#admin'){ document.body.classList.remove('no-chrome'); document.getElementById('top-nav').classList.remove('hidden'); showPage('admin'); return; }
  if(user){ document.body.classList.remove('no-chrome'); showPage('dashboard'); }
  else showPage('login');
}

init();
