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
let lastExamExport = null;
let quizTimeLeft   = {}; // per-question remaining seconds, persists across navigation
let quizTimedOut   = {}; // per-question flag once its timer has hit 0
let timerRemaining= 25;

// Practice
let practiceBank      = [];
let practiceQuestions = [];
let practiceAnswers   = {};
let practiceIndex     = 0;
let practiceConfig    = { subject:'all', count:10, timer:0, mode:'after' };
let practiceTimerInt  = null;
let practiceTimeLeft  = {}; // per-question remaining seconds, persists across navigation
let practiceTimedOut  = {};
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

// Admin (adminToken/adminJsLoaded declared near the admin-loading code further down;
// editingFakeId/notifColor live in admin.js, which only loads after login)

// PDF Hub
let pdfHubData = null;
const pdfState = { pub: { path: [] }, admin: { path: [] } };

// Leaderboard
let lbMode = 'alltime'; // 'alltime' | 'weekly'

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
const NAV_MAP={dashboard:'home',exams:'quiz',quiz:'quiz',practice:'quiz',result:'quiz',leaderboard:'ranks',profile:'profile'};

function navTap(btn,page){
  // Bounce animation
  btn.classList.add('tapped');
  setTimeout(()=>btn.classList.remove('tapped'),200);
  showPage(page);
}

