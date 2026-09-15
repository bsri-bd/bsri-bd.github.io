#!/usr/bin/env python3
"""Stamp the stylesheet and script links with a content hash.

    python3 tools/stamp_assets.py

Browsers cache assets/css/styles.css hard, so an edit can leave a returning
visitor rendering new markup against an old stylesheet — which does not look
like a cache problem, it looks like a broken page. Appending a hash of the file
to its URL means a changed file is a new URL, and a new URL is always fetched.

Run this after changing any CSS or JS, before committing.
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ["assets/css/styles.css", "assets/js/main.js"]


def digest(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:8]


def main():
    stamps = {a: digest(a) for a in ASSETS}
    changed = 0
    for page in sorted(ROOT.glob("*.html")):
        s = page.read_text(encoding="utf-8")
        out = s
        for asset, h in stamps.items():
            out = re.sub(r'(["\'])%s(\?v=[0-9a-f]+)?\1' % re.escape(asset),
                         lambda m: '%s%s?v=%s%s' % (m.group(1), asset, h, m.group(1)), out)
        if out != s:
            page.write_text(out, encoding="utf-8")
            changed += 1
    for a, h in stamps.items():
        print("  %-24s v=%s" % (a, h))
    print("  %d pages stamped" % changed)


if __name__ == "__main__":
    main()
