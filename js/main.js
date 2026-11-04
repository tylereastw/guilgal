/* Guilgal International: navigation, news filters and forms (no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  // header background after scrolling
  const nav = $('.nav');
  const onScroll = () => nav.classList.toggle('is-scrolled', scrollY > 160);
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

  // Forms: client-side validation. FORMS: set data-endpoint to the site's form handler.
  $$('[data-form]').forEach(form => form.addEventListener('submit', e => {
    e.preventDefault();
    let ok = true;
    $$('[required]', form).forEach(f => {
      const v = f.type === 'checkbox' ? f.checked : f.value.trim() !== '' && (f.type !== 'email' || /.+@.+\..+/.test(f.value));
      (f.closest('label') || f).classList.toggle('invalid', !v);
      ok = ok && v;
    });
    const msg = $('.form__msg', form) || form.nextElementSibling;
    msg.hidden = false;
    if (!ok) { msg.textContent = 'Please complete the required fields.'; return; }
    if (!form.dataset.endpoint) { msg.textContent = 'Thank you. This form is not yet connected; please email john@guilgal.org.'; return; }
    fetch(form.dataset.endpoint, { method: 'POST', body: new FormData(form) })
      .then(r => { msg.textContent = r.ok ? 'Thank you. We will be in touch.' : 'Sorry, something went wrong. Please email john@guilgal.org.'; if (r.ok) form.reset(); })
      .catch(() => { msg.textContent = 'Sorry, something went wrong. Please email john@guilgal.org.'; });
  }));
})();
