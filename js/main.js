/* GUILGAL — small interactions (no dependencies) */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  // header background once the page is scrolled
  const header = $('.site-header');
  const onScroll = () => header.classList.toggle('is-scrolled', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // mobile menu
  const toggle = $('.nav-toggle'), nav = $('#site-nav');
  const setMenu = open => { toggle.setAttribute('aria-expanded', open); nav.classList.toggle('is-open', open); };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  $$('a', nav).forEach(a => a.addEventListener('click', () => setMenu(false)));

  // active nav item follows the section in view
  const links = $$('a', nav);
  const spy = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    links.forEach(a => a.classList.toggle('is-active', a.getAttribute('href') === '#' + e.target.id));
  }), { rootMargin: '-45% 0px -50% 0px' });
  ['home', 'approach', 'services', 'contact'].forEach(id => spy.observe(document.getElementById(id)));

  // fade content in as each band arrives
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }), { threshold: 0.15 });
  $$('.reveal').forEach(el => io.observe(el));

  // contact form validation (matches the current site's behaviour)
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
    if (ok) {
      // TODO: connect to the site's form handler / e-mail service.
      form.querySelector('.btn').textContent = 'Thank you — message ready to send';
    }
  });
})();
