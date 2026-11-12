# MEDTAP UI redesign — Framer reference edition

> This guide records the redesign stage. [STEP_2.md](STEP_2.md) contains the latest
> shared template/style changes and the working account/profile screens.

This is the current home page and shared layout. The next functional feature is
on hold until you review this design. Earlier UI code remains documented as a
snapshot in UI_STEP_1.md; this guide contains the complete updated files.

## Open the redesigned website

**http://127.0.0.1:8000/**

The existing Django server is running with automatic reload. Refresh with Ctrl+F5
to discard cached styling. If the server is stopped, run from the MEDTAP folder:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

No dependency installation, database migration or new admin account is needed.
The built-in admin remains at http://127.0.0.1:8000/admin/.

## Chosen reference and design decision

The main reference is **[Mediso by Muzamal Hussain on Framer](https://www.framer.com/marketplace/templates/mediso/)**.
I reviewed its preview alongside [VitalCare](https://www.framer.com/marketplace/templates/vitalcare/)
and [Healthio](https://www.framer.com/marketplace/templates/healthio/).

Mediso's spacious typography, clear actions and healthcare portrait composition
fit the app's approachable healthcare identity. VitalCare's dramatic anatomical
hero would put more visual emphasis on presentation than the emergency actions;
Healthio's wellness direction was a less direct fit for this project. These are
my design judgments based on the previews and marketplace descriptions.

The resulting design is an original Django implementation inspired by those
patterns. You do not need to buy or import a Framer template to run this project.

## What changed

- The hero now sits inside a spacious pale blue-green canvas with a large, lighter
  headline and an original healthcare portrait.
- Hospital search is integrated into the hero instead of placed in a separate
  full-width box below it. The existing form, location feedback and fallbacks work
  as before; actual search results remain a clearly labelled preview.
- Navigation uses a compact wordmark and quieter links. Project preview status
  remains visible.
- Six service cards use generous spacing, circular icons, directional arrows and
  explicit availability labels.
- A separate emergency band contains the red SOS preview and direct Call 112 link.
- The mobile bottom bar now keeps both an SOS preview and Call 112 in reach.
- A dark navy footer gives the page a clearer finish and retains the disclaimer.
- Custom CSS remains in theme.css, with your six original colour tokens intact.
  The styles replace the earlier design rather than adding a second override file.

The app has no ratings, response-time statistics, claimed provider availability,
patient testimonials or named clinicians. The portrait is explicitly labelled as
an AI-generated illustration, not a listed provider. No emergency request or
ambulance booking is created by preview controls.

## Files changed or added

```text
MEDTAP/
|-- static/
|   |-- css/theme.css                 # replaced design system and responsive rules
|   `-- img/care-professional-v2.png   # new original hero image
|-- templates/
|   |-- base.html                     # updated mobile emergency actions
|   |-- core/home.html                # new page composition
|   `-- partials/
|       |-- navbar.html
|       |-- footer.html
|       |-- action_card.html
|       `-- sos_button.html           # shared main/mobile SOS preview button
|-- core/forms.py                     # shorter search placeholder
|-- README.md
|-- THIRD_PARTY.md
|-- UI_STEP_1.md                       # marks previous design as a snapshot
`-- UI_REDESIGN.md                     # this guide
```

Models, migrations, secrets, installed packages, views and JavaScript logic are
unchanged. Existing icon, message and modal partials continue to be used.

## Short viva explanation

Django template inheritance keeps the document shell in base.html. The home page
changes its composition while using the same view/form data. Reusable partials
avoid duplicating card and SOS behaviour. In particular, both SOS buttons share
the same preview wording and open the existing Bootstrap dialog.

CSS Grid defines the hero and service layouts; Bootstrap still supplies navigation,
dialogs, alerts, utility classes and footer columns. minmax(0, 1fr) and min-width: 0
allow narrow grid children and search inputs to shrink. Media queries switch the
hero to one column, simplify the search form and preserve the mobile emergency bar.

The image includes intrinsic width/height to reserve space before it loads. Its
alt text describes the illustration, and decorative icons stay aria-hidden. Focus
rings, 44px controls, live feedback and reduced-motion rules remain in place.
The persistent mobile SOS has a compact label and opens a preview; it does not
trigger geolocation or pretend an emergency was sent.

## Original hero asset and exact generation prompt

- Saved project asset: `static/img/care-professional-v2.png`.
- Dimensions: 1122 x 1402 pixels; approximately 2 MB.
- Mode: built-in **image_gen** tool; no API/CLI fallback.
- The original generated output was copied into the project and retained at its
  original destination. No Framer portrait asset was copied into the app.

Prompt:

```text
Use case: photorealistic-natural. Asset type: original photographic hero for MEDTAP, an Indian medical emergency web app, inspired by the calm editorial quality of premium healthcare websites. Create one high-end natural editorial portrait photograph in portrait 4:5 composition of a warm, confident Indian female healthcare professional in her early 30s wearing clean navy blue scrubs with a simple stethoscope, standing in a bright modern hospital corridor. Waist-up composition, subject in the middle with generous space around head and shoulders so it can crop to a website hero. She looks at camera with a gentle reassuring smile. Realistic skin texture, natural proportions, hands relaxed at waist if visible, soft daylight from large windows, pale blue-white background softly out of focus, subtle teal details in distant architecture, professional documentary photography, 50mm lens feel. The emotional tone is calm, capable, approachable and human, not dramatic or an emergency treatment scene. No other people in focus. No names, logos, badges with text, signs, typography, watermarks, charts, UI, or graphic overlays. No glamour retouching. No medical procedures. This is illustrative imagery and must not depict a named actual doctor.
```

If recreating these files elsewhere, also include the supplied PNG at the same
relative static path. The image is a binary project asset, not a code block.

## Complete updated code, file by file

### static/css/theme.css

Complete replacement theme with palette, components, layout and responsive behaviour.

```css
/* MEDTAP redesign: an original Django implementation inspired by Mediso on Framer. */
:root {
  --primary: #0077B6;
  --primary-dark: #023E8A;
  --accent: #2A9D8F;
  --emergency: #D62828;
  --bg: #F5F9FC;
  --text: #1F2933;
  --ink: #15333F;
  --muted: #526375;
  --accent-dark: #17665D;
  --surface: #FFFFFF;
  --hero-bg: #EDF5F6;
  --blue-soft: #EAF4FB;
  --teal-soft: #EAF6F3;
  --border: #D8E3E7;
  --radius: 1.5rem;
  --shadow: 0 16px 48px rgb(21 51 63 / 9%);
  --bs-body-font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --bs-body-font-size: 1rem;
  --bs-body-line-height: 1.65;
  --bs-body-color: var(--text);
  --bs-body-bg: var(--surface);
  --bs-link-color: var(--primary-dark);
  --bs-link-hover-color: var(--ink);
}
html { scroll-behavior: smooth; scroll-padding-top: 7rem; }
body { min-width: 320px; }
body, button, input, select, textarea { font-family: var(--bs-body-font-family); }
h1, h2, h3, h4 { color: var(--ink); font-weight: 500; line-height: 1.15; }
a { text-underline-offset: .2em; }
button, input, select, .btn { font-size: 1rem; }
button, .btn, .form-control, .form-select { min-height: 44px; }
[hidden] { display: none !important; }
:focus-visible { outline: 3px solid var(--primary-dark) !important; outline-offset: 4px; }
.form-control:focus { border-color: var(--primary-dark); box-shadow: 0 0 0 3px rgb(2 62 138 / 15%); }
.container { max-width: 1240px; }
.icon { display: inline-block; width: 1.25rem; height: 1.25rem; fill: currentColor; flex-shrink: 0; vertical-align: -.18em; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-lg { width: 1.75rem; height: 1.75rem; }
.skip-link { position: fixed; top: -6rem; left: 1rem; z-index: 2000; padding: .8rem 1.2rem; border-radius: .6rem; background: var(--primary-dark); color: white; }
.skip-link:focus { top: 1rem; color: white; }
.text-muted { color: var(--muted) !important; }
.eyebrow { margin-bottom: .85rem; color: var(--accent-dark); font-size: .75rem; font-weight: 600; letter-spacing: .13em; text-transform: uppercase; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: .6rem; border-radius: 999px; padding: .8rem 1.35rem; font-weight: 500; }
.btn-primary {
  --bs-btn-color: #fff;
  --bs-btn-bg: var(--primary-dark);
  --bs-btn-border-color: var(--primary-dark);
  --bs-btn-hover-color: #fff;
  --bs-btn-hover-bg: #032F67;
  --bs-btn-hover-border-color: #032F67;
  --bs-btn-active-color: #fff;
  --bs-btn-active-bg: #032F67;
  --bs-btn-active-border-color: #032F67;
}
.btn-outline-primary {
  --bs-btn-color: var(--primary-dark);
  --bs-btn-border-color: var(--border);
  --bs-btn-hover-color: var(--primary-dark);
  --bs-btn-hover-bg: var(--blue-soft);
  --bs-btn-hover-border-color: var(--primary-dark);
  --bs-btn-active-color: var(--primary-dark);
  --bs-btn-active-bg: var(--blue-soft);
  --bs-btn-active-border-color: var(--primary-dark);
}
.btn-emergency { background: var(--emergency); border: 1px solid var(--emergency); color: white; }
.btn-emergency:hover, .btn-emergency:active { background: #AF2020; border-color: #AF2020; color: white; }
.btn-close { box-sizing: border-box; width: 44px; height: 44px; min-width: 44px; min-height: 44px; background-size: .8rem; opacity: .8; }
.site-header { position: sticky; top: 0; z-index: 1020; background: rgb(255 255 255 / 98%); border-bottom: 1px solid #EAF0F2; }
.site-header .navbar { min-height: 94px; }
.navbar-brand { display: inline-flex; align-items: center; gap: .65rem; min-height: 44px; margin-right: 1.5rem; padding-block: .35rem; color: var(--ink); text-decoration: none; }
.brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 39px; height: 39px; border-radius: 50%; color: white; background: var(--primary-dark); }
.brand-word { font-size: 1.65rem; font-weight: 700; line-height: 1.1; letter-spacing: -.065em; }
.brand-dot { color: var(--accent-dark); }
.preview-label { margin-left: .35rem; border: 1px solid var(--border); border-radius: 999px; padding: .15rem .5rem; color: var(--muted); font-size: .65rem; font-weight: 500; letter-spacing: .02em; }
.navbar .nav-link { display: inline-flex; align-items: center; min-height: 44px; padding: .6rem .85rem !important; color: var(--muted); font-size: .88rem; font-weight: 500; background: none; border: 0; border-radius: 999px; text-decoration: none; }
.navbar .nav-link:hover, .navbar .nav-link.active { color: var(--primary-dark); }
.navbar .nav-link.active::after { content: ""; width: 4px; height: 4px; border-radius: 50%; background: var(--primary-dark); margin-left: .4rem; }
.navbar-toggler { min-width: 44px; border-color: var(--border); color: var(--ink); border-radius: 50%; }
.navbar-actions { display: flex; align-items: center; gap: .6rem; }
.navbar-actions .btn { font-size: .85rem; padding: .65rem 1.15rem; }
.site-main { min-height: 50vh; }
.message-container { padding-top: 1.25rem; }
.alert { border-radius: .8rem; }
.alert-danger { color: #831818; background: #FFF1F1; border-color: #EAB4B4; }
.alert-info { color: var(--primary-dark); background: var(--blue-soft); border-color: var(--border); }
.alert-success { color: var(--accent-dark); background: var(--teal-soft); border-color: #B8DCD3; }
.hero-section { padding: 1.5rem 1.5rem 0; }
.hero-shell { max-width: 1360px; margin: auto; padding: 3rem; border-radius: 1.8rem; background: var(--hero-bg); }
.hero-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 3.25rem; align-items: center; }
.hero-copy { min-width: 0; }
.hero-kicker { display: inline-flex; align-items: center; gap: .55rem; padding: .4rem .8rem; margin-bottom: 1.4rem; border: 1px solid #C8DAD8; border-radius: 999px; color: var(--accent-dark); background: #F6FBF9; font-size: .75rem; font-weight: 500; }
.hero-title { margin: 0 0 1.4rem; font-size: clamp(2.75rem, 4.8vw, 4.5rem); font-weight: 500; letter-spacing: -.07em; line-height: 1.04; }
.hero-title span { color: var(--primary-dark); }
.hero-description { max-width: 29rem; margin-bottom: 1.8rem; font-size: 1rem; color: var(--muted); line-height: 1.75; }
.hero-art { position: relative; margin: 0; min-width: 0; padding-bottom: .9rem; }
.hero-photo { display: block; width: 100%; height: 560px; object-fit: cover; object-position: 50% 35%; border-radius: 1.25rem; background: #DCE9EC; }
.hero-note { position: absolute; left: -1.3rem; bottom: 3.1rem; display: flex; align-items: center; gap: .85rem; width: min(310px, 90%); padding: 1.1rem; border: 1px solid rgb(255 255 255 / 80%); border-radius: 1rem; box-shadow: var(--shadow); background: white; }
.hero-note-icon { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 46px; height: 46px; border-radius: .85rem; color: var(--primary-dark); background: var(--blue-soft); }
.hero-note strong { display: block; font-size: .9rem; font-weight: 600; line-height: 1.4; color: var(--ink); }
.hero-note p { margin: .25rem 0 0; color: var(--muted); font-size: .75rem; line-height: 1.5; }
.image-caption { position: absolute; right: .2rem; bottom: -.65rem; margin: 0; color: var(--muted); font-size: .65rem; }
.search-panel { padding: 1.2rem; border: 1px solid #D5E2E4; border-radius: 1.1rem; background: var(--surface); box-shadow: 0 6px 18px rgb(21 51 63 / 3%); }
.search-panel h2 { font-size: 1rem; font-weight: 600; margin: 0 0 .8rem; letter-spacing: -.02em; }
.search-controls { display: flex; align-items: stretch; gap: .55rem; }
.query-field { display: flex; align-items: center; flex: 1; min-width: 0; gap: .25rem; border: 1px solid #7A9099; border-radius: 999px; padding-left: .8rem; color: var(--muted); background: #FAFCFC; }
.query-field:focus-within { border-color: var(--primary-dark); box-shadow: 0 0 0 2px rgb(2 62 138 / 15%); }
.query-field .form-control { min-width: 0; min-height: 50px; padding: .65rem .65rem .65rem .3rem; border: 0; border-radius: 999px; background: transparent; color: var(--text); font-size: 1rem; box-shadow: none; }
.query-field .form-control:focus-visible { outline-offset: 0; }
.query-field .form-control::placeholder { color: var(--muted); opacity: 1; font-size: .85rem; }
.search-controls .btn { padding-inline: 1rem; font-size: .85rem; white-space: nowrap; }
.location-button { display: inline-flex; align-items: center; gap: .45rem; margin-top: .4rem; padding: .4rem 0; min-height: 44px; color: var(--primary-dark); border: 0; background: transparent; font-size: .8rem; text-align: left; }
.location-button:hover { text-decoration: underline; text-underline-offset: .2em; }
.location-button:disabled { opacity: .8; }
.search-hint { margin: .1rem 0 0; color: var(--muted); font-size: .73rem; line-height: 1.6; }
.location-feedback { margin: .6rem 0 0; color: var(--primary-dark); font-size: .85rem; }
.location-feedback:empty { display: none; }
.search-feedback { margin-top: .8rem; padding: .85rem; border: 1px solid var(--border); border-radius: .7rem; color: var(--primary-dark); background: var(--blue-soft); font-size: .9rem; }
.form-errors { color: var(--primary-dark); font-size: .9rem; }
.hero-details { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem 1rem; color: var(--muted); font-size: .73rem; margin-top: 1.1rem; }
.hero-details span { display: inline-flex; align-items: center; gap: .4rem; }
.hero-details .icon { color: var(--accent-dark); }
.emergency-section { padding: 1.5rem 0 0; }
.emergency-band { display: flex; align-items: center; gap: 1.5rem; border: 1px solid #E9D4D1; border-radius: 1.25rem; padding: 1.3rem 1.6rem; background: #FFFAF9; }
.sos-button { display: flex; flex-shrink: 0; flex-direction: column; justify-content: center; align-items: center; gap: 0; width: 88px; height: 88px; min-height: 88px; padding: 0; color: white; background: var(--emergency); border: 5px solid white; border-radius: 50%; animation: sos-pulse 3.2s ease-out infinite; }
.sos-button:hover { color: white; background: #AF2020; }
.sos-button strong { font-size: 1.45rem; font-weight: 700; line-height: 1.2; letter-spacing: .03em; }
.sos-button span { font-size: .65rem; }
.emergency-copy { flex: 1; min-width: 0; }
.emergency-copy h2 { font-size: 1.3rem; letter-spacing: -.035em; margin: 0 0 .35rem; }
.emergency-copy p { margin: 0; max-width: 41rem; color: var(--muted); font-size: 1rem; }
.emergency-band > .btn { flex-shrink: 0; }
.quick-actions-section { padding: 5.5rem 0; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 2rem; margin-bottom: 2rem; }
.section-heading h2 { margin: 0; font-size: clamp(2rem, 3.1vw, 2.75rem); letter-spacing: -.055em; }
.section-heading > p { max-width: 17rem; margin: 0 0 .2rem; color: var(--muted); font-size: 1rem; }
.care-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.action-card { display: flex; flex-direction: column; align-items: flex-start; width: 100%; height: 100%; min-width: 0; min-height: 225px; padding: 1.7rem; border: 1px solid var(--border); border-radius: 1.1rem; background: white; color: var(--text); text-align: left; text-decoration: none; transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease; }
.action-card:hover { color: var(--text); border-color: #99BEC6; box-shadow: 0 10px 30px rgb(21 51 63 / 6%); transform: translateY(-3px); }
.action-card-top { display: flex; align-items: center; justify-content: space-between; width: 100%; margin-bottom: 1.6rem; }
.action-icon { display: inline-flex; align-items: center; justify-content: center; width: 50px; height: 50px; color: var(--primary-dark); background: var(--blue-soft); border-radius: 50%; }
.action-icon-teal { color: var(--accent-dark); background: var(--teal-soft); }
.action-arrow { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; color: var(--ink); border: 1px solid var(--border); border-radius: 50%; }
.action-title { font-size: 1.2rem; line-height: 1.3; font-weight: 500; letter-spacing: -.03em; color: var(--ink); }
.action-description { display: block; margin-top: .55rem; font-size: 1rem; line-height: 1.6; color: var(--muted); }
.action-status { display: inline-flex; align-items: center; gap: .4rem; font-size: .7rem; color: var(--muted); margin-top: 1rem; }
.action-status::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: #7A8B95; }
.action-status-ready { color: var(--accent-dark); }
.action-status-ready::before { background: var(--accent-dark); }
.how-section { padding: 0 0 5.5rem; }
.how-panel { display: grid; grid-template-columns: 1fr 1.15fr; gap: 4rem; padding: 3rem; border-radius: 1.5rem; background: var(--hero-bg); }
.how-intro h2 { font-size: clamp(2rem, 3vw, 2.65rem); letter-spacing: -.055em; }
.how-intro > p:last-child { max-width: 24rem; margin: 1rem 0 0; color: var(--muted); font-size: 1rem; }
.simple-step { display: flex; align-items: start; gap: 1.1rem; padding: 1.15rem 0; border-bottom: 1px solid #CEDFE2; }
.simple-step:first-child { padding-top: .25rem; }
.simple-step:last-child { border-bottom: 0; padding-bottom: 0; }
.step-number { color: var(--accent-dark); font-size: .8rem; line-height: 1.6; padding-top: .15rem; }
.simple-step h3 { font-size: 1.05rem; font-weight: 500; margin: 0 0 .35rem; }
.simple-step p { font-size: 1rem; color: var(--muted); margin: 0; }
.site-footer { background: #102F40; color: white; padding: 3.5rem 0 1.4rem; }
.site-footer .navbar-brand { color: white; }
.site-footer .brand-mark { background: white; color: #102F40; }
.site-footer .brand-dot { color: #9ED4C5; }
.footer-description { max-width: 23rem; margin-top: 1.2rem; color: #C0D2DF; font-size: .9rem; }
.footer-label { color: #C0D2DF; font-size: .72rem; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .8rem; }
.footer-call { display: inline-flex; align-items: center; gap: .75rem; min-height: 44px; color: white; font-size: 2.8rem; font-weight: 500; letter-spacing: -.04em; text-decoration: none; }
.footer-call:hover { color: #C9E6F5; }
.site-footer .text-muted { color: #C0D2DF !important; }
.site-footer :focus-visible { outline-color: white !important; }
.footer-disclaimer { max-width: 30rem; color: #E2ECF1; font-size: 1rem; }
.footer-disclaimer strong { display: block; color: white; font-weight: 500; margin-bottom: .6rem; }
.footer-bottom { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid #3A5361; color: #C0D2DF; font-size: .75rem; }
.mobile-emergency-bar { display: none; }
.modal-content { border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
.modal-header { padding: 1.2rem 1.4rem; border-color: var(--border); }
.modal-title { font-size: 1.2rem; font-weight: 500; }
.modal-body, .modal-footer { padding: 1.2rem 1.4rem; }
.modal-footer { border-color: var(--border); }
.critical-note { padding: .85rem; border-left: 3px solid var(--emergency); border-radius: .3rem; color: #831818; background: #FFF1F1; }
@keyframes sos-pulse {
  0%, 75%, 100% { box-shadow: 0 0 0 1px #E5C1BC, 0 0 0 6px rgb(214 40 40 / 4%); }
  40% { box-shadow: 0 0 0 1px #E5C1BC, 0 0 0 13px rgb(214 40 40 / 0%); }
}
@media (min-width: 992px) {
  .navbar-collapse { justify-content: flex-end; gap: 1.5rem; }
  .navbar-nav { gap: .15rem; }
}
@media (max-width: 1199.98px) {
  .hero-shell { padding: 2rem; }
  .hero-grid { gap: 2rem; }
  .hero-photo { height: 530px; }
  .hero-title { font-size: 3.5rem; }
  .navbar .nav-link { padding-inline: .65rem !important; }
  .navbar-collapse { gap: .7rem; }
}
@media (max-width: 991.98px) {
  body { padding-bottom: calc(82px + env(safe-area-inset-bottom)); }
  .site-header .navbar { min-height: 78px; }
  .navbar-collapse { padding-block: .75rem; }
  .navbar .nav-link { width: 100%; padding-inline: .85rem !important; }
  .navbar-actions { padding-top: .75rem; }
  .hero-grid { grid-template-columns: 1fr 1fr; gap: 1.5rem; }
  .hero-shell { padding: 2rem; }
  .hero-title { font-size: 2.8rem; }
  .hero-photo { height: 520px; }
  .hero-description { font-size: 1rem; }
  .search-controls { flex-direction: column; }
  .search-controls > .btn { min-height: 46px; }
  .hero-note { left: -.75rem; bottom: 3rem; padding: .8rem; gap: .6rem; }
  .hero-note-icon { width: 38px; height: 38px; }
  .hero-note strong { font-size: .8rem; }
  .hero-note p { font-size: .7rem; }
  .emergency-band { flex-wrap: wrap; gap: 1.2rem; }
  .emergency-copy { flex-basis: calc(100% - 110px); }
  .emergency-band > .btn:not(.sos-button) { margin-left: 110px; }
  .quick-actions-section { padding-block: 4rem; }
  .care-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .how-panel { gap: 2rem; padding: 2rem; }
  .how-section { padding-bottom: 4rem; }
  .mobile-emergency-bar { position: fixed; display: flex; justify-content: space-between; align-items: center; gap: .75rem; left: 0; right: 0; bottom: 0; z-index: 1030; padding: .6rem 1.25rem calc(.6rem + env(safe-area-inset-bottom)); border-top: 1px solid var(--border); background: white; box-shadow: 0 -4px 18px rgb(21 51 63 / 6%); }
  .mobile-emergency-bar p { font-size: .75rem; color: var(--muted); margin: 0; line-height: 1.4; }
  .mobile-emergency-bar strong { display: block; color: var(--text); font-weight: 600; }
  .mobile-bar-actions { display: flex; align-items: center; gap: .6rem; }
  .mobile-bar-actions > .btn { padding: .7rem 1rem; font-size: .85rem; }
  .sos-button-compact { min-height: 48px; height: 48px; width: 48px; border: 0; animation: none; }
  .sos-button-compact strong { font-size: .85rem; }
  .sos-button-compact span { font-size: .5rem; }
}
@media (max-width: 767.98px) {
  .hero-section { padding: .75rem .75rem 0; }
  .hero-shell { padding: 2rem 1.5rem 1.5rem; }
  .hero-grid { grid-template-columns: 1fr; gap: 1.75rem; }
  .hero-title { font-size: clamp(2.75rem, 8vw, 3.8rem); }
  .hero-description { max-width: 31rem; }
  .search-controls { flex-direction: row; }
  .hero-photo { height: 350px; object-position: 50% 32%; }
  .hero-note { left: .8rem; bottom: 2.5rem; width: 280px; }
  .hero-note strong { font-size: .85rem; }
  .hero-art { padding-bottom: 1.1rem; }
  .image-caption { right: .1rem; bottom: -.1rem; }
  .section-heading { flex-direction: column; align-items: start; gap: 1rem; }
  .section-heading > p { max-width: none; }
  .how-panel { grid-template-columns: 1fr; gap: 1.75rem; }
}
@media (max-width: 575.98px) {
  .container { padding-inline: 1.25rem; }
  .site-header .navbar { min-height: 74px; }
  .brand-word { font-size: 1.5rem; }
  .brand-mark { width: 36px; height: 36px; }
  .preview-label { font-size: .6rem; }
  .hero-shell { border-radius: 1.25rem; padding: 1.6rem 1.15rem 1.25rem; }
  .hero-kicker { margin-bottom: 1.2rem; font-size: .7rem; }
  .hero-title { font-size: clamp(2.6rem, 10.5vw, 3.5rem); margin-bottom: 1.1rem; }
  .hero-description { margin-bottom: 1.4rem; }
  .search-panel { padding: 1rem; }
  .search-controls { flex-direction: column; }
  .hero-photo { height: 300px; border-radius: 1rem; }
  .hero-note { width: 245px; max-width: calc(100% - 1.6rem); }
  .hero-details { gap: .55rem; font-size: .7rem; }
  .emergency-section { padding-top: 1.1rem; }
  .emergency-band { padding: 1.2rem; gap: 1rem; }
  .emergency-copy { flex-basis: calc(100% - 92px); }
  .emergency-copy h2 { font-size: 1.1rem; }
  .emergency-copy p { font-size: .9rem; }
  .emergency-band > .sos-button { width: 72px; height: 72px; min-height: 72px; }
  .emergency-band > .sos-button strong { font-size: 1.2rem; }
  .emergency-band > .btn:not(.sos-button) { margin-left: 0; width: 100%; }
  .quick-actions-section { padding-block: 3rem; }
  .section-heading { margin-bottom: 1.5rem; }
  .care-grid { gap: .65rem; }
  .action-card { padding: 1rem; min-height: 235px; border-radius: .85rem; }
  .action-card-top { margin-bottom: 1.2rem; }
  .action-icon { width: 42px; height: 42px; }
  .action-arrow { width: 27px; height: 27px; }
  .action-arrow .icon { width: .8rem; height: .8rem; }
  .action-title { font-size: 1rem; }
  .action-description { font-size: 1rem; line-height: 1.5; }
  .action-status { font-size: .65rem; }
  .how-panel { padding: 1.5rem; border-radius: 1.1rem; }
  .how-section { padding-bottom: 3rem; }
  .site-footer { padding-top: 2.5rem; }
  .footer-bottom { margin-top: 1.5rem; }
  .mobile-emergency-bar { padding-inline: 1rem; }
  .mobile-emergency-bar p { font-size: .65rem; }
  .mobile-bar-actions { gap: .45rem; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### templates/base.html

Shared document and mobile emergency bar. Existing static JS and modal behaviour are reused.

```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="MEDTAP is a medical emergency project that helps you find your way to care. In a real emergency, call 112.">
  <meta name="theme-color" content="#023E8A">
  <title>{% block title %}MEDTAP | A little closer to care{% endblock %}</title>
  <link rel="icon" href="{% static 'img/favicon.svg' %}" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'vendor/bootstrap/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'css/theme.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  {% include 'partials/navbar.html' %}
  <main id="main-content" class="site-main" tabindex="-1">
    {% include 'partials/messages.html' %}
    {% block content %}{% endblock %}
  </main>
  {% include 'partials/footer.html' %}
  {% include 'partials/feature_preview.html' %}
  <div class="mobile-emergency-bar" aria-label="Emergency call shortcut">
    <p><strong>Need urgent help?</strong>Call emergency services.</p>
    <div class="mobile-bar-actions">
      {% include 'partials/sos_button.html' with compact=True only %}
      <a href="tel:112" class="btn btn-primary">
        {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112
      </a>
    </div>
  </div>
  <script src="{% static 'vendor/bootstrap/bootstrap.bundle.min.js' %}" defer></script>
  <script src="{% static 'js/site.js' %}" defer></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### templates/partials/navbar.html

Responsive navigation and clear project-preview status.

```html
<header class="site-header">
  <nav class="navbar navbar-expand-lg" aria-label="Main navigation">
    <div class="container">
      <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
        <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
        <span class="brand-word">medtap<span class="brand-dot">.</span></span>
      </a>
      <span class="preview-label me-auto d-lg-none">Preview</span>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-navigation" aria-controls="main-navigation" aria-expanded="false" aria-label="Toggle navigation">
        {% include 'partials/icon.html' with name='list' class_name='icon-lg' only %}
      </button>
      <div class="collapse navbar-collapse" id="main-navigation">
        <ul class="navbar-nav">
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'core:home' %} active{% endif %}" {% if request.resolver_match.view_name == 'core:home' %}aria-current="page"{% endif %} href="{% url 'core:home' %}">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'core:home' %}#find-care">Find Hospitals</a></li>
          <li class="nav-item"><button class="nav-link" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="First-aid guides" data-preview-description="First-aid guides are not available in this preview. In a medical emergency, call 112 and follow the dispatcher's instructions.">First Aid</button></li>
          <li class="nav-item"><a class="nav-link" href="#emergency-numbers">Helplines</a></li>
        </ul>
        <div class="navbar-actions">
          <span class="preview-label d-none d-lg-inline">Project preview</span>
          <button class="btn btn-outline-primary" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="Your MEDTAP account" data-preview-description="Registration and login are coming soon. You can explore the home page without an account.">
            Login
          </button>
          <a class="btn btn-primary d-none d-lg-inline-flex" href="tel:112">
            {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112
          </a>
        </div>
      </div>
    </div>
  </nav>
</header>
```

### templates/partials/sos_button.html

One reusable SOS preview. compact=True selects the mobile bar appearance; describedby is optional.

```html
<button class="btn sos-button{% if compact %} sos-button-compact{% endif %}" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="SOS sharing is not available yet" data-preview-description="This is a preview of the SOS button. It does not create an emergency request, capture your location, or contact anyone." data-preview-critical="true" aria-label="SOS preview: does not send an emergency request"{% if describedby %} aria-describedby="{{ describedby }}"{% endif %}>
  <strong>SOS</strong><span>Preview</span>
</button>
```

### templates/partials/action_card.html

The same six cards, with lighter structure and explicit availability text.

```html
{% if card.href %}
<a href="{{ card.href }}" class="action-card" aria-describedby="action-description-{{ card.key }}">
{% else %}
<button type="button" class="action-card" aria-describedby="action-description-{{ card.key }}" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="{{ card.title }}" data-preview-description="{{ card.preview_description }}"{% if card.critical %} data-preview-critical="true"{% endif %}>
{% endif %}
  <span class="action-card-top">
    <span class="action-icon{% if card.tone == 'teal' %} action-icon-teal{% endif %}">{% include 'partials/icon.html' with name=card.icon class_name='icon-lg' only %}</span>
    <span class="action-arrow">{% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</span>
  </span>
  <span class="action-title">{{ card.title }}</span>
  <span class="action-description" id="action-description-{{ card.key }}">{{ card.description }}</span>
  <span class="action-status{% if card.available %} action-status-ready{% endif %}">{% if card.available %}Call shortcut available{% else %}Coming soon{% endif %}</span>
{% if card.href %}</a>{% else %}</button>{% endif %}
```

### templates/partials/footer.html

Shared footer content styled by the new dark footer rules.

```html
<footer class="site-footer">
  <div class="container">
    <div class="row g-4">
      <div class="col-lg-4">
        <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
          <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
          <span class="brand-word">medtap<span class="brand-dot">.</span></span>
        </a>
        <p class="footer-description">A little closer to care.<br>A student project built around a clearer, calmer path to help.</p>
      </div>
      <div class="col-sm-4 col-lg-3" id="emergency-numbers">
        <p class="footer-label mb-1">India emergency helpline</p>
        <a class="footer-call" href="tel:112">{% include 'partials/icon.html' with name='telephone' only %} 112</a>
        <p class="text-muted small mb-0">For immediate emergency assistance.</p>
      </div>
      <div class="col-sm-8 col-lg-5">
        <p class="footer-label">Please remember</p>
        <p class="footer-disclaimer mb-0"><strong>This app does not replace calling 112.</strong> SOS sharing and ambulance booking are not available in this preview. Nothing is sent or dispatched by this demo.</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {% now 'Y' %} MEDTAP. Built with care.</span>
      <span>Medical Emergency App &middot; Student project</span>
    </div>
  </div>
</footer>
```

### core/forms.py

Existing server validation with a shorter placeholder that fits the integrated search field.

```python
from django import forms


class CareSearchForm(forms.Form):
    """Validate the preview's read-only query; nearby search arrives later."""

    q = forms.CharField(
        label="Hospital name, area or postcode",
        min_length=2,
        max_length=120,
        widget=forms.TextInput(attrs={
            "id": "care-query",
            "class": "form-control",
            "placeholder": "Hospital, area or postcode",
            "autocomplete": "off",
            "aria-describedby": "search-hint search-errors",
        }),
    )

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())
```

### templates/core/home.html

Photo-led hero, integrated search, emergency band, services and simple next-step section.

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}MEDTAP | The right care, a little closer{% endblock %}
{% block content %}
<section class="hero-section" aria-labelledby="hero-heading">
  <div class="hero-shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <p class="hero-kicker">{% include 'partials/icon.html' with name='heart-pulse' class_name='icon-sm' only %} Healthcare, with a human touch</p>
        <h1 class="hero-title" id="hero-heading">The right care.<br>A little <span>closer.</span></h1>
        <p class="hero-description">Find your way to nearby hospitals, essential resources, and the people you count on. A clearer next step, when it matters most.</p>
        <section class="search-panel" id="find-care" aria-labelledby="search-heading">
          <h2 id="search-heading">Find nearby hospitals</h2>
          <form action="{% url 'core:home' %}#find-care" method="get" id="care-search-form" role="search" aria-label="Hospital search preview">
            <label class="visually-hidden" for="care-query">{{ search_form.q.label }}</label>
            <div class="search-controls">
              <div class="query-field">
                {% include 'partials/icon.html' with name='search' class_name='icon-sm' only %}
                {{ search_form.q }}
              </div>
              <button type="submit" class="btn btn-primary">Find care {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</button>
            </div>
            <button type="button" class="location-button" id="location-button" aria-describedby="location-feedback">
              <span id="location-idle">{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %}</span>
              <span class="spinner-border spinner-border-sm" id="location-spinner" aria-hidden="true" hidden></span>
              <span id="location-button-label">Use my location</span>
            </button>
            <p class="search-hint" id="search-hint">Search preview. Results and maps are coming soon.</p>
            <div id="search-errors" class="form-errors" role="alert">{% for error in search_form.q.errors %}<p class="mt-2 mb-0">{{ error }}</p>{% endfor %}</div>
          </form>
          <p class="location-feedback" id="location-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
          <div class="search-feedback" id="search-feedback" role="status" aria-live="polite" aria-atomic="true"{% if not search_preview %} hidden{% endif %}>Hospital results are not available in this preview. Nothing has been sent to a healthcare facility. For immediate emergency help, call 112.</div>
          <noscript><p class="search-hint">The location button needs JavaScript. You can still enter an area or call 112 directly.</p></noscript>
        </section>
        <div class="hero-details">
          <span>{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %} Location stays in this tab</span>
          <span>{% include 'partials/icon.html' with name='phone' class_name='icon-sm' only %} Made for your phone</span>
        </div>
      </div>
      <figure class="hero-art">
        <img class="hero-photo" src="{% static 'img/care-professional-v2.png' %}" width="1122" height="1402" fetchpriority="high" alt="Illustrative portrait of a healthcare professional in blue scrubs in a bright hospital corridor.">
        <div class="hero-note">
          <span class="hero-note-icon">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
          <div><strong>People first.<br>Every step of the way.</strong><p>A clearer path to the care around you.</p></div>
        </div>
        <figcaption class="image-caption">AI-generated illustration &middot; Not a listed provider</figcaption>
      </figure>
    </div>
  </div>
</section>
<section class="emergency-section" aria-labelledby="urgent-heading">
  <div class="container">
    <div class="emergency-band">
      {% include 'partials/sos_button.html' with describedby='sos-preview-note' only %}
      <div class="emergency-copy">
        <h2 id="urgent-heading">When it's urgent, start here.</h2>
        <p id="sos-preview-note">Call 112 for immediate emergency help. SOS sharing and ambulance booking are previews only.</p>
      </div>
      <a href="tel:112" class="btn btn-primary">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112 directly {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a>
    </div>
  </div>
</section>
<section class="quick-actions-section" id="quick-actions" aria-labelledby="quick-actions-heading">
  <div class="container">
    <div class="section-heading">
      <div><p class="eyebrow">Your care, connected</p><h2 id="quick-actions-heading">What do you need today?</h2></div>
      <p>Essential resources.<br>One place to start.</p>
    </div>
    <div class="care-grid">
      {% for card in quick_actions %}{% include 'partials/action_card.html' with card=card only %}{% endfor %}
    </div>
  </div>
</section>
<section class="how-section" aria-labelledby="how-heading">
  <div class="container">
    <div class="how-panel">
      <div class="how-intro">
        <p class="eyebrow">A calmer way forward</p>
        <h2 id="how-heading">For the moments<br>that matter.</h2>
        <p>Knowing where to start can make a difficult moment feel less overwhelming. We're building MEDTAP with that simple idea in mind.</p>
      </div>
      <div class="how-steps">
        <div class="simple-step"><span class="step-number" aria-hidden="true">01</span><div><h3>Call for urgent help</h3><p>Use the Call 112 shortcut to reach emergency services directly.</p></div></div>
        <div class="simple-step"><span class="step-number" aria-hidden="true">02</span><div><h3>Know what's around you</h3><p>Nearby facility search and maps are coming soon.</p></div></div>
        <div class="simple-step"><span class="step-number" aria-hidden="true">03</span><div><h3>Keep your people close</h3><p>Medical profiles and emergency contacts are coming next.</p></div></div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
{% block extra_js %}<script src="{% static 'js/home.js' %}" defer></script>{% endblock %}
```

## Verification completed

- Django system checks pass. Existing routes and admin still render.
- The home page, theme CSS and new hero image return HTTP 200 from the live server.
- Search validation, query escaping, messages, internal anchors, static file lookup
  and every rendered Bootstrap icon ID pass the existing checks.
- Location loading/error/success and dialog reset checks still pass.
- The new image has descriptive alt text, intrinsic dimensions and high fetch priority.
- Both SOS preview buttons are present, with consistent no-request-sent behaviour.
- Rendered HTML has no inline styles or inline event handlers.
- Measured new contrast pairs pass: hero heading 12.04:1, secondary text on hero
  5.59:1, footer text 9.00:1, footer main copy 11.65:1. The input boundary is 3.25:1,
  above the 3:1 non-text contrast threshold. White on red remains 5.01:1.

The browser access host and native UI pipe remain unavailable in this session.
Consequently I could not inspect a real browser screenshot, verify device overflow
visually, or exercise a real location-permission prompt. The listed rendering,
HTTP and isolated interaction checks do not replace that visual review.

Open the live home page and use Ctrl+F5, then review the layout at your usual desktop
and phone widths. Do not place a test call to 112. The next functional feature is
pending until you say **next** after reviewing this redesign.
