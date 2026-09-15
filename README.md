# Bangladeshi Student Research Initiative — website

A static site for BSRI, a volunteer-run research mentorship network connecting
undergraduate and postgraduate students in Bangladesh with researchers abroad.

Replaces the previous Google Site at `sites.google.com/view/bsri-bd`.

Live at **https://bsri-bd.github.io/**

## Structure

Eight pages. No build step, no dependencies, no framework.

```
index.html          Home — hero, who we are, the organising team, cohorts at a
                    glance, and the two application calls
about.html          The organising team, and how to join them
how-it-works.html   The four commitments, how a mentorship runs, and the code of conduct
cohorts.html        2025 and 2026 side by side; how a cycle is matched
mentors.html        The 24 mentors of the 2026 cohort
mentors-2025.html   The 17 mentors of the 2025 cohort
podcast.html        The conversation series — episode list is generated
apply.html          Mentee and mentor calls, and the contact form

assets/css/styles.css   All styling. Design tokens at the top of the file.
assets/js/main.js       Theme toggle only.
assets/img/             Logo, social preview and touch icon
favicon.ico             16/32/48, the B monogram
data/episodes.json      Hand-written episode summaries, keyed by video id
data/mentors-2026.json  Mentor profiles for the 2026 roster
data/mentors-2025.json  Mentor profiles for the 2025 roster
data/mentee-stories-2025.json  Selected mentee experiences
assets/img/mentors/     Mentor portraits, one per mentor, 320x320
assets/img/mentees/     Mentee portraits for the experiences section
tools/update_podcast.py Regenerates the episode list from the channel feed
tools/build_mentors.py  Regenerates both mentor rosters from the JSON
tools/build_stories.py  Regenerates the mentee experiences on cohorts.html
tools/crop_portraits.py Face-crops a folder of photos to square portraits
tools/stamp_assets.py   Cache-busts the CSS and JS links — run after editing either
tools/fetch_headshots.py Pulls portraits from Drive (see below)
.github/workflows/      Runs that script daily
.nojekyll               Tells GitHub Pages to serve the files as-is
```

Fonts load from Google Fonts; everything else ships with the repo.

### The nav and footer are repeated in every page

This is a plain static site with no templating, so the `<header>` and `<footer>`
blocks are duplicated across all eight files. **If you add a page or rename one,
update the nav in all eight.** The current page is marked in its own nav with
`class="is-current"` and `aria-current="page"` — set that on the right link when
you add a page.

That duplication is the deliberate trade for having no build step. If it starts
to hurt, the fix is a static site generator, not a script that rewrites the HTML
in place.

## Running it locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Use the server rather than opening the files directly — `file://` works but
relative links behave differently.

## Editing content

Content is plain HTML — there is no CMS.

| What | Where |
| --- | --- |
| A mentor's details | `data/mentors-2026.json` or `data/mentors-2025.json`, then run `python3 tools/build_mentors.py`. **Do not edit the roster HTML** — it is generated. |
| A mentor's portrait | drop a square image at `assets/img/mentors/<name-in-lowercase-with-dashes>.jpg` and rebuild |
| Research areas in the hero index | `index.html`, `.fieldindex__list` |
| Cohort figures | `cohorts.html` and the cards on `index.html` — **both**, they are duplicated |
| Organising team | `about.html` |
| Whether a call is open | the `.status` block in `index.html` and `apply.html` — **both**, they are duplicated |
| Form links | search all pages for `forms.gle` |
| A new video | Nothing — it appears automatically. To replace its auto-summary with a written one, add an entry to `data/episodes.json`. |
| Social links | three places, all duplicated per page: `masthead__social` (header), `sociallinks` (home page block), `social` (footer) |
| The logo | `assets/img/logo.png` and `logo-dark.png` — **two variants**, one per theme. Replace both together. |
| Social preview card | `assets/img/og.png`, 1200×630 |
| Colours, fonts, spacing | `assets/css/styles.css`, the `:root` token block |

### The podcast page updates itself

`podcast.html` between the `episodes:start` / `episodes:end` markers is
generated — **do not edit it by hand**, a run will overwrite you. A daily
GitHub Action reads the channel's public RSS feed and rewrites the list, so a
new video appears on the site on its own. No API key, token or secret: the feed
is public and nothing expires.

Summaries in `data/episodes.json` always win. A video with no entry there gets a
provisional summary from the first sentences of its YouTube description, and the
run prints its id so you know to write a proper one.

```bash
python3 tools/update_podcast.py              # update now
python3 tools/update_podcast.py --check      # fail if the page is stale, write nothing
python3 tools/update_podcast.py --feed f.xml # run against a saved feed, offline
```