function showPage(name){
  if(name==='quiz'&&quizQuestions.length===0){ toast('Enter the code from Discord to start the exam','info'); name='exams'; }
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
  if(name==='exams')       loadExamsHub();
  if(name==='leaderboard') loadLeaderboard();
  if(name==='profile')     loadProfile();
  if(name==='syllabus')    { loadSyllabus(); scheduleSylReminderBanner(); }
  if(name==='practice')    loadPracticePage();
  if(name==='vocabulary')  loadVocab();
  if(name==='admin')       initAdminPage();
  if(name==='pdfhub')      loadPdfHub('pub');
  if(name==='journal')     loadJournalPage();
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

// ── RECHECK / FLAG QUESTION ─────────────────────────────────────────────────────
const SUPPORT_DISCORD_URL='https://discord.com/users/710746320071032863';

function getCurrentQ(ctx){
  if(ctx==='practice') return practiceQuestions[practiceIndex];
  if(ctx==='main')     return quizQuestions[quizIndex];
  return null;
}

function recheckQuestion(ctx){
  const q=getCurrentQ(ctx);
  if(!q||!q.question){ toast('No question loaded to recheck','error'); return; }
  window.open(`https://www.google.com/search?q=${encodeURIComponent(q.question)}`,'_blank');
  toast('Opened the question in a new tab','info');
}

async function flagQuestion(ctx){
  const q=getCurrentQ(ctx);

  if(!q||!q.question){
    // General report — no specific question in context (e.g. opened from the more menu)
    window.open(SUPPORT_DISCORD_URL,'_blank');
    toast('Opened Discord — describe the issue there','info');
    return;
  }

  const optsText=['A','B','C','D'].map(k=>`${k}) ${q.options?.[k]??''}`).join('\n');
  const flagText=`🚩 Flagged Question\nSubject: ${q.subject||'—'}\n\n${q.question}\n\n${optsText}\n\nMarked answer: ${q.answer||'—'}`;

  try{
    await navigator.clipboard.writeText(flagText);
    toast('Question copied — paste it in the Discord chat that just opened','success');
  }catch{
    toast('Could not copy automatically — opening Discord, please describe the question','error');
  }
  window.open(SUPPORT_DISCORD_URL,'_blank');
}

// ── PILOT REQUEST ────────────────────────────────────────────────────────────
function openPilotModal(){
  document.getElementById('pilot-college').value='';
  document.getElementById('pilot-contact').value='';
  document.getElementById('pilot-message').value='';
  document.getElementById('pilot-err').textContent='';
  document.getElementById('pilot-modal-overlay').classList.remove('hidden');
  document.getElementById('pilot-modal').classList.remove('hidden');
}
function closePilotModal(){
  document.getElementById('pilot-modal-overlay').classList.add('hidden');
  document.getElementById('pilot-modal').classList.add('hidden');
}
async function submitPilotRequest(){
  const college=document.getElementById('pilot-college').value.trim();
  const contact=document.getElementById('pilot-contact').value.trim();
  const message=document.getElementById('pilot-message').value.trim();
  const errEl=document.getElementById('pilot-err');
  if(!college||!contact){ errEl.textContent='College name and contact are required'; return; }
  errEl.textContent='';

  const text=`🎓 Pilot Request\nFrom: ${user?.username||'Unknown'} (${user?.discord_id||'—'})\nCollege: ${college}\nContact: ${contact}${message?`\n\nDetails:\n${message}`:''}`;

  try{
    await navigator.clipboard.writeText(text);
    toast('Request copied — paste it in the Discord chat that just opened','success');
  }catch{
    toast('Could not copy automatically — opening Discord, please share the details','error');
  }
  window.open(SUPPORT_DISCORD_URL,'_blank');
  closePilotModal();
}

// ── LOGIN ─────────────────────────────────────────────────────────────────────
let loginCounterVal = null;
let loginCounterTimer = null;
function startLoginCounter(){
  if(loginCounterVal===null) loginCounterVal = getDailyPoolSize();
  document.getElementById('login-players').textContent = formatNum(loginCounterVal);
  if(loginCounterTimer) clearInterval(loginCounterTimer);
  loginCounterTimer = setInterval(()=>{
    const el=document.getElementById('login-players');
    if(!el || !document.getElementById('pg-login').classList.contains('active')){
      clearInterval(loginCounterTimer);
      return;
    }
    const delta = Math.floor(Math.random()*21)-10; // -10..+10
    loginCounterVal = Math.min(1400, Math.max(670, loginCounterVal+delta));
    el.textContent = formatNum(loginCounterVal);
  }, 2600);
}

async function loadLoginPage(){
  startLoginCounter();
  try{
    const data=await fetchScores();
    const ids=Object.keys(data.scores||{});
    document.getElementById('login-sessions').textContent=data.session_count||0;
    const sorted=ids.map(id=>({...data.scores[id],id})).sort((a,b)=>(b.points||0)-(a.points||0)).slice(0,5);
    const medals=['🥇','🥈','🥉'];
    document.getElementById('login-lb-list').innerHTML=sorted.length===0
      ?'<div class="empty-state">No players yet</div>'
      :sorted.map((p,i)=>`<div class="public-lb-row"><div class="lb-rank">${medals[i]||(i+1)}</div><div class="lb-name">${escHtml(p.username)}</div><div class="lb-pts">${formatNum(p.points)}</div></div>`).join('');
  }catch{
    document.getElementById('login-sessions').textContent='—';
    document.getElementById('login-lb-list').innerHTML='<div class="empty-state">Could not load</div>';
  }
}

// ── DASHBOARD ─────────────────────────────────────────────────────────────────
const LEVELS=[{name:'Initiate',min:0,max:500},{name:'Scholar',min:500,max:1500},{name:'Expert',min:1500,max:3000},{name:'Master',min:3000,max:Infinity}];

// Permanent activity tier — based on total days/quizzes completed (from days_completed)
const ACTIVITY_TIERS=[
  {name:'Bronze',  min:0,  icon:'🥉'},
  {name:'Silver',  min:15, icon:'🥈'},
  {name:'Gold',    min:40, icon:'🥇'},
  {name:'Diamond', min:80, icon:'💎'},
];
function getActivityTier(days){
  let t=ACTIVITY_TIERS[0];
  for(const tier of ACTIVITY_TIERS){ if(days>=tier.min) t=tier; }
  return t;
}
// ── DRAGON GROWTH / SHIELD STREAK WIDGET ────────────────────────────────────────
// 7-day cycles grow your dragon from a baby to its next life stage. Every completed
// cycle evolves it further. Missing 1-2 consecutive days cracks the shield but the
// dragon is safe; missing a 3rd resets it (handled server-side, lazily).
const DRAGON_TIERS=[
  {name:'Baby',     img:'assets/dragons/dragon-tier0-baby.gif'},
  {name:'Young',    img:'assets/dragons/dragon-tier1-young.gif'},
  {name:'Juvenile', img:'assets/dragons/dragon-tier2-juvenile.gif'},
  {name:'Mature',   img:'assets/dragons/dragon-tier3-mature.gif'},
  {name:'Adult',    img:'assets/dragons/dragon-tier4-adult.gif'},
];
const DRAGON_EMPTY_IMG='assets/dragons/dragon-empty.png';

function daysBetweenBD(a,b){
  const da=new Date(a+'T00:00:00Z').getTime();
  const db=new Date(b+'T00:00:00Z').getTime();
  return Math.round((db-da)/86400000);
}

function getDragonState(streak,lastDate){
  const today=getBDDate();
  const cycleIndex = streak>0 ? Math.floor((streak-1)/7) : 0;
  const tier = DRAGON_TIERS[Math.min(cycleIndex,DRAGON_TIERS.length-1)];
  const dayInCycle = streak>0 ? (((streak-1)%7)+1) : 0; // 1-7, how far through this stage's growth
  const gap = (streak>0 && lastDate) ? daysBetweenBD(lastDate,today) : 0;
  // gap 0-1 = safe (today or "haven't played today yet" — totally normal)
  // gap 2   = 1 day fully missed -> grace, 2 days left before reset
  // gap 3   = 2 days fully missed -> grace, 1 day left (last chance)
  // gap 4+  = already reset server-side (streak comes back as 0)
  const cracks = streak>0 ? Math.max(0,Math.min(2,gap-1)) : 0;
  const daysLeftToBreak = Math.max(0,4-gap);
  let phase='none';
  if(streak>0){
    if(cracks===0) phase = dayInCycle===7 ? 'complete' : 'building';
    else if(cracks===1) phase='grace1';
    else phase='grace2';
  }
  // Scale the sprite up gradually across the 7-day cycle (0.55 -> 1.0) so growth is visible
  // even though each stage is a single sprite, not 7 separate frames.
  const growScale = streak>0 ? (0.55 + (dayInCycle/7)*0.45).toFixed(2) : 0.5;
  return {streak,tier,cycleIndex,dayInCycle,cracks,gap,daysLeftToBreak,phase,growScale};
}

const DRAGON_PHASE_MSG={
  none:      (s)=>`No dragon yet — log in today to hatch one`,
  building:  (s)=>`🥚 Growing — Day ${s.dayInCycle}/7 of its ${s.tier.name} stage. Come back tomorrow!`,
  complete:  (s)=>`✨ Fully grown ${s.tier.name}! Shield holding strong — ${s.streak} day streak`,
  grace1:    (s)=>`⚠️ Grace period — 2 days left. Log in to repair the shield (your dragon is safe for now).`,
  grace2:    (s)=>`🚨 Last chance! Your dragon vanishes tomorrow if you don't log in today.`,
};
const DRAGON_PHASE_CLASS={none:'',building:'',complete:'safe',grace1:'warn',grace2:'danger'};

function buildDragonHTML(state){
  const {tier,streak,cracks,phase,growScale}=state;
  const img = streak>0 ? tier.img : DRAGON_EMPTY_IMG;
  const shieldHtml = streak>0 ? `<div class="dragon-shield crack-${cracks}">🛡️</div>` : '';
  const statusCls = DRAGON_PHASE_CLASS[phase];

  return `
    <div class="castle-header">
      <div class="castle-tier-name">${streak>0?tier.name:'No'} Dragon</div>
      <div class="castle-progress-tag">${streak>0?`Day ${state.dayInCycle}/7`:'Not hatched'}</div>
      <div class="castle-streak-num">${streak}🔥</div>
    </div>
    <div class="dragon-stage">
      ${shieldHtml}
      <img class="dragon-sprite ${streak===0?'dormant':''}" src="${img}" alt="${tier.name} dragon" style="transform:scale(${growScale})"/>
    </div>
    <div class="castle-status ${statusCls}">${DRAGON_PHASE_MSG[phase](state)}</div>`;
}

// Small icon + "Day X/7" summary — used on Profile so it doesn't duplicate the full
// Home widget. Tapping it jumps to the Dashboard where the full dragon widget lives.
function buildDragonCompactHTML(state){
  const {tier,dayInCycle,streak,phase}=state;
  const dot = phase==='grace1' ? '🟡' : phase==='grace2' ? '🔴' : streak>0 ? '🟢' : '⚪';
  const label = streak===0 ? 'No dragon yet' : `${tier.name} Dragon — Day ${dayInCycle}/7`;
  const img = streak>0 ? tier.img : DRAGON_EMPTY_IMG;
  return `<div class="castle-compact" onclick="showPage('dashboard')">
    <img class="castle-compact-icon dragon-compact-icon" src="${img}" alt=""/>
    <div class="castle-compact-info">
      <div class="castle-compact-label">${label}</div>
      <div class="castle-compact-sub">${dot} ${streak} day streak — tap to view</div>
    </div>
  </div>`;
}

function renderCastleWidget(elId,streak,lastDate,compact){
  const el=document.getElementById(elId);
  if(!el)return;
  const state=getDragonState(streak,lastDate);
  el.innerHTML = compact ? buildDragonCompactHTML(state) : buildDragonHTML(state);

  // Detect a break that just happened (client had a higher streak recorded last time we checked)
  const key='dragon_last_streak_'+(user?.discord_id||'anon');
  const prevSeen=Number(localStorage.getItem(key)||0);
  if(prevSeen>=3 && streak===0){
    toast('💔 Your dragon flew away! Log in daily to hatch a new one.','error');
  }
  localStorage.setItem(key,String(streak));
}
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

const GREETING_POOL={
  morning:  ['Good morning','Rise and grind','Morning, early bird!','Fresh start, huh?','Welcome again Doc!','How is life going?'],
  afternoon:['Good afternoon','Feeling lucky?','Back for more?','Midday hustle time','Because you\'re special'],
  evening:  ['Good evening','Look who\'s back!','Ready for round two?','Evening grind time','Almost fell for you, cutie pie'],
  night:    ['Late night grinding?','Burning the midnight oil?','Still up?','Night owl mode: activated','Welcome again Doc!'],
};
function pickGreeting(hr){
  const bucket = hr<5 ? 'night' : hr<12 ? 'morning' : hr<17 ? 'afternoon' : hr<21 ? 'evening' : 'night';
  const pool=GREETING_POOL[bucket];
  return pool[Math.floor(Math.random()*pool.length)];
}

function renderDashHero(scores){
  const me=scores?.scores?.[user.discord_id];
  const myStreak=scores?.streaks?.[user.discord_id]?.streak||0;
  const myLastDate=scores?.streaks?.[user.discord_id]?.last_date||'';
  const pts=me?.points||0;
  const acc=accuracyNum(me?.correct||0,me?.total||0);
  const lvl=getLevelInfo(pts);

  const hr=new Date(Date.now()+6*3600000).getHours();
  document.getElementById('dash-greeting').textContent=pickGreeting(hr);
  document.getElementById('dash-username').textContent=user.username;
  document.getElementById('dash-level-badge').textContent=lvl.name;
  document.getElementById('dash-pts-hero').textContent=formatNum(pts);
  document.getElementById('dash-streak-hero').textContent=myStreak;
  document.getElementById('dash-acc-hero').textContent=acc+'%';
  document.getElementById('level-fill').style.width=lvl.pct+'%';
  document.getElementById('level-current-label').textContent=formatNum(pts)+' pts';
  document.getElementById('level-next-label').textContent=lvl.nextName==='Max'?'Max Level':'Next: '+lvl.nextName+' ('+(lvl.ptsLeft)+' pts)';
  renderCastleWidget('dash-castle-widget',myStreak,myLastDate);

  const owed=me?.catchup_owed||0;
  const sec=document.getElementById('catchup-section');
  if(owed>0){
    sec.classList.remove('hidden');
    document.getElementById('catchup-title').textContent=`${owed} Questions to Catch Up`;
    document.getElementById('catchup-sub').textContent='Complete them to earn back your points';
  } else sec.classList.add('hidden');
}

// Passive dashboard notification — no interactive code entry here anymore,
// that lives on the Exams hub now. Just tells you what's going on and where to go.
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
    const exp=new Date(daily.expires_at+6*3600000).toISOString().slice(11,16);
    card.innerHTML=`<div class="status-badge live"><span class="dot"></span>Live Now</div><div class="status-title">🎯 Daily Quiz is live!</div><div class="status-sub">Closes at ${escHtml(exp)} BD</div><button class="btn-primary w-full mt-8" onclick="showPage('exams')">Go to Exams to Participate →</button>`;
  }
}

