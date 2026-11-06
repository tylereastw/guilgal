/* Guilgal International: navigation, news filters and forms (no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const hint = {
    has: k => { try { return localStorage.getItem('gi_in_' + k) === '1'; } catch { return false; } },
    set: k => { try { localStorage.setItem('gi_in_' + k, '1'); } catch {} },
    clear: k => { try { localStorage.removeItem('gi_in_' + k); } catch {} },
  };

  // header background after scrolling
  const nav = $('.nav');
  const onScroll = () => nav.classList.toggle('is-scrolled', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // mobile menu
  const burger = $('.burger'), links = $('.nav__links');
  const setMenu = open => { burger.setAttribute('aria-expanded', open); links.classList.toggle('is-open', open); document.body.style.overflow = open ? 'hidden' : ''; };
  burger.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
  $$('a', links).forEach(a => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

  // About submenu toggle (desktop also opens on hover and focus)
  $$('.nav__subtoggle').forEach(btn => btn.addEventListener('click', () => {
    const item = btn.closest('.nav__item');
    const open = !item.classList.contains('is-open');
    item.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', open);
  }));

  // News & Milestones: filter by kind and by project
  const feed = $('[data-feed]');
  if (feed && $('[data-project-filter]')) {
    let kind = 'all', project = '';
    const chips = $$('.chip[data-kind]'), select = $('[data-project-filter]'), empty = $('.feed__empty');
    const apply = () => {
      let shown = 0;
      $$('.news__card', feed).forEach(card => {
        const ok = (kind === 'all' || card.dataset.kind === kind) && (!project || card.dataset.project === project);
        card.hidden = !ok; if (ok) shown++;
      });
      empty.hidden = shown > 0;
    };
    chips.forEach(c => c.addEventListener('click', () => {
      kind = c.dataset.kind;
      chips.forEach(x => { x.classList.toggle('is-on', x === c); x.setAttribute('aria-pressed', x === c); });
      apply();
    }));
    select.addEventListener('change', () => { project = select.value; apply(); });
    const fromUrl = new URLSearchParams(location.search).get('project');
    if (fromUrl) { select.value = fromUrl; project = fromUrl; apply(); }
  }

  // Forms: validate, then submit. Netlify Forms picks up every form with data-netlify.
  const say = (form, text) => { const m = $('.form__msg', form); if (m) { m.hidden = false; m.textContent = text; } };
  const valid = form => {
    let ok = true;
    $$('[required]', form).forEach(f => {
      const v = f.type === 'checkbox' ? f.checked : f.value.trim() !== '' && (f.type !== 'email' || /.+@.+\..+/.test(f.value));
      (f.closest('label') || f).classList.toggle('invalid', !v);
      ok = ok && v;
    });
    if (!ok) say(form, 'Please complete the required fields.');
    return ok;
  };
  $$('form[data-netlify]').forEach(form => form.addEventListener('submit', e => {
    e.preventDefault();
    if (!valid(form)) return;
    const btn = $('button[type=submit]', form); btn.disabled = true;
    fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() })
      .then(r => { if (!r.ok) throw r; form.reset(); say(form, 'Thank you. Your message has been sent and we will be in touch.'); })
      .catch(() => say(form, 'Sorry, something went wrong. Please email john@guilgal.org.'))
      .finally(() => { btn.disabled = false; });
  }));

  // Partner login
  const login = $('form[data-login]');
  if (login) login.addEventListener('submit', async e => {
    e.preventDefault();
    if (!valid(login)) return;
    const data = Object.fromEntries(new FormData(login));
    const r = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).catch(() => null);
    if (r && r.ok) {
      hint.set('partner');
      const next = new URLSearchParams(location.search).get('next');
      location.href = next && next.startsWith('/members') ? next : '/members/';
    } else {
      const j = r ? await r.json().catch(() => ({})) : {};
      say(login, j.error || 'Sign in failed. Please try again.');
    }
  });

  // Partner portal: show only the projects on this account
  const portal = $('[data-portal]');
  if (portal) fetch('/api/me').then(r => (r.ok ? r.json() : Promise.reject(r))).then(me => {
    const who = $('[data-me]'); who.hidden = false; who.textContent = 'Signed in as ' + (me.name || me.email);
    let shown = 0;
    $$('.pcard', portal).forEach(c => {
      const slug = $('a', c).getAttribute('href').split('/').filter(Boolean).pop();
      const ok = me.projects.includes(slug); c.hidden = !ok; if (ok) shown++;
    });
    $('[data-none]').hidden = shown > 0;
  }).catch(() => {});
  $$('[data-logout]').forEach(b => b.addEventListener('click', () => fetch('/api/logout', { method: 'POST' }).finally(() => { hint.clear('partner'); location.href = '/login/'; })));

  // Footer: show "Log out" when signed in. A local hint avoids calling the server for
  // visitors who have never signed in; the server then confirms the session is still valid.
  const setFooter = (who, on) => {
    $$(`[data-when="${who}-in"]`).forEach(el => { el.hidden = !on; });
    $$(`[data-when="${who}-out"]`).forEach(el => { el.hidden = on; });
  };
  window.giFooter = setFooter;
  if (hint.has('partner')) {
    setFooter('partner', true);
    fetch('/api/me', { credentials: 'same-origin' }).then(r => { if (!r.ok) { hint.clear('partner'); setFooter('partner', false); } }).catch(() => {});
  }
  if (hint.has('admin')) {
    setFooter('admin', true);
    fetch('/api/admin/status', { credentials: 'same-origin' }).then(r => r.json()).then(s => { if (!s.signedIn) { hint.clear('admin'); setFooter('admin', false); } }).catch(() => {});
  }
  $$('[data-footer-logout]').forEach(b => b.addEventListener('click', () => {
    const who = b.dataset.footerLogout;
    const url = who === 'admin' ? '/api/admin/logout' : '/api/logout';
    fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}', credentials: 'same-origin' }).finally(() => {
      hint.clear(who);
      location.href = location.pathname.startsWith(who === 'admin' ? '/admin' : '/members') ? (who === 'admin' ? '/admin/' : '/login/') : location.href;
    });
  }));
})();
