  /* ---------- online accounts (GitHub version): Supabase sign-in, shared by the app and the teacher page ---------- */
  // The URL and publishable key are meant to be public: what each person can read or change is set by the
  // database's row level security, not by keeping these secret.
  const CLOUD = { url: "https://xovilczevfaqwhtuxsnw.supabase.co", key: "sb_publishable_imq2NpyH97FIbbGySbtvUw_b-7TzTzg",
    domains: ["schools.vic.edu.au", "education.vic.gov.au"] };
  const okDomain = e => CLOUD.domains.some(d => String(e).toLowerCase().endsWith("@" + d));
  // first.last2@schools.vic.edu.au → "First Last"
  const nameFromEmail = e => String(e).split("@")[0].replace(/\d+/g, "").split(/[._-]+/).filter(Boolean)
    .map(w => w[0].toUpperCase() + w.slice(1).toLowerCase()).join(" ").slice(0, 30);

  function makeAuth(SK) {
    let sess = null;
    try { sess = JSON.parse(localStorage.getItem(SK)); } catch (e) {}
    const keep = s => { sess = s; try { s ? localStorage.setItem(SK, JSON.stringify(s)) : localStorage.removeItem(SK); } catch (e) {} };
    const H = tok => Object.assign({ apikey: CLOUD.key, "Content-Type": "application/json" }, tok ? { Authorization: "Bearer " + tok } : {});
    async function call(path, opt) {
      let r;
      try { r = await fetch(CLOUD.url + path, opt); } catch (e) { const x = new Error("offline"); x.code = "offline"; throw x; }
      const t = await r.text(); let j = null;
      try { j = t ? JSON.parse(t) : null; } catch (e) { j = { msg: t }; }
      if (!r.ok) {
        const x = new Error((j && (j.msg || j.message || j.error_description || j.error)) || "Error " + r.status);
        x.status = r.status; x.code = j && (j.error_code || j.code); throw x;
      }
      return j;
    }
    const fromTok = j => ({ at: j.access_token, rt: j.refresh_token, exp: j.expires_at || Math.floor(Date.now() / 1000) + (j.expires_in || 3600),
      id: j.user.id, email: String(j.user.email || "").toLowerCase() });
    let refreshing = null;
    async function token() {
      if (!sess) { const x = new Error("signed out"); x.status = 401; throw x; }
      if (sess.exp - 60 > Date.now() / 1000) return sess.at;
      if (!refreshing) refreshing = call("/auth/v1/token?grant_type=refresh_token", { method: "POST", headers: H(), body: JSON.stringify({ refresh_token: sess.rt }) })
        .then(j => { keep(fromTok(j)); })
        .catch(e => { if (e.status === 400 || e.status === 401) keep(null); throw e; })
        .finally(() => { refreshing = null; });
      await refreshing;
      return sess.at;
    }
    const post = (path, body, tok) => call(path, { method: "POST", headers: H(tok), body: JSON.stringify(body) });
    return {
      user: () => sess && { id: sess.id, email: sess.email },
      signIn: async (email, password) => keep(fromTok(await post("/auth/v1/token?grant_type=password", { email, password }))),
      signOut: async () => { const s = sess; keep(null); if (s) try { await post("/auth/v1/logout", {}, s.at); } catch (e) {} },
      // the database: /rest/v1/<table>?…
      rest: async (path, opt = {}) => call(path, Object.assign({}, opt, { headers: Object.assign(H(await token()), opt.headers || {}) })),
    };
  }

  // Friendly words for what went wrong
  function authMsg(e) {
    const m = String(e && e.message || ""), c = e && e.code;
    if (c === "offline") return "Can't reach the server. Check the internet connection and try again.";
    if (c === "invalid_credentials" || /invalid login/i.test(m)) return "That email and password don't match. Check them on your slip, or ask your teacher for a new password.";
    if (e && e.status === 429) return "Too many tries. Wait a minute, then try again.";
    return "Something went wrong: " + m;
  }

  const AUTH_CSS = `
.au-wrap { position: fixed; inset: 0; z-index: 200; display: grid; place-items: center; padding: 16px; background: var(--paper);
  background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px); background-size: 28px 28px; overflow: auto; }
.au-box { width: min(420px, 100%); background: var(--card); border: 2px solid var(--line); border-radius: 18px; padding: 24px; display: grid; gap: 12px; color: var(--ink);
  font-family: var(--body); box-shadow: 0 10px 30px rgba(20, 30, 60, .08); }
.au-box h2 { margin: 0; font: 800 1.6rem var(--display); }
.au-box h2 span { color: var(--accent); }
.au-box p { margin: 0; color: var(--muted); line-height: 1.45; }
.au-box label { display: grid; gap: 4px; font-weight: 700; font-size: .9rem; }
.au-box input { font: 700 1.05rem var(--body); padding: 10px 12px; border: 2px solid var(--line); border-radius: 12px; background: var(--paper); color: var(--ink); width: 100%; }
.au-box input:focus { outline: none; border-color: var(--accent); }
.au-go { font: 800 1.05rem var(--display); padding: 12px; border: 0; border-radius: 12px; background: var(--accent); color: #fff; cursor: pointer; }
.au-go:disabled { opacity: .6; cursor: wait; }
.au-link { background: none; border: 0; padding: 0; color: var(--accent); font: 700 .92rem var(--body); text-decoration: underline; cursor: pointer; justify-self: start; }
.au-msg { min-height: 1.2em; font-weight: 700; color: var(--bad); }
.au-msg.ok { color: var(--good); }
.au-small { font-size: .82rem; }`;

  // The sign-in box. opts: { title (HTML), sub, onDone(user) }. Returns { show(), hide() }.
  function loginUI(auth, opts) {
    if (!document.getElementById("auCss")) { const st = document.createElement("style"); st.id = "auCss"; st.textContent = AUTH_CSS; document.head.appendChild(st); }
    const wrap = document.createElement("div"); wrap.className = "au-wrap"; wrap.hidden = true; document.body.appendChild(wrap);
    let email = "";
    const esc2 = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const box = inner => { wrap.innerHTML = `<form class="au-box" novalidate><h2>${opts.title}</h2>${inner}<p class="au-msg" role="status"></p></form>`; return wrap.firstChild; };
    const q = s => wrap.querySelector(s);
    const say = (t, ok) => { const m = q(".au-msg"); m.textContent = t; m.classList.toggle("ok", !!ok); };
    const busy = async (fn) => { const b = q(".au-go"); b.disabled = true; try { await fn(); } catch (e) { say(authMsg(e)); } b.disabled = false; };
    const checkEmail = v => { v = v.trim().toLowerCase(); if (!/^[^@\s]+@[^@\s]+$/.test(v)) { say("Type your school email address."); return null; }
      return v; };
    // Accounts are made by the teacher (on the teacher page), so there's only one step: email and password.
    function stepPassword() {
      const f = box(`<p>${opts.sub}</p>
        <label>School email<input type="email" name="em" autocomplete="username" placeholder="first.last@schools.vic.edu.au" value="${esc2(email)}"></label>
        <label>Password<input type="password" name="pw" autocomplete="current-password"></label>
        <button class="au-go" type="submit">Sign in</button>
        <p class="au-small">Your password is on the slip from your teacher. Lost it or forgot it? Ask your teacher for a new one.</p>`);
      q(email ? "[name=pw]" : "[name=em]").focus();
      f.onsubmit = e => { e.preventDefault(); const v = checkEmail(q("[name=em]").value); if (!v) return; email = v;
        const pw = q("[name=pw]").value; if (!pw) { say("Type your password."); return; }
        busy(async () => { await auth.signIn(v, pw); done(); }); };
    }
    function done() { wrap.hidden = true; wrap.innerHTML = ""; opts.onDone(auth.user()); }
    return { show() { wrap.hidden = false; stepPassword(); }, hide() { wrap.hidden = true; } };
  }
