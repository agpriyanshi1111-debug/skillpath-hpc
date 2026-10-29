const $ = (id) => document.getElementById(id);
const state = { profile: null, dashboard: null, roadmap: [], recommendations: [], careers: [], skillLevels: {} };
const levelNames = {0:"Not assessed",1:"Beginner",2:"Intermediate",3:"Advanced"};
const titles = {dashboard:"Your learning overview",profile:"Your learner profile",roadmap:"Your personalized roadmap",skills:"Skill recommendations",benchmark:"HPC performance benchmark",about:"Project information"};

async function api(url, options={}) {
  const res = await fetch(url, {headers:{"Content-Type":"application/json", ...(options.headers||{})}, ...options});
  const data = await res.json().catch(()=>({detail:"Unexpected server response"}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}
function showNotice(message, error=false) {
  const n=$("notice"); n.textContent=message; n.classList.remove("hidden","error"); if(error)n.classList.add("error");
  window.scrollTo({top:0,behavior:"smooth"}); setTimeout(()=>n.classList.add("hidden"),6000);
}
function escapeHtml(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function go(view) {
  document.querySelectorAll(".view").forEach(v=>v.classList.add("hidden"));
  $(`view-${view}`).classList.remove("hidden");
  document.querySelectorAll(".nav-link").forEach(b=>b.classList.toggle("active",b.dataset.view===view));
  $("page-title").textContent=titles[view]||"SkillPath";
  if(view==="dashboard") loadDashboard();
  if(view==="roadmap") renderRoadmap();
  if(view==="skills") renderRecommendations();
}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.view)));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.go)));
$("profile-shortcut").addEventListener("click",()=>go("profile"));

