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

})();
