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

  async function loadUsers() {
    const { users, projects } = await api('users');
    PROJECTS = projects;
    $('[data-users] tbody').innerHTML = users.map(u => `<tr>
      <td>${esc(u.email)}</td><td>${esc(u.name)}</td>
      <td>${u.projects.includes('*') ? 'All projects' : u.projects.map(p => esc(PROJECTS[p] || p)).join(', ') || '<em>None</em>'}</td>
      <td>${u.disabled ? 'Disabled' : 'Active'}</td><td>${u.lastLogin ? new Date(u.lastLogin).toLocaleString('en-GB') : 'Never'}</td>
      <td><button class="btn btn--sm btn--line-dark" data-edit="${esc(u.email)}">Edit</button> <button class="btn btn--sm btn--line-dark" data-del="${esc(u.email)}">Delete</button></td></tr>`).join('')
      || '<tr><td colspan="6">No partners yet.</td></tr>';
    $$('[data-edit]').forEach(b => b.addEventListener('click', () => {
      const u = users.find(x => x.email === b.dataset.edit), f = $('[data-user-form]');
      f.email.value = u.email; f.name.value = u.name; f.password.value = ''; f.resetPassword.checked = false; f.disabled.checked = u.disabled;
      $$('input[name=projects]', f).forEach(c => { c.checked = u.projects.includes(c.value); });
      f.scrollIntoView({ behavior: 'smooth' });
    }));
    $$('[data-del]').forEach(b => b.addEventListener('click', async () => {
      if (!confirm('Delete ' + b.dataset.del + '? They will lose access immediately.')) return;
      await api('users?email=' + encodeURIComponent(b.dataset.del), { method: 'DELETE' });
      loadUsers();
    }));
  }

  async function loadBriefs() {
    const { briefs, projects } = await api('briefs');
    $('[data-briefs]').innerHTML = Object.entries(projects).map(([slug, name]) => `<li>
      <strong>${esc(name)}</strong>
      <span class="small">${briefs[slug] ? esc(briefs[slug].filename) + ', uploaded ' + new Date(briefs[slug].uploaded).toLocaleDateString('en-GB') : 'No brief uploaded'}</span>
      <form data-brief="${slug}"><label class="sr" for="f-${slug}">PDF for ${esc(name)}</label><input id="f-${slug}" type="file" name="file" accept="application/pdf" required>
      <button class="btn btn--sm btn--gold" type="submit">Upload</button>${briefs[slug] ? ` <button class="btn btn--sm btn--line-dark" type="button" data-clear-brief="${slug}">Remove</button>` : ''}</form></li>`).join('');
    $$('form[data-brief]').forEach(f => f.addEventListener('submit', async e => {
      e.preventDefault();
      const fd = new FormData(f); fd.append('slug', f.dataset.brief);
      try { await api('briefs', { method: 'POST', body: fd }); loadBriefs(); } catch (err) { alert(err.message); }
    }));
    $$('[data-clear-brief]').forEach(b => b.addEventListener('click', async () => {
      if (!confirm('Remove this brief?')) return;
      await api('briefs?slug=' + b.dataset.clearBrief, { method: 'DELETE' });
      loadBriefs();
    }));
  }

  const start = () => { showApp(true); loadUsers(); loadBriefs(); };

  $('[data-admin-signin]').addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    try { await postJSON('login', { password: f.password.value, code: f.code.value }); f.reset(); start(); }
    catch (err) { say(f, err.message); }
  });
  $('[data-admin-logout]').addEventListener('click', async () => { await postJSON('logout', {}); showApp(false); });

  $('[data-user-form]').addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    const data = {
      email: f.email.value, name: f.name.value, password: f.password.value || undefined,
      resetPassword: f.resetPassword.checked, disabled: f.disabled.checked,
      projects: $$('input[name=projects]:checked', f).map(c => c.value),
    };
    try {
      const r = await postJSON('users', data);
      say(f, r.password ? `Saved. Password for ${r.user.email}: ${r.password} (copy it now; it is not shown again)` : 'Saved.');
      f.password.value = ''; f.resetPassword.checked = false;
      loadUsers();
    } catch (err) { say(f, err.message); }
  });

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