async function init(){
  try{
    const [careerData, health] = await Promise.all([api("/api/careers"),api("/api/health")]);
    state.careers=careerData.careers;
    $("career_goal").innerHTML=state.careers.map(c=>`<option>${escapeHtml(c)}</option>`).join("");
    const prof=await api("/api/profile/1");
    state.profile=prof;
    fillProfile(prof);
    await loadCareerSkills();
    await loadDashboard();
  }catch(e){showNotice(`Could not initialize the app: ${e.message}. Is the FastAPI server running?`,true);}
}
function fillProfile(p){
  $("name").value=p.name||"";
  $("education_level").value=p.education_level||"Undergraduate";
  $("branch").value=p.branch||"B.Tech CSE-AI";
  $("semester").value=p.semester||3;
  $("career_goal").value=p.career_goal;
  $("hours_per_week").value=p.hours_per_week||5;
  $("timeframe_weeks").value=String(p.timeframe_weeks||12);
  $("learning_format").value=p.learning_format||"Mixed";
  document.querySelectorAll("#interest-options input").forEach(i=>i.checked=(p.interests||[]).includes(i.value));
  state.skillLevels={...(p.skills||{})};
  $("student-label").textContent=p.name||"Student";
  $("profile-shortcut").textContent=(p.name||"S").split(/\s+/).map(x=>x[0]).join("").slice(0,2).toUpperCase();
}
$("career_goal").addEventListener("change",loadCareerSkills);
async function loadCareerSkills(){
  const career=$("career_goal").value;
  try{
    const data=await api(`/api/skills?career=${encodeURIComponent(career)}`);
    const unique={};
    data.skills.forEach(s=>unique[s.skill]=s);
    $("skill-assessment").innerHTML=Object.values(unique).map(s=>{
      const val=state.skillLevels[s.skill]??0;
      return `<div class="skill-level"><div class="skill-name">${escapeHtml(s.skill)}<small>${escapeHtml(s.category)} · target ${levelNames[s.target_level]}</small></div><select data-skill="${escapeHtml(s.skill)}" aria-label="${escapeHtml(s.skill)} proficiency"><option value="0" ${val===0?"selected":""}>Not assessed</option><option value="1" ${val===1?"selected":""}>Beginner</option><option value="2" ${val===2?"selected":""}>Intermediate</option><option value="3" ${val===3?"selected":""}>Advanced</option></select></div>`;
    }).join("");
  }catch(e){$("skill-assessment").innerHTML=`<div class="empty-state">${escapeHtml(e.message)}</div>`;}
}
$("skill-assessment").addEventListener("change",e=>{
  if(e.target.matches("select[data-skill]")) state.skillLevels[e.target.dataset.skill]=Number(e.target.value);
});
function collectProfile(){
  const interests=[...document.querySelectorAll("#interest-options input:checked")].map(i=>i.value);
  const skills={};
  document.querySelectorAll("#skill-assessment select[data-skill]").forEach(s=>{if(Number(s.value)>0)skills[s.dataset.skill]=Number(s.value);});
  return {
    ...(state.profile?.id?{id:state.profile.id}:{}),
    name:$("name").value.trim(),career_goal:$("career_goal").value,
    education_level:$("education_level").value,branch:$("branch").value.trim()||"B.Tech CSE-AI",
    semester:Number($("semester").value),interests,skills,
    hours_per_week:Number($("hours_per_week").value),timeframe_weeks:Number($("timeframe_weeks").value),
    learning_format:$("learning_format").value,focus_skills:[]
  };
}
$("profile-form").addEventListener("submit",async e=>{
  e.preventDefault();
  const btn=e.submitter;btn.disabled=true;btn.textContent="Building your roadmap…";
  try{
    const profile=await api("/api/profile",{method:"POST",body:JSON.stringify(collectProfile())});
    const result=await api("/api/roadmap/generate",{method:"POST",body:JSON.stringify({profile,limit:15})});
    state.profile=result.profile;state.roadmap=result.items;fillProfile(result.profile);
    const dash=await api(`/api/dashboard/${result.profile.id}`);state.dashboard=dash;
    showNotice(`Your roadmap is ready: ${result.items.length} skills prioritized for ${result.profile.career_goal}.`);
    go("dashboard");
  }catch(err){showNotice(err.message,true);}
  finally{btn.disabled=false;btn.innerHTML='Generate my learning path <span>→</span>';}
});
async function loadDashboard(){
  if(!state.profile)return;
  try{
    const d=await api(`/api/dashboard/${state.profile.id}`);state.dashboard=d;state.roadmap=d.items;
    $("student-label").textContent=d.profile.name;$("career-chip").textContent=d.career_goal;
    $("metric-gaps").textContent=d.total_gaps;$("metric-high").textContent=d.high_priority;
    $("metric-hours").textContent=`${d.recommended_hours}h`;$("metric-progress").textContent=`${d.completion_percent}%`;
    $("progress-fill").style.width=`${d.completion_percent}%`;
    const next=d.items.filter(i=>i.status!=="completed").slice(0,4);
    $("next-steps").innerHTML=next.length?next.map((i,idx)=>`<div class="step-row"><div class="step-rank">${String(idx+1).padStart(2,"0")}</div><div class="step-info"><b>${escapeHtml(i.skill)}</b><small>${escapeHtml(i.category)} · ${escapeHtml(i.priority||"Recommended")} priority</small></div><span class="step-hours">${i.estimated_hours} hrs</span></div>`).join(""):`<div class="empty-state"><b>Roadmap complete!</b>You have marked every roadmap item complete.</div>`;
    $("activity-list").innerHTML=d.activity.length?d.activity.slice(0,5).map(a=>`<div class="activity-item"><span class="activity-dot"></span><div><b>${escapeHtml(a.message)}</b><small>${new Date(a.created_at).toLocaleString()}</small></div></div>`).join(""):`<div class="subtle">Your updates will appear here.</div>`;
  }catch(e){showNotice(e.message,true);}
}
async function ensureRoadmap(){
  if(!state.profile)return;
  state.roadmap=await api(`/api/roadmap/${state.profile.id}`).then(d=>d.items);
}
async function renderRoadmap(){
  if(!state.profile)return;
  try{
    await ensureRoadmap();
    const total=state.roadmap.reduce((n,i)=>n+i.estimated_hours,0);
    const done=state.roadmap.filter(i=>i.status==="completed").length;
    const available=Number(state.profile.hours_per_week)*Number(state.profile.timeframe_weeks);
    $("roadmap-summary").innerHTML=`<div class="summary-box"><span>Skills in this plan</span><b>${state.roadmap.length}</b></div><div class="summary-box"><span>Estimated learning effort</span><b>${total} hrs</b></div><div class="summary-box"><span>Completed</span><b>${done}/${state.roadmap.length}</b></div>`;
    const foundation=state.roadmap.filter(i=>["Programming","Mathematics","Systems","Networking"].includes(i.category));
    const soft=state.roadmap.filter(i=>i.category==="Soft skill");
    const core=state.roadmap.filter(i=>!foundation.includes(i)&&!soft.includes(i));
    const milestones=[["01","Foundation building",foundation],["02","Core skills",core],["03","Communication & practice",soft]].filter(m=>m[2].length);
    $("roadmap-milestones").innerHTML=milestones.map(m=>`<article class="milestone-card"><span>${m[0]}</span><div><b>${m[1]}</b><small>${m[2].map(i=>escapeHtml(i.skill)).join(" · ")}</small></div></article>`).join("");
    $("roadmap-warning").innerHTML=total>available?`<div class="notice neutral">Timeline check: this roadmap estimates ${total} hours, while your current timeframe provides ${available} hours. Consider extending the timeframe or increasing weekly study time.</div>`:"";
    $("roadmap-list").innerHTML=state.roadmap.length?state.roadmap.map((i,idx)=>`
      <article class="roadmap-item"><div class="roadmap-number">${String(idx+1).padStart(2,"0")}</div><div class="roadmap-main"><h3>${escapeHtml(i.skill)}</h3><p>${escapeHtml(i.objective)}</p><div class="roadmap-meta"><span class="tag ${i.importance>=5?'high':''}">${escapeHtml(i.priority||"Recommended")} priority</span><span class="tag">${i.estimated_hours} learning hours</span><span class="tag">${escapeHtml(i.category)}</span>${i.status==="completed"?'<span class="tag completed">Completed</span>':""}</div><p><b>Why:</b> ${escapeHtml(i.reason)}</p><p><b>Prerequisites:</b> ${i.prerequisites?.length?i.prerequisites.map(escapeHtml).join(", "):"No prerequisites listed"}</p><p><b>Practice:</b> ${escapeHtml(i.activity)}</p><a class="resource-link" href="${escapeHtml(i.resource_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(i.resource_name)} ↗</a></div><div class="roadmap-controls"><select data-status="${i.id}" aria-label="Status for ${escapeHtml(i.skill)}"><option value="not_started" ${i.status==="not_started"?"selected":""}>Not started</option><option value="in_progress" ${i.status==="in_progress"?"selected":""}>In progress</option><option value="completed" ${i.status==="completed"?"selected":""}>Completed</option></select><input type="number" min="0" max="100000" step=".5" data-hours="${i.id}" value="${i.hours_logged||0}" aria-label="Learning hours logged"><input type="text" maxlength="2000" data-notes="${i.id}" placeholder="Learning note…" value="${escapeHtml(i.notes||"")}" aria-label="Learning note"><button data-save="${i.id}">Save progress</button></div></article>`).join(""):`<div class="empty-state"><b>No roadmap yet</b>Complete your profile to generate a personalized plan.</div>`;
  }catch(e){showNotice(e.message,true);}
}
$("roadmap-list").addEventListener("click",async e=>{
  const b=e.target.closest("[data-save]");if(!b)return;
  const id=b.dataset.save;
  const status=$(`[data-status="${id}"]`).value;
  const hours=Number($(`[data-hours="${id}"]`).value);
  const notes=$(`[data-notes="${id}"]`).value;
  try{await api(`/api/roadmap/items/${id}`,{method:"PATCH",body:JSON.stringify({status,hours_logged:hours,notes})});showNotice("Progress saved to the database.");await renderRoadmap();await loadDashboard();}catch(err){showNotice(err.message,true);}
});
$("regenerate-roadmap").addEventListener("click",async()=>{
  try{const result=await api("/api/roadmap/generate",{method:"POST",body:JSON.stringify({profile:collectProfile(),limit:15})});state.profile=result.profile;state.roadmap=result.items;showNotice("Recommendations and roadmap recalculated.");await renderRoadmap();await loadDashboard();}catch(e){showNotice(e.message,true);}
});
function renderRecommendations(){
  if(!state.roadmap.length){$("recommendation-list").innerHTML='<div class="empty-state">Generate your profile and roadmap first.</div>';return;}
  const priority=$("priority-filter").value,category=$("category-filter").value,status=$("status-filter").value;
  const rows=state.roadmap.filter(i=>(priority==="all"||(i.priority||"Medium")===priority)&&(category==="all"||i.category===category)&&(status==="all"||i.status===status));
  const cats=[...new Set(state.roadmap.map(i=>i.category))].sort();
  const old=$("category-filter").value;
  $("category-filter").innerHTML='<option value="all">All categories</option>'+cats.map(c=>`<option ${c===old?"selected":""}>${escapeHtml(c)}</option>`).join("");
  $("recommendation-count").textContent=`${rows.length} skills shown`;
  $("recommendation-list").innerHTML=rows.length?rows.map((i,idx)=>`<article class="recommendation-card"><div class="rec-rank">${String(idx+1).padStart(2,"0")}</div><div class="rec-content"><h3>${escapeHtml(i.skill)}</h3><div class="roadmap-meta"><span class="tag">${escapeHtml(i.category)}</span><span class="tag ${i.importance>=5?'high':''}">${escapeHtml(i.priority||"Recommended")} priority</span><span class="tag">${i.estimated_hours} hrs</span></div><p>Current level: <b>${levelNames[i.current_level]||"Not assessed"}</b> → target level: <b>${levelNames[i.target_level]}</b></p><p class="reason">${escapeHtml(i.reason)}</p><p><b>Next action:</b> ${escapeHtml(i.next_action||i.activity)}</p><a class="resource-link" href="${escapeHtml(i.resource_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(i.resource_name)} ↗</a></div><div class="rec-side"><div class="rec-score">${Number(i.score).toFixed(1)}</div><small>rule-based score / 100</small><div class="mini-bar"><span style="width:${Math.min(100,Math.max(0,i.score))}%"></span></div></div></article>`).join(""):'<div class="empty-state"><b>No matching skills</b>Try changing one of the filters.</div>';
}
["priority-filter","category-filter","status-filter"].forEach(id=>$(id).addEventListener("change",renderRecommendations));
$("run-benchmark").addEventListener("click",async()=>{
  const btn=$("run-benchmark");btn.disabled=true;btn.textContent="Running measured benchmark…";
  try{
    const r=await api("/api/benchmark/run",{method:"POST",body:JSON.stringify({profiles:Number($("bench-profiles").value),repeats:Number($("bench-repeats").value)})});
    $("benchmark-result").innerHTML=`<div class="bench-metrics"><div class="bench-metric"><span>Sequential average</span><b>${r.sequential_seconds}s</b></div><div class="bench-metric"><span>Threaded average</span><b>${r.threaded_seconds}s</b></div><div class="bench-metric"><span>Threaded / sequential ratio</span><b>${r.threaded_speedup}×</b></div></div><table class="bench-table"><thead><tr><th>Measurement</th><th>Result</th></tr></thead><tbody><tr><td>Profiles processed</td><td>${r.profiles}</td></tr><tr><td>Repeats</td><td>${r.repeats}</td></tr><tr><td>Sequential throughput</td><td>${r.sequential_profiles_per_second} profiles/s</td></tr><tr><td>Threaded throughput</td><td>${r.threaded_profiles_per_second} profiles/s</td></tr><tr><td>Python / OS</td><td>${escapeHtml(r.environment.python)} · ${escapeHtml(r.environment.os)}</td></tr><tr><td>Logical CPUs reported</td><td>${r.environment.cpu_count}</td></tr></tbody></table><p class="subtle">${escapeHtml(r.note)}</p>`;
  }catch(e){showNotice(e.message,true);}
  finally{btn.disabled=false;btn.innerHTML='Run benchmark <span>→</span>';}
});
init();


