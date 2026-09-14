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
program.html        The four commitments, and how a mentorship runs in practice
cohorts.html        2025 and 2026 side by side; how a cycle is matched
mentors.html        The 24 mentors of the 2026 cohort
mentors-2025.html   The 17 mentors of the 2025 cohort
podcast.html        The conversation series — the three published YouTube videos
conduct.html        Code of conduct and how to report a violation
apply.html          Mentee and mentor calls, and the contact form

assets/css/styles.css   All styling. Design tokens at the top of the file.
assets/js/main.js       Theme toggle only.
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
| A 2026 mentor | `mentors.html` — one `.mentor` block per person |
| A 2025 mentor | `mentors-2025.html` — same markup, plus an optional `.mentor__badge` for those mentoring again |
| Research areas in the hero index | `index.html`, `.fieldindex__list` |
| Cohort figures | `cohorts.html` and the cards on `index.html` — **both**, they are duplicated |
| Organising team | `index.html`, the "Who runs it" section |
| Form links | search all pages for `forms.gle` |
| A new video | `podcast.html`, the `EPISODES`-shaped `.episode` blocks — newest first |
| Social links | three places, all duplicated per page: `masthead__social` (header), `sociallinks` (home page block), `social` (footer) |
| Colours, fonts, spacing | `assets/css/styles.css`, the `:root` token block |

### Brand colours

Facebook blue and YouTube red are theme tokens (`--fb`, `--yt`), defined in all
three theme blocks alongside everything else, and lightened for dark mode so
they stay legible. They are the only colours on the site outside the palette,
and they are used only on the social links, where recognition is the point.

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

