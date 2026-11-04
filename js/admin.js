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
    $$('[data-edit]').forEach(b => b.addEventListener('click', () => editMode(users.find(x => x.email === b.dataset.edit))));
    $$('[data-del]').forEach(b => b.addEventListener('click', async () => {
      if (!confirm('Delete ' + b.dataset.del + '? They will lose access immediately.')) return;
      await api('users?email=' + encodeURIComponent(b.dataset.del), { method: 'DELETE' });
      loadUsers();
    }));
  }

  const start = () => { showApp(true); loadUsers(); };

  $('[data-admin-signin]').addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.target;
    try { await postJSON('login', { password: f.password.value, code: f.code.value }); f.reset(); start(); }
    catch (err) { say(f, err.message); }
  });
  $('[data-admin-logout]').addEventListener('click', async () => { await postJSON('logout', {}); showApp(false); });

  // ---------- add / edit partner form
  const form = $('[data-user-form]');
  const projectBoxes = () => $$('input[name=projects]', form);
  const syncAll = () => {
    const all = $('input[value="*"]', form).checked;
    projectBoxes().filter(c => c.value !== '*').forEach(c => { c.disabled = all; if (all) c.checked = false; });
  };
  const syncPw = () => { $('[data-choose]').hidden = form.pwmode.value !== 'choose'; };
  $('input[value="*"]', form).addEventListener('change', syncAll);
  $$('input[name=pwmode]', form).forEach(r => r.addEventListener('change', syncPw));

  function addMode() {
    form.reset();
    form.email.readOnly = false;
    $('[data-form-title]').textContent = 'Add a partner';
    $('[data-submit-label]').firstChild.textContent = 'Add partner ';
    $('[data-gen-label]').textContent = 'Create a secure password for me';
    $$('[data-only-edit]').forEach(el => { el.hidden = true; });
    $('[data-edit-note]').hidden = true;
    $('.form__msg', form).hidden = true;
    form.pwmode.value = 'generate';
    syncAll(); syncPw();
  }
  function editMode(u) {
    addMode();
    form.email.value = u.email; form.email.readOnly = true;
    form.name.value = u.name;
    projectBoxes().forEach(c => { c.checked = u.projects.includes(c.value); });
    form.active.checked = !u.disabled;
    $('[data-form-title]').textContent = 'Edit partner';
    $('[data-submit-label]').firstChild.textContent = 'Save changes ';
    $('[data-gen-label]').textContent = 'Create a new secure password';
    $$('[data-only-edit]').forEach(el => { el.hidden = false; });
    $('[data-edit-note]').hidden = false;
    $('[data-edit-email]').textContent = u.email;
    form.pwmode.value = 'keep';
    $('[data-details]').hidden = true;
    syncAll(); syncPw();
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  $('[data-cancel-edit]').addEventListener('click', addMode);

  function showDetails(email, password, isNew) {
    const loginUrl = location.origin + '/login/';
    const text = `Guilgal International partner portal\nSign in: ${loginUrl}\nEmail: ${email}\nPassword: ${password}`;
    $('[data-details-title]').textContent = isNew ? 'Partner added.' : 'New password created.';
    $('[data-details-text]').textContent = text;
    $('[data-mail-details]').href = 'mailto:' + encodeURIComponent(email) + '?subject=' + encodeURIComponent('Your Guilgal International partner login') +
      '&body=' + encodeURIComponent('Hello,\n\nYou now have access to the Guilgal International partner portal.\n\n' + text + '\n\nPlease keep these details private.\n');
    $('[data-details]').hidden = false;
  }
  $('[data-copy-details]').addEventListener('click', e => {
    navigator.clipboard.writeText($('[data-details-text]').textContent).then(() => { e.target.textContent = 'Copied'; setTimeout(() => { e.target.textContent = 'Copy details'; }, 1500); });
  });

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
      if (pw) showDetails(r.user.email, pw, isNew); else $('[data-details]').hidden = true;
      say(form, isNew ? 'Partner added.' : 'Changes saved.');
      if (isNew) { const keep = $('.form__msg', form).textContent; addMode(); say(form, keep); }
      else { form.pwmode.value = 'keep'; form.password.value = ''; syncPw(); }
      loadUsers();
    } catch (err) { say(form, err.message); }
  });
  addMode();

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
