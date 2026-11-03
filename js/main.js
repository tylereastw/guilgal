/* GUILGAL — navigation, section tracking, contact form (no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  // navigation background after scrolling
  const nav = $('.nav');
  const onScroll = () => nav.classList.toggle('is-scrolled', scrollY > 30);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // mobile menu
  const burger = $('.burger'), links = $('.nav__links');
  const setMenu = open => { burger.setAttribute('aria-expanded', open); links.classList.toggle('is-open', open); document.body.style.overflow = open ? 'hidden' : ''; };
  burger.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
  $$('a', links).forEach(a => a.addEventListener('click', () => setMenu(false)));

  // highlight the section in view
  const items = $$('a:not(.btn)', links);
  const spy = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    items.forEach(a => a.classList.toggle('is-active', a.getAttribute('href') === '#' + e.target.id));
  }), { rootMargin: '-40% 0px -55% 0px' });
  items.forEach(a => { const href = a.getAttribute('href'); if (href.length > 1) { const t = $(href); if (t) spy.observe(t); } });

  // dotted route through the four approach steps, drawn from their actual positions
  const path = $('.method__path'), route = path && $('.method__route path', path);
  const drawRoute = () => {
    if (!route) return;
    const box = path.getBoundingClientRect();
    const nums = $$('.method__num', path).map(n => n.getBoundingClientRect());
    let d = '';
    for (let i = 0; i < nums.length - 1; i++) {
      const a = nums[i], b = nums[i + 1];
      const side = b.left - a.right > 40; // next step sits to the right → leave sideways, else leave downwards
      const x1 = side ? a.right + 14 : a.left + a.width / 2, y1 = side ? a.top + a.height / 2 : a.bottom + 10;
      const x2 = side ? b.left - 14 : b.left + b.width / 2, y2 = side ? b.top + b.height / 2 : b.top - 10;
      const [sx1, sy1, sx2, sy2] = [x1 - box.left, y1 - box.top, x2 - box.left, y2 - box.top];
      const c = side ? `C${sx1 + (sx2 - sx1) / 2} ${sy1} ${sx2 - (sx2 - sx1) / 2} ${sy2}` : `C${sx1} ${sy1 + (sy2 - sy1) / 2} ${sx2} ${sy2 - (sy2 - sy1) / 2}`;
      d += `M${sx1} ${sy1} ${c} ${sx2} ${sy2} `;
    }
    route.setAttribute('d', d.trim());
  };
  drawRoute();
  addEventListener('resize', drawRoute);
  if (document.fonts) document.fonts.ready.then(drawRoute);

})();
