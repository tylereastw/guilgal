/* Guilgal International: partner access admin panel */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const api = (path, opts = {}) => fetch('/api/admin/' + path, { credentials: 'same-origin', ...opts }).then(async r => {
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(j.error || 'Request failed'), { status: r.status });
    return j;
  });
  const postJSON = (path, data, method = 'POST') => api(path, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  const say = (form, text) => { const m = $('.form__msg', form); m.hidden = false; m.textContent = text; };
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let PROJECTS = {};

  const show = which => ['setup', 'login', 'app'].forEach(k => { $('[data-admin-' + k + ']').hidden = k !== which; });
  const showApp = on => show(on ? 'app' : 'login');

  // ---------- partner list
  let USERS = [];
  const initials = u => (u.name || u.email).split(/[\s@.]+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('');
  const projectNames = u => u.projects.includes('*') ? ['All projects'] : u.projects.map(p => PROJECTS[p] || p);
  const when = t => {
    if (!t) return 'Never signed in';
    const d = Math.floor((Date.now() - t) / 864e5);
    return 'Last signed in ' + (d < 1 ? 'today' : d === 1 ? 'yesterday' : d < 30 ? d + ' days ago' : 'on ' + new Date(t).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }));
  };

  function renderUsers() {
    const q = $('[data-search]').value.trim().toLowerCase();
    const list = USERS.filter(u => !q || [u.email, u.name, ...projectNames(u)].join(' ').toLowerCase().includes(q));
    const active = USERS.filter(u => !u.disabled).length;
    $('[data-stats]').textContent = USERS.length ? `${USERS.length} partner${USERS.length === 1 ? '' : 's'} · ${active} active${USERS.length - active ? ' · ' + (USERS.length - active) + ' paused' : ''}` : '';
    $('[data-users]').innerHTML = list.map(u => {
      const names = projectNames(u);
      return `<li class="urow${u.disabled ? ' is-paused' : ''}">
        <span class="urow__avatar" aria-hidden="true">${esc(initials(u))}</span>
        <div class="urow__who"><strong>${esc(u.name || u.email)}</strong>${u.name ? `<span>${esc(u.email)}</span>` : ''}<small>${when(u.lastLogin)}</small></div>
        <div class="urow__projects">${names.length ? names.map(n => `<span class="chip-sm">${esc(n)}</span>`).join('') : '<span class="chip-sm chip-sm--warn">No projects yet</span>'}</div>
        <span class="badge ${u.disabled ? 'badge--off' : 'badge--on'}">${u.disabled ? 'Paused' : 'Active'}</span>
        <div class="urow__actions">
          <button class="btn btn--sm btn--gold" data-invite="${esc(u.email)}">Invitation</button>
          <button class="btn btn--sm btn--line-dark" data-edit="${esc(u.email)}">Edit</button>
          <button class="btn btn--sm btn--line-dark" data-toggle="${esc(u.email)}">${u.disabled ? 'Resume' : 'Pause'}</button>
          <button class="btn btn--sm btn--line-dark btn--danger" data-del="${esc(u.email)}">Delete</button>
        </div></li>`;
    }).join('') || `<li class="ulist__empty">${USERS.length ? 'No partners match your search.' : 'No partners yet. Click <b>+ Add partner</b> to invite your first partner.'}</li>`;
  }

  async function loadUsers() {
    const { users, projects } = await api('users');
    PROJECTS = projects;
    USERS = users.sort((a, b) => (a.name || a.email).localeCompare(b.name || b.email));
    renderUsers();
  }
  $('[data-search]').addEventListener('input', renderUsers);
  const byEmail = em => USERS.find(x => x.email === em);
  $('[data-users]').addEventListener('click', async e => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.edit) editMode(byEmail(b.dataset.edit));
    if (b.dataset.invite) inviteChoice(byEmail(b.dataset.invite));
    if (b.dataset.toggle) {
      const u = byEmail(b.dataset.toggle);
      if (!u.disabled && !confirm(`Pause ${u.name || u.email}? They will be signed out and cannot sign in until you resume their access.`)) return;
      await postJSON('users', { email: u.email, name: u.name, projects: u.projects, disabled: !u.disabled });
      loadUsers();
    }
    if (b.dataset.del) {
      const u = byEmail(b.dataset.del);
      if (!confirm(`Delete ${u.name || u.email}? They will lose access immediately. You can add them again later.`)) return;
      await api('users?email=' + encodeURIComponent(u.email), { method: 'DELETE' });
      loadUsers();
    }
  });

  // tabs
  $$('[data-tab]').forEach(t => t.addEventListener('click', () => {
    $$('[data-tab]').forEach(x => { const on = x === t; x.classList.toggle('is-on', on); x.setAttribute('aria-selected', on); });
    $$('[data-panel]').forEach(p => { p.hidden = p.dataset.panel !== t.dataset.tab; });
  }));

  const adminHint = on => { try { on ? localStorage.setItem('gi_in_admin', '1') : localStorage.removeItem('gi_in_admin'); } catch {} window.giFooter && window.giFooter('admin', on); };
  const start = () => { showApp(true); adminHint(true); loadUsers(); };

  $('[data-admin-signin]').addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    try { await postJSON('login', { password: f.password.value, code: f.code.value }); f.reset(); start(); }
    catch (err) { say(f, err.message); }
  });
  $('[data-admin-logout]').addEventListener('click', async () => { await postJSON('logout', {}); adminHint(false); showApp(false); });

  // dialogs
  const dlg = $('[data-user-dialog]'), idlg = $('[data-invite-dialog]');
  $$('[data-close]').forEach(b => b.addEventListener('click', () => b.closest('dialog').close()));

  // ---------- add / edit partner dialog
  const form = $('[data-user-form]');
  const projectBoxes = () => $$('input[name=projects]', form);
  const syncAll = () => {
    const all = $('input[value="*"]', form).checked;
    projectBoxes().filter(c => c.value !== '*').forEach(c => { c.disabled = all; if (all) c.checked = false; });
  };
  const syncPw = () => { $('[data-choose]').hidden = form.pwmode.value !== 'choose'; };
  $('input[value="*"]', form).addEventListener('change', syncAll);
  $$('input[name=pwmode]', form).forEach(r => r.addEventListener('change', syncPw));

  function resetForm() {
    form.reset(); form.hidden = false; $('[data-details]').hidden = true;
    $('.form__msg', form).hidden = true;
    form.pwmode.value = 'generate';
  }
  function addMode() {
    resetForm();
    form.email.readOnly = false;
    $('[data-form-title]').textContent = 'Add a partner';
    $('[data-submit-label]').firstChild.textContent = 'Add partner ';
    $('[data-gen-label]').textContent = 'Create a secure password for me';
    $$('[data-only-edit]').forEach(el => { el.hidden = true; });
    syncAll(); syncPw();
    dlg.showModal(); form.email.focus();
  }
  function editMode(u) {
    resetForm();
    form.email.value = u.email; form.email.readOnly = true;
    form.name.value = u.name;
    projectBoxes().forEach(c => { c.checked = u.projects.includes(c.value); });
    form.active.checked = !u.disabled;
    $('[data-form-title]').textContent = 'Edit ' + (u.name || u.email);
    $('[data-submit-label]').firstChild.textContent = 'Save changes ';
    $('[data-gen-label]').textContent = 'Create a new secure password';
    $$('[data-only-edit]').forEach(el => { el.hidden = false; });
    form.pwmode.value = 'keep';
    syncAll(); syncPw();
    dlg.showModal();
  }
  $('[data-add]').addEventListener('click', addMode);

  let lastSaved = null;
  function showDetails(user, password, isNew) {
    lastSaved = { user, password };
    $('[data-details-title]').textContent = isNew ? '✓ Partner added' : '✓ New password created';
    $('[data-details-text]').textContent = `Sign in: ${location.origin}/login/\nEmail: ${user.email}\nPassword: ${password}`;
    form.hidden = true; $('[data-details]').hidden = false;
  }
  $('[data-copy-details]').addEventListener('click', e => {
    navigator.clipboard.writeText($('[data-details-text]').textContent).then(() => { e.target.textContent = 'Copied'; setTimeout(() => { e.target.textContent = 'Copy details'; }, 1500); });
  });
  $('[data-details-invite]').addEventListener('click', () => { dlg.close(); openInvite(lastSaved.user, lastSaved.password); });

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const isNew = !form.email.readOnly;
    const mode = form.pwmode.value;
    if (!form.email.value.trim()) return say(form, 'Enter the partner\'s email address.');
    if (mode === 'choose' && form.password.value.length < 10) return say(form, 'Passwords must be at least 10 characters.');
    const projects = projectBoxes().filter(c => c.checked).map(c => c.value);
    if (!projects.length && !confirm('No projects are ticked, so this partner will not see anything yet. Continue?')) return;
    const data = {
      email: form.email.value, name: form.name.value, projects,
      password: mode === 'choose' ? form.password.value : undefined,
      resetPassword: mode === 'generate' && !isNew,
      disabled: isNew ? false : !form.active.checked,
    };
    try {
      const r = await postJSON('users', data);
      const pw = r.password || (mode === 'choose' ? form.password.value : null);
      await loadUsers();
      if (pw) showDetails(r.user, pw, isNew); else dlg.close();
    } catch (err) { say(form, err.message); }
  });

  // ---------- invitations
  let inviteFor = null;
  function inviteChoice(u) {
    inviteFor = u;
    $('[data-invite-who]').textContent = u.name || u.email;
    $('.form__msg', idlg).hidden = true;
    idlg.showModal();
  }
  $('[data-invite-new]').addEventListener('click', async () => {
    try {
      const u = inviteFor;
      const r = await postJSON('users', { email: u.email, name: u.name, projects: u.projects, resetPassword: true, disabled: u.disabled });
      idlg.close(); loadUsers(); openInvite(r.user, r.password);
    } catch (err) { say(idlg, err.message); }
  });
  $('[data-invite-nopw]').addEventListener('click', () => { idlg.close(); openInvite(inviteFor, null); });

  function inviteHTML(u, password) {
    const o = location.origin;
    const img = n => `${o}/public/images/v2/${n}`;
    const slugs = u.projects.includes('*') ? Object.keys(PROJECTS) : u.projects.filter(s => PROJECTS[s]);
    const hello = u.name ? `Dear ${esc(u.name.split(' ')[0])},` : 'Hello,';
    const F = 'font-family:Arial,Helvetica,sans-serif;';
    const step = (n, t, d) => `<tr><td style="vertical-align:top;padding:0 12px 12px 0;width:30px"><div style="width:28px;height:28px;border-radius:14px;background:#D7B46E;color:#10291F;${F}font-weight:bold;font-size:14px;line-height:28px;text-align:center">${n}</div></td>
      <td style="${F}font-size:14px;line-height:1.45;color:#13251D;padding-bottom:12px"><b>${t}</b><br>${d}</td></tr>`;
    const qrs = slugs.map(s => `<td style="padding:8px;text-align:center;vertical-align:top;width:150px">
        <img src="${img('qr/project-' + s + '.png')}" width="120" height="120" alt="QR code for ${esc(PROJECTS[s])}" style="display:block;margin:0 auto 6px;border:1px solid #E4DED0">
        <div style="${F}font-size:13px;font-weight:bold;color:#13251D">${esc(PROJECTS[s])}</div>
        <div style="${F}font-size:11px;color:#5C6B63;word-break:break-all"><a href="${o}/members/projects/${s}/" style="color:#9A7A3A">Open project page</a></div></td>`);
    const rows = []; for (let i = 0; i < qrs.length; i += 3) rows.push('<tr>' + qrs.slice(i, i + 3).join('') + '</tr>');
    return `<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #E4DED0;border-collapse:collapse">
  <tr><td style="background:#10291F;padding:22px 28px;border-bottom:3px solid #D7B46E">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="padding-right:14px"><img src="${img('logo-emblem.jpg')}" width="54" height="54" alt="" style="display:block;border-radius:27px"></td>
    <td><div style="font-family:Georgia,'Times New Roman',serif;font-size:24px;letter-spacing:2px;color:#D7B46E">GUILGAL</div><div style="${F}font-size:10px;letter-spacing:4px;color:#ffffff">INTERNATIONAL</div></td></tr></table></td></tr>
  <tr><td style="padding:28px 28px 8px">
    <div style="${F}font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#9A7A3A;font-weight:bold">Partner portal invitation</div>
    <h1 style="font-family:Georgia,'Times New Roman',serif;font-weight:normal;font-size:26px;line-height:1.25;color:#10291F;margin:8px 0 16px">Your private access to Guilgal International project information</h1>
    <p style="${F}font-size:14px;line-height:1.55;color:#13251D;margin:0 0 12px">${hello}</p>
    <p style="${F}font-size:14px;line-height:1.55;color:#13251D;margin:0 0 20px">You have been given access to the Guilgal International partner portal, where you can view project information, maps, technical summaries and milestones, and download project briefs${slugs.length ? ` for: <b>${slugs.map(s => esc(PROJECTS[s])).join(', ')}</b>` : ''}.</p>
  </td></tr>
  <tr><td style="padding:0 28px">
    <table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;background:#F6F3EB;border-left:3px solid #D7B46E"><tr><td style="padding:16px 18px;${F}font-size:14px;line-height:1.7;color:#13251D">
      <b>Sign in:</b> <a href="${o}/login/" style="color:#9A7A3A">${o.replace(/^https?:\/\//, '')}/login/</a><br>
      <b>Email:</b> ${esc(u.email)}<br>
      <b>Password:</b> ${password ? `<span style="font-family:Consolas,Menlo,monospace;font-size:15px;background:#ffffff;padding:2px 6px;border:1px solid #E4DED0">${esc(password)}</span>` : 'sent to you separately'}
    </td></tr></table>
  </td></tr>
  <tr><td style="padding:24px 28px 4px">
    <div style="${F}font-size:15px;font-weight:bold;color:#10291F;margin-bottom:12px">How to sign in</div>
    <table role="presentation" cellpadding="0" cellspacing="0">
      ${step(1, 'Open the sign-in page', `Go to <a href="${o}/login/" style="color:#9A7A3A">${o.replace(/^https?:\/\//, '')}/login/</a>, or scan a QR code below with your phone camera.`)}
      ${step(2, 'Enter your email and password', 'Use the details above. You stay signed in on that device for 30 days.')}
      ${step(3, 'Open your projects', 'Your partner portal lists every project you can see. Each project page has a <b>Download project brief</b> button.')}
    </table>
  </td></tr>
  ${rows.length ? `<tr><td style="padding:8px 20px 8px"><div style="${F}font-size:15px;font-weight:bold;color:#10291F;margin:0 8px 6px">Scan to open a project</div>
    <div style="${F}font-size:12px;color:#5C6B63;margin:0 8px 6px">Each code opens the project page. You will be asked to sign in first if you are not already.</div>
    <table role="presentation" cellpadding="0" cellspacing="0">${rows.join('')}</table></td></tr>` : `<tr><td style="padding:8px 28px;text-align:center"><img src="${img('qr/login.png')}" width="120" height="120" alt="QR code for the sign-in page" style="border:1px solid #E4DED0"><div style="${F}font-size:12px;color:#5C6B63">Scan to sign in</div></td></tr>`}
  <tr><td style="padding:16px 28px 26px;${F}font-size:12px;line-height:1.55;color:#5C6B63;border-top:1px solid #E4DED0">
    Please keep these details private; the information in the portal is confidential and shared under your confidentiality agreement. If you need help or forget your password, reply to this email or contact <a href="mailto:john@guilgal.org" style="color:#9A7A3A">john@guilgal.org</a>.<br><br>Guilgal International Ltd, registered in England and Wales. Guilgal International does not provide investment, financial or legal advice. Nothing in this invitation is an offer or solicitation.
  </td></tr>
</table>`;
  }

  function inviteText(u, password) {
    const o = location.origin;
    const slugs = u.projects.includes('*') ? Object.keys(PROJECTS) : u.projects.filter(s => PROJECTS[s]);
    return `${u.name ? 'Dear ' + u.name.split(' ')[0] + ',' : 'Hello,'}

You have been given access to the Guilgal International partner portal${slugs.length ? ' for: ' + slugs.map(s => PROJECTS[s]).join(', ') : ''}.

Sign in: ${o}/login/
Email: ${u.email}
Password: ${password || 'sent to you separately'}

How to sign in
1. Open the sign-in page above.
2. Enter your email and password. You stay signed in on that device for 30 days.
3. Open your projects from the partner portal. Each project page has a Download project brief button.
${slugs.length ? '\nProject pages\n' + slugs.map(s => `${PROJECTS[s]}: ${o}/members/projects/${s}/`).join('\n') + '\n' : ''}
Please keep these details private. If you need help, contact john@guilgal.org.

Guilgal International`;
  }

  function openInvite(u, password) {
    const html = inviteHTML(u, password), text = inviteText(u, password);
    const mailto = 'mailto:' + encodeURIComponent(u.email) + '?subject=' + encodeURIComponent('Your Guilgal International partner portal access') + '&body=' + encodeURIComponent(text);
    const data = JSON.stringify({ html, text, mailto }).replace(/</g, '\\u003c');
    const doc = `<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Invitation: ${esc(u.name || u.email)}</title>
<style>
  body{margin:0;background:#EDE8DC;font-family:Arial,Helvetica,sans-serif;color:#13251D}
  .bar{position:sticky;top:0;z-index:2;background:#10291F;color:#fff;padding:12px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.2)}
  .bar p{margin:0 12px 0 0;font-size:13px;color:rgba(255,255,255,.85);max-width:420px}
  .bar button,.bar a{font:bold 12px Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;padding:11px 16px;border-radius:4px;cursor:pointer;border:1.5px solid #D7B46E;background:transparent;color:#D7B46E;text-decoration:none}
  .bar .main{background:#D7B46E;color:#10291F}
  .sheet{padding:28px 16px 60px}
  @media print{.bar{display:none}body{background:#fff}.sheet{padding:0}@page{size:A4;margin:12mm}}
</style></head><body>
<div class="bar"><p data-msg>Copy the invitation and paste it into a new email to ${esc(u.email)}. The QR codes and layout come with it.</p>
  <button class="main" data-copy>Copy invitation</button><a data-mail>Open email draft</a><button data-print>Save as PDF / print</button></div>
<div class="sheet" id="invite">${html}</div>
<script>
  const D = ${data};
  const msg = document.querySelector('[data-msg]');
  document.querySelector('[data-mail]').href = D.mailto;
  document.querySelector('[data-print]').onclick = () => print();
  document.querySelector('[data-copy]').onclick = async () => {
    try {
      await navigator.clipboard.write([new ClipboardItem({ 'text/html': new Blob([D.html], { type: 'text/html' }), 'text/plain': new Blob([D.text], { type: 'text/plain' }) })]);
    } catch (e) {
      const r = document.createRange(); r.selectNode(document.getElementById('invite'));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand('copy'); s.removeAllRanges();
    }
    msg.textContent = 'Copied. Click Open email draft, select the message text and paste (Ctrl+V or Cmd+V) to replace it with the formatted invitation.';
  };
<\/script></body></html>`;
    const url = URL.createObjectURL(new Blob([doc], { type: 'text/html' }));
    const w = window.open(url, '_blank');
    if (!w) alert('Please allow pop-ups for this page to open the invitation.');
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }

  $$('[data-copy]').forEach(b => b.addEventListener('click', () => {
    navigator.clipboard.writeText(b.dataset.copy).then(() => { b.textContent = 'Copied'; setTimeout(() => { b.textContent = 'Copy link'; }, 1500); });
  }));

  // First-time authenticator setup
  let setupPassword = '';
  $('[data-setup-start]').addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    try {
      const r = await postJSON('setup', { password: f.password.value });
      setupPassword = f.password.value;
      $('[data-setup-qr]').innerHTML = r.qr;
      $('[data-setup-key]').textContent = r.secret.replace(/(.{4})/g, '$1 ').trim();
      f.hidden = true; $('[data-setup-confirm]').hidden = false;
    } catch (err) { say(f, err.message); }
  });
  $('[data-setup-confirm]').addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    try { await postJSON('setup/confirm', { password: setupPassword, code: f.code.value }); setupPassword = ''; start(); }
    catch (err) { say(f, err.message); }
  });

  api('users').then(start).catch(async () => {
    const st = await api('status').catch(() => ({}));
    if (st.needsSetup) show('setup');
    else {
      show('login');
      if (st.configured === false) say($('[data-admin-signin]'), 'Admin access is not configured yet. Set ADMIN_PASSWORD in Netlify and redeploy.');
    }
  });
})();