It never writes an empty list: if the feed is unreachable or returns no
entries, it exits with an error and leaves the page alone.

### Mentor rosters are generated

Both roster pages are built from JSON between their `mentors:start` /
`mentors:end` markers — edit the data, not the HTML:

```bash
python3 tools/build_mentors.py
```

A person who mentors in both cohorts is written once, in the 2026 file; the
2025 file refers to them with `{"ref": true}` and the generator resolves it,
adding the "Also mentoring in 2026" badge. Use `display_name` where the two
cohorts recorded a different form of the name.

A mentor with a portrait in `assets/img/mentors/` gets their photo; anyone
else gets their initials, so a missing file degrades quietly instead of
showing a broken image.

**Portraits.** The originals are private Google Form uploads. To pull them,
share the two Form "File responses" folders as *anyone with the link can
view*, run `python3 tools/fetch_headshots.py`, then revoke the sharing — the images
live in the repo from then on.

Several mentors submitted environmental or full-body photos, so the script
crops around the **detected face** (OpenCV YuNet, model fetched on first run)
rather than the image centre. If no face is found at working size it retries on
an upscaled copy, which is what rescues a small or low-resolution photo; at the 72px size the site renders, a centre crop
left some faces unrecognisable. Without the model it falls back to a centre
crop. It skips anything that does not come back as an image, so running it
while the folders are still private changes nothing.

The Drive file ids live in `data/headshot-sources.local.json`, which is
gitignored: a Drive id is a capability, not just a label, and this repo is
public.

### Mentee experiences

The section on `cohorts.html` is generated from
`data/mentee-stories-2025.json` between its `stories:start` / `stories:end`
markers:

```bash
python3 tools/build_stories.py
```

Two rules for whoever edits it:

- **The quotations are reproduced exactly as the mentees gave them.** Change
  the project, affiliation or mentor if they are wrong; never the quote.
- **It is a selection, not a record.** The lede says these are experiences
  mentees shared, not the full year. Do not let an edit imply otherwise.

New portraits go through `python3 tools/crop_portraits.py <src-dir>
assets/img/mentees` so they get the same face-aware square crop as the
mentors. A mentee without a photo falls back to initials.

### The logo

The masthead shows `logo.png` in light themes and `logo-dark.png` in dark ones,
switched in CSS on the same tokens as everything else. Two files are needed
because the logo's "SR" is dark charcoal, which disappears on a dark ground —
the dark variant remaps the charcoal and green to the dark-theme ink and accent
and leaves the red alone.

Both were derived from a flat JPEG by keying out its background, so the edges
carry slight softness. **If a vector or transparent original exists, use it** —
regenerate both variants and the favicon from that instead.

### Brand colours

Facebook blue and YouTube red are theme tokens (`--fb`, `--yt`), defined in all
three theme blocks alongside everything else, and lightened for dark mode so
they stay legible. They are the only colours on the site outside the palette,
and they are used only on the social links, where recognition is the point.

### After editing CSS or JS, stamp it

```bash
python3 tools/stamp_assets.py
```

Browsers cache `styles.css` hard. Without this, someone who has visited before
gets the new markup against their old stylesheet — which does not look like a
caching problem, it looks like a broken page: elements that should stack run
together on one line, portraits render full width. The stamp appends a hash of
the file to its URL, so a changed file is a new URL and always gets fetched.

### Theming

Colours are defined once as CSS custom properties in `:root`, then redefined for
dark mode in two places — a `prefers-color-scheme` media query (for viewers on
the OS default) and a `[data-theme="dark"]` block (for the explicit toggle).
Change a colour in all three or the themes drift apart.

## Deploying

The site is static, so any host works. For GitHub Pages:

1. **Settings → Pages**
2. Source: *Deploy from a branch*
3. Branch: `main`, folder: `/ (root)`

Note: GitHub Pages will not serve a **private** repository on a free account.
While the repo stays private, preview the site locally, or make the repo public
when you are ready to publish.

## Deploying

This repo is the organisation site: because it is named `bsri-bd.github.io`,
GitHub Pages serves it at the root, `https://bsri-bd.github.io/`.

1. **Settings → Pages**
2. Source: *Deploy from a branch*
3. Branch: `main`, folder: `/ (root)`

Pushing to `main` republishes. There is no build step, so what is in the repo is
what is served.

On a Free plan GitHub Pages only serves **public** repositories. An
organisation site repo therefore has to be public to be live.

## Contributing

Content is plain HTML and the whole site is eight files plus one stylesheet.
Edit the page you want, check it locally, and open a pull request.

No mentee names, email addresses, application scores, or internal documents
belong in this repo.

