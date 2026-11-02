/* GUILGAL — scroll journey interactions (no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let vh = innerHeight;

  // seeded random so generated scenery is identical on every load
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

  /* ---------- generated scenery ---------- */
  // Tree-crown silhouette: a row of rounded crowns riding on a gentle undulating baseline
  function canopyPath(w, h, base, amp, minW, maxW, crown) {
    let d = `M0 ${h} L0 ${base}`;
    let x = 0;
    while (x < w) {
      const cw = minW + rnd() * (maxW - minW);
      const nx = Math.min(w + 40, x + cw);
      const by = base + Math.sin(nx / 260) * amp + Math.sin(nx / 90) * amp * 0.3;
      const top = by - crown * (0.5 + rnd() * 0.8);
      d += ` C${x + cw * 0.05} ${top} ${x + cw * 0.95} ${top} ${nx} ${by}`;
      x = nx;
    }
    return d + ` L${w + 40} ${h} Z`;
  }
  function ridgePath(w, h, base, amp, freq, phase) {
    let d = `M0 ${h}`;
    for (let x = 0; x <= w; x += 20) {
      const y = base - Math.sin(x / freq + phase) * amp - Math.sin(x / (freq * 0.37) + phase * 2) * amp * 0.35 - rnd() * 6;
      d += ` L${x} ${y.toFixed(1)}`;
    }
    return d + ` L${w} ${h} Z`;
  }

  const back = $('.canopy--back'), front = $('.canopy--front');
  if (back) back.setAttribute('d', canopyPath(1600, 400, 250, 26, 40, 90, 60));
  if (front) front.setAttribute('d', canopyPath(1600, 400, 330, 18, 60, 130, 70));
  $$('.record__ridges .ridge').forEach((p, i) =>
    p.setAttribute('d', ridgePath(1600, 300, 120 + i * 60, 40 - i * 8, 220 + i * 60, i * 1.7)));

  // Contour map: two hills built from noisy concentric rings
  const contourG = $('.contours__lines'), gridG = $('.contours__grid');
  const contourPaths = [];
  if (contourG) {
    const NS = 'http://www.w3.org/2000/svg';
    for (let x = 0; x <= 500; x += 50) gridG.insertAdjacentHTML('beforeend', `<line x1="${x}" y1="0" x2="${x}" y2="420"/>`);
    for (let y = 0; y <= 420; y += 50) gridG.insertAdjacentHTML('beforeend', `<line x1="0" y1="${y}" x2="500" y2="${y}"/>`);
    const hills = [
      { cx: 300, cy: 190, rings: 9, step: 19, ph: 0.4 },
      { cx: 160, cy: 270, rings: 5, step: 17, ph: 2.1 },
    ];
    hills.forEach(hl => {
      for (let k = 1; k <= hl.rings; k++) {
        const pts = [];
        for (let i = 0; i < 48; i++) {
          const t = (i / 48) * Math.PI * 2;
          const r = k * hl.step * (1 + 0.16 * Math.sin(3 * t + hl.ph + k * 0.25) + 0.08 * Math.sin(5 * t - k * 0.6) + 0.12 * Math.cos(t - hl.ph));
          pts.push([hl.cx + Math.cos(t) * r * 1.15, hl.cy + Math.sin(t) * r * 0.85]);
        }
        // closed Catmull-Rom → cubic Bézier
        let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
        for (let i = 0; i < pts.length; i++) {
          const p0 = pts[(i - 1 + pts.length) % pts.length], p1 = pts[i], p2 = pts[(i + 1) % pts.length], p3 = pts[(i + 2) % pts.length];
          d += ` C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)} ${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)} ${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
        }
        const path = document.createElementNS(NS, 'path');
        path.setAttribute('d', d + 'Z');
        if (k % 4 === 0) path.classList.add('major');
        contourG.appendChild(path);
        const len = path.getTotalLength();
        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = reduce ? 0 : len;
        contourPaths.push({ path, len, order: (hl.rings - k) / hl.rings });
      }
    });
  }

  // Prologue: split into words for scroll-driven reading
  const words = [];
  $$('[data-words]').forEach(el => {
    const hl = /^(congo|archive,|field,|evidence\.)$/i;
    el.innerHTML = el.textContent.trim().split(/\s+/).map(w => `<span class="w${hl.test(w) ? ' hl' : ''}">${w}</span>`).join(' ');
    words.push(...$$('.w', el));
  });

  /* ---------- header / nav ---------- */
  const header = $('.site-header');
  const toggle = $('.nav-toggle'), nav = $('#site-nav');
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', open);
    nav.classList.toggle('is-open', open);
  });
  $$('a', nav).forEach(a => a.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }));

  /* ---------- reveal on enter ---------- */
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('is-in');
    io.unobserve(e.target);
    $$('[data-count]', e.target).forEach(countUp);
  }), { threshold: 0.18, rootMargin: '0px 0px -6% 0px' });
  $$('.reveal').forEach(el => io.observe(el));

  function countUp(el) {
    const end = +el.dataset.count;
    if (reduce) { el.textContent = end; return; }
    const t0 = performance.now(), dur = 1600;
    const tick = t => {
      const p = clamp((t - t0) / dur);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  /* ---------- scroll-driven scenes ---------- */
  const sections = ['home', 'prologue', 'archive', 'field', 'discovery', 'record', 'contact'].map(id => document.getElementById(id));
  const railStops = $$('.rail__stops li');
  const rail = $('.rail'), railFill = $('.rail__fill'), readout = $('.rail__readout');
  const navLinks = $$('.site-nav a');
  const navMap = { home: 0, prologue: 0, archive: 1, field: 2, discovery: 2, record: 2, contact: 3 };
  const railMap = { home: 0, prologue: 0, archive: 1, field: 2, discovery: 3, record: 4, contact: 5 };

  const parallax = $$('[data-parallax]');
  const canopies = $$('.canopy');
  const archiveMap = $('.archive__map');
  const field = $('#field');
  const trace = $('.drill__trace'), bit = $('.drill__bit'), depthVal = $('.depth__val');
  const steps = $$('.step');
  const samplesG = $('.samples');
  const SAMPLE_DEPTHS = [150, 260, 420, 560, 600, 740];
  const MAX_DEPTH_M = 120, TOP = 108, BOTTOM = 800;
  let samplesDrawn = 0;

  // progress of a section through the viewport: 0 when its top hits the bottom, 1 when its bottom hits the top
  const through = el => { const r = el.getBoundingClientRect(); return clamp((vh - r.top) / (r.height + vh)); };
  // progress of a tall section with a sticky child: 0 at pin start, 1 at pin end
  const pinned = el => { const r = el.getBoundingClientRect(); return clamp(-r.top / (r.height - vh)); };

  function frame() {
    const y = scrollY;
    header.classList.toggle('is-scrolled', y > 40);

    // hero parallax + canopy
    parallax.forEach(el => {
      const r = el.parentElement.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      el.style.transform = `translate3d(0, ${(-r.top * +el.dataset.parallax).toFixed(1)}px, 0)`;
    });
    canopies.forEach(p => { p.style.transform = `translateY(${(-y * +p.dataset.speed).toFixed(1)}px)`; });

    // prologue words
    if (words.length) {
      const p = clamp(pinned(sections[1]) * 1.15);
      const n = Math.round(p * words.length);
      words.forEach((w, i) => w.classList.toggle('on', reduce || i < n));
    }

    // archive contours draw in
    if (contourPaths.length && !reduce) {
      const p = clamp((through(sections[2]) - 0.12) / 0.4);
      contourPaths.forEach(c => {
        const local = clamp((p - c.order * 0.5) / 0.5);
        c.path.style.strokeDashoffset = (c.len * (1 - local)).toFixed(1);
      });
      archiveMap.classList.toggle('targets-on', p > 0.85);
    } else if (archiveMap) archiveMap.classList.add('targets-on');

    // field: drill descent
    const fp = pinned(field);
    const drillP = clamp(fp / 0.9);
    const yBit = TOP + (BOTTOM - TOP) * drillP;
    trace.setAttribute('y2', yBit.toFixed(1));
    bit.setAttribute('cy', yBit.toFixed(1));
    const depth = Math.round(drillP * MAX_DEPTH_M);
    depthVal.textContent = depth;
    const active = Math.min(steps.length - 1, Math.floor(fp * steps.length));
    steps.forEach((s, i) => { s.classList.toggle('is-active', i === active); s.classList.toggle('is-done', i < active); });
    const want = SAMPLE_DEPTHS.filter(d => d <= yBit).length;
    if (want !== samplesDrawn) {
      samplesG.innerHTML = SAMPLE_DEPTHS.slice(0, want).map((d, i) =>
        `<g><line x1="206" y1="${d}" x2="236" y2="${d}" stroke="#fff" stroke-width="1"/><rect x="236" y="${d - 7}" width="14" height="14" rx="2"/><text x="256" y="${d + 4}">S-${String(i + 1).padStart(2, '0')}</text></g>`).join('');
      samplesDrawn = want;
    }

    // which section is at the centre of the screen?
    let cur = 0;
    sections.forEach((s, i) => { if (s.getBoundingClientRect().top < vh * 0.5) cur = i; });
    const id = sections[cur].id;
    navLinks.forEach((a, i) => a.classList.toggle('is-active', i === navMap[id]));

    // journey rail
    const total = document.documentElement.scrollHeight - vh;
    rail.classList.toggle('is-visible', y > vh * 0.6);
    rail.classList.toggle('on-light', id === 'archive');
    railFill.style.height = `${clamp(y / total) * 100}%`;
    railStops.forEach((li, i) => {
      li.classList.toggle('is-passed', i <= railMap[id]);
      li.classList.toggle('is-current', i === railMap[id]);
    });
    const labels = {
      home: 'Canopy · 620 m asl',
      prologue: 'Canopy · 620 m asl',
      archive: 'Desk study · records',
      field: `Drill hole · −${depth} m`,
      discovery: 'Oxide zone · Cu',
      record: 'Track record',
      contact: 'Surface · your project',
    };
    readout.textContent = labels[id];
  }

  // on narrow screens the cross-section fills a slim column, so crop it rather than shrink it
  const strata = $('.strata');
  const fitStrata = () => strata.setAttribute('preserveAspectRatio', innerWidth <= 900 ? 'xMidYMid slice' : 'xMidYMid meet');
  fitStrata();
  addEventListener('resize', fitStrata);

  let ticking = false;
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { frame(); ticking = false; }); } };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', () => { vh = innerHeight; onScroll(); });
  frame();

  // hero content reveals immediately
  requestAnimationFrame(() => $$('.hero .reveal').forEach(el => el.classList.add('is-in')));

  /* ---------- contact form ---------- */
  const form = $('#contact-form');
  form.addEventListener('submit', e => {
    e.preventDefault();
    let ok = true;
    $$('input[required], textarea[required]', form).forEach(f => {
      const valid = f.type === 'checkbox' ? f.checked : f.value.trim() !== '';
      f.closest('label').classList.toggle('invalid', !valid);
      ok = ok && valid;
    });
    $('.form__error', form).hidden = ok;
    $('.form__ok', form).hidden = !ok;
    // TODO: connect to the site's form handler / email service.
  });
})();
