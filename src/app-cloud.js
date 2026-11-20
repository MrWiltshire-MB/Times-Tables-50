  // Each student's progress is kept online in their own row (only they, and teachers, can read it) as well as in this browser.
  // This browser's copy is used straight away; the online copy is updated a couple of seconds after every save.
  const CA = makeAuth("tt50-cloud-session"), META = "tt50-cloud";
  const meta = () => { try { return JSON.parse(localStorage.getItem(META)) || {}; } catch (e) { return {}; } };
  const setMeta = m => { try { localStorage.setItem(META, JSON.stringify(m)); } catch (e) {} };
  const histLen = s => Object.values((s && s.profiles) || {}).reduce((a, p) => a + ((p && p.history) || []).length, 0);
  const rerender = () => { try { if (typeof renderSections === "function") renderSections(); if (view === "homeView") renderHome(); else paintName(); } catch (e) {} };
  // Put the online copy on this device
  function useData(d) {
    try { localStorage.setItem(KEY, JSON.stringify(d)); localStorage.setItem(REV, String(readRev() + 1)); } catch (e) {}
    store = load(); myRev = readRev();
    if (!histLen(store) && histLen(d)) store = Object.assign(load(), d); // this browser can't save: use it from memory
  }
  // Status line (bottom left)
  const bar = document.createElement("div"); bar.className = "cl-bar"; bar.hidden = true; document.body.appendChild(bar);
  const st = document.createElement("style");
  st.textContent = `.cl-bar { position: fixed; z-index: 30; left: 10px; bottom: 8px; font: .8rem var(--body); color: var(--muted); display: flex; gap: 8px; align-items: center; flex-wrap: wrap; max-width: calc(100vw - 220px); }
.cl-bar b { color: var(--ink); } .cl-bar .ok { color: var(--good); } .cl-bar .warn { color: var(--bad); }
.cl-bar button { background: none; border: 0; padding: 0; font: 700 .8rem var(--body); color: var(--accent); text-decoration: underline; cursor: pointer; }
body:has(#quiz:not([hidden])) .cl-bar { display: none; }
@media (max-width: 700px) { .cl-bar { position: static; justify-content: center; max-width: none; padding: 8px 0 40px; } }
.cl-wait { position: fixed; inset: 0; z-index: 190; display: grid; place-items: center; background: var(--paper); font: 800 1.2rem var(--display); color: var(--ink); }`;
  document.head.appendChild(st);
  let cstate = "ok";
  function paintBar() {
    const u = CA.user(); bar.hidden = !u; if (!u) return;
    const m = meta(), s = cstate === "signin" ? `<span class="warn">Signed out. Sign in again to save online.</span>`
      : cstate === "off" ? `<span class="warn">Not saved online yet (no connection). It will keep trying.</span>`
      : m.dirty ? `<span>Saving online…</span>` : `<span class="ok">✓ Saved online</span>`;
    bar.innerHTML = `${s}<span>·</span><span>${esc(u.email)}</span><button type="button" data-cl="${cstate === "signin" ? "in" : "out"}">${cstate === "signin" ? "Sign in" : "Sign out"}</button>`;
  }
  bar.addEventListener("click", e => { const b = e.target.closest("[data-cl]"); if (!b) return; if (b.dataset.cl === "in") gate.show(); else signOutNow(); });

  let pushT = null, pushing = false;
  function queuePush(ms = 2000) {
    const u = CA.user(); if (!u) return;
    const m = meta(); if (m.uid && m.uid !== u.id) return; // not this person's progress (shouldn't happen)
    m.uid = u.id; m.dirty = true; setMeta(m); paintBar();
    clearTimeout(pushT); pushT = setTimeout(push, ms);
  }
  async function push() {
    const u = CA.user(); if (!u) return;
    if (pushing) { clearTimeout(pushT); pushT = setTimeout(push, 1500); return; }
    pushing = true; const stamp = readRev();
    try {
      const rows = await CA.rest("/rest/v1/progress?on_conflict=user_id&select=updated_at", { method: "POST",
        headers: { Prefer: "resolution=merge-duplicates,return=representation" },
        body: JSON.stringify({ user_id: u.id, name: P().name, data: store }) });
      const m = meta(); m.uid = u.id; m.at = rows && rows[0] && rows[0].updated_at; if (readRev() === stamp) m.dirty = false; setMeta(m);
      cstate = "ok";
    } catch (e) {
      if (isGone(e)) { pushing = false; return goneNow(); }
      cstate = e.status === 401 || !CA.user() ? "signin" : "off";
      if (cstate === "off") { clearTimeout(pushT); pushT = setTimeout(push, 30000); }
    }
    pushing = false; paintBar();
  }
  // Every save on this device also goes online
  const saveLocal = save;
  save = function () { saveLocal(); queuePush(); };

  // After signing in (or opening the app signed in): bring this device and the online copy together
  async function syncIn() {
    const u = CA.user(), m = meta();
    const rows = await CA.rest(`/rest/v1/progress?select=data,updated_at&user_id=eq.${u.id}`), row = rows && rows[0];
    if (m.uid && m.uid !== u.id) { // this device last had someone else's progress (they signed out)
      useData(row ? row.data : { profiles: {}, current: null, settings: {} }); setMeta({ uid: u.id, at: row && row.updated_at });
      if (!row) await push(); return;
    }
    if (!row) { setMeta({ uid: u.id, dirty: true }); await push(); return; } // first sign-in: this device's progress goes online
    const keepLocal = histLen(store) > histLen(row.data);
    if (!m.uid) { if (keepLocal) { setMeta({ uid: u.id, dirty: true }); await push(); } else { useData(row.data); setMeta({ uid: u.id, at: row.updated_at }); } return; }
    if (row.updated_at !== m.at) { // changed on another device
      if (m.dirty && keepLocal) await push(); else { useData(row.data); setMeta({ uid: u.id, at: row.updated_at }); }
    } else if (m.dirty) await push();
  }
  function afterSync() {
    rerender(); paintBar();
    const n = $("ngName"); if (n && !n.value && CA.user()) n.value = nameFromEmail(CA.user().email);
  }
  async function start() {
    const w = document.createElement("div"); w.className = "cl-wait"; w.textContent = "Loading your progress…"; document.body.appendChild(w);
    try { await Promise.race([CA.check().then(syncIn), new Promise((_, no) => setTimeout(() => no(new Error("slow")), 10000))]); cstate = "ok"; }
    catch (e) { if (isGone(e)) return goneNow(); cstate = e.status === 401 || !CA.user() ? "signin" : "off"; if (cstate === "off") queuePush(30000); }
    w.remove(); afterSync();
    if (cstate === "signin") gate.show();
  }
  // The teacher deleted this account: sign out and clear this device (its progress was deleted too)
  const isGone = e => !!e && (e.code === "user_not_found" || e.code === "23503" || /does not exist|foreign key/i.test(e.message || ""));
  async function goneNow() {
    clearTimeout(pushT); save = () => {}; // nothing more is written (closing a round would otherwise save it again)
    await CA.signOut();
    try { [KEY, REV, META].forEach(k => localStorage.removeItem(k)); sessionStorage.setItem("tt50-note", "That account has been deleted. Ask your teacher if you need a new one."); } catch (e) {}
    location.reload();
  }
  async function signOutNow() {
    if (meta().dirty) { clearTimeout(pushT); await push(); }
    if (meta().dirty && !confirm("Your latest progress hasn't saved online yet (no connection). Sign out anyway and lose it?")) return;
    save = () => {}; await CA.signOut();
    // Leave nothing behind on this device for the next person
    try { [KEY, REV, META].forEach(k => localStorage.removeItem(k)); } catch (e) {}
    location.reload();
  }
  // Coming back to the tab: pick up progress made on another device (only on the home screen, never mid-round)
  document.addEventListener("visibilitychange", async () => {
    if (document.hidden || !CA.user()) return;
    try { await CA.check(); } catch (e) { if (isGone(e)) return goneNow(); }
    if (meta().dirty || view !== "homeView") return;
    try { const r = await CA.rest(`/rest/v1/progress?select=updated_at&user_id=eq.${CA.user().id}`);
      if (r && r[0] && r[0].updated_at !== meta().at) { await syncIn(); afterSync(); } } catch (e) {}
  });

  const gate = loginUI(CA, { title: "Times Tables <span>50</span>", sub: "Sign in with your school email to save your progress online.",
    onDone: () => { cstate = "ok"; start(); } });
  if (CA.user()) start(); else gate.show();
