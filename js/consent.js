/* Guilgal International: cookie consent and Microsoft Clarity.
   Clarity (analytics cookies) loads only after the visitor accepts. The choice is kept in
   localStorage for 12 months; "Cookie settings" in the footer reopens the banner.
   Not included on /members/, /admin/ or /login/, so private pages are never recorded. */
(() => {
  const CLARITY_ID = 'z8gzw297n1';
  const KEY = 'gi_cookie_consent';
  const YEAR = 365 * 864e5;

  const read = () => {
    try { const v = JSON.parse(localStorage.getItem(KEY)); return v && Date.now() - v.t < YEAR ? v.choice : null; } catch { return null; }
  };
  const save = choice => { try { localStorage.setItem(KEY, JSON.stringify({ choice, t: Date.now() })); } catch {} };

  let loaded = false;
  function loadClarity() {
    if (loaded) return; loaded = true;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_ID);
    window.clarity('consent');
  }
  function clearClarityCookies() {
    ['_clck', '_clsk', 'CLID', 'ANONCHK', 'MR', 'MUID', 'SM'].forEach(n => {
      document.cookie = n + '=; Max-Age=0; path=/';
      document.cookie = n + '=; Max-Age=0; path=/; domain=.' + location.hostname.replace(/^www\./, '');
    });
  }

  const banner = document.createElement('div');
  banner.className = 'cookies';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', 'Cookie preferences');
  banner.hidden = true;
  banner.innerHTML = `
    <div class="cookies__text">
      <strong>Cookies</strong>
      <p>We use essential cookies to make this site work. With your permission we also use Microsoft Clarity analytics cookies to understand how the site is used, so we can improve it. <a href="/cookies/">Cookie Policy</a></p>
    </div>
    <div class="cookies__actions">
      <button type="button" class="btn btn--sm btn--line" data-cookie="rejected">Essential only</button>
      <button type="button" class="btn btn--sm btn--gold" data-cookie="accepted">Accept analytics</button>
    </div>`;
  document.body.appendChild(banner);

  banner.addEventListener('click', e => {
    const b = e.target.closest('[data-cookie]'); if (!b) return;
    const choice = b.dataset.cookie;
    const was = read();
    save(choice);
    banner.hidden = true;
    if (choice === 'accepted') loadClarity();
    else if (was === 'accepted') { clearClarityCookies(); location.reload(); }
  });
  document.querySelectorAll('[data-cookie-settings]').forEach(el => el.addEventListener('click', e => { e.preventDefault(); banner.hidden = false; }));

  const choice = read();
  if (choice === 'accepted') loadClarity();
  else if (!choice) banner.hidden = false;
})();
