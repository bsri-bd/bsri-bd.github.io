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