let quizData = null;
$("load-quiz").addEventListener("click", async () => {
  const button = $("load-quiz"); button.disabled = true; button.textContent = "Loading…";
  try {
    quizData = await api("/api/quiz");
    $("quiz-questions").innerHTML = `<p class="subtle">${escapeHtml(quizData.notice)}</p>` + quizData.questions.map((q, index) => `<fieldset class="quiz-question"><legend>${index + 1}. ${escapeHtml(q.question)}</legend>${q.options.map((option, oi) => `<label><input type="radio" name="${q.id}" value="${oi}"> ${escapeHtml(option)}</label>`).join("")}</fieldset>`).join("");
    $("submit-quiz").disabled = false; $("quiz-result").innerHTML = "";
  } catch (e) { showNotice(e.message, true); }
  finally { button.disabled = false; button.textContent = "Reload quiz"; }
});
$("submit-quiz").addEventListener("click", async () => {
  if (!quizData) return;
  const answers = {};
  quizData.questions.forEach(q => { const selected = document.querySelector(`input[name="${q.id}"]:checked`); if (selected) answers[q.id] = Number(selected.value); });
  try {
    const result = await api("/api/quiz", {method:"POST", body:JSON.stringify({answers})});
    const details = result.explanations.map((x, i) => `<li><b>Question ${i + 1}:</b> ${x.correct ? "Correct" : `Correct answer: ${escapeHtml(x.correct_answer)}`} — ${escapeHtml(x.explanation)}</li>`).join("");
    $("quiz-result").innerHTML = `<div class="quiz-result"><b>${result.correct}/${result.total} correct · ${result.score_percent}%</b><p>Suggested Python level: <b>${escapeHtml(result.level_label)}</b>. ${escapeHtml(result.notice)}</p><button type="button" class="btn btn-secondary" id="apply-quiz-level">Apply to Python Programming</button><ol>${details}</ol></div>`;
    $("apply-quiz-level").addEventListener("click", () => {
      const select = document.querySelector('[data-skill="Python Programming"]');
      if (!select) { showNotice("Python Programming is not in this career's assessment list. Switch to a mapped career containing Python first.", true); return; }
      select.value = String(result.suggested_python_level); state.skillLevels["Python Programming"] = result.suggested_python_level;
      showNotice(`Python Programming level set to ${result.level_label}. Submit the profile to save and regenerate your roadmap.`);
    });
  } catch (e) { showNotice(e.message, true); }
});
