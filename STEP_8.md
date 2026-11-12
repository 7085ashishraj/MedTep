# Step 8 — Mobile UI and accessibility polish

This step is implemented in your workspace. It finishes the shared interface
after Steps 1–7. It keeps the existing medical-blue/teal theme and original
Framer-inspired design, with practical improvements for small screens and keyboards.
The full files below replace the corresponding snapshots in earlier tutorials.

## What changed and why

| Change | Why it helps |
| --- | --- |
| Remove the body's fixed 320px minimum width | A 320px browser with a scrollbar has less than 320px of content space; the old minimum caused horizontal scrolling. |
| Compact the header and emergency bar below 360px | Keep the logo, menu toggle, SOS and Call 112 usable without squeezing or wrapping the call label. The decorative Preview badge is hidden here. |
| Limit the expanded mobile menu height and allow scrolling | Navigation stays above the fixed emergency bar in a short landscape viewport. |
| Escape closes the menu and restores focus | Keyboard users can dismiss navigation and know where they are. Moving focus into page content also closes an open menu without pulling focus back. |
| Script-free navigation fallback | Links remain visible when enhancements are unavailable; the expanded fallback header scrolls with the page. |
| Error summaries explicitly focus fields | Choosing an error opens containing coordinate details, focuses the input and scrolls it into view. Hidden fields receive a useful reload message rather than an unusable link. |
| Optional Show/Hide password controls | Users can inspect typing mistakes without changing authentication or password validation. These buttons never submit the form and start hidden until JavaScript works. |
| Stronger control borders | Inputs, outlined buttons and the navigation toggle are easier to identify against white surfaces. |
| White SOS lettering in the mobile bar | The bar's contextual text rule now targets its paragraph only, preserving the SOS button's contrast. |
| Brief SOS pulse and reduced-motion support | The SOS cue runs once; reduced-motion preferences disable animation and transitions. |
| Dismissible completed/failed SOS notice | Users can clear an old notice and return to the button; hiding it does not send anything or change the retry ID. Loading notices cannot be dismissed. |
| Branded 400/403/404/500 pages | Give users calm recovery links and Call 112 without displaying internal exception details. |
| Remove the old feature-preview modal | All six home actions now lead to implemented pages. |
| Current-page markers on transport navigation | Both visible styling and `aria-current` identify the active section. |

The existing form validation, CSRF protection, private profiles, operator
permissions, manual SOS sharing and first-aid provenance remain in place.
The disclaimer **This app does not replace calling 112** remains visible in the
footer. This step adds no medical advice, dispatch integration, dependency or secret.

## Files in this step

```text
MEDTAP/
├── core/
│   ├── error_test_urls.py       # isolated test URL configuration only
│   ├── test_ui.py               # 9 Django UI/error-response tests
│   └── ui_frontend_tests.cjs    # 9 isolated shared-script/contrast checks
├── emergency/frontend_tests.cjs # now 12 SOS checks
├── static/
│   ├── css/theme.css           # full shared stylesheet
│   └── js/
│       ├── site.js             # keyboard, error and password enhancements
│       └── sos.js              # existing SOS capture plus notice dismissal
└── templates/
    ├── base.html
    ├── 400.html
    ├── 403.html
    ├── 404.html
    ├── 500.html
    └── partials/
        ├── navbar.html
        ├── action_card.html
        ├── form_errors.html
        ├── form_fields.html
        └── sos_controls.html
```

Delete `templates/partials/feature_preview.html`; its base-template include has
also been removed. No model, migration, production URL, app view or `.env` change
is required. `core/error_test_urls.py` is loaded only by test settings; do not add
its deliberate error routes to `config/urls.py`.

## Exact commands — PowerShell

Run in the MEDTAP folder in VS Code, using the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
node core/ui_frontend_tests.cjs
node facilities/frontend_tests.cjs
node emergency/frontend_tests.cjs
node emergency/ambulance_frontend_tests.cjs
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Expect no Django system-check issues, `No changes detected`, **178 Django tests
passing**, and **38 JavaScript checks** (9 shared UI, 9 facilities, 12 SOS,
8 ambulance). Node is needed only for these frontend checks. Use the existing
development server if port 8000 is already occupied. This step requires neither
`migrate` nor another `createsuperuser`; use the account created in earlier steps.

