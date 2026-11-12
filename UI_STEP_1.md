# UI Step 1: theme, shared layout, then home page

> This is the first UI version. The current Framer-inspired redesign and its complete
> updated code are documented in [UI_REDESIGN.md](UI_REDESIGN.md).

Your latest instruction brings the UI foundation and home page forward before the
account screens. This step is implemented. Stop here and say **next** when you want
to continue. Registration/login/profile screens and all facility, map, SOS tracking
and first-aid screens remain for later steps.

The earlier STEP_1.md is a snapshot of the original setup. This guide gives the
current code for files added or changed by this UI step.

## What to open

- Home page: **http://127.0.0.1:8000/**
- Built-in admin: http://127.0.0.1:8000/admin/

The existing development server was restarted with automatic reload. If it is
already running, refresh the home page; do not start another server on port 8000.
To start it yourself in VS Code's PowerShell terminal:

```powershell
Set-Location 'C:\Users\Ashish\OneDrive\Desktop\MEDTAP'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Leave that terminal open. Stop the server with Ctrl+C. Expect a successful system
check and a development-server URL, then a calm blue/white home page containing a
red SOS preview, search bar, six action cards, footer disclaimer and mobile call
shortcut. No new migrations or superuser are needed for this UI step. If you have
not created an admin account yet, do it in a second terminal:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

If the page looks cached after editing CSS, refresh with Ctrl+F5.

## New and changed files

```text
MEDTAP/
|-- config/
|   |-- settings.py                  # adds core and static source directory
|   `-- urls.py                      # includes the home URL module
|-- core/                            # page-level app; no database models
|   |-- __init__.py
|   |-- apps.py
|   |-- forms.py
|   |-- views.py
|   `-- urls.py
|-- templates/
|   |-- base.html
|   |-- core/
|   |   `-- home.html
|   `-- partials/
|       |-- icon.html
|       |-- navbar.html
|       |-- footer.html
|       |-- messages.html
|       |-- feature_preview.html
|       `-- action_card.html
|-- static/
|   |-- css/theme.css
|   |-- js/site.js
|   |-- js/home.js
|   |-- img/favicon.svg
|   `-- vendor/
|       |-- bootstrap/
|       |   |-- bootstrap.min.css
|       |   |-- bootstrap.bundle.min.js
|       |   `-- LICENSE
|       `-- bootstrap-icons/
|           |-- bootstrap-icons.svg
|           `-- LICENSE
|-- README.md
|-- THIRD_PARTY.md
`-- UI_STEP_1.md
```

All existing models, migrations, secrets and dependency requirements are unchanged.
`core` is a small additional app for site-level pages. Keeping it separate avoids
placing the home page in a domain app such as accounts or facilities.

## Implementation order and viva explanations

1. **theme.css:** centralises every requested palette variable, typography, spacing,
   buttons and responsive rules. Bootstrap supplies the grid and accessible component
   behaviours; the theme provides MEDTAP's own appearance. Custom styles are external.
2. **base.html:** supplies one HTML document, font/style/script links, shared navigation,
   messages, footer and dialog. Child pages override title/content/extra_css/extra_js
   blocks. Script defer preserves order and waits for the document to be parsed.
3. **Reusable partials:** navbar/footer avoid duplication; icon.html loads decorative
   Bootstrap SVG symbols; action_card.html renders all six shortcuts consistently.
   SVG icons are aria-hidden because adjacent text supplies their meaning.
4. **core view and URL:** a function-based GET-only view renders the home page. A
   namespaced app-level URL keeps routing organised. It does not query patient data.
5. **CareSearchForm:** validates a read-only query on the server, even if JavaScript
   is disabled or bypassed. It trims/normalises spaces and enforces 2–120 characters.
   GET is appropriate because searching is read-only. A CSRF token is not needed for
   this GET form; CSRF middleware remains enabled for later POST forms.
6. **home.html:** extends the base layout, renders the search form and includes the
   card partial in a loop. Django auto-escapes query values and card descriptions.
7. **home.js:** supplies loading/denied/unavailable/timeout/success location states.
   It requests location only after a click, resets loading on every outcome and offers
   a manual area/postcode fallback. Coordinates are validated, then discarded; they
   are not saved, logged, sent over the network, or added to a URL. No background
   geolocation occurs. Later nearby search will add a real data flow.
8. **site.js:** configures one reusable Bootstrap preview modal with textContent,
   rather than injecting HTML. Bootstrap handles focus trapping, Escape and focus
   return. Critical previews clearly say nothing has been sent or booked.
9. **Static files:** STATICFILES_DIRS points to editable static/ source files.
   STATIC_ROOT remains the deployment output directory used by collectstatic.
   They must be different directories. Bootstrap and the icon sprite are local;
   Inter is requested from Google Fonts with a system-font fallback.

## Preview behaviour, without pretending features exist

- SOS opens a clearly labelled preview dialog. It creates no EmergencyRequest and
  contacts nobody. The prominent disclaimer and direct Call 112 link remain visible.
- Ambulance, Blood Banks, Pharmacies and First Aid open named availability dialogs.
- Find Hospitals scrolls to the search form; a submitted query displays a clear
  results-not-available notice. No fake hospitals, distances or opening hours appear.
- Helplines scrolls to the actual 112 footer shortcut. The separate helpline screen
  and region-specific 108/102 records are reserved for their planned feature.
- Login is an explicit coming-soon dialog. It does not redirect to the staff admin.
- tel:112 asks the device to handle an ordinary phone link. The website itself does
  not place calls; a desktop without a phone handler may ask you to select an app.

112 is India's unified emergency number, as described by the
[Ministry of Home Affairs](https://www.mha.gov.in/emergency-response-support-system-erss).
No real hospital records or first-aid instructions were added.

## Accessibility and design choices

- The requested six palette values are preserved exactly in :root.
- A darker teal is used for small text; the requested teal is also used decoratively.
  Key measured contrast ratios are body text 13.94:1, secondary text 5.83:1,
  white on dark-blue buttons 10.20:1, white on SOS red 5.01:1 and dark-teal labels
  on their pale background 6.13:1. These pairs exceed WCAG AA's 4.5:1 text threshold.
- Body text starts at 16px. Core explanatory card/emergency/disclaimer text is also
  16px. Compact labels and secondary metadata use smaller sizes.
- Interactive controls have at least 44px targets. Focus rings are visible; a skip
  link reaches main content; form labels and live status regions are present.
- No information relies on colour alone. SVGs are decorative; future meaningful
  images must have appropriate alt text.
- The red token is reserved for SOS, critical warnings and the mobile emergency call.
- The sticky call shortcut appears below the desktop navigation breakpoint. Body
  padding and safe-area insets keep the shortcut from covering page content.
- Breakpoints use the Bootstrap grid. Small-screen SOS content is compact; cards
  use two columns on narrow screens and three on desktop.
- The SOS pulse and card hover lift are subtle. prefers-reduced-motion disables
  motion, including smooth scrolling.

These are implementation checks, not a claim of a complete WCAG conformance audit.
Browser/screen-reader visual checks are still necessary.

The layout draws on healthcare design patterns from the
[NHS Design System](https://service-manual.nhs.uk/design-system),
[Apollo 24|7](https://www.apollo247.com/) and
[Cleveland Clinic](https://my.clevelandclinic.org/). Practo blocked automated access.
No third-party branding or medical copy is reproduced. Bootstrap's official
[getting-started documentation](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
and [Icons](https://icons.getbootstrap.com/) describe the underlying assets.

## Keep these requirements for later UI steps

| Later screen | Accepted requirements |
| --- | --- |
| Account/profile | Medical ID card, blood group, allergies, conditions, emergency contacts; validated forms and private access. |
| Facilities | Cards with type, distance, 24x7 badge, speciality tags, Call and Directions; no unverified availability claims. |
| Nearby search | Leaflet/OpenStreetMap list/map split view, filters, geolocation loading and manual fallback. |
| SOS | Minimal confirmation with real request state; sharing plus Google Maps link; no simulated sent/assigned status. |
| Ambulance | Requested/accepted/on-the-way/completed timeline backed by actual operator updates. |
| First aid | Readable numbered step cards with icons, reviewed sources and clear emergency warning. |
| Helplines | Verified regional numbers, including appropriate 112/108/102 coverage; visible call actions. |

All screens will extend this base, reuse partials and messages, avoid inline custom
styles, keep red for critical actions, and preserve mobile focus/tap-target rules.
Do not add these screens until the next requested feature.

## Complete custom code, file by file

The following files already exist in your workspace. Each block is complete.
Vendor files are distributed under their own licenses and are installed by the
commands near the end; they are not pasted into this tutorial.

### static/css/theme.css

All palette tokens, components, focus rules, breakpoints and reduced-motion handling.

```css
/* MEDTAP: shared design tokens. Keep custom styles in this file. */
:root {
  --primary: #0077B6;
  --primary-dark: #023E8A;
  --accent: #2A9D8F;
  --emergency: #D62828;
  --bg: #F5F9FC;
  --text: #1F2933;
  --muted: #526375;
  --accent-dark: #17665D;
  --surface: #FFFFFF;
  --blue-soft: #EAF4FB;
  --teal-soft: #EAF6F3;
  --border: #D8E3EC;
  --shadow: 0 10px 36px rgb(2 62 138 / 6%);
  --radius: 1.25rem;
  --bs-body-font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --bs-body-font-size: 1rem;
  --bs-body-line-height: 1.65;
  --bs-body-color: var(--text);
  --bs-body-bg: var(--bg);
  --bs-link-color: var(--primary-dark);
  --bs-link-hover-color: var(--text);
}