// Full interactive card — lives on the Exams hub. Same states as above, but this
// one actually has the code-entry flow that unlocks the daily quiz.
function renderExamDailyCard(daily,history){
  const card=document.getElementById('exam-daily-card');
  if(!card)return;
  const now=Date.now(), bdDate=getBDDate();
  const todayDone=history.includes(bdDate);
  if(!daily||!daily.date){
    card.innerHTML=`<div class="eoc-icon">🗓️</div><div class="eoc-body"><div class="status-badge waiting"><span class="dot"></span>Waiting</div><div class="eoc-title">No Quiz Posted Yet</div><div class="eoc-sub">Check back after 5 AM Bangladesh time</div></div>`;return;
  }
  const isOpen=now>=daily.open_at&&now<daily.expires_at;
  const isExpired=now>=daily.expires_at;
  const notYet=now<daily.open_at;
  if(todayDone){
    card.innerHTML=`<div class="eoc-icon">✅</div><div class="eoc-body"><div class="status-badge done"><span class="dot"></span>Completed</div><div class="eoc-title">Done for Today</div><div class="eoc-sub">Well done. See you tomorrow.</div></div>`;return;
  }
  if(notYet){
    const t=new Date(daily.open_at+6*3600000).toISOString().slice(11,16);
    card.innerHTML=`<div class="eoc-icon">🗓️</div><div class="eoc-body"><div class="status-badge waiting"><span class="dot"></span>Scheduled</div><div class="eoc-title">Quiz Not Open Yet</div><div class="eoc-sub">Opens at ${escHtml(t)} BD</div></div>`;return;
  }
  if(isExpired){
    card.innerHTML=`<div class="eoc-icon">⏰</div><div class="eoc-body"><div class="status-badge expired"><span class="dot"></span>Expired</div><div class="eoc-title">Today's Quiz Closed</div><div class="eoc-sub">Closed at 3:00 AM BD · Opens again at 5:00 AM BD</div></div>`;return;
  }
  if(isOpen){
    const exp=new Date(daily.expires_at+6*3600000).toISOString().slice(11,16);
    card.innerHTML=`<div class="eoc-icon">📅</div><div class="eoc-body"><div class="status-badge live"><span class="dot"></span>Live Now</div><div class="eoc-title">Daily Exam</div><div class="eoc-sub">Closes at ${escHtml(exp)} BD · Enter code from Discord</div><div class="code-entry"><input class="code-input" id="code-field" placeholder="ENTER CODE" maxlength="6" autocomplete="off" spellcheck="false" oninput="this.value=this.value.toUpperCase()" onkeydown="if(event.key==='Enter')verifyCode()"/><button class="btn-primary" id="code-btn" onclick="verifyCode()">Go</button></div><div class="code-error" id="code-err"></div></div>`;
  }
}