Open [MEDTAP](http://127.0.0.1:8000/). Shared CSS and scripts now have a release
query suffix in `base.html` so browsers request the updated files instead of a
cached earlier version. If a browser still looks old, use Ctrl+F5 (Windows/Linux)
or Command+Shift+R (macOS). Future deployments should use versioned/hashed static
assets; that configuration belongs to the deployment step.

## What you should see

1. At a 320px-wide viewport, the home page, login, registration, facility search,
   first-aid library and helplines fit without horizontal scrolling. The logo
   and menu button stay on one row; the bottom bar keeps SOS and Call 112 clear.
2. Open the mobile menu in a short landscape viewport. The menu scrolls within
   its available height. Focus a navigation link and press Escape: focus returns
   to the menu toggle. Tab into the page: the menu closes without stealing focus.
3. Login has one Show password button; registration has two. Each changes to Hide
   when used. Passwords remain hidden initially. Toggling never submits or logs
   the input. Keep passwords hidden before sharing a screenshot.
4. Open [an intentionally invalid coordinate search](http://127.0.0.1:8000/facilities/?latitude=bad&longitude=0).
   The error summary receives focus. Choose its Latitude error: the coordinate
   section opens and the latitude field receives focus above the emergency bar.
5. An invalid registration still explains that the account was not created.
   Django renders field descriptions/errors and their ARIA references; the
   shared enhancement makes the summary links move keyboard focus correctly.
6. With scripts disabled, navigation links are expanded and the header is no
   longer sticky. Passwords, regular form submission, manual coordinate search
   and ordinary telephone links still work. GPS capture and live enhancements
   require JavaScript; the existing manual-entry links remain available.
7. All six home service cards navigate to actual implemented features. The
   Ambulance navigation item marks the current transport section. Authorised
   operators also get the Operator queue marker.

Do not call emergency numbers or share a real location just to test layout.
An unsigned-in SOS link still takes you through the normal sign-in flow. No real
calls, messages, geolocation permissions or provider requests were used during
this step's visual verification.

### Error pages and DEBUG

Django automatically selects `400.html`, `403.html`, `404.html` and `500.html`
from the template directory for the matching error responses. No error view or
URL override is needed in production. Keep the development setting as it is:
Django's development diagnostics may appear with `DEBUG=True`. The automated
tests temporarily use `DEBUG=False` and real exceptions to verify branded pages,
correct HTTP status codes and absence of the diagnostic marker.

Do not toggle your real `.env` merely to provoke errors. The 500 template extends
the common layout without relying on a database query for its content. Shared
assets must still be served normally by the eventual production host.

## Verification recorded for this step

- Full Django suite: **178 passed**. Tests use a separate test database.
- JavaScript: **38 checks passed** across the four commands above.
- Migration drift: **No changes detected**.
- Public-page browser measurements at 320×568: document content width and client
  width both **305px** on each of the six public pages (the scrollbar occupies
  the remaining width). The final narrow header is approximately **75px** tall.
- Landscape menu at 568×320: expanded header bottom **208px**, emergency bar top
  **252px**; the menu's scrollable region was **144px** tall. Escape returned
  focus to the collapsed toggle.
- The coordinate error link focused `id_latitude` with its rectangle between the
  sticky header and bottom bar.
- Separate fictional preview data was used for medical profile, transport
  timeline and operator-form layout checks: each measured **305px** content and
  client width. No existing user's profile, access or transport status was changed.
- An isolated script-free response showed all navigation links with zero script
  tags, a static header and no misleading menu toggle. This checks the fallback
  markup/styles; it is not a claim of a full browser-settings or assistive-tech audit.
- Browser Show/Hide checks confirmed password → text → password input types;
  input values were not inspected. Branded 500 appearance was also previewed
  using fictional data. The separate preview server was stopped afterwards.
- Final browser-computed mobile SOS colours: white lettering (`rgb(255, 255, 255)`)
  on the requested emergency red (`rgb(214, 40, 40)`).

### Accessibility decisions for your viva

**Progressive enhancement:** the server sends working links and forms first.
The root starts with `no-js`; the script removes it only when Bootstrap Collapse
is available. The fallback keeps navigation visible rather than relying on a
toggle that cannot work. Password controls are initially hidden and activate
only when the matching input exists.

**Focus and semantics:** real links navigate; real buttons perform actions.
The navigation toggle keeps `aria-controls` and Bootstrap-managed
`aria-expanded`, following the [WAI disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/).
It is ordinary website navigation, so it does not use application-style menu
roles or a modal focus trap. Error links call `focus()` as well as scrolling;
scrolling alone does not move a keyboard user's insertion point.

**Contrast and controls:** the checked normal-text palette pairs meet at least
4.5:1; stronger borders meet 3:1 on white. The normal/large-text AA thresholds
are explained in [WAI Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
The requested 44px target remains our design goal for primary controls. WCAG
2.2 AA's target-size minimum is 24px with exceptions; 44px is the enhanced
criterion, as distinguished by [WAI Target Size Minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).
Inline text links and native checkboxes are not universally enlarged to 44px.

**Honest scope:** these are focused checks, not WCAG certification. A full
screen-reader audit, forced-colours testing, real-phone keyboard/safe-area
testing and all platform/browser combinations remain outside this pass. The
Node tests calculate selected source-colour pairs; they do not inspect every
rendered element or replace human review.

**Error responses:** a friendly 404 must still return HTTP 404, rather than 200,
so clients understand that the resource is missing. The tests check status codes
and privacy as well as text. They deliberately raise errors in a test-only URL
configuration, keeping deliberate failures out of the real application's routes.

## Complete current files

Copy each full block into the file named immediately above it. Shared files are
included in full, even when this step changes only a few lines. Keep the existing
locally vendored Bootstrap, Leaflet, icon sprite and original image assets.

### `templates/base.html`

Shared layout: progressive-enhancement marker, release asset URLs and no obsolete preview modal.

```html
{% load static %}
<!doctype html>
<html lang="en" class="no-js">
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
  <link rel="stylesheet" href="{% static 'css/theme.css' %}?v=20261112b">
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
  {% include 'partials/sos_controls.html' %}
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
  <script src="{% static 'js/site.js' %}?v=20261112a" defer></script>
  <script src="{% static 'js/sos.js' %}?v=20261112a" defer></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### `templates/partials/navbar.html`

Navigation keeps permission checks and identifies active transport/operator sections.

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
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.namespace == 'facilities' %} active{% endif %}"{% if request.resolver_match.namespace == 'facilities' %} aria-current="page"{% endif %} href="{% url 'facilities:nearby' %}">Find Hospitals</a></li>
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'firstaid:guide_list' or request.resolver_match.view_name == 'firstaid:guide_detail' %} active{% endif %}"{% if request.resolver_match.view_name == 'firstaid:guide_list' or request.resolver_match.view_name == 'firstaid:guide_detail' %} aria-current="page"{% endif %} href="{% url 'firstaid:guide_list' %}">First Aid</a></li>
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'firstaid:helplines' %} active{% endif %}"{% if request.resolver_match.view_name == 'firstaid:helplines' %} aria-current="page"{% endif %} href="{% url 'firstaid:helplines' %}">Helplines</a></li>
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'emergency:ambulance_start' or request.resolver_match.view_name == 'emergency:ambulance_request' or request.resolver_match.view_name == 'emergency:ambulance_detail' %} active{% endif %}"{% if request.resolver_match.view_name == 'emergency:ambulance_start' or request.resolver_match.view_name == 'emergency:ambulance_request' or request.resolver_match.view_name == 'emergency:ambulance_detail' %} aria-current="page"{% endif %} href="{% url 'emergency:ambulance_start' %}">Ambulance</a></li>
          {% if user.is_staff and perms.emergency.view_ambulancerequest and perms.emergency.change_ambulancerequest %}<li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'emergency:operator_dashboard' or request.resolver_match.view_name == 'emergency:operator_update' %} active{% endif %}"{% if request.resolver_match.view_name == 'emergency:operator_dashboard' or request.resolver_match.view_name == 'emergency:operator_update' %} aria-current="page"{% endif %} href="{% url 'emergency:operator_dashboard' %}">Operator queue</a></li>{% endif %}
        </ul>
        <div class="navbar-actions">
          {% if not user.is_authenticated %}<span class="preview-label d-none d-lg-inline">Project preview</span>{% endif %}
          {% if user.is_authenticated %}
          <a class="btn btn-outline-primary" href="{% url 'accounts:profile' %}">My profile</a>
          <form method="post" action="{% url 'accounts:logout' %}" class="logout-form">{% csrf_token %}<button class="btn btn-outline-primary" type="submit">Sign out</button></form>
          {% else %}
          <a class="btn btn-outline-primary" href="{% url 'accounts:login' %}">Login</a>
          {% endif %}
          <a class="btn btn-primary d-none d-lg-inline-flex" href="tel:112">
            {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112
          </a>
        </div>
      </div>
    </div>
  </nav>
</header>
```

### `templates/partials/action_card.html`

Every implemented home action is an ordinary navigation link.

```html
<a href="{{ card.href }}" class="action-card" aria-describedby="action-description-{{ card.key }}">
  <span class="action-card-top">
    <span class="action-icon{% if card.tone == 'teal' %} action-icon-teal{% endif %}">{% include 'partials/icon.html' with name=card.icon class_name='icon-lg' only %}</span>
    <span class="action-arrow">{% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</span>
  </span>
  <span class="action-title">{{ card.title }}</span>
  <span class="action-description" id="action-description-{{ card.key }}">{{ card.description }}</span>
  <span class="action-status action-status-ready">{{ card.status }}</span>
</a>
```

### `templates/partials/form_errors.html`

Accessible summary links for visible fields and a generic recovery message for invalid hidden fields.

```html
{% if form.errors %}
<div class="form-error-summary" id="form-error-summary" role="alert" tabindex="-1" aria-labelledby="form-error-heading">
  <h2 id="form-error-heading">{{ error_heading|default:'Please check your details' }}</h2>
  {% if error_intro %}<p>{{ error_intro }}</p>{% endif %}
  <ul>
    {% for error in form.non_field_errors %}<li>{{ error }}</li>{% endfor %}
    {% for field in form %}{% for error in field.errors %}<li>{% if field.is_hidden %}Some form details are missing or invalid. Reload this page and try again.{% else %}<a href="#{{ field.id_for_label }}">{{ field.label }}: {{ error }}</a>{% endif %}</li>{% endfor %}{% endfor %}
  </ul>
</div>
{% endif %}
```

### `templates/partials/form_fields.html`

Reusable fields preserve Django's validation/ARIA output and add optional password controls.

```html
{% for field in form %}
{% if field.is_hidden %}{{ field }}{% else %}
<div class="field-wrapper">
  {% if field.field.widget.input_type == 'checkbox' %}
  <label class="checkbox-label" for="{{ field.id_for_label }}">{{ field }} <span>{{ field.label }}</span></label>
  {% else %}
  <label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}{% if field.field.required %}<span class="required-marker" aria-hidden="true"> *</span>{% else %}<span class="optional-label"> (optional)</span>{% endif %}</label>
  {% if field.field.widget.input_type == 'password' %}
  <div class="password-control">{{ field }}<button type="button" class="password-toggle" data-toggle-password data-password-label="{{ field.label }}" aria-controls="{{ field.id_for_label }}" aria-label="Show {{ field.label|lower }}" hidden>Show</button></div>
  {% else %}{{ field }}{% endif %}
  {% endif %}
  {% if field.help_text %}<div class="field-help" id="{{ field.auto_id }}_helptext">{{ field.help_text }}</div>{% endif %}
  {% if field.errors %}<ul class="field-errors" id="{{ field.auto_id }}_error">{% for error in field.errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}
</div>
{% endif %}
{% endfor %}
```

### `templates/partials/sos_controls.html`

Signed-in CSRF form and live notice with a dismiss button, initially hidden.

```html
{% if user.is_authenticated %}
<form id="sos-request-form" method="post" action="{% url 'emergency:create' %}" hidden>{% csrf_token %}</form>
<div class="sos-feedback" id="sos-feedback" role="status" aria-live="polite" tabindex="-1" hidden>
  <button type="button" class="btn-close sos-feedback-close" id="sos-feedback-dismiss" aria-label="Hide SOS notice" hidden></button>
  <span class="spinner-border spinner-border-sm" id="sos-spinner" aria-hidden="true" hidden></span>
  <p id="sos-feedback-text"></p>
  <a href="{% url 'emergency:start' %}" id="sos-fallback" hidden>Open SOS page for manual entry or saved requests</a>
</div>
{% endif %}
```

### `static/css/theme.css`

Complete theme including the existing screens, stronger borders, narrow-screen layout, script-free fallback and motion preferences.

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
  --control-border: #708791;
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
html { scroll-behavior: smooth; scroll-padding-top: 7rem; scroll-padding-bottom: calc(7rem + env(safe-area-inset-bottom)); }
body { min-width: 0; }
body, button, input, select, textarea { font-family: var(--bs-body-font-family); }
h1, h2, h3, h4 { color: var(--ink); font-weight: 500; line-height: 1.15; }
a { text-underline-offset: .2em; }
button, input, select, .btn { font-size: 1rem; }
button, .btn, .form-control, .form-select { min-height: 44px; }
.form-control, .form-select { border-color: var(--control-border); }
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
  --bs-btn-border-color: var(--control-border);
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
.navbar-toggler { min-width: 44px; border-color: var(--control-border); color: var(--ink); border-radius: 50%; }
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
.search-hint { margin: .1rem 0 0; color: var(--muted); font-size: .73rem; line-height: 1.6; }
.location-feedback { margin: .6rem 0 0; color: var(--primary-dark); font-size: .85rem; }
.location-feedback:empty { display: none; }
.hero-details { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem 1rem; color: var(--muted); font-size: .73rem; margin-top: 1.1rem; }
.hero-details span { display: inline-flex; align-items: center; gap: .4rem; }
.hero-details .icon { color: var(--accent-dark); }
.emergency-section { padding: 1.5rem 0 0; }
.emergency-band { display: flex; align-items: center; gap: 1.5rem; border: 1px solid #E9D4D1; border-radius: 1.25rem; padding: 1.3rem 1.6rem; background: #FFFAF9; }
.sos-button { display: flex; flex-shrink: 0; flex-direction: column; justify-content: center; align-items: center; gap: 0; width: 88px; height: 88px; min-height: 88px; padding: 0; color: white; background: var(--emergency); border: 5px solid white; border-radius: 50%; animation: sos-pulse 3.2s ease-out 1; }
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
  .navbar-collapse { padding-block: .75rem; max-height: calc(100vh - 176px); max-height: max(88px, calc(100dvh - 176px)); overflow-y: auto; overscroll-behavior: contain; scroll-padding-block: .6rem; }
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
  .mobile-emergency-bar > p > strong { display: block; color: var(--text); font-weight: 600; }
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
/* Accounts: shared forms and a private medical ID, using the existing theme. */
.account-section { padding: 3rem 0 4.5rem; }
.auth-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: start; }
.auth-intro { padding: 2.7rem; border-radius: var(--radius); background: var(--hero-bg); }
.auth-intro h1 { font-size: clamp(2rem, 3.2vw, 3rem); letter-spacing: -.055em; margin-bottom: 1.4rem; }
.auth-intro > p { font-size: 1rem; color: var(--muted); }
.auth-intro > .eyebrow { color: var(--accent-dark); font-size: .75rem; }
.auth-benefits { display: grid; gap: 1.2rem; margin-top: 2rem; }
.auth-benefits > div { display: flex; align-items: start; gap: .8rem; color: var(--muted); font-size: 1rem; }
.auth-benefits .icon { margin-top: .2rem; color: var(--accent-dark); }
.auth-intro .auth-reminder { border-top: 1px solid #CADCE0; padding-top: 1.3rem; margin: 2rem 0 0; }
.account-panel { padding: 2rem; min-width: 0; border: 1px solid var(--border); border-radius: 1.2rem; background: white; }
.account-panel > h1 { font-size: clamp(1.8rem, 3vw, 2.4rem); letter-spacing: -.045em; }
.account-panel > h2, .panel-title-row > h2 { font-size: 1.5rem; letter-spacing: -.035em; margin-bottom: 1rem; }
.field-wrapper { margin-bottom: 1.35rem; min-width: 0; }
.field-wrapper .form-label { display: block; font-weight: 500; font-size: .9rem; margin-bottom: .5rem; }
.field-wrapper .form-control, .field-wrapper .form-select { min-height: 48px; padding: .7rem .85rem; border: 1px solid #7A9099; border-radius: .6rem; background-color: #FCFDFD; font-size: 1rem; }
.field-wrapper textarea.form-control { resize: vertical; }
.field-wrapper [aria-invalid='true'] { border: 2px solid var(--primary-dark); }
.field-help { margin-top: .45rem; color: var(--muted); font-size: .8rem; line-height: 1.6; }
.field-help ul { margin: .25rem 0 0; padding-left: 1.2rem; }
.field-errors { margin: .45rem 0 0; padding-left: 1.2rem; color: var(--primary-dark); font-size: .9rem; }
.required-marker { color: var(--primary-dark); }
.optional-label { color: var(--muted); font-weight: 400; font-size: .8rem; }
.checkbox-label { display: flex; min-height: 44px; align-items: center; gap: .8rem; cursor: pointer; }
.checkbox-label .form-check-input { width: 1.2rem; height: 1.2rem; margin: 0; float: none; flex-shrink: 0; border-color: #6B818A; }
.checkbox-label .form-check-input:checked { background-color: var(--primary-dark); border-color: var(--primary-dark); }
.form-error-summary { padding: 1rem 1.2rem; margin-bottom: 1.5rem; border: 2px solid var(--primary-dark); border-radius: .7rem; background: var(--blue-soft); color: var(--primary-dark); }
.form-error-summary h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: .5rem; }
.form-error-summary ul { margin: .4rem 0; padding-left: 1.2rem; }
.form-error-summary a { display: flex; align-items: center; min-height: 44px; color: var(--primary-dark); font-size: .9rem; }
.auth-switch { margin: 1.4rem 0 0; font-size: .9rem; color: var(--muted); }
.auth-switch a { display: inline-flex; align-items: center; min-height: 44px; font-weight: 500; }
.account-form-shell { max-width: 740px; margin: 0 auto; }
.back-link { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; margin-bottom: .8rem; color: var(--primary-dark); font-size: .9rem; }
.account-form-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; margin-top: 1.6rem; }
.profile-page-heading { display: flex; align-items: end; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 2rem; }
.profile-page-heading h1 { font-size: clamp(2rem, 3.5vw, 3rem); letter-spacing: -.055em; }
.profile-layout { display: grid; grid-template-columns: .9fr 1.3fr; gap: 2rem; align-items: start; }
.medical-id { background: var(--hero-bg); border: 1px solid #C6D9DB; border-radius: 1.4rem; padding: 2rem; overflow-wrap: anywhere; }
.medical-id-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem; align-items: center; margin-bottom: 2rem; }
.medical-id-top > span:first-child { color: var(--primary-dark); font-weight: 600; display: inline-flex; gap: .5rem; align-items: center; font-size: .85rem; }
.privacy-label { display: inline-flex; align-items: center; gap: .35rem; color: var(--accent-dark); font-size: .7rem; }
.medical-id h2 { font-size: 1.8rem; letter-spacing: -.045em; margin-bottom: .25rem; }
.medical-id-username { font-size: .85rem; color: var(--muted); }
.blood-group-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; padding-block: 1.2rem; margin-top: 1.8rem; border-block: 1px solid #C6D9DB; }
.medical-id-label { font-size: .8rem; color: var(--muted); margin-bottom: .35rem; }
.blood-group-value { font-size: 2rem; font-weight: 500; color: var(--primary-dark); margin: 0; line-height: 1.3; }
.self-reported, .primary-label { display: inline-flex; font-size: .7rem; padding: .25rem .6rem; border-radius: 999px; color: var(--accent-dark); background: #F5FCF9; border: 1px solid #B7D2C9; }
.medical-id-caption { font-size: .8rem; color: var(--muted); margin: 1.2rem 0 0; }
.profile-privacy-note { margin: 1.1rem .3rem 0; color: var(--muted); font-size: .8rem; }
.profile-details { display: grid; gap: 1.5rem; min-width: 0; }
.medical-detail { padding-block: 1.1rem; border-bottom: 1px solid var(--border); }
.medical-detail h3 { font-size: .85rem; color: var(--muted); font-weight: 500; }
.medical-detail p { margin-bottom: 0; font-size: 1rem; overflow-wrap: anywhere; }
.panel-title-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-bottom: .5rem; }
.panel-title-row > h2 { margin: 0; }
.panel-title-row > .btn { font-size: .8rem; padding-inline: .9rem; }
.contact-item { padding-top: 1.5rem; margin-top: 1.5rem; border-top: 1px solid var(--border); overflow-wrap: anywhere; }
.contact-heading { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
.contact-heading h3 { font-size: 1.1rem; font-weight: 500; margin: 0; }
.contact-relationship { color: var(--muted); font-size: .85rem; margin: .3rem 0; }
.contact-phone { margin-bottom: .75rem; font-size: 1rem; }
.contact-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.contact-actions .btn { font-size: .8rem; padding: .6rem .9rem; }
.empty-contacts { padding: 2rem 0 .5rem; }
.empty-contacts h3 { font-size: 1.2rem; margin-top: 1rem; }
.empty-contacts p { color: var(--muted); font-size: 1rem; margin-bottom: 0; }
.logout-form { margin: 0; }
.navbar-actions { flex-wrap: wrap; }
@media (max-width: 991.98px) {
  .auth-layout { gap: 1.5rem; }
  .auth-intro, .account-panel { padding: 1.5rem; }
  .profile-layout { grid-template-columns: 1fr 1.3fr; gap: 1.3rem; }
  .medical-id { padding: 1.5rem; }
}
@media (max-width: 767.98px) {
  .account-section { padding: 1.75rem 0 3rem; }
  .auth-layout, .profile-layout { grid-template-columns: 1fr; }
  .auth-benefits { display: none; }
  .auth-intro h1 { font-size: 2rem; }
  .auth-intro .auth-reminder { margin-top: 1rem; padding-top: 1rem; }
  .profile-page-heading { align-items: start; }
}
/* Facility finder: one filter form, an accessible card list and a companion map. */
.home-location-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; margin-top: .85rem; }
.home-location-actions .btn { font-size: .85rem; padding: .6rem .9rem; }
.home-location-actions > a { display: inline-flex; min-height: 44px; align-items: center; font-size: .85rem; }
.finder-section { padding: 3rem 0 4rem; background: linear-gradient(var(--hero-bg), white 440px); }
.finder-heading { display: flex; justify-content: space-between; align-items: end; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 2rem; }
.finder-heading h1 { font-size: clamp(2.25rem, 4vw, 3.5rem); letter-spacing: -.055em; }
.finder-heading p:last-child { max-width: 34rem; margin-bottom: 0; color: var(--muted); }
.finder-notice { display: flex; align-items: start; gap: .8rem; padding: 1rem 1.2rem; margin-bottom: 1.5rem; background: #F8FCFE; color: var(--primary-dark); border: 1px solid #BDD4E2; border-radius: 1rem; }
.finder-notice .icon { margin-top: .2rem; }
.finder-notice p { margin: 0; font-size: .9rem; }
.finder-filter-panel { padding: 1.5rem; background: white; border: 1px solid var(--border); border-radius: 1.25rem; box-shadow: 0 8px 28px rgb(21 51 63 / 5%); }
.finder-filters { display: grid; grid-template-columns: 1.5fr 1fr 1fr .8fr; gap: 1rem; }
.finder-filters .field-wrapper { margin-bottom: .8rem; }
.finder-filter-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 1rem; }
.finder-filter-actions > .btn { margin-left: auto; }
.finder-reset { display: inline-flex; align-items: center; gap: .4rem; min-height: 44px; font-size: .9rem; }
.finder-location { border-top: 1px solid var(--border); margin-top: 1.3rem; padding-top: 1.3rem; }
.finder-location-actions { display: flex; flex-wrap: wrap; gap: .6rem; }
.finder-location-actions .btn { font-size: .9rem; }
.finder-location .location-feedback { margin: .8rem 0; }
.finder-location details { margin-top: .5rem; }
.finder-location summary { display: list-item; min-height: 44px; padding-block: .5rem; color: var(--primary-dark); cursor: pointer; font-weight: 500; }
.manual-location-fields { display: grid; grid-template-columns: 1fr 1fr auto; align-items: end; gap: 1rem; margin-top: .5rem; }
.manual-location-fields .field-wrapper { margin-bottom: 0; }
.manual-location-fields .btn { min-height: 48px; }
.finder-privacy { color: var(--muted); font-size: .85rem; max-width: 68rem; margin: .8rem 0 0; }
.finder-results-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .5rem; margin: 2.5rem 0 1.2rem; scroll-margin-top: 8rem; }
.finder-results-heading h2 { font-size: 1.6rem; letter-spacing: -.035em; }
.finder-results-heading p { color: var(--muted); font-size: .9rem; margin: 0; }
.finder-layout { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.5rem; align-items: start; }
.facility-list { display: grid; gap: 1rem; min-width: 0; }
.facility-card { border: 1px solid var(--border); border-radius: 1.1rem; padding: 1.4rem; background: white; scroll-margin-top: 8rem; overflow-wrap: anywhere; transition: box-shadow .18s ease, transform .18s ease; }
.facility-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.facility-card:target { border-color: var(--primary-dark); }
.facility-card-top { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem; margin-bottom: .9rem; }
.facility-number { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: var(--primary-dark); color: white; font-size: .8rem; }
.facility-type, .facility-demo-label, .facility-hours { display: inline-flex; padding: .25rem .55rem; border-radius: 999px; font-size: .75rem; font-weight: 500; }
.facility-type { background: var(--blue-soft); color: var(--primary-dark); }
.facility-demo-label { background: #F1F3F5; color: #46515D; border: 1px dashed #65727F; }
.facility-card h3 { font-size: 1.4rem; letter-spacing: -.035em; line-height: 1.3; }
.facility-meta { display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; color: var(--muted); font-size: .85rem; margin: .8rem 0; }
.facility-hours { background: var(--teal-soft); color: var(--accent-dark); }
.facility-address { font-size: 1rem; color: var(--muted); }
.facility-specialities { list-style: none; display: flex; flex-wrap: wrap; gap: .4rem; padding: 0; margin-bottom: 1rem; }
.facility-specialities li { border: 1px solid var(--border); border-radius: .4rem; padding: .2rem .5rem; font-size: .75rem; color: var(--muted); }
.facility-demo-note { font-size: .85rem; color: var(--muted); padding: .6rem .8rem; background: var(--bg); border-radius: .5rem; }
.facility-card-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.facility-card-actions .btn { font-size: .85rem; padding: .6rem .85rem; }
.facility-card-actions .btn:disabled { opacity: 1; color: #5B6877; background: #F1F3F5; border-color: #D8E3E7; cursor: default; }
.facility-map-button { min-height: 44px; border: 0; background: transparent; color: var(--primary-dark); text-decoration: underline; text-underline-offset: .2em; font-size: .85rem; padding: .5rem .75rem; }
.finder-empty { padding: 2.5rem 1.5rem; background: var(--bg); border-radius: 1.1rem; }
.finder-empty h3 { margin-top: 1.4rem; font-size: 1.5rem; }
.finder-empty p { color: var(--muted); }
.finder-pagination { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: .8rem; padding-top: .75rem; }
.finder-pagination span { color: var(--muted); font-size: .9rem; }
.finder-map-panel { position: sticky; top: 115px; min-width: 0; border: 1px solid var(--border); border-radius: 1.1rem; background: var(--bg); overflow: hidden; }
.finder-map-heading { padding: 1.2rem 1.2rem .5rem; }
.finder-map-heading h2 { font-size: 1.2rem; letter-spacing: -.025em; }
.finder-map-heading p { color: var(--muted); font-size: .85rem; }
.facility-map { height: 430px; width: 100%; background: #E5ECEE; z-index: 0; font-family: var(--bs-body-font-family); }
.map-feedback, .map-credit { margin: 0; padding: .8rem 1.2rem; color: var(--muted); font-size: .85rem; }
.map-credit { padding-top: .2rem; }
.map-credit a, .map-card-link { display: inline-flex; min-height: 44px; align-items: center; }
.map-legend { display: flex; flex-wrap: wrap; gap: .7rem; padding: 0 1.2rem; color: var(--muted); font-size: .75rem; }
.map-legend > span { display: inline-flex; align-items: center; gap: .4rem; }
.legend-dot { display: inline-block; width: 12px; height: 12px; background: var(--primary-dark); border-radius: 50%; }
.legend-demo { background: #46515D; }
.legend-origin { background: var(--accent-dark); }
.facility-pin { display: flex !important; flex-direction: column; justify-content: center; align-items: center; border-radius: 50% 50% 50% 0; transform-origin: center; background: var(--primary-dark); color: white; border: 2px solid white; box-shadow: 0 2px 8px rgb(0 0 0 / 25%); }
.facility-pin span { font-weight: 700; font-size: 1rem; line-height: 1; }
.facility-pin small { font-size: .65rem; line-height: 1; margin-top: .25rem; }
.facility-pin-demo { background: #46515D; border-style: dashed; }
.search-location-pin { display: flex !important; align-items: center; justify-content: center; border: 3px solid white; border-radius: 50%; background: var(--accent-dark); color: white; font-size: 1.8rem; box-shadow: 0 2px 8px rgb(0 0 0 / 25%); }
.finder-map-panel .leaflet-control-zoom a { width: 44px; height: 44px; line-height: 44px; }
.finder-map-panel .leaflet-popup-content { font-size: .9rem; line-height: 1.6; }
.finder-map-panel .leaflet-popup-close-button { width: 44px; height: 44px; line-height: 44px; }
.finder-map-panel .leaflet-popup-content-wrapper { padding-right: 1rem; }
.finder-map-panel .leaflet-control-attribution { max-width: 100%; font-size: .7rem; }
@media (max-width: 991.98px) {
  .finder-filters { grid-template-columns: 1fr 1fr; }
  .finder-map-panel { top: 95px; }
  .facility-map { height: 380px; }
}
@media (max-width: 767.98px) {
  .finder-section { padding-top: 1.75rem; }
  .finder-layout { grid-template-columns: 1fr; }
  .finder-map-panel { position: static; }
  .manual-location-fields { grid-template-columns: 1fr 1fr; }
  .manual-location-fields .btn { grid-column: 1 / -1; }
  .finder-filter-panel { padding: 1.1rem; }
}
@media (max-width: 575.98px) {
  .finder-heading h1 { font-size: 2.3rem; }
  .finder-filters, .manual-location-fields { grid-template-columns: 1fr; gap: .5rem; }
  .finder-filter-actions > .btn { margin-left: 0; }
  .finder-filter-actions { gap: .6rem; }
  .finder-filter-actions > .checkbox-label { width: 100%; }
  .facility-card { padding: 1.1rem; }
}
/* SOS capture and manual sharing: no implied dispatch or delivery status. */
.sos-button { text-decoration: none; }
.sos-button[aria-disabled='true'] { animation: none; opacity: .75; cursor: wait; }
.sos-page { max-width: 1100px; }
.sos-heading { margin-bottom: 1.6rem; }
.sos-heading h1 { font-size: clamp(2.1rem, 4vw, 3.2rem); letter-spacing: -.05em; }
.sos-heading > p:last-child { color: var(--muted); max-width: 42rem; }
.sos-critical-note { padding: 1rem 1.2rem; border-left: 4px solid var(--emergency); border-radius: .5rem; background: #FFF4F3; color: #7C2020; margin-bottom: 1.5rem; }
.sos-critical-note a { color: #7C2020; display: inline-flex; align-items: center; min-height: 44px; }
.sos-layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.5rem; align-items: start; }
.sos-start-panel > .sos-button { margin: 1.5rem 0; }
.sos-start-panel > p, .sos-contact p { color: var(--muted); }
.sos-manual-summary { min-height: 44px; padding-block: .6rem; color: var(--primary-dark); cursor: pointer; }
.sos-recent-list { padding-left: 1.1rem; color: var(--muted); }
.sos-recent-list a { display: inline-flex; align-items: center; min-height: 44px; }
.sos-timeline { list-style: none; padding-left: 1.4rem; margin: 1.5rem 0 2rem; border-left: 2px solid var(--border); }
.sos-timeline li { position: relative; padding: 0 0 1.3rem .35rem; }
.sos-timeline li:last-child { padding-bottom: 0; }
.sos-timeline li::before { content: ''; position: absolute; left: -1.85rem; top: .3rem; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--muted); background: white; }
.sos-timeline .sos-step-complete::before { background: var(--accent-dark); border-color: var(--accent-dark); }
.sos-timeline strong { display: block; font-weight: 600; color: var(--ink); }
.sos-timeline span { display: block; color: var(--muted); font-size: .9rem; }
.sos-message { min-height: 260px; line-height: 1.7; padding: 1rem; font-size: 1rem; resize: vertical; }
.sos-share-actions { display: flex; flex-wrap: wrap; gap: .6rem; margin: 1rem 0; }
.sos-share-actions .btn { font-size: .9rem; }
.sos-contact { padding: 1.2rem 0; border-bottom: 1px solid var(--border); overflow-wrap: anywhere; }
.sos-contact .contact-heading h3 { font-size: 1.1rem; }
.sos-contact p { font-size: .9rem; margin: .4rem 0; }
.sos-feedback { position: fixed; top: 105px; right: 1rem; z-index: 1030; width: min(420px, calc(100% - 2rem)); border: 2px solid var(--primary-dark); border-radius: 1rem; padding: 1.2rem; color: var(--primary-dark); background: white; box-shadow: var(--shadow); }
.sos-feedback p { margin: .5rem 0 0; }
.sos-feedback a { display: inline-flex; align-items: center; min-height: 44px; margin-top: .6rem; }
@media (max-width: 767.98px) {
  .sos-layout { grid-template-columns: 1fr; }
  .sos-feedback { top: 88px; }
}
/* Ambulance project requests and operator queue. */
.ambulance-location-list { display: grid; gap: 1rem; }
.ambulance-location-card, .operator-queue-card { display: flex; flex-wrap: wrap; gap: 1.2rem; align-items: center; justify-content: space-between; }
.ambulance-location-card h2 { font-size: 1.35rem; }
.ambulance-location-card p:last-child { color: var(--muted); margin-bottom: 0; }
.ambulance-status { display: inline-flex; align-items: center; min-height: 36px; border-radius: 999px; background: var(--blue-soft); color: var(--primary-dark); padding: .35rem .8rem; font-weight: 600; font-size: .85rem; }
.ambulance-timeline { list-style: none; padding: 0; margin: 1.8rem 0; }
.ambulance-timeline li { position: relative; margin-left: .5rem; padding: 0 0 1.6rem 1.7rem; border-left: 2px solid var(--border); }
.ambulance-timeline li:last-child { padding-bottom: .3rem; border-left-color: transparent; }
.ambulance-timeline li::before { content: ''; position: absolute; left: -7px; top: .3rem; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--muted); background: white; }
.ambulance-timeline .ambulance-step-reached::before { border-color: var(--accent-dark); background: var(--accent-dark); }
.ambulance-timeline .ambulance-step-current::before { outline: 3px solid #B8DCD3; outline-offset: 2px; }
.ambulance-timeline strong { display: block; color: var(--ink); font-weight: 500; }
.ambulance-timeline span { display: block; margin-top: .25rem; color: var(--muted); font-size: .85rem; }
.ambulance-reference-heading { font-size: 1.1rem; margin-top: 1.6rem; }
.ambulance-sos-link { margin: 0 0 1.5rem; }
.operator-counts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
.operator-counts > div { background: var(--hero-bg); border: 1px solid var(--border); border-radius: 1rem; padding: 1.2rem; }
.operator-counts strong, .operator-counts span { display: block; }
.operator-counts strong { color: var(--ink); font-size: 2rem; font-weight: 500; }
.operator-counts span { color: var(--muted); font-size: .9rem; }
.operator-filter { display: flex; align-items: end; flex-wrap: wrap; gap: 1rem; margin: 1.4rem 0; }
.operator-filter .field-wrapper { margin: 0; min-width: 200px; }
.operator-queue-card h2 { font-size: 1.25rem; overflow-wrap: anywhere; }
.operator-queue-card .eyebrow { margin-bottom: .4rem; }
.operator-event-list { list-style: none; padding: 0; margin: 1rem 0; }
.operator-event-list li { border-top: 1px solid var(--border); padding: .9rem 0; }
.operator-event-list strong, .operator-event-list span { display: block; }
.operator-event-list strong { font-weight: 500; }
.operator-event-list span { color: var(--muted); font-size: .85rem; overflow-wrap: anywhere; }
@media (min-width: 992px) and (max-width: 1199.98px) {
  .navbar .nav-link { padding-inline: .45rem !important; font-size: .8rem; }
  .navbar-actions .btn { padding-inline: .7rem; font-size: .8rem; }
  .navbar-brand { margin-right: .7rem; }
}
@media (max-width: 575.98px) {
  .operator-counts { gap: .5rem; }
  .operator-counts > div { padding: .8rem; }
  .operator-counts span { font-size: .8rem; }
  .operator-queue-card { gap: .8rem; }
  .operator-queue-card > div:first-child { width: 100%; }
}
/* First-aid library: readable numbered steps and regional helpline coverage. */
.firstaid-section { padding: 3rem 0 4rem; background: linear-gradient(var(--hero-bg), white 400px); }
.firstaid-heading { display: flex; align-items: end; justify-content: space-between; flex-wrap: wrap; gap: 1.2rem; margin-bottom: 2rem; }
.firstaid-heading h1 { font-size: clamp(2.25rem, 4vw, 3.4rem); letter-spacing: -.055em; }
.firstaid-heading p:last-child { max-width: 42rem; color: var(--muted); margin: .9rem 0 0; }
.firstaid-notice { display: flex; align-items: start; gap: .85rem; padding: 1.2rem; border: 1px solid #BDD4E2; border-radius: 1rem; color: var(--primary-dark); background: #F5FAFD; margin-bottom: 1.6rem; }
.firstaid-notice > .icon { margin-top: .25rem; }
.firstaid-notice p { margin: .4rem 0 0; }
.firstaid-search { display: flex; align-items: end; flex-wrap: wrap; gap: .8rem; margin: 1.8rem 0; }
.firstaid-search .field-wrapper { margin: 0; flex: 1 1 260px; max-width: 540px; }
.firstaid-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.2rem; }
.firstaid-card { display: flex; flex-direction: column; align-items: start; gap: .7rem; padding: 1.6rem; border: 1px solid var(--border); border-radius: 1.2rem; background: white; text-decoration: none; color: var(--text); transition: transform .18s ease, box-shadow .18s ease; }
.firstaid-card:hover { transform: translateY(-3px); box-shadow: var(--shadow); color: var(--text); }
.firstaid-card > .action-icon { margin-bottom: .6rem; }
.firstaid-card h2 { font-size: 1.5rem; letter-spacing: -.035em; margin: 0; }
.firstaid-card > .eyebrow { font-size: .7rem; margin: 0; }
.firstaid-card > p:not(.eyebrow) { color: var(--muted); margin: .2rem 0 .8rem; }
.firstaid-card-link { display: inline-flex; align-items: center; gap: .5rem; margin-top: auto; min-height: 44px; color: var(--primary-dark); font-weight: 500; }
.firstaid-card-date { color: var(--muted); font-size: .8rem; }
.firstaid-library-note { margin-top: 2rem; padding: 1.5rem; border: 1px solid var(--border); border-radius: 1rem; background: var(--bg); color: var(--muted); }
.firstaid-library-note h2 { font-size: 1.35rem; }
.firstaid-library-note p:last-child { margin-bottom: 0; }
.firstaid-reading { max-width: 880px; }
.firstaid-review-line { color: var(--muted); font-size: .85rem; margin-bottom: 1.4rem; }
.firstaid-reading .firstaid-heading h1 { max-width: 40rem; }
.firstaid-caution { padding: 1.3rem; margin: 1.5rem 0; background: var(--teal-soft); border: 1px solid #B7D2C9; border-radius: 1rem; }
.firstaid-caution h2 { font-size: 1.2rem; color: var(--accent-dark); }
.firstaid-caution p { color: var(--accent-dark); margin: 0; }
.firstaid-step-list { list-style: none; padding: 0; display: grid; gap: 1rem; margin: 2rem 0; }
.firstaid-step-list li { display: grid; grid-template-columns: 52px minmax(0, 1fr); align-items: start; gap: 1rem; padding: 1.5rem; background: white; border: 1px solid var(--border); border-radius: 1rem; }
.firstaid-step-number { display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 50%; background: var(--blue-soft); color: var(--primary-dark); font-weight: 600; }
.firstaid-step-list h2 { font-size: 1.35rem; letter-spacing: -.025em; line-height: 1.3; }
.firstaid-step-list p { color: var(--text); margin-bottom: 0; font-size: 1.05rem; line-height: 1.8; }
.firstaid-sources { border-top: 1px solid var(--border); padding-top: 1.5rem; margin: 2rem 0; color: var(--muted); }
.firstaid-sources h2 { font-size: 1.4rem; }
.firstaid-sources ul { padding-left: 1.2rem; }
.firstaid-sources a { display: inline-flex; align-items: center; flex-wrap: wrap; gap: .4rem; min-height: 44px; }
.helpline-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.2rem; align-items: stretch; }
.helpline-card { display: flex; flex-direction: column; align-items: start; padding: 1.5rem; border: 1px solid var(--border); border-radius: 1.2rem; background: white; }
.helpline-card-national { border-color: #9BB5C8; background: #F5FAFD; }
.helpline-card-top { display: flex; align-items: center; justify-content: space-between; gap: .7rem; width: 100%; }
.helpline-number { color: var(--primary-dark); font-size: 3.5rem; letter-spacing: -.05em; margin: 1.4rem 0 .5rem; line-height: 1; }
.helpline-card h2 { font-size: 1.45rem; line-height: 1.25; margin-bottom: .8rem; }
.helpline-card > p:not(.helpline-number) { color: var(--muted); }
.helpline-region { font-size: .85rem; }
.helpline-card > .btn { margin-top: auto; }
.helpline-source { margin-top: 1.3rem; padding-top: .8rem; width: 100%; border-top: 1px solid var(--border); color: var(--muted); font-size: .8rem; }
.helpline-source p { margin: 0; }
.helpline-source a { display: inline-flex; align-items: center; gap: .4rem; min-height: 44px; }
.footer-helplines-link { display: inline-flex; min-height: 44px; align-items: center; color: #E1EDF4; font-size: .85rem; margin-top: .6rem; }
.footer-helplines-link:hover { color: white; }
@media (max-width: 991.98px) {
  .firstaid-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .helpline-grid { grid-template-columns: 1fr; }
}
@media (max-width: 575.98px) {
  .firstaid-section { padding-top: 1.75rem; }
  .firstaid-grid { grid-template-columns: 1fr; }
  .firstaid-heading h1 { font-size: 2.4rem; }
  .firstaid-heading > .action-icon { display: none; }
  .firstaid-step-list li { grid-template-columns: 38px minmax(0, 1fr); padding: 1rem; gap: .8rem; }
  .firstaid-step-number { width: 36px; height: 36px; font-size: .85rem; }
  .firstaid-step-list h2 { font-size: 1.2rem; }
}
/* Shared accessibility and small-screen finishing details. */
.password-control { display: flex; align-items: stretch; }
.password-control > .form-control { min-width: 0; width: 1%; flex: 1; border-radius: .6rem 0 0 .6rem; }
.password-toggle { min-width: 64px; min-height: 48px; border: 1px solid var(--control-border); border-left: 0; border-radius: 0 .6rem .6rem 0; background: var(--blue-soft); color: var(--primary-dark); font-size: .9rem; padding: .5rem .8rem; }
.password-toggle:hover { background: #DDEEF9; }
.no-js .password-control > .form-control { border-radius: .6rem; }
.sos-feedback-close { float: right; margin: -.4rem -.4rem .1rem .5rem; }
.mobile-bar-actions > a[href='tel:112'] { white-space: nowrap; }
.error-page { max-width: 760px; padding-block: 3rem 4rem; }
.error-page h1 { font-size: clamp(2.1rem, 4vw, 3rem); letter-spacing: -.045em; }
.error-page > p:not(.eyebrow) { max-width: 40rem; color: var(--muted); }
.error-actions { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 1.5rem; }
.no-js .navbar-toggler { display: none; }
.no-js .navbar-collapse { display: block; max-height: none; overflow: visible; }
.no-js .site-header { position: static; }
@media (max-width: 991.98px) {
  .no-js .navbar-collapse { flex-basis: 100%; }
}
@media (max-width: 359.98px) {
  .site-header .preview-label { display: none; }
  .mobile-emergency-bar { justify-content: center; }
  .mobile-emergency-bar > p { display: none; }
  .mobile-bar-actions { gap: 1rem; }
  .mobile-bar-actions > a[href='tel:112'] { min-width: 120px; }
  .care-grid { grid-template-columns: 1fr; }
  .action-card { min-height: auto; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### `static/js/site.js`

Small shared enhancements for navigation, error focus and password visibility; no credentials are read.

```javascript
"use strict";

(() => {
  // Keep all navigation links visible if JavaScript or Bootstrap is unavailable.
  if (window.bootstrap?.Collapse) document.documentElement.classList.remove("no-js");

  const summary = document.getElementById("form-error-summary");
  if (summary) {
    summary.focus();
    summary.addEventListener("click", (event) => {
      const link = event.target.closest('a[href^="#"]');
      if (!link) return;
      const field = document.getElementById(link.getAttribute("href").slice(1));
      if (!field || field.type === "hidden") return;
      event.preventDefault();
      let details = field.closest("details");
      while (details) {
        details.open = true;
        details = details.parentElement?.closest("details");
      }
      field.focus();
      field.scrollIntoView({ block: "center", behavior: "instant" });
    });
  }

  const menu = document.getElementById("main-navigation");
  const menuButton = document.querySelector('[aria-controls="main-navigation"]');
  if (menu && menuButton && window.bootstrap?.Collapse) {
    const hideMenu = () => window.bootstrap.Collapse.getOrCreateInstance(menu, { toggle: false }).hide();
    menu.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !menu.classList.contains("show")) return;
      event.preventDefault();
      hideMenu();
      menuButton.focus();
    });
    document.addEventListener("focusin", (event) => {
      if (menu.classList.contains("show") && !menu.contains(event.target) && !menuButton.contains(event.target)) hideMenu();
    });
  }

  document.querySelectorAll("[data-toggle-password]").forEach((button) => {
    const field = document.getElementById(button.getAttribute("aria-controls"));
    if (!field || field.type !== "password") return;
    button.hidden = false;
    button.addEventListener("click", () => {
      const show = field.type === "password";
      field.type = show ? "text" : "password";
      button.textContent = show ? "Hide" : "Show";
      button.setAttribute("aria-label", `${show ? "Hide" : "Show"} ${button.dataset.passwordLabel.toLowerCase()}`);
    });
  });
})();
```

### `static/js/sos.js`

Existing protected SOS capture and copy flow, with non-submitting notice dismissal.

```javascript
"use strict";

(() => {
  const form = document.getElementById("sos-request-form");
  if (form) {
    const triggers = document.querySelectorAll("[data-sos-trigger]");
    const feedback = document.getElementById("sos-feedback");
    const text = document.getElementById("sos-feedback-text");
    const spinner = document.getElementById("sos-spinner");
    const fallback = document.getElementById("sos-fallback");
    const dismiss = document.getElementById("sos-feedback-dismiss");
    let busy = false;
    let requestId = null;
    let originTrigger = null;

    function show(message, loading = false) {
      feedback.hidden = false;
      spinner.hidden = !loading;
      text.textContent = message;
      fallback.hidden = loading;
      if (dismiss) dismiss.hidden = loading;
      triggers.forEach((trigger) => trigger.setAttribute("aria-disabled", String(loading)));
      feedback.focus();
    }

    function fail(message) {
      busy = false;
      show(message);
    }

    if (dismiss) dismiss.addEventListener("click", () => {
      // Hiding a failure notice does not cancel, delete or resend a request.
      feedback.hidden = true;
      originTrigger?.focus();
    });

    async function save(latitude, longitude) {
      const body = new FormData(form);
      body.set("request_id", requestId);
      body.set("latitude", latitude.toFixed(6));
      body.set("longitude", longitude.toFixed(6));
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 15000);
      show("Saving your location. No one is being contacted automatically.", true);
      try {
        const response = await fetch(form.action, {
          method: "POST", body, credentials: "same-origin",
          headers: { Accept: "application/json" }, signal: controller.signal,
        });
        if (!response.ok || response.redirected) throw new Error("Save unconfirmed");
        const data = await response.json();
        if (typeof data.url !== "string" || !/^\/emergency\/sos\/[0-9a-f-]+\/$/i.test(data.url)) {
          throw new Error("Invalid redirect");
        }
        window.location.assign(data.url);
      } catch {
        fail("We couldn't confirm saving. Check Recently saved on the SOS page, or tap SOS to retry. Retrying this button uses the same request ID.");
      } finally {
        clearTimeout(timer);
      }
    }

    triggers.forEach((trigger) => trigger.addEventListener("click", (event) => {
      // Preserve ordinary open-in-new-tab behavior; GET never creates a request.
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (busy) return;
      originTrigger = trigger;
      if (!window.isSecureContext || !navigator.geolocation || !window.crypto?.randomUUID) {
        fail("Automatic location capture is unavailable. Use the SOS page to enter coordinates, or call 112.");
        return;
      }
      busy = true;
      requestId = requestId || window.crypto.randomUUID();
      show("Finding your location. Your browser may ask for permission. For urgent help, call 112.", true);
      try {
        navigator.geolocation.getCurrentPosition((position) => {
          const { latitude, longitude } = position.coords;
          if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
              Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
            fail("We couldn't read valid coordinates. Open the SOS page for manual entry or call 112.");
            return;
          }
          save(latitude, longitude);
        }, (error) => {
          const errors = {
            1: "Location permission was declined.",
            2: "Your location is unavailable right now.",
            3: "Finding your location took too long.",
          };
          fail((errors[error.code] || "Location capture failed.") + " Open the SOS page for manual entry, or call 112.");
        }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
      } catch {
        fail("Location capture failed. Open the SOS page for manual entry, or call 112.");
      }
    }));
  }

  const copyButton = document.getElementById("copy-sos-message");
  const message = document.getElementById("sos-message");
  const copyFeedback = document.getElementById("copy-feedback");
  if (copyButton && message) {
    copyButton.hidden = false;
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(message.value);
        copyFeedback.textContent = "Message copied. Paste it into your chosen app and send it yourself.";
      } catch {
        message.focus();
        message.select();
        copyFeedback.textContent = "Copy is unavailable. The message is selected; use your device's Copy command.";
      }
    });
  }
})();
```

### `templates/400.html`

Bad-request recovery page.

```html
{% extends 'base.html' %}
{% block title %}Request could not be read | MEDTAP{% endblock %}
{% block content %}<section class="container error-page"><p class="eyebrow">Request could not be read · 400</p><h1>Please try<br>that page again.</h1><p>We couldn't read this request. Return home and open the page you need.</p><div class="error-actions"><a class="btn btn-primary" href="{% url 'core:home' %}">Go to home</a><a class="btn btn-outline-primary" href="tel:112">Call 112</a></div></section>{% endblock %}
```

### `templates/403.html`

Permission-denied recovery page without revealing private details.

```html
{% extends 'base.html' %}
{% block title %}Access restricted | MEDTAP{% endblock %}
{% block content %}<section class="container error-page"><p class="eyebrow">Access restricted · 403</p><h1>This page needs<br>the right account.</h1><p>You may need to sign in with an account allowed to use this page. Your private records are protected.</p><div class="error-actions"><a class="btn btn-primary" href="{% url 'core:home' %}">Go to home</a><a class="btn btn-outline-primary" href="{% url 'accounts:login' %}">Sign in</a><a class="btn btn-outline-primary" href="tel:112">Call 112</a></div></section>{% endblock %}
```

### `templates/404.html`

Missing-page recovery with home and directory links.

```html
{% extends 'base.html' %}
{% block title %}Page unavailable | MEDTAP{% endblock %}
{% block content %}<section class="container error-page"><p class="eyebrow">Page unavailable · 404</p><h1>Let's find<br>a way forward.</h1><p>This page may have moved, may not exist, or may be unavailable to your account.</p><div class="error-actions"><a class="btn btn-primary" href="{% url 'core:home' %}">Go to home</a><a class="btn btn-outline-primary" href="{% url 'facilities:nearby' %}">Find care</a><a class="btn btn-outline-primary" href="tel:112">Call 112</a></div></section>{% endblock %}
```

### `templates/500.html`

Generic server-error page with direct emergency help.

```html
{% extends 'base.html' %}
{% block title %}Something went wrong | MEDTAP{% endblock %}
{% block content %}<section class="container error-page"><p class="eyebrow">Something went wrong · 500</p><h1>We couldn't load<br>this page.</h1><p>Please try again in a moment. For urgent emergency assistance, call 112 directly.</p><div class="error-actions"><a class="btn btn-primary" href="{% url 'core:home' %}">Go to home</a><a class="btn btn-outline-primary" href="tel:112">Call 112</a></div></section>{% endblock %}
```

### `core/error_test_urls.py`

Only isolated tests load these deliberate exception routes.

```python
"""Only used by isolated error-page tests; not included by config.urls."""
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.urls import path

from config.urls import urlpatterns as application_urls


def error_view(request, code):
    errors = {
        400: SuspiciousOperation, 403: PermissionDenied,
        404: Http404, 500: RuntimeError,
    }
    raise errors[code]("PRIVATE diagnostic text must not reach a public error page")


urlpatterns = [path("_ui-test-error/<int:code>/", error_view), *application_urls]
```

### `core/test_ui.py`

Nine tests cover shared markup, form relationships, escaped profile text, navigation and actual Django error handlers.

```python
from contextlib import nullcontext
from html import unescape
from html.parser import HTMLParser

from django import forms
from django.template.loader import render_to_string
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import MedicalProfile, User


class Markup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


class SharedUiTests(TestCase):
    def test_public_pages_have_one_main_landmark_named_navigation_and_no_duplicate_ids(self):
        for name in ("core:home", "accounts:login", "accounts:register", "facilities:nearby", "firstaid:guide_list", "firstaid:helplines"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            markup = Markup(response.content.decode())
            self.assertEqual(sum(tag == "main" for tag, _ in markup.nodes), 1)
            self.assertTrue(any(tag == "nav" and a.get("aria-label") == "Main navigation" for tag, a in markup.nodes))
            ids = [a["id"] for _, a in markup.nodes if "id" in a]
            self.assertEqual(len(ids), len(set(ids)), name)
            self.assertNotContains(response, 'id="feature-preview"')

    def test_password_controls_are_optional_buttons_with_existing_input_targets(self):
        for name, count in (("accounts:login", 1), ("accounts:register", 2)):
            response = self.client.get(reverse(name))
            nodes = Markup(response.content.decode()).nodes
            passwords = {a["id"] for tag, a in nodes if tag == "input" and a.get("type") == "password"}
            buttons = [a for tag, a in nodes if tag == "button" and "data-toggle-password" in a]
            self.assertEqual(len(buttons), count)
            for button in buttons:
                self.assertEqual(button["type"], "button")
                self.assertIn(button["aria-controls"], passwords)
                self.assertIn("hidden", button)

    def test_invalid_registration_errors_reference_real_fields_and_descriptions(self):
        response = self.client.post(reverse("accounts:register"), {"username": "", "first_name": ""})
        nodes = Markup(response.content.decode()).nodes
        ids = {a["id"] for _, a in nodes if "id" in a}
        fields = [a for tag, a in nodes if tag == "input" and a.get("aria-invalid") == "true"]
        self.assertTrue(fields)
        for field in fields:
            described = field.get("aria-describedby", "").split()
            self.assertTrue(described)
            self.assertTrue(set(described).issubset(ids), field)
            self.assertTrue(any(tag == "a" and a.get("href") == "#" + field["id"] for tag, a in nodes))
        self.assertIn("Your account hasn't been created", unescape(response.content.decode()))

    def test_hidden_field_errors_do_not_link_to_unfocusable_inputs(self):
        class DemoForm(forms.Form):
            token = forms.IntegerField(widget=forms.HiddenInput)
        form = DemoForm({"token": "bad"})
        self.assertFalse(form.is_valid())
        html = render_to_string("partials/form_errors.html", {"form": form})
        self.assertIn("Reload this page", html)
        self.assertNotIn('href="#id_token"', html)
        self.assertNotIn("Token:", html)

    def test_home_service_cards_all_navigate_to_implemented_pages(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(len(response.context["quick_actions"]), 6)
        self.assertTrue(all(card.get("href") and card.get("status") for card in response.context["quick_actions"]))
        self.assertNotContains(response, "data-bs-toggle=\"modal\"")

    def test_transport_navigation_marks_current_page(self):
        user = User.objects.create_user(username="fake-ui-user")
        self.client.force_login(user)
        response = self.client.get(reverse("emergency:ambulance_start"))
        self.assertTrue(any(tag == "a" and a.get("href") == reverse("emergency:ambulance_start")
                            and a.get("aria-current") == "page" for tag, a in Markup(response.content.decode()).nodes))

    def test_profile_large_unbroken_content_stays_escaped(self):
        user = User.objects.create_user(username="fake-ui-profile")
        MedicalProfile.objects.create(user=user, allergies="<script>" + "A" * 300 + "</script>")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertNotContains(response, "<script>AAA")
        self.assertContains(response, "&lt;script&gt;AAA")


@override_settings(DEBUG=False, ROOT_URLCONF="core.error_test_urls", ALLOWED_HOSTS=["testserver"])
class ErrorPageTests(TestCase):
    def test_error_pages_keep_their_status_and_hide_diagnostics(self):
        client = Client(raise_request_exception=False)
        for code in (400, 403, 404, 500):
            logger = "django.security.SuspiciousOperation" if code == 400 else "django.request"
            captured_log = self.assertLogs(logger, level="WARNING") if code != 404 else nullcontext()
            with self.subTest(code=code), captured_log:
                response = client.get(f"/_ui-test-error/{code}/")
                self.assertEqual(response.status_code, code)
                self.assertContains(response, 'href="tel:112"', status_code=code)
                self.assertContains(response, 'id="main-content"', status_code=code)
                self.assertNotContains(response, "PRIVATE diagnostic text", status_code=code)

    def test_plain_unknown_url_uses_branded_404(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertContains(response, "Let's find", status_code=404)
```

### `core/ui_frontend_tests.cjs`

Nine dependency-free checks exercise keyboard/error/password behavior and selected real theme colours.

```javascript
// No browser credentials or form values are read by these isolated UI checks.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static/js/site.js"), "utf8");
const css = fs.readFileSync(path.join(__dirname, "..", "static/css/theme.css"), "utf8");

function element() {
  return { events: {}, attributes: {}, hidden: true, dataset: {}, classes: new Set(),
    addEventListener(name, callback) { this.events[name] = callback; },
    getAttribute(name) { return this.attributes[name]; },
    setAttribute(name, value) { this.attributes[name] = value; },
    focus() { this.focused = true; },
    scrollIntoView(options) { this.scrolled = options; },
  };
}
function fixture({ bootstrap = true, withSummary = true, passwordTarget = true } = {}) {
  const summary = element(), menu = element(), menuButton = element(), field = element();
  const password = element(), toggle = element(), html = element();
  field.type = "text"; password.type = "password";
  const outer = { open: false, parentElement: null };
  const inner = { open: false, parentElement: { closest: () => outer } };
  field.closest = () => inner;
  menu.classes.add("show");
  menu.classList = { contains: (name) => menu.classes.has(name) };
  html.classes.add("no-js");
  html.classList = { remove: (name) => html.classes.delete(name) };
  menu.contains = (node) => node === menu;
  menuButton.contains = (node) => node === menuButton;
  toggle.attributes["aria-controls"] = "id_password";
  toggle.dataset.passwordLabel = "Password confirmation";
  const nodes = { "form-error-summary": withSummary ? summary : null, "main-navigation": menu,
    "id_field": field, "id_password": passwordTarget ? password : null };
  let hideCount = 0;
  const documentEvents = {};
  vm.runInNewContext(code, {
    window: bootstrap ? { bootstrap: { Collapse: {
      getOrCreateInstance: () => ({ hide() { hideCount += 1; menu.classes.delete("show"); } }),
    } } } : {},
    document: {
      documentElement: html, getElementById: (id) => nodes[id],
      querySelector: () => menuButton, querySelectorAll: () => [toggle],
      addEventListener: (name, callback) => { documentEvents[name] = callback; },
    },
  });
  return { summary, menu, menuButton, field, password, toggle, html, inner, outer,
    documentEvents, get hideCount() { return hideCount; } };
}

let count = 0;
function test(name, run) { run(); count += 1; console.log(`PASS ${name}`); }
test("navigation keeps the no-script fallback until Bootstrap is available", () => {
  assert.equal(fixture({ bootstrap: false }).html.classes.has("no-js"), true);
  assert.equal(fixture().html.classes.has("no-js"), false);
});
test("error summaries focus on load and open nested details before field focus", () => {
  const state = fixture();
  assert.equal(state.summary.focused, true);
  const link = { getAttribute: () => "#id_field" };
  state.summary.events.click({ target: { closest: () => link }, preventDefault() {} });
  assert.equal(state.inner.open, true);
  assert.equal(state.outer.open, true);
  assert.equal(state.field.focused, true);
  assert.equal(state.field.scrolled.behavior, "instant");
});
test("missing and hidden error targets are ignored safely", () => {
  const state = fixture(); state.field.type = "hidden";
  state.summary.events.click({ target: { closest: () => ({ getAttribute: () => "#id_field" }) }, preventDefault() {} });
  assert.equal(state.field.focused, undefined);
  state.summary.events.click({ target: { closest: () => ({ getAttribute: () => "#missing" }) }, preventDefault() {} });
});
test("Escape closes expanded navigation and returns focus to its button", () => {
  const state = fixture();
  state.menu.events.keydown({ key: "Escape", preventDefault() {} });
  assert.equal(state.hideCount, 1);
  assert.equal(state.menuButton.focused, true);
  state.menu.events.keydown({ key: "Escape", preventDefault() {} });
  assert.equal(state.hideCount, 1);
});
test("tabbing into page content closes the menu without stealing focus", () => {
  const state = fixture();
  state.documentEvents.focusin({ target: state.menu });
  assert.equal(state.hideCount, 0);
  state.documentEvents.focusin({ target: state.field });
  assert.equal(state.hideCount, 1);
  assert.equal(state.menuButton.focused, undefined);
});
test("password buttons change visibility and accessible labels without reading values", () => {
  const state = fixture();
  assert.equal(state.toggle.hidden, false);
  state.toggle.events.click();
  assert.equal(state.password.type, "text");
  assert.equal(state.toggle.attributes["aria-label"], "Hide password confirmation");
  state.toggle.events.click();
  assert.equal(state.password.type, "password");
  assert.equal(state.toggle.attributes["aria-label"], "Show password confirmation");
});
test("pages without a summary or matching password target remain usable", () => {
  assert.equal(fixture({ withSummary: false, passwordTarget: false }).toggle.hidden, true);
});

function color(name) {
  const match = css.match(new RegExp(`--${name}:\\s*(#[0-9a-fA-F]{6})\\s*;`));
  assert.ok(match, name);
  return match[1];
}
function luminance(hex) {
  const channels = [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255)
    .map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
}
function contrast(first, second) {
  const [low, high] = [luminance(first), luminance(second)].sort((a, b) => a - b);
  return (high + .05) / (low + .05);
}
test("selected text palette pairs meet 4.5:1 contrast", () => {
  const pairs = [["text", "surface"], ["muted", "surface"], ["muted", "hero-bg"],
    ["primary-dark", "blue-soft"], ["accent-dark", "teal-soft"], ["surface", "primary-dark"], ["surface", "emergency"]];
  for (const [foreground, background] of pairs) {
    const ratio = contrast(color(foreground), color(background));
    assert.ok(ratio >= 4.5, `${foreground}/${background}: ${ratio}`);
  }
});
test("control borders have at least 3:1 contrast on the page surface", () => {
  assert.ok(contrast(color("control-border"), color("surface")) >= 3);
});
console.log(`${count} shared UI checks passed.`);
```

### `emergency/frontend_tests.cjs`

Twelve SOS checks, including hiding a failed notice without sending or altering its retry identifier.

```javascript
// Run with Node. Mocks never request real GPS, contact anybody, or send an SMS.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static", "js", "sos.js"), "utf8");
const uuid = "00000000-0000-4000-8000-000000000001";
const detail = `/emergency/sos/${uuid}/`;
const settle = () => new Promise(setImmediate);

function element() {
  return { hidden: true, value: "message & location", textContent: "", attributes: {}, events: {},
    addEventListener(name, callback) { this.events[name] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; },
    focus() { this.focused = true; }, select() { this.selected = true; },
  };
}
function fixture({ guest = false, secure = true, fetchImpl, clipboardFails = false } = {}) {
  const nodes = {};
  for (const id of ["sos-request-form", "sos-feedback", "sos-feedback-text", "sos-spinner", "sos-fallback", "sos-feedback-dismiss", "copy-sos-message", "sos-message", "copy-feedback"]) nodes[id] = element();
  nodes["sos-request-form"].action = "/emergency/sos/create/";
  const triggers = [element(), element()];
  const captures = [], posts = [], navigations = [], copies = [];
  let idCalls = 0;
  class FakeFormData {
    constructor() { this.values = new Map([["csrfmiddlewaretoken", "isolated-test-token"]]); }
    set(key, value) { this.values.set(key, value); }
    get(key) { return this.values.get(key); }
  }
  vm.runInNewContext(code, {
    document: { getElementById: (id) => guest && id === "sos-request-form" ? null : nodes[id], querySelectorAll: () => triggers },
    window: { isSecureContext: secure, crypto: { randomUUID: () => { idCalls += 1; return uuid; } }, location: { assign: (url) => navigations.push(url) } },
    navigator: { geolocation: { getCurrentPosition: (ok, fail, options) => captures.push({ ok, fail, options }) },
      clipboard: { async writeText(text) { if (clipboardFails) throw Error("denied"); copies.push(text); } } },
    FormData: FakeFormData, AbortController, setTimeout, clearTimeout,
    fetch: async (url, options) => {
      posts.push({ url, options });
      if (fetchImpl) return fetchImpl();
      return { ok: true, redirected: false, json: async () => ({ url: detail, created: true }) };
    },
  });
  return { nodes, triggers, captures, posts, navigations, copies,
    click: (index = 0, event = {}) => triggers[index].events.click({ preventDefault() {}, ...event }),
    success: (lat = 0, lon = 77.59000012) => captures.at(-1).ok({ coords: { latitude: lat, longitude: lon } }),
    get idCalls() { return idCalls; },
  };
}

(async () => {
  let count = 0;
  async function test(name, run) { await run(); count += 1; console.log(`PASS ${name}`); }
  await test("guest links keep their normal login destination", () => {
    const state = fixture({ guest: true });
    assert.equal(state.triggers[0].events.click, undefined);
    assert.equal(state.captures.length, 0);
  });
  await test("capture starts on a tap only and duplicate desktop/mobile taps are ignored", () => {
    const state = fixture();
    assert.equal(state.captures.length, 0);
    state.click(0); state.click(1);
    assert.equal(state.captures.length, 1);
    assert.equal(state.captures[0].options.timeout, 10000);
    assert.equal(state.captures[0].options.maximumAge, 0);
    assert.equal(state.nodes["sos-spinner"].hidden, false);
    assert.equal(state.triggers[1].attributes["aria-disabled"], "true");
  });
  await test("a successful capture includes CSRF, rounds coordinates and navigates to the owned result", async () => {
    const state = fixture(); state.click(); state.success(); await settle();
    assert.equal(state.posts.length, 1);
    const options = state.posts[0].options;
    assert.equal(options.method, "POST");
    assert.equal(options.body.get("csrfmiddlewaretoken"), "isolated-test-token");
    assert.equal(options.body.get("latitude"), "0.000000");
    assert.equal(options.body.get("longitude"), "77.590000");
    assert.equal(options.body.get("request_id"), uuid);
    assert.deepEqual(state.navigations, [detail]);
  });
  await test("denial, unavailability and timeout reveal the manual fallback without posting", () => {
    for (const errorCode of [1, 2, 3, 99]) {
      const state = fixture(); state.click(); state.captures[0].fail({ code: errorCode });
      assert.equal(state.posts.length, 0);
      assert.equal(state.nodes["sos-spinner"].hidden, true);
      assert.equal(state.nodes["sos-fallback"].hidden, false);
      assert.match(state.nodes["sos-feedback-text"].textContent, /manual entry/);
    }
  });
  await test("nonfinite and out-of-range fixes never reach the server", () => {
    for (const [lat, lon] of [[NaN, 0], [0, Infinity], [91, 0], [0, -181]]) {
      const state = fixture(); state.click(); state.success(lat, lon);
      assert.equal(state.posts.length, 0);
      assert.match(state.nodes["sos-feedback-text"].textContent, /valid coordinates/);
    }
  });
  await test("an uncertain network save keeps the UUID for a safe retry", async () => {
    let attempt = 0;
    const state = fixture({ fetchImpl: () => {
      attempt += 1;
      if (attempt === 1) throw Error("offline");
      return { ok: true, redirected: false, json: async () => ({ url: detail }) };
    } });
    state.click(); state.success(); await settle();
    assert.match(state.nodes["sos-feedback-text"].textContent, /couldn't confirm/);
    state.click(); state.success(); await settle();
    assert.equal(state.posts.length, 2);
    assert.equal(state.posts[0].options.body.get("request_id"), state.posts[1].options.body.get("request_id"));
    assert.equal(state.idCalls, 1);
    assert.deepEqual(state.navigations, [detail]);
  });
  await test("expired login and non-success responses never pretend a save succeeded", async () => {
    for (const response of [{ ok: false }, { ok: true, redirected: true }]) {
      const state = fixture({ fetchImpl: () => response });
      state.click(); state.success(); await settle();
      assert.equal(state.navigations.length, 0);
      assert.match(state.nodes["sos-feedback-text"].textContent, /Recently saved/);
    }
  });
  await test("untrusted redirect URLs cannot navigate away", async () => {
    const state = fixture({ fetchImpl: () => ({ ok: true, json: async () => ({ url: "https://example.invalid/" }) }) });
    state.click(); state.success(); await settle();
    assert.equal(state.navigations.length, 0);
  });
  await test("insecure contexts and modified clicks do not capture GPS", () => {
    const state = fixture({ secure: false }); state.click();
    assert.equal(state.captures.length, 0);
    assert.match(state.nodes["sos-feedback-text"].textContent, /Automatic location capture is unavailable/);
    const modified = fixture(); modified.click(0, { ctrlKey: true });
    assert.equal(modified.captures.length, 0);
  });
  await test("copying only writes the message to the clipboard", async () => {
    const state = fixture(); await state.nodes["copy-sos-message"].events.click();
    assert.deepEqual(state.copies, [state.nodes["sos-message"].value]);
    assert.equal(state.posts.length, 0);
    assert.match(state.nodes["copy-feedback"].textContent, /send it yourself/);
  });
  await test("clipboard denial selects the message and explains manual copy", async () => {
    const state = fixture({ clipboardFails: true }); await state.nodes["copy-sos-message"].events.click();
    assert.equal(state.nodes["sos-message"].selected, true);
    assert.match(state.nodes["copy-feedback"].textContent, /Copy command/);
  });
  await test("hiding a failed SOS notice returns focus without sending or changing the retry ID", () => {
    const state = fixture(); state.click(1);
    assert.equal(state.nodes["sos-feedback-dismiss"].hidden, true);
    state.captures[0].fail({ code: 1 });
    assert.equal(state.nodes["sos-feedback-dismiss"].hidden, false);
    state.nodes["sos-feedback-dismiss"].events.click();
    assert.equal(state.nodes["sos-feedback"].hidden, true);
    assert.equal(state.triggers[1].focused, true);
    assert.equal(state.posts.length, 0);
    state.click(1);
    assert.equal(state.idCalls, 1);
  });
  console.log(`${count} SOS frontend checks passed.`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
```

## Stop here

Step 8 is complete. After your **next**, Step 9 will review and strengthen
the main model/view tests and project verification. Deployment is Step 10.
