/* Theme toggle. Three states, matching how the page is authored:
   no stamp = follow the OS; data-theme="light" / "dark" = an explicit choice. */
(function () {
  "use strict";

  var root = document.documentElement;
  var btn = document.getElementById("theme-toggle");
  var KEY = "bsri-theme";

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function remember(value) {
    try {
      if (value) { localStorage.setItem(KEY, value); }
      else { localStorage.removeItem(KEY); }
    } catch (e) { /* private mode, blocked storage — the toggle still works */ }
  }

  var saved = stored();
  if (saved === "light" || saved === "dark") {
    root.setAttribute("data-theme", saved);
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  if (btn) {
    btn.addEventListener("click", function () {
      var current = root.getAttribute("data-theme");
      var isDark = current ? current === "dark" : systemPrefersDark();
      var next = isDark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      remember(next);
    });
  }
})();

/* Mobile navigation. The nav is a panel below the bar under 58rem; without
   this button there is no way to reach the other pages on a phone. */
(function () {
  "use strict";

  var btn = document.getElementById("nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (!btn || !nav) { return; }

  function setOpen(open) {
    nav.classList.toggle("is-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    setOpen(btn.getAttribute("aria-expanded") !== "true");
  });

  // Following a link should not leave the panel open behind the new page.
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) { setOpen(false); }
  });

  document.addEventListener("click", function (e) {
    if (!nav.contains(e.target) && !btn.contains(e.target)) { setOpen(false); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") {
      setOpen(false);
      btn.focus();
    }
  });

  // Resizing past the breakpoint must not leave a stuck open panel.
  window.addEventListener("resize", function () {
    if (window.innerWidth > 928) { setOpen(false); }
  });
})();