html { scroll-behavior: smooth; scroll-padding-top: 7rem; }
body { min-width: 320px; }
body, button, input, select, textarea { font-family: var(--bs-body-font-family); }
h1, h2, h3, h4 { color: var(--primary-dark); font-weight: 700; line-height: 1.18; }
a { text-underline-offset: .2em; }
button, input, select, .btn { font-size: 1rem; }
button, .btn, .form-control, .form-select { min-height: 44px; }
:focus-visible { outline: 3px solid var(--primary-dark) !important; outline-offset: 4px; }
.form-control:focus, .form-select:focus {
  border-color: var(--primary-dark);
  box-shadow: 0 0 0 3px rgb(2 62 138 / 16%);
}
[hidden] { display: none !important; }
.container { max-width: 1184px; }
.icon { display: inline-block; width: 1.25rem; height: 1.25rem; fill: currentColor; flex-shrink: 0; vertical-align: -.18em; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-lg { width: 1.75rem; height: 1.75rem; }
.skip-link { position: fixed; top: -6rem; left: 1rem; z-index: 2000; padding: .8rem 1.2rem; background: var(--primary-dark); color: white; border-radius: .5rem; }
.skip-link:focus { top: 1rem; color: white; }
.text-muted { color: var(--muted) !important; }
.eyebrow { color: var(--accent-dark); font-size: .78rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
.eyebrow::before { content: ""; display: inline-block; width: .45rem; height: .45rem; margin-right: .5rem; border-radius: 50%; background: var(--accent); vertical-align: .1em; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: .6rem; padding: .75rem 1.15rem; border-radius: .7rem; font-weight: 600; }
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
.btn-emergency { color: white; background: var(--emergency); border: 1px solid var(--emergency); }
.btn-emergency:hover, .btn-emergency:active { color: white; background: #AF2020; border-color: #AF2020; }
.btn-close { box-sizing: border-box; width: 44px; height: 44px; min-width: 44px; min-height: 44px; background-size: .85rem; opacity: .8; }
.site-header { position: sticky; top: 0; z-index: 1020; background: var(--surface); border-bottom: 1px solid var(--border); }
.site-header .navbar { min-height: 86px; }
.navbar-brand { display: inline-flex; align-items: center; gap: .75rem; color: var(--primary-dark); padding-block: .5rem; margin-right: 1.5rem; }
.brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 45px; height: 45px; border-radius: .85rem; background: var(--primary-dark); color: white; }
.brand-word { display: block; font-size: 1.35rem; font-weight: 800; letter-spacing: -.06em; line-height: 1.1; }
.brand-caption { display: block; color: var(--muted); font-size: .68rem; line-height: 1.4; letter-spacing: .03em; }
.navbar .nav-link { display: inline-flex; align-items: center; min-height: 44px; padding: .6rem .85rem !important; color: var(--muted); font-size: .9rem; font-weight: 500; background: none; border: 0; border-radius: .5rem; text-decoration: none; }
.navbar .nav-link:hover, .navbar .nav-link.active { color: var(--primary-dark); background: var(--blue-soft); }
.navbar-toggler { min-width: 44px; border-color: var(--border); color: var(--primary-dark); }
.navbar-actions { display: flex; gap: .65rem; align-items: center; }
.navbar-actions .btn { padding: .6rem 1rem; font-size: .9rem; }
.preview-strip { padding: .6rem 0; background: var(--blue-soft); color: var(--primary-dark); font-size: .8rem; }
.preview-strip .container { display: flex; align-items: center; gap: .55rem; }
.preview-strip a { color: inherit; font-weight: 700; }
.site-main { min-height: 50vh; }
.message-container { padding-top: 1.25rem; }
.message-container:empty { display: none; }
.alert { border-radius: .8rem; }
.alert-danger { color: #831818; background: #FFF1F1; border-color: #EAB4B4; }
.alert-info { color: var(--primary-dark); background: var(--blue-soft); border-color: var(--border); }
.alert-success { color: var(--accent-dark); background: var(--teal-soft); border-color: #B8DCD3; }
.hero-section { padding: 3.75rem 0 3rem; }
.hero-copy { padding-right: 2.5rem; }
.hero-title { font-size: clamp(2.5rem, 4.6vw, 4rem); letter-spacing: -.055em; margin: 1.15rem 0 1.4rem; }
.hero-title span { color: var(--primary); }
.hero-description { max-width: 32rem; color: var(--muted); font-size: 1.05rem; }
.hero-details { display: flex; flex-wrap: wrap; gap: .8rem 1.4rem; margin-top: 1.6rem; color: var(--muted); font-size: .85rem; }
.hero-details span { display: inline-flex; align-items: center; gap: .45rem; }
.hero-details .icon { color: var(--accent-dark); }
.emergency-panel { position: relative; overflow: hidden; padding: 1.9rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow); }
.emergency-panel::before { position: absolute; content: ""; height: 4px; background: var(--emergency); top: 0; left: 0; right: 0; }
.panel-heading { display: flex; align-items: flex-start; gap: .8rem; }
.critical-icon { display: inline-flex; justify-content: center; align-items: center; width: 44px; height: 44px; border-radius: .75rem; color: var(--emergency); background: #FFF1F1; flex-shrink: 0; }
.panel-heading h2 { color: var(--text); font-size: 1.2rem; margin: .1rem 0 .3rem; }
.panel-heading p { color: var(--muted); font-size: 1rem; margin-bottom: 0; }
.sos-button { display: flex; flex-direction: column; gap: 0; width: 138px; height: 138px; border-radius: 50%; margin: 1.8rem auto 1.3rem; color: white; background: var(--emergency); border: 6px solid white; box-shadow: 0 0 0 1px #F1D1D1; animation: sos-pulse 3.2s ease-out infinite; }
.sos-button strong { font-size: 2.1rem; font-weight: 800; letter-spacing: .05em; line-height: 1.25; }
.sos-button span { font-size: .75rem; font-weight: 500; }
.sos-button:hover { color: white; background: #AF2020; }
.emergency-panel .demo-note { margin: 0 auto 1rem; max-width: 22rem; color: var(--muted); font-size: 1rem; text-align: center; }
.emergency-panel .call-link { width: 100%; }
.find-care-section { margin-bottom: 3.25rem; }
.search-panel { padding: 1.7rem 1.9rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow); }
.search-heading { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.1rem; }
.search-heading h2 { font-size: 1.15rem; margin: 0; }
.search-heading .icon { color: var(--primary-dark); }
.search-fields { display: flex; align-items: end; gap: .8rem; }
.search-input-group { flex: 1; }
.search-input-group .form-label { color: var(--muted); font-size: .8rem; font-weight: 500; margin-bottom: .4rem; }
.search-input-group .form-control { min-height: 52px; border-color: var(--border); border-radius: .7rem; background: var(--bg); }
.search-fields .btn { min-height: 52px; white-space: nowrap; }
.location-button { border-color: var(--border); background: white; color: var(--primary-dark); }
.location-button:hover { background: var(--blue-soft); border-color: var(--primary-dark); }
.search-hint { color: var(--muted); font-size: .8rem; margin: .8rem 0 0; }
.location-feedback { margin: .85rem 0 0; color: var(--primary-dark); font-size: .9rem; }
.search-feedback { margin-top: 1rem; padding: .9rem 1.1rem; border-radius: .7rem; background: var(--blue-soft); color: var(--primary-dark); }
.section-heading { display: flex; justify-content: space-between; align-items: end; gap: 1rem; margin-bottom: 1.5rem; }
.section-heading h2 { font-size: clamp(1.65rem, 3vw, 2rem); letter-spacing: -.035em; margin: .4rem 0 0; }
.section-heading > p { max-width: 21rem; color: var(--muted); font-size: .9rem; margin-bottom: .2rem; }
.quick-actions-section { padding-bottom: 3.5rem; }
.action-card { display: flex; width: 100%; height: 100%; text-align: left; flex-direction: column; padding: 1.45rem; background: var(--surface); border: 1px solid var(--border); border-radius: 1rem; color: var(--text); box-shadow: 0 4px 15px rgb(2 62 138 / 2%); text-decoration: none; transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease; }
.action-card:hover { color: var(--text); transform: translateY(-3px); box-shadow: var(--shadow); border-color: #9FBFD8; }
.action-card-top { display: flex; align-items: center; justify-content: space-between; gap: .5rem; margin-bottom: 1.2rem; }
.action-icon { display: inline-flex; width: 46px; height: 46px; justify-content: center; align-items: center; color: var(--primary-dark); background: var(--blue-soft); border-radius: .8rem; }
.action-icon-teal { color: var(--accent-dark); background: var(--teal-soft); }
.action-arrow { color: var(--muted); }
.action-title { color: var(--primary-dark); font-size: 1rem; line-height: 1.4; font-weight: 700; }
.action-description { display: block; margin-top: .35rem; color: var(--muted); font-size: 1rem; line-height: 1.6; }
.coming-soon { display: inline-block; align-self: flex-start; color: var(--muted); font-size: .7rem; margin-top: .85rem; background: var(--bg); border: 1px solid var(--border); padding: .15rem .5rem; border-radius: .35rem; }
.reassurance-section { padding-bottom: 3.75rem; }
.reassurance-panel { background: var(--blue-soft); border: 1px solid #D6E8F6; border-radius: var(--radius); padding: 2rem 2.3rem; }
.reassurance-panel h2 { font-size: 1.4rem; letter-spacing: -.025em; }
.reassurance-panel > .row > div > p { color: var(--muted); font-size: .9rem; max-width: 27rem; margin: .75rem 0 0; }
.simple-step { display: flex; gap: .9rem; align-items: flex-start; padding-block: .5rem; }
.step-number { display: inline-flex; min-width: 32px; height: 32px; justify-content: center; align-items: center; border: 1px solid #B5CDDE; border-radius: 50%; color: var(--primary-dark); background: white; font-size: .85rem; font-weight: 700; }
.simple-step h3 { color: var(--text); font-size: .9rem; margin: .1rem 0 .3rem; }
.simple-step p { margin: 0; color: var(--muted); font-size: .83rem; }
.site-footer { background: var(--surface); border-top: 1px solid var(--border); padding: 2.25rem 0 1.2rem; }
.footer-description { color: var(--muted); font-size: .85rem; max-width: 23rem; margin-top: 1rem; }
.footer-label { color: var(--muted); font-size: .75rem; text-transform: uppercase; letter-spacing: .1em; font-weight: 600; }
.footer-call { display: inline-flex; align-items: center; gap: .6rem; min-height: 44px; color: var(--primary-dark); font-size: 1.35rem; font-weight: 700; text-decoration: none; }
.footer-bottom { display: flex; gap: .75rem; justify-content: space-between; flex-wrap: wrap; border-top: 1px solid var(--border); margin-top: 1.6rem; padding-top: 1.1rem; color: var(--muted); font-size: .75rem; }
.footer-disclaimer { max-width: 34rem; color: var(--text); font-size: 1rem; }
.mobile-emergency-bar { display: none; }
.modal-content { border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
.modal-header { padding: 1.2rem 1.4rem; border-color: var(--border); }
.modal-title { font-size: 1.2rem; }
.modal-body, .modal-footer { padding: 1.2rem 1.4rem; }
.modal-footer { border-color: var(--border); }
.critical-note { color: #831818; padding: .85rem; background: #FFF1F1; border-left: 3px solid var(--emergency); border-radius: .3rem; }

@keyframes sos-pulse {
  0%, 75%, 100% { box-shadow: 0 0 0 1px #F1D1D1, 0 0 0 8px rgb(214 40 40 / 4%); }
  40% { box-shadow: 0 0 0 1px #F1D1D1, 0 0 0 16px rgb(214 40 40 / 0%); }
}
@media (min-width: 992px) {
  .navbar-collapse { justify-content: flex-end; gap: 1.25rem; }
  .navbar-nav { gap: .15rem; }
}
@media (max-width: 991.98px) {
  body { padding-bottom: calc(78px + env(safe-area-inset-bottom)); }
  .site-header .navbar { min-height: 76px; }
  .navbar-collapse { padding-block: .75rem; }
  .navbar .nav-link { width: 100%; }
  .navbar-actions { padding-top: .75rem; }
  .hero-section { padding: 2.5rem 0; }
  .hero-copy { padding-right: 0; }
  .search-fields { flex-wrap: wrap; }
  .search-input-group { flex-basis: 100%; }
  .search-fields .btn { flex: 1; }
  .section-heading { align-items: start; }
  .section-heading > p { max-width: 16rem; }
  .mobile-emergency-bar { display: flex; position: fixed; z-index: 1030; bottom: 0; left: 0; right: 0; padding: .65rem 1.25rem calc(.65rem + env(safe-area-inset-bottom)); background: white; border-top: 1px solid var(--border); box-shadow: 0 -4px 18px rgb(2 62 138 / 6%); align-items: center; justify-content: space-between; gap: .75rem; }
  .mobile-emergency-bar p { color: var(--muted); font-size: .75rem; line-height: 1.4; margin: 0; }
  .mobile-emergency-bar p strong { color: var(--text); display: block; }
  .mobile-emergency-bar .btn { min-width: 132px; }
}
@media (max-width: 575.98px) {
  html { scroll-padding-top: 5.5rem; }
  body { padding-bottom: calc(78px + env(safe-area-inset-bottom)); }
  .container { padding-inline: 1.25rem; }
  .navbar-brand { gap: .6rem; }
  .brand-mark { width: 40px; height: 40px; }
  .preview-strip { font-size: .75rem; }
  .hero-section { padding-top: 2rem; padding-bottom: 1.5rem; }
  .hero-title { font-size: clamp(2.3rem, 9.5vw, 3.2rem); margin-top: .8rem; }
  .hero-description { font-size: 1rem; }
  .hero-details { margin-top: 1.2rem; gap: .6rem 1rem; font-size: .8rem; }
  .emergency-panel { display: grid; grid-template-columns: 1fr 100px; gap: 1rem; padding: 1.3rem; }
  .emergency-panel .panel-heading { grid-column: 1; gap: .6rem; }
  .emergency-panel .critical-icon { display: none; }
  .emergency-panel .sos-button { grid-column: 2; grid-row: 1; width: 100px; height: 100px; margin: 0; }
  .emergency-panel .sos-button strong { font-size: 1.7rem; }
  .emergency-panel .demo-note { grid-column: 1 / -1; text-align: left; margin: 0; }
  .emergency-panel .call-link { grid-column: 1 / -1; }
  .search-panel { padding: 1.3rem; }
  .search-fields .btn { padding-inline: .65rem; font-size: .85rem; }
  .search-fields .icon { width: 1rem; height: 1rem; }
  .section-heading { flex-direction: column; gap: .6rem; }
  .section-heading > p { max-width: none; }
  .action-card { padding: 1rem; }
  .action-card-top { margin-bottom: 1rem; }
  .action-title { font-size: .9rem; }
  .action-description { font-size: 1rem; }
  .coming-soon { font-size: .65rem; }
  .quick-actions-section, .find-care-section { margin-bottom: 0; padding-bottom: 2.25rem; }
  .reassurance-section { padding-bottom: 2.25rem; }
  .reassurance-panel { padding: 1.5rem; }
  .site-footer { padding-top: 1.75rem; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### templates/base.html

The single base document, with extension blocks and shared partials.

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
  <div class="preview-strip">
    <div class="container">
      {% include 'partials/icon.html' with name='info-circle' class_name='icon-sm' only %}
      <span>Project preview. For immediate emergency help, call 112.</span>
    </div>
  </div>
  <main id="main-content" class="site-main" tabindex="-1">
    {% include 'partials/messages.html' %}
    {% block content %}{% endblock %}
  </main>
  {% include 'partials/footer.html' %}
  {% include 'partials/feature_preview.html' %}
  <div class="mobile-emergency-bar" aria-label="Emergency call shortcut">
    <p><strong>Need urgent help?</strong>Call emergency services directly.</p>
    <a href="tel:112" class="btn btn-emergency">
      {% include 'partials/icon.html' with name='telephone' only %} Call 112
    </a>
  </div>
  <script src="{% static 'vendor/bootstrap/bootstrap.bundle.min.js' %}" defer></script>
  <script src="{% static 'js/site.js' %}" defer></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### templates/partials/icon.html

A reusable decorative Bootstrap SVG icon. Pass the symbol name and an optional CSS class.

```html
{% load static %}<svg class="icon {{ class_name|default:'' }}" aria-hidden="true" focusable="false"><use href="{% static 'vendor/bootstrap-icons/bootstrap-icons.svg' %}#{{ name }}"></use></svg>
```

### templates/partials/navbar.html

Responsive navigation, collapsed menu, active Home link and preview actions.

```html
<header class="site-header">
  <nav class="navbar navbar-expand-lg" aria-label="Main navigation">
    <div class="container">
      <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
        <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' class_name='icon-lg' only %}</span>
        <span><span class="brand-word">MEDTAP</span><span class="brand-caption">A little closer to care</span></span>
      </a>
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
          <button class="btn btn-outline-primary" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="Your MEDTAP account" data-preview-description="Registration and login are coming soon. You can explore the home page without an account.">
            {% include 'partials/icon.html' with name='person-circle' class_name='icon-sm' only %} Login
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

### templates/partials/footer.html

Emergency number, project context and the required visible disclaimer.

```html
<footer class="site-footer">
  <div class="container">
    <div class="row g-4">
      <div class="col-lg-4">
        <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
          <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
          <span><span class="brand-word">MEDTAP</span><span class="brand-caption">A little closer to care</span></span>
        </a>
        <p class="footer-description">A student project with a simple purpose: make the path to nearby care easier to understand.</p>
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

### templates/partials/messages.html

Escaped Django messages mapped to dismissible Bootstrap alerts.

```html
{% if messages %}
<div class="container message-container" aria-label="Notifications">
  {% for message in messages %}
  <div class="alert {% if message.level == DEFAULT_MESSAGE_LEVELS.ERROR %}alert-danger{% elif message.level == DEFAULT_MESSAGE_LEVELS.SUCCESS %}alert-success{% else %}alert-info{% endif %} alert-dismissible fade show" role="{% if message.level == DEFAULT_MESSAGE_LEVELS.ERROR %}alert{% else %}status{% endif %}">
    {{ message }}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Dismiss notification"></button>
  </div>
  {% endfor %}
</div>
{% endif %}
```

### templates/partials/feature_preview.html

One honest availability dialog, reused without creating additional screens.

```html
<div class="modal fade" id="feature-preview" tabindex="-1" aria-labelledby="preview-title" aria-describedby="preview-description">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title" id="preview-title">Coming soon</h2>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close dialog"></button>
      </div>
      <div class="modal-body">
        <p id="preview-description">This feature is not available in this preview.</p>
        <p class="critical-note mb-0" id="preview-critical-note" hidden>No request has been sent. No ambulance has been booked. In a real emergency, call 112.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline-primary" type="button" data-bs-dismiss="modal">Back to home</button>
        <a class="btn btn-emergency" href="tel:112" id="preview-call" hidden>{% include 'partials/icon.html' with name='telephone' only %} Call 112</a>
      </div>
    </div>
  </div>
</div>
```

### static/js/site.js

Updates the shared dialog for the clicked action and resets critical state each time.

```javascript
"use strict";

// Bootstrap manages focus trapping, Escape, dismissal, and focus return for dialogs.
const previewModal = document.getElementById("feature-preview");
if (previewModal) {
  previewModal.addEventListener("show.bs.modal", (event) => {
    const trigger = event.relatedTarget;
    const critical = trigger?.dataset.previewCritical === "true";
    document.getElementById("preview-title").textContent = trigger?.dataset.previewTitle || "Coming soon";
    document.getElementById("preview-description").textContent = trigger?.dataset.previewDescription || "This feature is not available in this preview.";
    document.getElementById("preview-critical-note").hidden = !critical;
    document.getElementById("preview-call").hidden = !critical;
  });
}
```

### static/img/favicon.svg

A small original vector favicon; no external hospital logo is used.

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#023E8A"/><path d="M10 32h11l5-12 10 25 6-13h12" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>
```

### config/settings.py

Complete current settings. The changes in this step are core registration and STATICFILES_DIRS.

```python
from pathlib import Path

from decouple import AutoConfig, Csv

BASE_DIR = Path(__file__).resolve().parent.parent
env = AutoConfig(search_path=str(BASE_DIR))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "facilities.apps.FacilitiesConfig",
    "emergency.apps.EmergencyConfig",
    "firstaid.apps.FirstaidConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

### config/urls.py

Complete current project routing, now including the core home URL.

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("facilities/", include("facilities.urls")),
    path("emergency/", include("emergency.urls")),
    path("first-aid/", include("firstaid.urls")),
    path("", include("core.urls")),
]
```

### core/__init__.py

Create an empty package marker file.

```python

```

### core/apps.py

Registers the page-level core app with Django.

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
```

### core/forms.py

Validates and normalises the search preview query.

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
            "placeholder": "Search hospitals, area or postcode",
            "autocomplete": "off",
            "aria-describedby": "search-hint search-errors",
        }),
    )

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())
```

### core/views.py

A GET-only home view passes form state and card data to the template.

```python
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .forms import CareSearchForm


@require_GET
def home(request):
    search_form = CareSearchForm(request.GET if "q" in request.GET else None)
    search_preview = search_form.is_bound and search_form.is_valid()
    quick_actions = [
        {
            "key": "hospitals", "title": "Nearby Hospitals", "icon": "hospital",
            "description": "Find a place for the care you need.",
            "href": "#find-care",
        },
        {
            "key": "ambulance", "title": "Ambulance", "icon": "truck-front",
            "description": "Request transport and follow its progress.",
            "preview_description": "Ambulance requests are not available in this preview. For immediate emergency assistance, call 112.",
            "critical": True,
        },
        {
            "key": "blood-banks", "title": "Blood Banks", "icon": "droplet",
            "description": "Look for blood banks in your area.", "tone": "teal",
            "preview_description": "Blood bank search is coming soon. This preview does not display or verify blood availability.",
        },
        {
            "key": "pharmacies", "title": "Pharmacies", "icon": "capsule",
            "description": "Find a pharmacy close to you.", "tone": "teal",
            "preview_description": "Pharmacy search is coming soon. This preview does not list opening hours or medicine availability.",
        },
        {
            "key": "first-aid", "title": "First Aid", "icon": "bandaid",
            "description": "Clear, step-by-step guides for urgent moments.",
            "preview_description": "First-aid guides are not available in this preview. In a medical emergency, call 112 and follow the dispatcher's instructions.",
        },
        {
            "key": "helplines", "title": "Helplines", "icon": "telephone",
            "description": "Keep essential emergency numbers in reach.",
            "href": "#emergency-numbers", "available": True,
        },
    ]
    return render(request, "core/home.html", {
        "search_form": search_form,
        "search_preview": search_preview,
        "quick_actions": quick_actions,
    })
```

### core/urls.py

Namespaced app-level routing exposes core:home at the root URL.

```python
from django.urls import path

from . import views

app_name = "core"
urlpatterns = [path("", views.home, name="home")]
```

### templates/partials/action_card.html

One card layout used for real anchor shortcuts and clearly labelled preview buttons.

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
  {% if not card.available %}<span class="coming-soon">Coming soon</span>{% endif %}
{% if card.href %}</a>{% else %}</button>{% endif %}
```

### templates/core/home.html

The first public screen extends base.html instead of repeating its markup.

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}MEDTAP | Help is closer than you think{% endblock %}
{% block content %}
<section class="hero-section" aria-labelledby="hero-heading">
  <div class="container">
    <div class="row align-items-center g-4 g-lg-5">
      <div class="col-lg-7">
        <div class="hero-copy">
          <p class="eyebrow mb-0">A clearer path to care</p>
          <h1 class="hero-title" id="hero-heading">Help is closer<br>than <span>you think.</span></h1>
          <p class="hero-description mb-0">Finding help should feel simple. A place for nearby hospitals, essential resources, and the people you count on.</p>
          <div class="hero-details">
            <span>{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %} Care close to you</span>
            <span>{% include 'partials/icon.html' with name='heart-pulse' class_name='icon-sm' only %} Designed around people</span>
          </div>
        </div>
      </div>
      <div class="col-lg-5">
        <aside class="emergency-panel" aria-labelledby="urgent-heading">
          <div class="panel-heading">
            <span class="critical-icon">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
            <div><h2 id="urgent-heading">Need urgent help?</h2><p>In an emergency, call 112 first.</p></div>
          </div>
          <button class="btn sos-button" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="SOS sharing is not available yet" data-preview-description="This is a preview of the SOS button. It does not create an emergency request, capture your location, or contact anyone." data-preview-critical="true" aria-label="SOS preview: does not send an emergency request" aria-describedby="sos-preview-note">
            <strong>SOS</strong><span>Preview</span>
          </button>
          <p class="demo-note" id="sos-preview-note">Demo only. SOS sharing and ambulance booking are not available yet.</p>
          <a class="btn btn-outline-primary call-link" href="tel:112">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112 directly</a>
        </aside>
      </div>
    </div>
  </div>
</section>

<section class="find-care-section" id="find-care" aria-labelledby="search-heading">
  <div class="container">
    <div class="search-panel">
      <div class="search-heading">
        {% include 'partials/icon.html' with name='search' only %}
        <h2 id="search-heading">Find nearby hospitals</h2>
      </div>
      <form action="{% url 'core:home' %}#find-care" method="get" id="care-search-form" role="search" aria-label="Hospital search preview">
        <div class="search-fields">
          <div class="search-input-group">
            <label class="form-label" for="care-query">{{ search_form.q.label }}</label>
            {{ search_form.q }}
          </div>
          <button type="button" class="btn location-button" id="location-button" aria-describedby="location-feedback">
            <span id="location-idle">{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %}</span>
            <span class="spinner-border spinner-border-sm" id="location-spinner" aria-hidden="true" hidden></span>
            <span id="location-button-label">Use my location</span>
          </button>
          <button type="submit" class="btn btn-primary">Find hospitals {% include 'partials/icon.html' with name='arrow-right' class_name='icon-sm' only %}</button>
        </div>
        <p class="search-hint" id="search-hint">Search preview &middot; Results and maps are coming soon. Location stays in this tab.</p>
        <div id="search-errors" class="form-errors" role="alert">{% for error in search_form.q.errors %}<p class="mt-2 mb-0">{{ error }}</p>{% endfor %}</div>
      </form>
      <p class="location-feedback" id="location-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
      <div class="search-feedback" id="search-feedback" role="status" aria-live="polite" aria-atomic="true"{% if not search_preview %} hidden{% endif %}>Hospital results are not available in this preview. Nothing has been sent to a healthcare facility. For immediate emergency help, call 112.</div>
      <noscript><p class="search-hint">The location button needs JavaScript. You can still enter an area above or call 112 directly.</p></noscript>
    </div>
  </div>
</section>

<section class="quick-actions-section" id="quick-actions" aria-labelledby="quick-actions-heading">
  <div class="container">
    <div class="section-heading">
      <div><p class="eyebrow mb-0">Find your next step</p><h2 id="quick-actions-heading">The help you're looking for.</h2></div>
      <p>Simple shortcuts to the care and information that matter.</p>
    </div>
    <div class="row g-3">
      {% for card in quick_actions %}
      <div class="col-6 col-lg-4">{% include 'partials/action_card.html' with card=card only %}</div>
      {% endfor %}
    </div>
  </div>
</section>

<section class="reassurance-section" aria-labelledby="reassurance-heading">
  <div class="container">
    <div class="reassurance-panel">
      <div class="row g-4 align-items-center">
        <div class="col-lg-5">
          <p class="eyebrow mb-2">For the moments that matter</p>
          <h2 id="reassurance-heading">A little preparation.<br>A clearer next step.</h2>
          <p>MEDTAP is growing one feature at a time. Emergency services are always your first call when help is urgent.</p>
        </div>
        <div class="col-lg-7">
          <div class="simple-step"><span class="step-number" aria-hidden="true">1</span><div><h3>Call for urgent help</h3><p>Use the Call 112 shortcut to reach emergency services.</p></div></div>
          <div class="simple-step"><span class="step-number" aria-hidden="true">2</span><div><h3>Find care around you</h3><p>Nearby facility search and maps are coming soon.</p></div></div>
          <div class="simple-step"><span class="step-number" aria-hidden="true">3</span><div><h3>Keep your people close</h3><p>Medical profiles and emergency contacts are coming next.</p></div></div>
        </div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
{% block extra_js %}<script src="{% static 'js/home.js' %}" defer></script>{% endblock %}
```

### static/js/home.js

Search-preview feedback and permission-based location loading/fallback handling.

```javascript
"use strict";

(() => {
  const form = document.getElementById("care-search-form");
  const query = document.getElementById("care-query");
  const feedback = document.getElementById("search-feedback");
  const errors = document.getElementById("search-errors");
  const locationButton = document.getElementById("location-button");
  const locationLabel = document.getElementById("location-button-label");
  const locationSpinner = document.getElementById("location-spinner");
  const locationIdle = document.getElementById("location-idle");
  const locationFeedback = document.getElementById("location-feedback");
  if (!form || !query || !locationButton) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    query.value = query.value.trim().replace(/\s+/g, " ");
    if (!form.reportValidity()) return;
    if (query.value.length < 2) {
      errors.textContent = "Enter at least two characters for a hospital, area or postcode.";
      query.setAttribute("aria-invalid", "true");
      query.focus();
      return;
    }
    errors.textContent = "";
    query.removeAttribute("aria-invalid");
    feedback.hidden = false;
    feedback.textContent = "Hospital results are not available in this preview. Nothing has been sent to a healthcare facility. For immediate emergency help, call 112.";
  });

  function setLoading(loading) {
    locationButton.disabled = loading;
    locationButton.setAttribute("aria-busy", String(loading));
    locationSpinner.hidden = !loading;
    locationIdle.hidden = loading;
    locationLabel.textContent = loading ? "Finding location…" : "Use my location";
  }

  function showFailure(message) {
    setLoading(false);
    locationFeedback.textContent = message;
  }

  locationButton.addEventListener("click", () => {
    if (!window.isSecureContext) {
      showFailure("Location needs a secure connection. Please enter your area or postcode instead.");
      return;
    }
    if (!navigator.geolocation) {
      showFailure("Your browser cannot share a location. Please enter your area or postcode instead.");
      return;
    }
    setLoading(true);
    locationFeedback.textContent = "Finding your location. You may be asked for permission.";

    try {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // Validate the response without sending, logging or storing coordinates.
          const { latitude, longitude } = position.coords;
          if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
              Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
            showFailure("We couldn't read your location. Please enter your area or postcode instead.");
            return;
          }
          setLoading(false);
          locationLabel.textContent = "Refresh location";
          locationFeedback.textContent = "Location received for this preview only. It has not been sent or saved. Nearby results are coming soon.";
        },
        (error) => {
          const messages = {
            1: "Location permission was declined. That's okay — enter your area or postcode instead.",
            2: "We couldn't find your location. Please enter your area or postcode instead.",
            3: "Finding your location took too long. Try again or enter your area or postcode instead.",
          };
          showFailure(messages[error.code] || "Location is unavailable right now. Please enter your area or postcode instead.");
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
      );
    } catch {
      showFailure("Location is unavailable right now. Please enter your area or postcode instead.");
    }
  });
})();
```

## Vendor assets: already downloaded

If recreating the project, run the following PowerShell commands once from MEDTAP.
Keep the supplied licenses. These are pinned official npm distribution files served
through jsDelivr; there is no runtime dependency on that CDN for core styling/icons.

```powershell
New-Item -ItemType Directory -Force -Path 'static/vendor/bootstrap','static/vendor/bootstrap-icons' | Out-Null
Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css' -OutFile 'static/vendor/bootstrap/bootstrap.min.css' -UseBasicParsing
Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js' -OutFile 'static/vendor/bootstrap/bootstrap.bundle.min.js' -UseBasicParsing
Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/LICENSE' -OutFile 'static/vendor/bootstrap/LICENSE' -UseBasicParsing
Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/bootstrap-icons.svg' -OutFile 'static/vendor/bootstrap-icons/bootstrap-icons.svg' -UseBasicParsing
Invoke-WebRequest 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/LICENSE' -OutFile 'static/vendor/bootstrap-icons/LICENSE' -UseBasicParsing
```

## Verification and limits

Completed:

- Django system checks and migration drift checks pass; no model change was needed.
- Home GET succeeds; POST receives 405; the built-in admin still loads.
- Server-side query bounds, whitespace normalisation and HTML escaping pass.
- Shared Django success/error messages render with dismiss buttons.
- Every rendered internal anchor target, static file and Bootstrap icon ID exists.
- No inline style attributes or inline event handlers appear in the rendered home.
- Text/button colour pairs pass the measured AA contrast thresholds.
- JavaScript syntax checks and isolated behaviour tests pass for location loading,
  denial, timeout, unavailability, invalid coordinates, success and thrown errors.
- Search preview and dialog critical/noncritical resets pass isolated JS tests.
- Live HTTP checks return 200 for home, admin and all required local CSS/JS/icon assets.

The browser access host/native UI pipe was unavailable, so I could not visually
inspect a real desktop/mobile viewport or test browser permission prompts. I did
not install an alternate browser or claim screenshot-based verification. This UI
should still be checked in your browser before calling its visual QA complete.

Manual checks to try:

1. Open home at desktop width, then resize to about 390px. Check for overflow and
   confirm the fixed Call 112 bar does not cover the footer or other content.
2. Use Tab to reach the skip link, menu, search, location and cards; check focus rings.
3. Open/close the mobile navigation and the SOS preview; press Escape in the dialog.
4. Click Use my location, then deny permission. Expect a friendly area/postcode
   fallback and a re-enabled button. Permission handling on localhost needs no API key.
5. Submit a query. Expect a clear not-available notice, not fake search results.
6. Enable your OS's reduced-motion preference; the SOS pulse/hover motion should stop.

Do not place test emergency calls. Inspect the tel:112 link without completing a
call. Regional numbers and live emergency workflows remain for later steps.

Stop here. Say **next** to continue with registration, login and medical profiles,
using this theme. Other screens remain pending until their own feature steps.
