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
  items.forEach(a => { const t = $(a.getAttribute('href')); if (t) spy.observe(t); });

  // contact form validation
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
    if (ok) $('button', form).textContent = 'Thank you — message ready to send';
    // TODO: connect to the site's form handler / e-mail service.
  });
})();