async function loadExamsHub(){
  const card=document.getElementById('exam-daily-card');
  card.innerHTML='<div class="center-spinner"><div class="spinner"></div></div>';
  try{
    const [daily,history]=await Promise.all([
      fetchDaily().catch(()=>null),
      fetchHistory(user.discord_id).catch(()=>[]),
    ]);
    renderExamDailyCard(daily,Array.isArray(history)?history:[]);
  }catch{
    card.innerHTML='<div class="empty-state">Failed to load. Check your connection.</div>';
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
  quizAnswers={}; quizIndex=0; quizTimeLeft={}; quizTimedOut={};
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
  const answered=!!quizAnswers[q.id];
  ['A','B','C','D'].forEach(k=>{
    const btn=document.createElement('button');
    btn.className='option-btn'+(quizAnswers[q.id]===k?' selected':'')+(answered?' locked':'');
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
  const q=quizQuestions[quizIndex];
  if(quizAnswers[q.id])return; // already answered — locked in, ignore further taps
  clearTimer();
  quizAnswers[q.id]=key;
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
// Per-question, persisted in quizTimeLeft — navigating away and back (dot-nav,
// prev/next) does NOT grant a fresh 25s. Once a question's timer hits 0 it stays
// locked at 0; answering a question also freezes its clock (no point ticking down
// on something already decided).
const TIMER_SECONDS=25;
function startTimer(){
  clearTimer();
  const q=quizQuestions[quizIndex];
  if(!q)return;
  if(quizTimeLeft[q.id]===undefined) quizTimeLeft[q.id]=TIMER_SECONDS;
  const alreadyAnswered=!!quizAnswers[q.id];
  const alreadyTimedOut=!!quizTimedOut[q.id];
  updateTimerUI(quizTimeLeft[q.id]);
  if(alreadyAnswered||alreadyTimedOut)return; // frozen — no countdown for a settled question
  timerInterval=setInterval(()=>{
    quizTimeLeft[q.id]--;
    updateTimerUI(quizTimeLeft[q.id]);
    if(quizTimeLeft[q.id]<=0){
      quizTimeLeft[q.id]=0;
      quizTimedOut[q.id]=true;
      clearTimer();
      autoAdvance();
    }
  },1000);
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
  lastExamExport={
    type:isCatchup?'Catch-Up Session':'Daily Quiz',
    date:getBDDate(), correct:res.correct, total:res.total, points:res.points,
    questions:prev.map(q=>{ const r=resultMap[q.id]||{}; return{question:q.question,options:q.options,answer:q.answer,given:r.given||quizAnswers[q.id]||'—',isCorrect:!!r.correct,explanation:q.explanation||'',subject:q.subject||''}; }),
  };
  quizQuestions=[]; quizAnswers={};
}

function exportLastExam(){
  if(!lastExamExport){ toast('Nothing to export yet','error'); return; }
  const e=lastExamExport;
  const acc=e.total?Math.round(e.correct/e.total*100):0;
  let out=`QUIZ CHAOS — EXAM EXPORT\n`;
  out+=`${'='.repeat(40)}\n`;
  out+=`Type: ${e.type}\nDate: ${e.date}\nScore: ${e.correct}/${e.total} (${acc}%)${e.points?` · +${e.points} pts`:''}\n`;
  out+=`${'='.repeat(40)}\n\n`;
  e.questions.forEach((q,i)=>{
    out+=`Q${i+1}. [${q.isCorrect?'CORRECT':'WRONG'}]${q.subject?` (${q.subject})`:''}\n${q.question}\n`;
    ['A','B','C','D'].forEach(k=>{ if(q.options?.[k]!==undefined) out+=`   ${k}) ${q.options[k]}\n`; });
    out+=`Correct answer: ${q.answer}\n`;
    if(!q.isCorrect) out+=`Your answer: ${q.given}\n`;
    if(q.explanation) out+=`Explanation: ${q.explanation}\n`;
    out+=`\n`;
  });
  const mistakes=e.questions.filter(q=>!q.isCorrect);
  if(mistakes.length){
    out+=`${'='.repeat(40)}\nMISTAKES SUMMARY (${mistakes.length})\n${'='.repeat(40)}\n\n`;
    mistakes.forEach((q,i)=>{ out+=`${i+1}. ${q.question}\n   Correct: ${q.answer} — ${q.options?.[q.answer]??''}\n   You picked: ${q.given} — ${q.options?.[q.given]??''}\n\n`; });
  }
  const blob=new Blob([out],{type:'text/plain'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url; a.download=`quiz-chaos-${e.date}-${e.type.replace(/[^a-z0-9]+/gi,'-').toLowerCase()}.txt`;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  toast('Exam exported','success');
}

// ── LEADERBOARD ───────────────────────────────────────────────────────────────
// ── FAKE RANK ESTIMATION (cosmetic only — never changes real data) ─────────────
// Deterministic pseudo-random fraction in [0,1) from a string seed, so results
// are stable for everyone on the same day instead of jumping around per reload.
function seededFrac(seedStr){
  let h=0;
  for(let i=0;i<seedStr.length;i++){ h=(h*31+seedStr.charCodeAt(i))>>>0; }
  h^=h<<13; h>>>=0; h^=h>>>17; h^=h<<5; h>>>=0;
  return h/4294967295;
}
// Stable "active players today" figure — same number the login counter is based on
function getDailyPoolSize(){
  return Math.floor(670 + seededFrac('pool-'+getBDDate())*(1400-670));
}
// Estimates where a user outside the real top 25 would "plausibly" sit, given how
// far their score is from the #25 cutoff. Small gap -> just past 25. Big gap or a
// fresh account -> deep in the pool, capped short of dead-last so it stays believable.
function estimateFakeRank(userScore, top25FloorScore, userId){
  const pool=getDailyPoolSize();
  const capRank=Math.round(pool*0.75);
  const gap=Math.max(0, top25FloorScore-userScore);
  const mid=300, steep=60; // tuned so ~100pt gap -> low 50s, ~450pt+ gap -> deep pool
  const t=1/(1+Math.exp((mid-gap)/steep));
  let rank=26+Math.round((capRank-26)*t);
  const jitter=Math.round((seededFrac('jitter-'+getBDDate()+'-'+userId)-0.5)*20); // ±10, stable per user/day
  return Math.min(pool-10, Math.max(27, rank+jitter));
}

function toggleLbMode(mode){
  if(lbMode===mode)return;
  lbMode=mode;
  document.querySelectorAll('.lb-mode-btn').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
  renderLeaderboard();
}

async function loadLeaderboard(){
  const list=document.getElementById('lb-list');
  list.innerHTML='<div class="center-spinner"><div class="spinner"></div></div>';
  try{
    scoresData=await fetchScores();
    renderLeaderboard();
  }catch{ list.innerHTML='<div class="empty-state">Failed to load</div>'; }
}

function renderLeaderboard(){
  const list=document.getElementById('lb-list');
  if(!scoresData){ list.innerHTML='<div class="empty-state">Failed to load</div>'; return; }
  const data=scoresData;
  const weeklyPts=data.weekly?.points||{};
  const isWeekly=lbMode==='weekly';

  let sorted=Object.keys(data.scores||{}).map(id=>({
    id,...data.scores[id],
    streak:data.streaks?.[id]?.streak||0,
    weeklyPts:weeklyPts[id]||0,
  }));
  sorted.sort((a,b)=> isWeekly ? (b.weeklyPts-a.weeklyPts) : ((b.points||0)-(a.points||0)) );
  if(isWeekly) sorted=sorted.filter(p=>p.weeklyPts>0);

  // Work out the real user's standing against the FULL list before we cap the display to 25
  let yourRankHtml='';
  if(user){
    const myIndex=sorted.findIndex(p=>p.id===user.discord_id);
    const myVal=isWeekly?(weeklyPts[user.discord_id]||0):(scoresData?.scores?.[user.discord_id]?.points||0);
    if(myIndex>=25 && sorted.length>=25){
      const floorScore=isWeekly?sorted[24].weeklyPts:sorted[24].points;
      const gap=Math.max(0,floorScore-myVal);
      const fakeRank=estimateFakeRank(myVal,floorScore,user.discord_id);
      yourRankHtml=`<div class="lb-your-rank">
        <div class="lb-your-rank-num">#${formatNum(fakeRank)}</div>
        <div class="lb-your-rank-info">
          <div class="lb-your-rank-label">Your Rank</div>
          <div class="lb-your-rank-gap">${gap>0?`${formatNum(gap)} pts from Top 25`:'Right on the edge of Top 25'}</div>
        </div>
      </div>`;
    } else if(myIndex<0 && sorted.length>=25){
      // User has no entry at all yet (e.g. hasn't played this week) — still show them a plausible spot
      const floorScore=isWeekly?sorted[24].weeklyPts:sorted[24].points;
      const fakeRank=estimateFakeRank(0,floorScore,user.discord_id);
      yourRankHtml=`<div class="lb-your-rank">
        <div class="lb-your-rank-num">#${formatNum(fakeRank)}</div>
        <div class="lb-your-rank-info">
          <div class="lb-your-rank-label">Your Rank</div>
          <div class="lb-your-rank-gap">${isWeekly?'Play today to start climbing':'Complete a quiz to get ranked'}</div>
        </div>
      </div>`;
    }
  }

  sorted=sorted.slice(0,25);

  if(!sorted.length){ list.innerHTML=`<div class="empty-state">${isWeekly?'No points scored yet this week':'No players yet'}</div>`+yourRankHtml; return; }

  const medals=['🥇','🥈','🥉'];
  const podium=sorted.slice(0,3);
  const rest=sorted.slice(3);

  let html='';
  if(podium.length){
    // Reorder visually as 2nd-1st-3rd for a classic podium look
    const order=[podium[1],podium[0],podium[2]].filter(Boolean);
    html+=`<div class="lb-podium">`+order.map(p=>{
      if(!p)return'';
      const rank=sorted.indexOf(p)+1;
      const isMe=user&&p.id===user.discord_id;
      const tier=getActivityTier(p.days_completed||0);
      const val=isWeekly?p.weeklyPts:p.points;
      return`<div class="lb-podium-slot rank-${rank}${isMe?' me':''}">
        <div class="lb-podium-medal">${medals[rank-1]}</div>
        <div class="lb-podium-name">${escHtml(p.username)}</div>
        <div class="lb-podium-pts">${formatNum(val)}</div>
        <div class="lb-podium-stand">${rank}</div>
      </div>`;
    }).join('')+`</div>`;
  }

  html+=rest.map((p,i)=>{
    const rank=i+4;
    const isMe=user&&p.id===user.discord_id;
    const acc=accuracy(p.correct||0,p.total||0);
    const tier=getActivityTier(p.days_completed||0);
    const val=isWeekly?p.weeklyPts:p.points;
    const trophyBadge=p.weekly_trophies?`<span class="lb-trophy" title="${p.weekly_trophies}x Weekly Champion">🏆${p.weekly_trophies>1?'×'+p.weekly_trophies:''}</span>`:'';
    return`<div class="lb-item${isMe?' me':''}">
      <div class="rank-num">${rank}</div>
      <div class="lb-info">
        <div class="lb-username">${escHtml(p.username)}${trophyBadge}<span class="lb-tier-icon" title="${tier.name} tier — ${p.days_completed||0} days completed">${tier.icon}</span>${isMe?' <span style="color:var(--red-bright);font-size:10px;font-weight:700;">you</span>':''}</div>
        <div class="lb-meta">${acc} · ${p.streak} day streak</div>
      </div>
      <div class="lb-right">
        <div class="lb-pts-big">${formatNum(val)}</div>
        <div class="lb-streak">${isWeekly?'this week':formatNum(p.correct||0)+' correct'}</div>
      </div>
    </div>`;
  }).join('');

  list.innerHTML=html+yourRankHtml;
}

// ── PROFILE ───────────────────────────────────────────────────────────────────
async function loadProfile(){
  if(!user)return;

  // Avatar
  const av   = avatarUrl(user.discord_id, user.avatar);
  const img  = document.getElementById('prof-avatar');
  const fall = document.getElementById('prof-avatar-fallback');
  if(av){ img.src=av; img.classList.remove('hidden'); fall.classList.add('hidden'); }
  else{ fall.textContent=(user.username||'P')[0].toUpperCase(); fall.classList.remove('hidden'); img.classList.add('hidden'); }

  document.getElementById('prof-name').textContent = user.username;
  document.getElementById('prof-id').textContent   = '#' + user.discord_id;

  try{
    const [scores, history] = await Promise.all([
      fetchScores(),
      fetchHistory(user.discord_id).catch(()=>[]),
    ]);

    const me       = scores?.scores?.[user.discord_id];
    const myStreak = scores?.streaks?.[user.discord_id]?.streak || 0;
    const myLastDate = scores?.streaks?.[user.discord_id]?.last_date || '';
    const pts      = me?.points || 0;
    const correct  = me?.correct || 0;
    const total    = me?.total   || 0;

    // Rank
    const sorted = Object.keys(scores?.scores||{})
      .map(id=>({id, pts:scores.scores[id]?.points||0}))
      .sort((a,b)=>b.pts-a.pts);
    const realIndex = sorted.findIndex(p=>p.id===user.discord_id);
    let rank = realIndex+1;
    if((realIndex>=25 || realIndex<0) && sorted.length>=25){
      const floorScore=sorted[24].pts;
      rank = estimateFakeRank(pts, floorScore, user.discord_id);
    }

    // Level
    const lvl = getLevelInfo(pts);

    // Identity card
    document.getElementById('prof-rank').textContent        = rank>0 ? `#${rank}` : 'Unranked';
    document.getElementById('prof-rank-callout').textContent= rank>0 ? `#${rank}` : '—';
    document.getElementById('prof-level-badge').textContent = lvl.name;
    renderCastleWidget('prof-castle-widget',myStreak,myLastDate,true);

    // Permanent activity tier — based on total days/quizzes completed
    const tier = getActivityTier(me?.days_completed || 0);
    const tierEl = document.getElementById('prof-tier-badge');
    tierEl.textContent = `${tier.icon} ${tier.name}`;
    tierEl.classList.remove('hidden');

    // Weekly champion trophy count (permanent record of past top-5 weeks)
    const trophyEl = document.getElementById('prof-trophy-badge');
    if(me?.weekly_trophies){
      trophyEl.textContent = `🏆 ×${me.weekly_trophies}`;
      trophyEl.classList.remove('hidden');
    } else {
      trophyEl.classList.add('hidden');
    }

    // Level arc on avatar ring (stroke-dasharray 226 = 2π×36)
    const arc    = document.getElementById('prof-level-arc');
    const arcPct = lvl.pct / 100;
    if(arc) {
      requestAnimationFrame(()=>requestAnimationFrame(()=>{
        arc.style.strokeDashoffset = 226 * (1 - arcPct);
      }));
    }

    // Level bar
    document.getElementById('prof-level-fill').style.width  = lvl.pct + '%';
    document.getElementById('prof-level-pts').textContent   = formatNum(pts) + ' pts';
    document.getElementById('prof-level-next').textContent  =
      lvl.nextName === 'Max' ? 'Max Level' : 'Next: ' + lvl.nextName + ' (' + lvl.ptsLeft + ' pts)';

    // Stat row
    document.getElementById('prof-pts').textContent     = formatNum(pts);
    document.getElementById('prof-streak').textContent  = myStreak;
    document.getElementById('prof-correct').textContent = formatNum(correct);
    document.getElementById('prof-acc').textContent     = accuracy(correct, total);

    // Calendar, report card, missed
    renderCalendar(Array.isArray(history) ? history : []);
    renderReportCard(me, scores);
    renderMissedQuestions(me?.wrong_questions || []);

  } catch(e) {
    toast('Failed to load profile', 'error');
    renderCalendar([]);
    renderReportCard(null, null);
    renderMissedQuestions([]);
  }
}

function renderCalendar(doneDates){
  const grid=document.getElementById('cal-grid'), today=getBDDate();
  const days=[];
  for(let i=29;i>=0;i--) days.push(new Date(Date.now()+6*3600000-i*86400000).toISOString().slice(0,10));
  grid.innerHTML=days.map(d=>{
    let cls='cal-day'; if(doneDates.includes(d))cls+=' done'; if(d===today)cls+=' today';
    return`<div class="${cls}" title="${d}"></div>`;
  }).join('');

  const hint=document.getElementById('cal-sparse-hint');
  if(doneDates.length<7){
    hint.textContent=`${doneDates.length}/30 days logged so far — this fills in as you keep your streak going!`;
    hint.classList.remove('hidden');
  } else {
    hint.classList.add('hidden');
  }
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
    +`<div class="rc-legend">${['S','A+','A','B','C','D'].map(g=>`<span class="rc-legend-item"><span class="rc-legend-dot ${gradeClass(g)}"></span>${g}</span>`).join('')}</div>`
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
  practiceAnswers={}; practiceIndex=0; practiceTimeLeft={}; practiceTimedOut={};
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
    else if(practiceAnswers[q.id]) cls+=' locked';
    btn.className=cls;
    btn.innerHTML=`<span class="option-key">${k}</span><span>${escHtml(q.options?.[k]??'')}</span>`;
    if(!isRev&&!practiceAnswers[q.id]) btn.addEventListener('click',()=>selectPracticeOption(k)); else btn.disabled=true;
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
  const q=practiceQuestions[practiceIndex];
  if(practiceAnswers[q.id])return; // already answered — locked in
  practiceAnswers[q.id]=key; clearPracticeTimer();
  if(practiceConfig.mode==='immediately'){ renderPracticeQuestion(); if(practiceIndex<practiceQuestions.length-1) setTimeout(()=>{ practiceIndex++; renderPracticeQuestion(); },2000); }
  else{ renderPracticeQuestion(); if(practiceIndex<practiceQuestions.length-1) setTimeout(()=>{ practiceIndex++; renderPracticeQuestion(); },300); }
}
function practiceNav(dir){ clearPracticeTimer(); practiceIndex=Math.max(0,Math.min(practiceQuestions.length-1,practiceIndex+dir)); renderPracticeQuestion(); }

function startPracticeTimer(){
  clearPracticeTimer();
  const q=practiceQuestions[practiceIndex];
  if(!q)return;
  if(practiceTimeLeft[q.id]===undefined) practiceTimeLeft[q.id]=practiceConfig.timer;
  const alreadyAnswered=!!practiceAnswers[q.id];
  const alreadyTimedOut=!!practiceTimedOut[q.id];
  updateTimerUI(practiceTimeLeft[q.id],'pq-');
  if(alreadyAnswered||alreadyTimedOut)return;
  practiceTimerInt=setInterval(()=>{
    practiceTimeLeft[q.id]--;
    updateTimerUI(practiceTimeLeft[q.id],'pq-');
    if(practiceTimeLeft[q.id]<=0){
      practiceTimeLeft[q.id]=0;
      practiceTimedOut[q.id]=true;
      clearPracticeTimer();
      if(practiceIndex<practiceQuestions.length-1){ practiceIndex++; renderPracticeQuestion(); }
      else{ renderPracticeQuestion(); toast('Time up!','error'); }
    }
  },1000);
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
  lastExamExport={
    type:'Practice Session ('+(practiceConfig.subject==='all'?'All Subjects':practiceConfig.subject)+')',
    date:getBDDate(), correct, total, points:0,
    questions:results.map(q=>({question:q.question,options:q.options,answer:q.answer,given:q.given||'—',isCorrect:q.isCorrect,explanation:q.explanation||'',subject:q.subject||''})),
  };
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

// Smart reminders — each tag has a pool of playful phrasings, picked at random
const TAG_CONFIG={
  '@goal:':{type:'goal',msgs:[
    (name,text)=>`Don't fall asleep, ${name} — you promised you'd finish "${text}"!`,
    (name,text)=>`${name}, your goal is watching you sleep on it: "${text}" 👀`,
    (name,text)=>`Plot twist: "${text}" isn't going to finish itself.`,
    (name,text)=>`Achievement locked until you do this: "${text}"`,
    (name,text)=>`Your future self called — still waiting on "${text}"`,
    (name,text)=>`Bro really set "${text}" as a goal and vanished 💀`,
  ]},
  '@reminder:':{type:'reminder',msgs:[
    (name,text)=>`Ding ding! ${name}, you set a reminder: "${text}"`,
    (name,text)=>`This is your friendly (annoying) nudge: "${text}"`,
    (name,text)=>`${name}, remember this? "${text}"`,
    (name,text)=>`Tick tock. You wanted a reminder for: "${text}"`,
    (name,text)=>`Past-you left this for present-you: "${text}"`,
  ]},
  '@finish:':{type:'finish',msgs:[
    (name,text)=>`Unfinished business, ${name}: "${text}" — still hanging.`,
    (name,text)=>`Cliffhanger alert: "${text}" needs an ending.`,
    (name,text)=>`${name}, did "${text}" finish itself? (No.)`,
    (name,text)=>`"${text}" is still sitting there. Judging you.`,
  ]},
  '@left:':{type:'left',msgs:[
    (name,text)=>`Right where you left it, ${name}: "${text}"`,
    (name,text)=>`Picking up the trail: "${text}"`,
    (name,text)=>`Your bookmark says: "${text}"`,
    (name,text)=>`Continue where you dropped off — "${text}"`,
  ]},
};
function pickReminderMsg(config,name,text){
  const pool=config.msgs;
  return pool[Math.floor(Math.random()*pool.length)](name,text);
}

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
  const delay=Math.floor(Math.random()*(240000-90000))+90000; // 1.5-4 min — most sessions are short, so keep this snappy
  reminderTimeout=setTimeout(showRandomReminder,delay);
}
function showRandomReminder(){
  // Skip the floating popup while the dedicated syllabus banner already owns this page
  if(document.getElementById('pg-syllabus')?.classList.contains('active')){ scheduleReminderCheck(); return; }
  const notes=getAllTaggedNotes();
  if(!notes.length){ scheduleReminderCheck(); return; }
  const pick=notes[Math.floor(Math.random()*notes.length)];
  const name=user?.username||'Student';
  const msg=pickReminderMsg(pick.config,name,pick.text);
  document.getElementById('reminder-text').textContent=msg;
  const tagEl=document.getElementById('reminder-tag');
  tagEl.textContent=pick.config.type.charAt(0).toUpperCase()+pick.config.type.slice(1);
  tagEl.className='reminder-tag '+pick.config.type;
  document.getElementById('reminder-popup').classList.remove('hidden');
  scheduleReminderCheck();
}
function dismissReminder(){ document.getElementById('reminder-popup').classList.add('hidden'); }

// Dedicated inline banner shown shortly after opening the Syllabus Tracker itself —
// this is the page where tagged notes actually live, so surface them here fast.
let sylReminderTimeout=null;
function scheduleSylReminderBanner(){
  if(sylReminderTimeout)clearTimeout(sylReminderTimeout);
  sylReminderTimeout=setTimeout(showSylReminderBanner,3500);
}
function showSylReminderBanner(){
  const banner=document.getElementById('syl-reminder-banner');
  if(!banner||!document.getElementById('pg-syllabus')?.classList.contains('active'))return;
  const notes=getAllTaggedNotes();
  if(!notes.length)return;
  const pick=notes[Math.floor(Math.random()*notes.length)];
  const name=user?.username||'Student';
  const msg=pickReminderMsg(pick.config,name,pick.text);
  document.getElementById('syl-reminder-text').textContent=msg;
  const tagEl=document.getElementById('syl-reminder-tag');
  tagEl.textContent=pick.config.type.charAt(0).toUpperCase()+pick.config.type.slice(1);
  tagEl.className='reminder-tag '+pick.config.type;
  banner.classList.remove('hidden');
}
function dismissSylReminder(){ document.getElementById('syl-reminder-banner').classList.add('hidden'); }

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
let adminToken = null;
let adminJsLoaded = false;

function initAdminPage(){
  if(adminToken){
    document.getElementById('admin-lock').classList.add('hidden');
    document.getElementById('admin-dash').classList.remove('hidden');
    ensureAdminAssetsLoaded().then(()=>loadAdminData());
  } else {
    document.getElementById('admin-lock').classList.remove('hidden');
    document.getElementById('admin-dash').classList.add('hidden');
    document.getElementById('admin-pw').value='';
    document.getElementById('admin-pw-err').textContent='';
  }
}

async function adminLogin(){
  const pw=document.getElementById('admin-pw').value;
  const errEl=document.getElementById('admin-pw-err');
  const btn=document.querySelector('#admin-lock .btn-primary');
  errEl.textContent='';
  if(btn){ btn.disabled=true; btn.textContent='Checking…'; }
  try{
    const res=await fetch(API+'/admin-login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw})});
    if(!res.ok){ errEl.textContent='Wrong password.'; document.getElementById('admin-pw').value=''; return; }
    const data=await res.json();
    adminToken=data.token;
    document.getElementById('admin-lock').classList.add('hidden');
    document.getElementById('admin-dash').classList.remove('hidden');
    await ensureAdminAssetsLoaded();
    loadAdminData();
  }catch(e){
    errEl.textContent='Login failed: '+e.message;
  }finally{
    if(btn){ btn.disabled=false; btn.textContent='Unlock'; }
  }
}

// Admin markup + admin-only code are never shipped to a regular visitor — they're
// fetched only after a successful server-verified login, so opening DevTools as a
// normal user shows no trace of fake-player controls, bulk bot add, etc.
async function ensureAdminAssetsLoaded(){
  if(adminJsLoaded)return;
  const dashEl=document.getElementById('admin-dash');
  const html=await fetch('admin-page.html').then(r=>r.text());
  dashEl.innerHTML=html;
  await new Promise((resolve,reject)=>{
    const s=document.createElement('script');
    s.src='admin.js';
    s.onload=resolve; s.onerror=()=>reject(new Error('Failed to load admin.js'));
    document.body.appendChild(s);
  });
  adminJsLoaded=true;
}


// ── PDF HUB ───────────────────────────────────────────────────────────────────
async function loadPdfHub(mode){
  const listId = mode==='admin' ? 'adm-pdf-list' : 'pdf-hub-list';
  const el = document.getElementById(listId);
  if(!el) return;
  el.innerHTML='<div class="center-spinner"><div class="spinner"></div></div>';
  try{
    pdfHubData = await apiFetch('/pdf-hub');
    pdfState[mode].path = [];
    renderPdfHub(mode);
  }catch{ el.innerHTML='<div class="empty-state">Failed to load</div>'; }
}

function pdfNode(mode){
  let node = pdfHubData || {folders:[],files:[]};
  for(const step of pdfState[mode].path){
    node = (node.folders||[]).find(f=>f.id===step.id);
    if(!node) return {folders:[],files:[]};
  }
  return node;
}

function pdfEsc(s){ return escHtml(s).replace(/'/g,"&#39;"); }

function renderPdfHub(mode){
  const isAdmin = mode==='admin';
  const listId  = isAdmin?'adm-pdf-list':'pdf-hub-list';
  const crumbId = isAdmin?'adm-pdf-crumb':'pdf-hub-crumb';
  const el = document.getElementById(listId);
  const crumbEl = document.getElementById(crumbId);
  if(!el) return;
  const path = pdfState[mode].path;
  const node = pdfNode(mode);

  if(crumbEl){
    crumbEl.innerHTML = `<span class="pdf-crumb${path.length===0?' active':''}" onclick="pdfGoCrumb('${mode}',0)">Hub</span>` +
      path.map((s,i)=>` <span class="pdf-crumb-sep">/</span> <span class="pdf-crumb${i===path.length-1?' active':''}" onclick="pdfGoCrumb('${mode}',${i+1})">${escHtml(s.name)}</span>`).join('');
  }

  const folders = node.folders||[], files = node.files||[];
  if(!folders.length && !files.length){
    el.innerHTML = `<div class="empty-state">Empty folder${isAdmin?' — add something below':''}</div>`;
    return;
  }
  el.innerHTML =
    folders.map(f=>`<div class="pdf-item pdf-folder" onclick="pdfOpenFolder('${mode}','${f.id}','${pdfEsc(f.name)}')">
      <div class="pdf-item-icon">📁</div>
      <div class="pdf-item-name">${escHtml(f.name)}</div>
      ${isAdmin?`<button class="pdf-del-btn" onclick="event.stopPropagation();deletePdfItem('folder','${f.id}','${pdfEsc(f.name)}')">✕</button>`:'<div class="pdf-item-arrow">→</div>'}
    </div>`).join('') +
    files.map(f=>`<div class="pdf-item pdf-file" onclick="pdfOpenFile('${pdfEsc(f.url)}','${pdfEsc(f.name)}')">
      <div class="pdf-item-icon">📄</div>
      <div class="pdf-item-name">${escHtml(f.name)}</div>
      ${isAdmin?`<button class="pdf-del-btn" onclick="event.stopPropagation();deletePdfItem('file','${f.id}','${pdfEsc(f.name)}')">✕</button>`:'<div class="pdf-item-arrow">↗</div>'}
    </div>`).join('');
}

function pdfOpenFolder(mode,id,name){ pdfState[mode].path.push({id,name}); renderPdfHub(mode); }
function pdfGoCrumb(mode,i){ pdfState[mode].path = pdfState[mode].path.slice(0,i); renderPdfHub(mode); }
function pdfOpenFile(url,name){ window.open(url,'_blank'); toast(`Opening ${name}`,'info'); }


// ── STUDY JOURNAL ────────────────────────────────────────────────────────────
// Entirely local to this device (localStorage) — it's a personal journal, not
// something that needs to sync across devices or be visible to anyone else.
function getJournalKey(){ return 'qc_journal_'+(user?.discord_id||'anon'); }
function loadJournalData(){
  try{
    const raw=localStorage.getItem(getJournalKey());
    if(!raw) return {weaknesses:'',targets:[],activeSession:null};
    return {weaknesses:'',targets:[],activeSession:null,...JSON.parse(raw)};
  }catch{ return {weaknesses:'',targets:[],activeSession:null}; }
}
function saveJournalData(j){ localStorage.setItem(getJournalKey(),JSON.stringify(j)); }

function loadJournalPage(){
  const j=loadJournalData();
  document.getElementById('jr-weakness').value=j.weaknesses||'';
  renderJournalTargets(j);
  renderSessionArea(j);
}

// -- Weakness notes --
function saveJournalWeakness(){
  const j=loadJournalData();
  j.weaknesses=document.getElementById('jr-weakness').value;
  saveJournalData(j);
  toast('Notes saved','success');
}

// -- Daily targets --
function renderJournalTargets(j){
  const el=document.getElementById('jr-targets-list');
  if(!j.targets.length){ el.innerHTML='<div class="empty-state" style="padding:16px;">No targets yet — add your first one above</div>'; return; }
  el.innerHTML=j.targets.map((t,i)=>`
    <div class="jr-target-item">
      <div class="jr-checkbox ${t.done?'checked':''}" onclick="toggleJournalTarget(${i})">${t.done?'✓':''}</div>
      <div class="jr-target-text ${t.done?'done':''}">${escHtml(t.text)}</div>
      <button class="pdf-del-btn" onclick="deleteJournalTarget(${i})">✕</button>
    </div>`).join('');
}
function addJournalTarget(){
  const inp=document.getElementById('jr-target-input');
  const text=inp.value.trim();
  if(!text){ toast('Write a target first','error'); return; }
  const j=loadJournalData();
  j.targets.push({text,done:false});
  saveJournalData(j);
  inp.value='';
  renderJournalTargets(j);
}
function toggleJournalTarget(i){
  const j=loadJournalData();
  if(!j.targets[i])return;
  j.targets[i].done=!j.targets[i].done;
  saveJournalData(j);
  renderJournalTargets(j);
}
function deleteJournalTarget(i){
  const j=loadJournalData();
  j.targets.splice(i,1);
  saveJournalData(j);
  renderJournalTargets(j);
}
function clearCompletedTargets(){
  const j=loadJournalData();
  const before=j.targets.length;
  j.targets=j.targets.filter(t=>!t.done);
  saveJournalData(j);
  renderJournalTargets(j);
  if(j.targets.length<before) toast('Cleared completed targets','success');
}

// -- Study session designer / timer --
let sessionTickInterval=null;
const SESSION_PRESETS=[15,25,45,60];

function renderSessionArea(j){
  const el=document.getElementById('jr-session-area');
  if(!el)return;
  if(sessionTickInterval){ clearInterval(sessionTickInterval); sessionTickInterval=null; }

  if(j.activeSession){
    renderActiveSessionUI(j);
  } else {
    el.innerHTML=`
      <input class="code-input fake-input" id="jr-session-label" placeholder="What are you working on? e.g. Chemistry Ch 3" style="letter-spacing:0;font-size:14px;text-transform:none;width:100%;"/>
      <div class="jr-preset-row">
        ${SESSION_PRESETS.map(m=>`<button class="jr-preset-chip" data-min="${m}" onclick="selectSessionPreset(${m})">${m}m</button>`).join('')}
      </div>
      <input class="code-input fake-input mt-8" id="jr-session-custom" type="number" min="1" max="240" placeholder="Or enter custom minutes" style="letter-spacing:0;font-size:14px;text-transform:none;width:100%;"/>
      <button class="btn-primary w-full mt-8" onclick="startStudySession()">▶ Start Session</button>`;
  }
}
function selectSessionPreset(min){
  document.getElementById('jr-session-custom').value=min;
  document.querySelectorAll('.jr-preset-chip').forEach(c=>c.classList.toggle('active',Number(c.dataset.min)===min));
}
function startStudySession(){
  const label=document.getElementById('jr-session-label').value.trim();
  const mins=Number(document.getElementById('jr-session-custom').value);
  if(!label){ toast('Give this session a target','error'); return; }
  if(!mins||mins<1){ toast('Pick or enter a duration','error'); return; }
  const j=loadJournalData();
  j.activeSession={label,durationMin:mins,startTs:Date.now(),endTs:Date.now()+mins*60000};
  saveJournalData(j);
  renderSessionArea(j);
  toast(`Session started — ${mins} min on "${label}"`,'success');
  armSessionWatcher();
}
function stopStudySession(){
  const j=loadJournalData();
  j.activeSession=null;
  saveJournalData(j);
  renderSessionArea(j);
  toast('Session stopped','info');
}
function renderActiveSessionUI(j){
  const el=document.getElementById('jr-session-area');
  const s=j.activeSession;
  el.innerHTML=`
    <div class="jr-timer-box">
      <div class="jr-timer-label">${escHtml(s.label)}</div>
      <div class="jr-timer-clock" id="jr-timer-clock">--:--</div>
      <button class="btn-secondary w-full mt-8" onclick="stopStudySession()">Stop Session</button>
    </div>`;
  tickSessionClock();
  sessionTickInterval=setInterval(tickSessionClock,1000);
}
function tickSessionClock(){
  const j=loadJournalData();
  const s=j.activeSession;
  const clockEl=document.getElementById('jr-timer-clock');
  if(!s||!clockEl){ if(sessionTickInterval){clearInterval(sessionTickInterval);sessionTickInterval=null;} return; }
  const remaining=s.endTs-Date.now();
  if(remaining<=0){
    completeStudySession();
    return;
  }
  const mm=String(Math.floor(remaining/60000)).padStart(2,'0');
  const ss=String(Math.floor((remaining%60000)/1000)).padStart(2,'0');
  clockEl.textContent=`${mm}:${ss}`;
}
function completeStudySession(){
  if(sessionTickInterval){ clearInterval(sessionTickInterval); sessionTickInterval=null; }
  const j=loadJournalData();
  const s=j.activeSession;
  if(!s)return;
  j.activeSession=null;
  saveJournalData(j);
  if(document.getElementById('pg-journal')?.classList.contains('active')) renderSessionArea(j);

  // Reuse the existing reminder-popup UI for a prominent break nudge
  const tagEl=document.getElementById('reminder-tag');
  tagEl.textContent='Break Time';
  tagEl.className='reminder-tag break';
  document.getElementById('reminder-text').textContent=`🎉 "${s.label}" session complete! Take a 5-10 min break before your next round.`;
  document.getElementById('reminder-popup').classList.remove('hidden');
}

// Fires the break reminder even if the user has navigated away from the Journal page —
// checked once at app start, since the timer itself only ticks visibly while the page is open.
function armSessionWatcher(){
  const j=loadJournalData();
  if(!j.activeSession)return;
  const remaining=j.activeSession.endTs-Date.now();
  if(remaining<=0){ completeStudySession(); return; }
  setTimeout(()=>{
    // Re-check in case it was stopped manually in the meantime
    const latest=loadJournalData();
    if(latest.activeSession && latest.activeSession.endTs<=Date.now()) completeStudySession();
  }, remaining+250);
}

// ── SPLASH SCREEN ─────────────────────────────────────────────────────────────
const SPLASH_STEPS = [
  { label: 'Initialising...', pct: 15  },
  { label: 'Loading assets...', pct: 35 },
  { label: 'Connecting...', pct: 60    },
  { label: 'Fetching data...', pct: 80 },
  { label: 'Ready', pct: 100           },
];

function setSplashProgress(pct, label) {
  const fill  = document.getElementById('splash-loader-fill');
  const lbl   = document.getElementById('splash-loader-label');
  if (fill) fill.style.width  = pct + '%';
  if (lbl)  lbl.textContent   = label;
}

function hideSplash() {
  const splash = document.getElementById('splash-screen');
  if (!splash) return;
  splash.classList.add('hiding');
  setTimeout(() => splash.classList.add('hidden'), 520);
}

async function runSplash() {
  // Step through progress labels
  for (let i = 0; i < SPLASH_STEPS.length - 1; i++) {
    const step  = SPLASH_STEPS[i];
    setSplashProgress(step.pct, step.label);
    // Earlier steps faster, last step holds a bit longer
    const delay = i < 2 ? 200 + Math.random() * 150 : 300 + Math.random() * 200;
    await new Promise(r => setTimeout(r, delay));
  }
}

// ── INIT ──────────────────────────────────────────────────────────────────────
async function init(){
  initParticles();

  // Run splash animation concurrently with data loading
  await runSplash();

  loadUser();

  setSplashProgress(100, 'Ready');
  await new Promise(r => setTimeout(r, 350));

  hideSplash();

  if(location.hash==='#admin'){
    document.body.classList.remove('no-chrome');
    document.getElementById('top-nav').classList.remove('hidden');
    showPage('admin'); return;
  }
  if(user){ document.body.classList.remove('no-chrome'); showPage('dashboard'); armSessionWatcher(); }
  else showPage('login');
}

init();
