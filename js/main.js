/* GUILGAL — scroll choreography (no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let vh = innerHeight;

  /* header + mobile menu */
  const header = $('.site-header');
  const toggle = $('.nav-toggle'), nav = $('#site-nav');
  const setMenu = o => { toggle.setAttribute('aria-expanded', o); nav.classList.toggle('is-open', o); };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  $$('a', nav).forEach(a => a.addEventListener('click', () => setMenu(false)));

  /* layers that drift at their own speed, relative to their chapter */
  const layers = $$('[data-speed]').map(el => ({ el, speed: +el.dataset.speed, ch: el.closest('.ch') }));

  /* the pinned field chapter */
  const field = $('#field');
  const earth = $('.field__earth');
  const steps = $$('.steps li');
  const depthOut = $('[data-depth]');
  const prints = [1, 2, 3, 4].map(i => $('.pile__' + i));
  // where each print starts and where it lands
  const from = [
    { x: -40, y: 30, r: -14 }, { x: 50, y: -30, r: 12 }, { x: -50, y: 40, r: -10 }, { x: 40, y: 50, r: 14 },
  ];
  const to = [{ r: -3 }, { r: 3 }, { r: -2 }, { r: 2.5 }];

  /* survey line + readout */
  const survey = $('.survey'), fill = $('.survey__line i'), readout = $('[data-readout]');
  const chapters = $$('.ch');
  const navLinks = $$('.site-nav a');
  const navFor = { top: 0, archive: 1, field: 2, seam: 2, record: 2, contact: 3 };
  const labelFor = {
    top: 'Above the canopy', archive: 'The archive · desk study', field: 'The field',
    seam: 'The seam · −120 m', record: 'The record', contact: 'Back to the surface',
  };

  function frame() {
    const y = scrollY;
    header.classList.toggle('is-scrolled', y > 40);

    if (!reduce) {
      for (const l of layers) {
        const r = l.ch.getBoundingClientRect();
        if (r.bottom < -300 || r.top > vh + 300) continue;
        // distance of the chapter's centre from the viewport centre
        const d = r.top + r.height / 2 - vh / 2;
        l.el.style.transform = `translate3d(0, ${(d * l.speed).toFixed(1)}px, 0) rotate(${l.el.dataset.rot || 0}deg)`;
      }
    }

    // field: 0 at pin start → 1 at pin end
    const fr = field.getBoundingClientRect();
    const p = clamp(-fr.top / (fr.height - vh));
    earth.style.opacity = clamp((p - 0.25) / 0.6).toFixed(3);
    depthOut.textContent = Math.round(p * 120);
    prints.forEach((el, i) => {
      const local = clamp((p - i * 0.22) / 0.2);           // each print has its own window
      const e = 1 - Math.pow(1 - local, 3);                 // ease out
      const f = from[i];
      el.style.opacity = reduce ? 1 : local;
      el.style.transform = reduce
        ? `rotate(${to[i].r}deg)`
        : `translate3d(${lerp(f.x, 0, e)}%, ${lerp(f.y, 0, e)}%, 0) rotate(${lerp(f.r, to[i].r, e)}deg) scale(${lerp(1.1, 1, e)})`;
    });
    const on = Math.min(3, Math.floor(p / 0.22));
    steps.forEach((li, i) => { li.classList.toggle('is-on', i === on); li.classList.toggle('is-done', i < on); });

    // which chapter is under the viewport centre?
    let cur = chapters[0];
    chapters.forEach(c => { if (c.getBoundingClientRect().top < vh * 0.5) cur = c; });
    const id = cur.id;
    navLinks.forEach((a, i) => a.classList.toggle('is-active', i === navFor[id]));
    survey.classList.toggle('is-on', y > vh * 0.5);
    survey.classList.toggle('on-light', id === 'archive' || id === 'record');
    fill.style.height = (clamp(y / (document.documentElement.scrollHeight - vh)) * 100).toFixed(2) + '%';
    readout.textContent = id === 'field' ? `The field · −${Math.round(p * 120)} m` : labelFor[id];
  }

  let ticking = false;
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { frame(); ticking = false; }); } };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', () => { vh = innerHeight; onScroll(); });
  frame();

  /* contact form */
  const form = $('#contact-form');
  form.addEventListener('submit', e => {
    e.preventDefault();
    let ok = true;
    $$('[required]', form).forEach(f => {
      const valid = f.type === 'checkbox' ? f.checked : f.value.trim() !== '';
      f.closest('label').classList.toggle('invalid', !valid);
      ok = ok && valid;
    });
    $('.form__msg', form).hidden = ok;
    if (ok) $('.btn', form).textContent = 'Thank you — message ready to send';
    // TODO: connect to the site's form handler / e-mail service.
  });
})();
