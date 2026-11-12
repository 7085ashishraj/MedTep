# Step 7 — First-aid guides and Indian emergency helplines

This step is implemented in the workspace. Complete the earlier steps first.
The guide below contains full current source files, exact commands, verification
notes and viva explanations. Use it for the current first-aid, navigation, footer,
home-action and stylesheet files; earlier guides preserve their own snapshots.

## What is available

- Five public adult educational guides: CPR, severe external bleeding, thermal
  burns/scalds, choking and recovery position.
- Searchable cards, numbered readable steps, urgent advice, scope warnings,
  primary/supporting source links and explicit review metadata.
- A public page for 112, 108 and 102, with direct call links and coverage labels.
- Django admin editing of guides/ordered steps and helpline source metadata.
- Read-only APIs for the library, individual steps and helplines.

**Sources were checked on 12 November 2026. Clinical review of MEDTAP's summaries
is not recorded.** Those statements are different and are displayed separately.
These brief summaries do not replace first-aid training, professional care or an
emergency dispatcher. The seeded guidance is for adults aged 18+, with important
exceptions stated on the page. No actual test calls were made.

[FIRST_AID_SOURCES.md](FIRST_AID_SOURCES.md) records the full source provenance,
scope, localisation and update responsibilities. Linked organisations do not
endorse MEDTAP. UK source articles may refer to 999/111; our emergency shortcuts
use India's 112, explicitly explained in the UI.

## Folder structure for this step

```text
MEDTAP/
├── FIRST_AID_SOURCES.md
├── firstaid/
│   ├── validators.py             # HTTPS references and non-future check dates
│   ├── models.py                 # audience, source-check metadata and headings
│   ├── content.py                # original summaries and fixed evidence date
│   ├── services.py               # publication gates and public data shapes
│   ├── forms.py                  # validated library search/page parameters
│   ├── views.py                  # consistent read-only HTML and API views
│   ├── urls.py
│   ├── admin.py                  # guide steps inline and source metadata
│   ├── tests.py                  # 28 new Django tests
│   ├── migrations/
│   │   └── 0002_emergencyhelpline_is_nationwide_and_more.py
│   └── management/
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── seed_firstaid.py
├── core/views.py                 # actual first-aid/helpline quick actions
├── templates/
│   ├── firstaid/
│   │   ├── guide_list.html
│   │   ├── guide_detail.html
│   │   └── helplines.html
│   └── partials/
│       ├── firstaid_notice.html
│       ├── navbar.html
│       └── footer.html
└── static/css/theme.css          # complete current theme
```

No new Python dependency, secret, JavaScript module or API key is required.
The existing Django templates, Bootstrap and icon sprite supply the UI. There
are no copied medical diagrams or AI-generated anatomy illustrations.

## Exact commands — PowerShell

Run from MEDTAP in VS Code:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_firstaid
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test firstaid emergency accounts facilities
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The migration and seed are already applied in your workspace. The first seed
created **5 guides and 3 helpline references**. A repeat run creates zero when
all those entries already exist. It preserves edited summaries, steps, dates,
unpublished guides and inactive helpline entries; it does not reset or republish
them. The evidence date is a fixed constant, not the date the command runs.

Expect **169 Django tests passing** (the previous 141 plus 28 first-aid tests).
The existing 28 JavaScript checks are unchanged; these new pages work without a
new script. Their existing commands remain:

```powershell
node emergency/ambulance_frontend_tests.cjs
node emergency/frontend_tests.cjs
node facilities/frontend_tests.cjs
```

Do not start a second server on an occupied port. Use the existing development
server, or stop it with Ctrl+C before restarting. No `.env` change is needed.
Verify migration state if needed:

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations firstaid
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Both firstaid migrations should be `[X]`; drift checking should report
`No changes detected`. The migration adds metadata/headings and validation
definitions. It keeps existing content. Old entries without required source-check
metadata remain stored but do not become public automatically.

## What to see in your browser

1. Open [First-aid library](http://127.0.0.1:8000/first-aid/). It is public, so no
   login is needed. You should see five adult guide cards.
2. Search for `CPR` and choose **Find guide**. One card should match. Empty searches
   browse the catalogue, and an unknown term gives a useful empty state.
3. Open the CPR card. It shows adult scope, urgent advice, review metadata, numbered
   step cards and links to the underlying guidance. It says clinical review of
   our summary is not recorded; the source-check date does not imply otherwise.
4. Check the choking, bleeding, burns and recovery-position pages. These are short
   educational summaries with explicit limitations, not a diagnosis or complete
   training course. Do not delay real emergency help to browse the app.
5. Open [Helplines](http://127.0.0.1:8000/first-aid/helplines/). The order is 112,
   108, 102. The two latter cards say **State/UT dependent**. The 102 card describes
   patient transport, not a guaranteed nationwide emergency ambulance.
6. On a phone, cards stack and step text stays readable. The Call 112 shortcut
   remains available. Viewing a page does not place a call. A `tel:` link needs a
   compatible calling device/app and the user's action.

The [MHA ERSS page](https://www.mha.gov.in/emergency-response-support-system-erss)
supports the nationwide 112 description. The
[NHM transport reference](https://nhm.gov.in/nhm/index1.php?lang=1&level=2&lid=189&sublinkid=1217)
distinguishes emergency response from basic patient transport. It does not prove
both 108 and 102 work identically in every state. This directory check is not a
test of local connectivity, capacity or response times.

## Admin management

Use an existing superuser. If you have not created one, do so interactively:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Open [Django admin](http://127.0.0.1:8000/admin/) and the **Firstaid** section.
Ordinary registration does not grant content-editing rights.

- **First aid guides:** edit title, slug, adult scope, summary, urgent advice,
  warnings, source links and publication state. Steps are inlines with position,
  heading and plain-text instruction. Use consecutive positions starting at 1.
- Publishing requires an HTTPS source URL and an actual source-check date. The
  admin also requires at least one step and rejects gaps/duplicate step positions.
- Leave **Reviewed on** empty unless a qualified clinician actually reviewed this
  app's wording. Do not copy the source organisation's review date into it.
- **Emergency helplines:** edit official references, region/coverage description,
  nationwide flag, source URL, source-check date and active flag. Active entries
  need source metadata. Do not infer nationwide coverage from a regional number.

Check/review dates cannot be in the future, and source URLs cannot contain login
credentials or a non-HTTPS scheme. Public read helpers re-check URL safety too.
Publishing is an editorial action, not an automated clinical approval process.
Source changes and summary edits need deliberate rechecking by the maintainer;
the seed command does not monitor source updates or expire content automatically.

## Read-only APIs

| Endpoint | Response |
| --- | --- |
| `GET /first-aid/api/guides/` | Catalogue with `count`, `next`, `previous`, `results` |
| `GET /first-aid/api/guides/adult-cpr/` | One guide with ordered step data |
| `GET /first-aid/api/helplines/` | Number, region, coverage, source check and `tel:` URL |

The list accepts optional `q` (maximum 120 characters) and positive `page`, with
20 results per page. HTML and API use the same validation/publication helper.
Missing/unpublished entries return 404, invalid search parameters return 400 and
POST returns 405. APIs are intentionally public read-only exceptions to the
project's default authenticated DRF permission; private accounts/SOS stay protected.

Each guide includes `source_checked_on`, `clinical_reviewed_on`, audience, urgent
advice, warnings and source links. The clinical date is JSON null for the seeded
release. The detail endpoint adds steps with position/heading/instruction. Render
instruction text as plain text, as our Django templates do. Metadata does not
guarantee that guidance will remain current without ongoing editorial review.

```powershell
$guideResult = Invoke-RestMethod 'http://127.0.0.1:8000/first-aid/api/guides/adult-cpr/'
$guideResult.title
$guideResult.clinical_reviewed_on
$guideResult.steps | Select-Object position, heading
$numberResult = Invoke-RestMethod 'http://127.0.0.1:8000/first-aid/api/helplines/'
$numberResult.results | Select-Object number, name, region, is_nationwide
```

## Viva notes

**Content and presentation are separate.** Models hold editable content and
evidence metadata; templates render cards and numbered steps. `content.py` is a
repeatable initial content batch, not hardcoded template paragraphs. The database
becomes the source of truth after admin edits.

**Publication gates.** A public guide needs the publish flag, a non-future source
check, a safe HTTPS source and at least one step. Drafts and empty/unverified
entries stay out of HTML and JSON alike. Helplines need the active flag, a valid
check date, a safe source and a valid non-placeholder number. Source link safety
does not automatically establish medical authority: editors still choose and
actually check authoritative references. Clinical-review dates are distinct.

**Validation at several boundaries.** Model validation covers dates and URLs;
admin inline formsets cover complete, consecutive steps; forms cover query/page
parameters. Public services defensively hide malformed source links, even if a
direct database write bypassed normal model validation. The templates auto-escape
all content. There is no `safe` HTML rendering of medical instructions.

**A safe, idempotent seed.** One atomic transaction creates missing guides, steps
and helplines. Validation failure rolls back the new batch. Existing slugs and
number/region pairs are preserved instead of overwritten. A repeat run never
pretends a new source review took place. The fixed check date is intentional.

**Small-catalogue design.** The helper prefetches steps, validates source URLs and
returns a small Python list shared by HTML/API. This is appropriate for five
educational guides; pagination limits response size, not candidate scanning. For
a large editorial catalogue, optimise the validated-publication representation
and query plan rather than assuming this is an indexed full-text search engine.

**Privacy and availability.** No login, medical profile, location request, outgoing
message, live call or transport request is needed to read a guide. The text is
stored in SQLite and the core UI assets are local. External reference pages and
Google Fonts may need internet, with system-font fallbacks for the latter. This
is still a Django website, not an offline-installed mobile first-aid app.

## Verification

- 169 Django tests passed. The 28 new tests cover source/date validation,
  publication defaults/gates, seed rollback/preservation, ordered steps, public
  APIs, HTML escaping, regional coverage labels, search/pagination and admin rules.
- A focused 28-test firstaid run passed again after the reading-layout and
  helpline-priority adjustments. Existing JavaScript was not changed by this step.
- System checks, icon-sprite references and migration-drift checks pass.
- Browser review confirmed search → guide navigation, numbered phone steps,
  explicit clinical-review status, desktop helpline cards and no horizontal
  overflow. The current helpline page is left open for you to review.
- No calls were placed and no clinician reviewed the app summaries during this
  task. Software test success is not medical validation.

## Complete code, file by file

Create parent folders as needed. Replace each file below in full. Empty package
markers are intentional. Keep the existing base, settings and other app files
from prior steps. Full medical provenance is in FIRST_AID_SOURCES.md.

### `firstaid/validators.py`

Reusable HTTPS-source and date checks.

```python
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone


def validate_https_source(value):
    URLValidator(schemes=["https"])(value)
    parsed = urlsplit(value)
    if parsed.username or parsed.password:
        raise ValidationError("Source links must not contain login credentials.")


def validate_not_future(value):
    if value > timezone.localdate():
        raise ValidationError("A check or review date cannot be in the future.")
```

### `firstaid/models.py`

Existing content models plus audience, source-check metadata, headings and coverage.

```python
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from common.models import TimeStampedModel
from django.core.exceptions import ValidationError

from .validators import validate_https_source, validate_not_future


class FirstAidGuide(TimeStampedModel):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    summary = models.TextField()
    audience = models.CharField(max_length=100, default="Adults (18 years and over)")
    urgent_advice = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    source_url = models.URLField(blank=True, validators=[validate_https_source])
    supporting_source_url = models.URLField(blank=True, validators=[validate_https_source])
    source_checked_on = models.DateField(
        null=True, blank=True, validators=[validate_not_future],
        help_text="Date the linked sources were checked; not a clinical review.",
    )
    reviewed_on = models.DateField(
        null=True, blank=True, validators=[validate_not_future],
        help_text="Only enter a date if a qualified clinician actually reviewed this app's text.",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["title", "pk"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.is_published:
            errors = {}
            if not self.source_url:
                errors["source_url"] = "A published guide needs an authoritative source link."
            if not self.source_checked_on:
                errors["source_checked_on"] = "Record when the source was actually checked."
            if errors:
                raise ValidationError(errors)


class FirstAidStep(models.Model):
    guide = models.ForeignKey(
        FirstAidGuide, on_delete=models.CASCADE, related_name="steps",
    )
    position = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    heading = models.CharField(max_length=120, blank=True)
    instruction = models.TextField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["guide", "position"], name="unique_position_per_guide",
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1), name="firstaid_positive_position",
            ),
        ]

    def __str__(self):
        return f"{self.guide.title}: step {self.position}"


class EmergencyHelpline(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(
        max_length=16,
        validators=[RegexValidator(r"\A\+?[0-9]{2,15}\Z", "Enter 2 to 15 digits; optional +.")],
    )
    region = models.CharField(max_length=100, help_text="Country, state, or service area.")
    description = models.TextField(blank=True)
    is_nationwide = models.BooleanField(default=False)
    source_url = models.URLField(blank=True, validators=[validate_https_source])
    verified_on = models.DateField(
        null=True, blank=True, validators=[validate_not_future],
        help_text="Date the official source was checked; this does not record a test call.",
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["region", "name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["number", "region"], name="unique_helpline_number_per_region",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.number})"

    def clean(self):
        super().clean()
        if self.is_active and (not self.source_url or not self.verified_on):
            raise ValidationError("An active helpline needs an official source and its check date.")
```

### `firstaid/content.py`

Original adult summaries and official helpline references with a fixed evidence date.

```python
"""Original, concise educational summaries; source checks are not clinical reviews.

Dates are fixed evidence dates, not the day a seed command happens to run.
See FIRST_AID_SOURCES.md for full provenance, scope and update responsibilities.
"""
from datetime import date

SOURCE_CHECKED_ON = date(2026, 11, 12)
MHA_SOURCE = "https://www.mha.gov.in/emergency-response-support-system-erss"
NHM_SOURCE = "https://nhm.gov.in/nhm/index1.php?lang=1&level=2&lid=189&sublinkid=1217"

GUIDES = [
    {
        "slug": "adult-cpr", "title": "CPR for an adult",
        "summary": "For an adult who is unresponsive and not breathing normally. Gasping is not normal breathing.",
        "urgent_advice": "Call 112 on speaker immediately if the person is unresponsive. Assess breathing while connecting and follow the dispatcher.",
        "warnings": "Adult guidance only. Children, babies and drowning need different approaches; ask the dispatcher. Do not delay CPR to read this page.",
        "source_url": "https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/adult-basic-life-support-guidelines",
        "supporting_source_url": "https://www.resus.org.uk/public-resource/how-do-cpr",
        "steps": [
            ("Check safety and response", "Approach only if safe. Shout for help and check whether the person responds. Call 112 and check for normal breathing."),
            ("Start compressions", "If unresponsive with absent or abnormal breathing, put one hand's heel at the centre of the chest over the lower breastbone; place the other hand on top. Keep arms straight."),
            ("Push firmly and regularly", "Compress 5–6 cm at 100–120 compressions per minute. Let the chest rise fully between pushes and minimise pauses."),
            ("Use your training and an AED", "If trained in rescue breaths, alternate 30 compressions with 2 breaths; otherwise keep compressing. Ask another person to fetch an AED, switch it on and follow its prompts. Nobody should touch the person during analysis or shock."),
            ("Continue helping", "Continue CPR until professionals take over, normal breathing returns, or you cannot continue. Follow the dispatcher and AED."),
        ],
    },
    {
        "slug": "severe-bleeding", "title": "Severe external bleeding",
        "summary": "Act promptly to control major bleeding from an external wound.",
        "urgent_advice": "Get emergency help through 112 while applying pressure. Use speakerphone or ask someone else to call.",
        "warnings": "This short guide does not cover open chest wounds. If pressure does not control a severe limb bleed, follow dispatcher instructions about further measures; use equipment according to your training.",
        "source_url": "https://www.sja.org.uk/first-aid-advice/severe-bleeding/",
        "supporting_source_url": "https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines",
        "steps": [
            ("Protect yourself if possible", "Check for danger and use disposable gloves if available. Expose the wound enough to see where blood is coming from."),
            ("Apply firm pressure", "Press directly on the wound using a sterile dressing or clean cloth. If an object is embedded, leave it in place and press around it, not on it."),
            ("Maintain control", "Keep pressure on the bleeding. Once controlled, secure the dressing without cutting off circulation. Follow the dispatcher's advice if bleeding continues."),
            ("Monitor while help comes", "Keep the person warm and watch responsiveness and breathing. If they become unresponsive and are not breathing normally, start CPR with dispatcher guidance."),
        ],
    },
    {
        "slug": "thermal-burns", "title": "Burns and scalds",
        "summary": "Initial care for heat or hot-liquid burns. Chemical and electrical burns need emergency assessment.",
        "urgent_advice": "Call 112 for a large or deep burn, burns to the face or genitals, chemical/electrical injury, or breathing difficulty. Seek medical advice if unsure.",
        "warnings": "Do not apply ice, oils, butter or creams. Do not burst blisters or pull away anything stuck to the burn. This is not a chemical or electrical burn treatment guide.",
        "source_url": "https://www.nhs.uk/conditions/burns-and-scalds/",
        "supporting_source_url": "https://www.sja.org.uk/first-aid-advice/burns-and-scalds/",
        "steps": [
            ("Leave the heat source safely", "Stop exposure to heat without putting yourself in danger."),
            ("Cool the affected skin", "Use cool running water for 20 minutes as soon as possible. Keep the rest of the person warm."),
            ("Remove loose items", "Take off nearby jewellery and clothing before swelling develops, but leave stuck material alone."),
            ("Cover after cooling", "Lay clean cling film loosely over a cooled body or limb burn; do not wrap it around the limb or put it on the face. Arrange appropriate medical assessment."),
        ],
    },
    {
        "slug": "adult-choking", "title": "Choking in an adult",
        "summary": "Distinguish effective coughing from a severe airway blockage.",
        "urgent_advice": "If the person cannot breathe, speak or cough effectively, get someone to call 112 or use speakerphone while helping.",
        "warnings": "Never sweep fingers blindly inside the mouth. Do not use abdominal thrusts in pregnancy. If pregnant or you cannot reach around the abdomen, use chest thrusts instead and follow the dispatcher. Children and babies require different guidance.",
        "source_url": "https://www.sja.org.uk/first-aid-advice/choking/",
        "supporting_source_url": "https://www.resus.org.uk/professional-library/faqs/faqs-basic-life-support-cpr",
        "steps": [
            ("Encourage an effective cough", "If they can cough and breathe, encourage coughing and monitor. If coughing becomes ineffective, act immediately."),
            ("Give up to five back blows", "Support the upper body, lean the person forward and strike between the shoulder blades with the heel of your hand. Check after each blow; stop if the blockage clears."),
            ("If needed, give up to five thrusts", "For a non-pregnant adult, stand behind them, put a fist above the navel and below the breastbone, grasp it with your other hand and pull sharply inward and upward. For chest thrusts, position hands over the lower breastbone and pull inward."),
            ("Repeat or begin CPR", "Alternate up to five back blows and five appropriate thrusts until clear. If unresponsive, lower them safely, ensure 112 is called and start CPR. Arrange medical evaluation after abdominal thrusts or chest compressions."),
        ],
    },
    {
        "slug": "recovery-position", "title": "Recovery position",
        "summary": "For an unresponsive adult who is breathing normally. Keep checking breathing.",
        "urgent_advice": "Call 112. If breathing is absent, abnormal or only gasping, use CPR instead and follow the dispatcher.",
        "warnings": "If a spinal injury is suspected, minimise movement and follow the dispatcher. Keeping the airway open takes priority. Do not give food or drink to an unresponsive person.",
        "source_url": "https://www.sja.org.uk/first-aid-advice/recovery-position/",
        "supporting_source_url": "https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines",
        "steps": [
            ("Check normal breathing", "Ensure the scene is safe and call 112. Use the recovery position only when the person is unresponsive but breathing normally."),
            ("Position the arms and knee", "Kneel beside them. Place the nearer arm out at a right angle with palm up. Hold the far hand against the nearer cheek; bend the far knee with its foot on the ground."),
            ("Roll onto the side", "Keep the hand at the cheek and pull the bent knee towards you to roll the person onto their side. Adjust the upper leg for support."),
            ("Keep the airway open and monitor", "Gently tilt the head back and lift the chin. Stay with them and keep checking breathing until help takes over. If breathing becomes abnormal or stops, follow dispatcher instructions and start CPR."),
        ],
    },
]

HELPLINES = [
    {"name": "Emergency Response Support System", "number": "112", "region": "India — nationwide", "is_nationwide": True,
     "description": "Unified emergency access for police, fire and health emergencies. Call directly in a real emergency; MEDTAP does not place the call or connect to ERSS automatically.", "source_url": MHA_SOURCE},
    {"name": "Emergency ambulance response", "number": "108", "region": "India — participating states/UTs", "is_nationwide": False,
     "description": "Primarily emergency response for critical illness, trauma and accidents where locally operational. Availability and routing vary by state/UT; this is not a nationwide coverage guarantee. Use 112 if unsure.", "source_url": NHM_SOURCE},
    {"name": "Patient transport", "number": "102", "region": "India — participating states/UTs", "is_nationwide": False,
     "description": "Basic patient transport, particularly for pregnant women and children, where available. Eligibility and local operation vary. It is not a substitute for emergency response; use 112 in a real emergency.", "source_url": NHM_SOURCE},
]
```

### `firstaid/services.py`

One publication/URL-safety boundary for both HTML and API consumers.

```python
import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from .models import EmergencyHelpline, FirstAidGuide
from .validators import validate_https_source

ICONS = {
    "adult-cpr": "heart-pulse", "severe-bleeding": "droplet", "thermal-burns": "thermometer-half",
    "adult-choking": "lungs", "recovery-position": "person-heart",
}
SOURCE_LABELS = {
    "www.nhs.uk": "NHS", "www.sja.org.uk": "St John Ambulance",
    "www.resus.org.uk": "Resuscitation Council UK", "www.mha.gov.in": "Ministry of Home Affairs",
    "nhm.gov.in": "National Health Mission",
}


def source_link(url):
    try:
        validate_https_source(url)
    except ValidationError:
        return None
    host = urlsplit(url).hostname
    return {"label": SOURCE_LABELS.get(host, host), "url": url}


def public_guides(query=""):
    guides = FirstAidGuide.objects.filter(
        is_published=True, source_checked_on__lte=timezone.localdate(), steps__isnull=False,
    ).prefetch_related("steps").distinct()
    if query:
        guides = guides.filter(Q(title__icontains=query) | Q(summary__icontains=query))
    # The small educational catalogue also checks URLs at read time so even
    # malformed direct database writes cannot expose an unsafe source link.
    return [guide for guide in guides if source_link(guide.source_url)]


def guide_sources(guide):
    return [link for url in (guide.source_url, guide.supporting_source_url) if url and (link := source_link(url))]


def public_helplines():
    candidates = EmergencyHelpline.objects.filter(
        is_active=True, verified_on__lte=timezone.localdate(),
    ).order_by("-is_nationwide", "number", "region", "pk")
    lines = [line for line in candidates if source_link(line.source_url)
             and re.fullmatch(r"\+?[0-9]{2,15}", line.number) and line.number.strip("+0")]
    priority = {"112": 0, "108": 1, "102": 2}
    return sorted(lines, key=lambda line: (not line.is_nationwide, priority.get(line.number, 99), line.number, line.region, line.pk))


def guide_data(guide, *, include_steps=False):
    data = {
        "slug": guide.slug, "title": guide.title, "summary": guide.summary,
        "audience": guide.audience, "urgent_advice": guide.urgent_advice,
        "warnings": guide.warnings, "source_checked_on": guide.source_checked_on,
        "clinical_reviewed_on": guide.reviewed_on, "sources": guide_sources(guide),
    }
    if include_steps:
        data["steps"] = [{"position": step.position, "heading": step.heading, "instruction": step.instruction} for step in guide.steps.all()]
    return data
```

### `firstaid/forms.py`

Validate catalogue search and pagination parameters.

```python
from django import forms


class GuideSearchForm(forms.Form):
    q = forms.CharField(
        required=False, max_length=120, label="Search guides",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "CPR, bleeding, burns…"}),
    )
    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput)

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())
```

### `firstaid/views.py`

Read-only function-based public pages and DRF endpoints.

```python
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, authentication_classes, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .forms import GuideSearchForm
from .services import ICONS, guide_data, guide_sources, public_guides, public_helplines, source_link


def find_guide(slug):
    for guide in public_guides():
        if guide.slug == slug:
            return guide
    raise Http404("This guide is unavailable or is not published.")


def search_page(form):
    try:
        return Paginator(public_guides(form.cleaned_data["q"]), 20).page(form.cleaned_data["page"] or 1)
    except InvalidPage as exc:
        raise Http404("That guide page does not exist.") from exc


def page_query(params, number):
    query = params.copy()
    query["page"] = number
    return "?" + query.urlencode()


@require_GET
def guide_list(request):
    form = GuideSearchForm(request.GET)
    page = search_page(form) if form.is_valid() else None
    return render(request, "firstaid/guide_list.html", {
        "form": form, "page_obj": page,
        "cards": [{"guide": guide, "icon": ICONS.get(guide.slug, "bandaid")} for guide in page] if page else [],
        "previous_query": page_query(request.GET, page.previous_page_number()) if page and page.has_previous() else None,
        "next_query": page_query(request.GET, page.next_page_number()) if page and page.has_next() else None,
    }, status=400 if form.errors else 200)


@require_GET
def guide_detail(request, slug):
    guide = find_guide(slug)
    return render(request, "firstaid/guide_detail.html", {
        "guide": guide, "sources": guide_sources(guide), "icon": ICONS.get(guide.slug, "bandaid"),
    })


@require_GET
def helplines(request):
    return render(request, "firstaid/helplines.html", {
        "lines": [{"line": line, "source": source_link(line.source_url)} for line in public_helplines()],
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def guide_list_api(request):
    form = GuideSearchForm(request.query_params)
    if not form.is_valid():
        return Response({"errors": dict(form.errors)}, status=400)
    page = search_page(form)
    return Response({
        "count": page.paginator.count,
        "next": request.build_absolute_uri(page_query(request.query_params, page.next_page_number())) if page.has_next() else None,
        "previous": request.build_absolute_uri(page_query(request.query_params, page.previous_page_number())) if page.has_previous() else None,
        "results": [guide_data(guide) for guide in page],
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def guide_detail_api(request, slug):
    return Response(guide_data(find_guide(slug), include_steps=True))


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def helplines_api(request):
    return Response({"results": [{
        "name": line.name, "number": line.number, "region": line.region,
        "is_nationwide": line.is_nationwide, "description": line.description,
        "source_checked_on": line.verified_on, "source": source_link(line.source_url),
        "call_url": "tel:" + line.number,
    } for line in public_helplines()]})
```

### `firstaid/urls.py`

App-level namespaced routes under the existing first-aid prefix.

```python
from django.urls import path

from . import views

app_name = "firstaid"
urlpatterns = [
    path("", views.guide_list, name="guide_list"),
    path("helplines/", views.helplines, name="helplines"),
    path("api/guides/", views.guide_list_api, name="guide_list_api"),
    path("api/guides/<slug:slug>/", views.guide_detail_api, name="guide_detail_api"),
    path("api/helplines/", views.helplines_api, name="helplines_api"),
    path("<slug:slug>/", views.guide_detail, name="guide_detail"),
]
```

### `firstaid/admin.py`

Editable content with inline ordered steps and honest review metadata.

```python
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import EmergencyHelpline, FirstAidGuide, FirstAidStep


class GuideStepsFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        kept = [form for form in self.forms if form.cleaned_data and not form.cleaned_data.get("DELETE")
                and form.cleaned_data.get("instruction")]
        if self.instance.is_published and not kept:
            raise ValidationError("A published guide must have at least one instruction step.")
        positions = sorted(form.cleaned_data["position"] for form in kept)
        if positions and positions != list(range(1, len(positions) + 1)):
            raise ValidationError("Number steps consecutively from 1, without gaps.")


class FirstAidStepInline(admin.StackedInline):
    model = FirstAidStep
    formset = GuideStepsFormSet
    extra = 1
    fields = ["position", "heading", "instruction"]


@admin.register(FirstAidGuide)
class FirstAidGuideAdmin(admin.ModelAdmin):
    list_display = ["title", "audience", "is_published", "source_checked_on", "reviewed_on"]
    list_filter = ["is_published", "source_checked_on"]
    search_fields = ["title", "summary", "slug"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [FirstAidStepInline]
    fieldsets = [
        ("Guide", {"fields": ["title", "slug", "audience", "summary", "urgent_advice", "warnings"]}),
        ("Sources and publication", {"fields": ["source_url", "supporting_source_url", "source_checked_on", "reviewed_on", "is_published"],
         "description": "A source check is not a clinical review. Published summaries need current authoritative sources. Only record a clinical review if it actually took place."}),
        ("Record", {"fields": ["created_at", "updated_at"]}),
    ]


@admin.register(EmergencyHelpline)
class EmergencyHelplineAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "region", "is_nationwide", "is_active", "verified_on"]
    list_filter = ["is_nationwide", "is_active"]
    search_fields = ["name", "number", "region"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "number", "region", "description", "is_nationwide", "source_url", "verified_on", "is_active", "created_at", "updated_at"]
```

### `firstaid/management/__init__.py`

Empty Python package marker.

```python

```

### `firstaid/management/commands/__init__.py`

Empty management-command package marker.

```python

```

### `firstaid/management/commands/seed_firstaid.py`

Create missing records transactionally while preserving staff edits.

```python
from copy import deepcopy

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from firstaid.content import GUIDES, HELPLINES, SOURCE_CHECKED_ON
from firstaid.models import EmergencyHelpline, FirstAidGuide, FirstAidStep


class Command(BaseCommand):
    help = "Add source-checked educational guides and official helpline references; preserve existing edits."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        guide_count = helpline_count = 0
        try:
            with transaction.atomic():
                for entry in deepcopy(GUIDES):
                    steps = entry.pop("steps")
                    if FirstAidGuide.objects.filter(slug=entry["slug"]).exists():
                        continue
                    guide = FirstAidGuide(**entry, source_checked_on=SOURCE_CHECKED_ON, is_published=True)
                    guide.full_clean()
                    guide.save()
                    for position, (heading, instruction) in enumerate(steps, 1):
                        step = FirstAidStep(guide=guide, position=position, heading=heading, instruction=instruction)
                        step.full_clean()
                        step.save()
                    guide_count += 1
                for entry in deepcopy(HELPLINES):
                    if EmergencyHelpline.objects.filter(number=entry["number"], region=entry["region"]).exists():
                        continue
                    helpline = EmergencyHelpline(**entry, verified_on=SOURCE_CHECKED_ON, is_active=True)
                    helpline.full_clean()
                    helpline.save()
                    helpline_count += 1
        except (ValidationError, IntegrityError) as error:
            raise CommandError(f"Content seed rolled back: {error}") from error
        self.stdout.write(self.style.SUCCESS(
            f"Created {guide_count} guides and {helpline_count} helpline references. Existing records were preserved.\n"
            f"Sources checked on {SOURCE_CHECKED_ON}; clinical review is not recorded. No test calls were made."
        ))
```

### `firstaid/migrations/0002_emergencyhelpline_is_nationwide_and_more.py`

Complete generated migration; old data and empty review fields are retained.

```python
# Generated by Django 6.1.3 on 2026-11-12 14:11

import firstaid.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstaid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencyhelpline',
            name='is_nationwide',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='firstaidguide',
            name='audience',
            field=models.CharField(default='Adults (18 years and over)', max_length=100),
        ),
        migrations.AddField(
            model_name='firstaidguide',
            name='source_checked_on',
            field=models.DateField(blank=True, help_text='Date the linked sources were checked; not a clinical review.', null=True, validators=[firstaid.validators.validate_not_future]),
        ),
        migrations.AddField(
            model_name='firstaidguide',
            name='supporting_source_url',
            field=models.URLField(blank=True, validators=[firstaid.validators.validate_https_source]),
        ),
        migrations.AddField(
            model_name='firstaidguide',
            name='urgent_advice',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='firstaidguide',
            name='warnings',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='firstaidstep',
            name='heading',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='emergencyhelpline',
            name='source_url',
            field=models.URLField(blank=True, validators=[firstaid.validators.validate_https_source]),
        ),
        migrations.AlterField(
            model_name='emergencyhelpline',
            name='verified_on',
            field=models.DateField(blank=True, help_text='Date the official source was checked; this does not record a test call.', null=True, validators=[firstaid.validators.validate_not_future]),
        ),
        migrations.AlterField(
            model_name='firstaidguide',
            name='reviewed_on',
            field=models.DateField(blank=True, help_text="Only enter a date if a qualified clinician actually reviewed this app's text.", null=True, validators=[firstaid.validators.validate_not_future]),
        ),
        migrations.AlterField(
            model_name='firstaidguide',
            name='source_url',
            field=models.URLField(blank=True, validators=[firstaid.validators.validate_https_source]),
        ),
    ]
```

### `core/views.py`

Home quick actions now point to the published first-aid and helpline pages.

```python
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .forms import CareSearchForm


@require_GET
def home(request):
    search_form = CareSearchForm()
    facility_url = reverse("facilities:nearby")
    quick_actions = [
        {
            "key": "hospitals", "title": "Nearby Hospitals", "icon": "hospital",
            "description": "Find a place for the care you need.",
            "href": facility_url, "status": "Explore nearby care",
        },
        {
            "key": "ambulance", "title": "Ambulance", "icon": "truck-front",
            "description": "Request transport and follow its progress.",
            "href": reverse("emergency:ambulance_start"), "status": "Project request & status",
        },
        {
            "key": "blood-banks", "title": "Blood Banks", "icon": "droplet",
            "description": "Look for blood banks in your area.", "tone": "teal",
            "href": facility_url + "?facility_type=blood_bank", "status": "Browse blood banks",
        },
        {
            "key": "pharmacies", "title": "Pharmacies", "icon": "capsule",
            "description": "Find a pharmacy close to you.", "tone": "teal",
            "href": facility_url + "?facility_type=pharmacy", "status": "Browse pharmacies",
        },
        {
            "key": "first-aid", "title": "First Aid", "icon": "bandaid",
            "description": "Clear, step-by-step guides for urgent moments.",
            "href": reverse("firstaid:guide_list"), "status": "Read adult first-aid guides",
        },
        {
            "key": "helplines", "title": "Helplines", "icon": "telephone",
            "description": "Keep essential emergency numbers in reach.",
            "href": reverse("firstaid:helplines"), "status": "Numbers & coverage",
        },
    ]
    return render(request, "core/home.html", {
        "search_form": search_form,
        "quick_actions": quick_actions,
    })
```

### `templates/partials/firstaid_notice.html`

A concise shared educational scope notice for the library.

```html
<div class="firstaid-notice">{% include 'partials/icon.html' with name='info-circle' only %}<div><strong>Short educational summaries for adults.</strong><p>These pages do not replace first-aid training, a clinician or the emergency dispatcher. This app does not replace calling 112. Do not delay getting help to read a guide.</p></div></div>
```

### `templates/firstaid/guide_list.html`

Searchable responsive cards with source-check dates.

```html
{% extends 'base.html' %}
{% block title %}First-aid guides | MEDTAP{% endblock %}
{% block content %}
<section class="firstaid-section"><div class="container">
  <header class="firstaid-heading"><div><p class="eyebrow">Know the next step</p><h1>A little guidance.<br>When it matters.</h1><p>Clear first steps for adult emergencies, with sources you can check.</p></div><a class="btn btn-primary" href="tel:112">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112</a></header>
  {% include 'partials/firstaid_notice.html' %}
  <form method="get" class="firstaid-search" role="search" aria-label="Search first-aid guides"><div class="field-wrapper"><label class="form-label" for="{{ form.q.id_for_label }}">{{ form.q.label }}</label>{{ form.q }}</div><button class="btn btn-primary" type="submit">Find guide {% include 'partials/icon.html' with name='search' class_name='icon-sm' only %}</button><a class="finder-reset" href="{% url 'firstaid:guide_list' %}">Clear search</a></form>
  {% include 'partials/form_errors.html' with form=form error_heading='Please check your search' only %}
  <div class="firstaid-grid">{% for card in cards %}<a class="firstaid-card" href="{% url 'firstaid:guide_detail' card.guide.slug %}" aria-describedby="guide-summary-{{ card.guide.pk }}"><span class="action-icon">{% include 'partials/icon.html' with name=card.icon class_name='icon-lg' only %}</span><p class="eyebrow">{{ card.guide.audience }}</p><h2>{{ card.guide.title }}</h2><p id="guide-summary-{{ card.guide.pk }}">{{ card.guide.summary }}</p><span class="firstaid-card-link">Read the steps {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</span><span class="firstaid-card-date">Source checked {{ card.guide.source_checked_on|date:'d M Y' }}</span></a>{% empty %}{% if not form.errors %}<div class="account-panel"><h2>No guides found</h2><p>Try another term or clear your search. Call 112 for emergency help.</p></div>{% endif %}{% endfor %}</div>
  {% if page_obj.paginator.num_pages > 1 %}<nav class="finder-pagination" aria-label="Guide pages">{% if previous_query %}<a class="btn btn-outline-primary" href="{{ previous_query }}">Previous</a>{% endif %}<span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>{% if next_query %}<a class="btn btn-outline-primary" href="{{ next_query }}">Next</a>{% endif %}</nav>{% endif %}
  <div class="firstaid-library-note"><p>Source checks are not clinical reviews of our summaries. Each guide states its review status and links to the original guidance.</p><a class="back-link" href="{% url 'firstaid:helplines' %}">View Indian emergency helplines {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a></div>
</div></section>
{% endblock %}
```

### `templates/firstaid/guide_detail.html`

Readable numbered instructions with urgent advice, scope and direct source links.

```html
{% extends 'base.html' %}
{% block title %}{{ guide.title }} | MEDTAP{% endblock %}
{% block content %}
<section class="firstaid-section"><div class="container firstaid-reading">
  <a class="back-link" href="{% url 'firstaid:guide_list' %}">All first-aid guides</a>
  <header class="firstaid-heading"><div><p class="eyebrow">{{ guide.audience }}</p><h1>{{ guide.title }}</h1><p>{{ guide.summary }}</p></div><span class="action-icon">{% include 'partials/icon.html' with name=icon class_name='icon-lg' only %}</span></header>
  <p class="firstaid-review-line">Educational summary · Source checked {{ guide.source_checked_on|date:'d M Y' }} · {% if guide.reviewed_on %}Clinical review recorded {{ guide.reviewed_on|date:'d M Y' }}{% else %}Clinical review of this summary is not recorded{% endif %}</p>
  <div class="sos-critical-note"><strong>Get help first.</strong> {% if guide.urgent_advice %}{{ guide.urgent_advice }}{% else %}Call 112 for a medical emergency and follow the dispatcher.{% endif %}<a href="tel:112">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112</a></div>
  {% if guide.warnings %}<aside class="firstaid-caution" aria-labelledby="guide-caution-heading"><h2 id="guide-caution-heading">Before you act</h2><p>{{ guide.warnings }}</p></aside>{% endif %}
  <ol class="firstaid-step-list" aria-label="First-aid steps">{% for step in guide.steps.all %}<li><span class="firstaid-step-number" aria-hidden="true">{{ step.position|stringformat:'02d' }}</span><div><h2>{% if step.heading %}{{ step.heading }}{% else %}Step {{ step.position }}{% endif %}</h2><p>{{ step.instruction }}</p></div></li>{% endfor %}</ol>
  <section class="firstaid-sources" aria-labelledby="guide-source-heading"><p class="eyebrow">Read the full guidance</p><h2 id="guide-source-heading">Sources &amp; review status</h2><p>Source checked {{ guide.source_checked_on|date:'d M Y' }}. {% if guide.reviewed_on %}Clinical review recorded {{ guide.reviewed_on|date:'d M Y' }}.{% else %}<strong>Clinical review of this summary is not recorded.</strong>{% endif %}</p><ul>{% for source in sources %}<li><a href="{{ source.url }}" target="_blank" rel="noopener noreferrer">{{ source.label }} — original guidance {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a></li>{% endfor %}</ul><p class="field-help">MEDTAP's brief text is an original educational summary, not an endorsement by the linked organisations. Some original sources refer to UK numbers; use 112 for emergencies in India.</p></section>
  <a class="btn btn-outline-primary" href="{% url 'firstaid:helplines' %}">Emergency helplines {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %}</a>
</div></section>
{% endblock %}
```

### `templates/firstaid/helplines.html`

Official-number references with explicit coverage and no automatic calls.

```html
{% extends 'base.html' %}
{% block title %}Emergency helplines in India | MEDTAP{% endblock %}
{% block content %}
<section class="firstaid-section"><div class="container">
  <header class="firstaid-heading"><div><p class="eyebrow">India · emergency contacts</p><h1>The numbers<br>to keep close.</h1><p>Call directly from your phone. These links do not create a MEDTAP request or notify a contact automatically.</p></div><span class="action-icon">{% include 'partials/icon.html' with name='telephone' class_name='icon-lg' only %}</span></header>
  <div class="sos-critical-note"><strong>This app does not replace calling 112.</strong> For a real emergency or if you are unsure which service operates locally, call 112. <a href="tel:112">Call 112 now</a></div>
  <div class="helpline-grid">{% for row in lines %}<article class="helpline-card{% if row.line.is_nationwide %} helpline-card-national{% endif %}" aria-labelledby="helpline-title-{{ row.line.pk }}"><div class="helpline-card-top"><span class="action-icon">{% include 'partials/icon.html' with name='telephone' only %}</span><span class="facility-type">{% if row.line.is_nationwide %}Nationwide{% else %}State/UT dependent{% endif %}</span></div><p class="helpline-number">{{ row.line.number }}</p><h2 id="helpline-title-{{ row.line.pk }}">{{ row.line.name }}</h2><p class="helpline-region">{{ row.line.region }}</p><p>{{ row.line.description }}</p><a class="btn btn-primary" href="tel:{{ row.line.number }}" aria-label="Call {{ row.line.number }} for {{ row.line.name }}">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call {{ row.line.number }}</a><div class="helpline-source"><p>Source checked {{ row.line.verified_on|date:'d M Y' }}</p><a href="{{ row.source.url }}" target="_blank" rel="noopener noreferrer">{{ row.source.label }} {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a></div></article>{% empty %}<div class="account-panel"><h2>No verified directory entries available</h2><p>Use the Call 112 shortcut for a real emergency.</p></div>{% endfor %}</div>
  <div class="firstaid-library-note"><h2>Availability depends on the service</h2><p>108 and 102 are not guaranteed to operate identically across India. An official-source check does not confirm a live connection, vehicle availability or response time. No test calls were made. Follow the call handler's instructions.</p><a class="back-link" href="{% url 'firstaid:guide_list' %}">Browse adult first-aid guides {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a></div>
</div></section>
{% endblock %}
```

### `templates/partials/navbar.html`

Working first-aid and helpline links with current-page indicators.

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
          <li class="nav-item"><a class="nav-link" href="{% url 'emergency:ambulance_start' %}">Ambulance</a></li>
          {% if user.is_staff and perms.emergency.view_ambulancerequest and perms.emergency.change_ambulancerequest %}<li class="nav-item"><a class="nav-link" href="{% url 'emergency:operator_dashboard' %}">Operator queue</a></li>{% endif %}
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

### `templates/partials/footer.html`

The existing disclaimer/112 shortcut plus the 108/102 coverage link.

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
        <a class="footer-helplines-link" href="{% url 'firstaid:helplines' %}">108 / 102 availability &amp; sources</a>
      </div>
      <div class="col-sm-8 col-lg-5">
        <p class="footer-label">Please remember</p>
        <p class="footer-disclaimer mb-0"><strong>This app does not replace calling 112.</strong> SOS sharing is manual. Transport requests are project records; no ambulance dispatch service is connected.</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {% now 'Y' %} MEDTAP. Built with care.</span>
      <span>Medical Emergency App &middot; Student project</span>
    </div>
  </div>
</footer>
```

### `static/css/theme.css`

Complete current theme, including earlier screens and readable first-aid/helpline layouts.

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
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### `firstaid/tests.py`

Twenty-eight new model, seed, view, API and admin tests.

```python
from copy import deepcopy
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User

from .content import GUIDES, HELPLINES, SOURCE_CHECKED_ON
from .models import EmergencyHelpline, FirstAidGuide, FirstAidStep
from .services import public_guides, public_helplines, source_link


def guide_values(**changes):
    values = dict(title="Test educational guide", slug="test-guide", summary="Test summary",
                  source_url="https://www.nhs.uk/conditions/burns-and-scalds/",
                  source_checked_on=timezone.localdate(), is_published=True)
    values.update(changes)
    return values


class FirstAidModelTests(TestCase):
    def test_models_default_to_draft_inactive_and_no_clinical_review(self):
        guide = FirstAidGuide(title="Draft", slug="draft", summary="Draft text")
        guide.full_clean()
        self.assertFalse(guide.is_published)
        self.assertIsNone(guide.reviewed_on)
        self.assertIsNone(guide.source_checked_on)
        line = EmergencyHelpline(name="Test", number="112", region="Test region")
        line.full_clean()
        self.assertFalse(line.is_active)
        self.assertFalse(line.is_nationwide)

    def test_published_guide_and_active_helpline_require_source_metadata(self):
        with self.assertRaises(ValidationError):
            FirstAidGuide(**guide_values(source_url="", source_checked_on=None)).full_clean()
        with self.assertRaises(ValidationError):
            EmergencyHelpline(name="Test", number="112", region="Test", is_active=True).full_clean()

    def test_source_urls_reject_non_https_credentials_and_script_schemes(self):
        for url in ("http://example.com/", "javascript:alert(1)", "https://user:pass@example.com/"):
            with self.subTest(url=url):
                with self.assertRaises(ValidationError):
                    FirstAidGuide(**guide_values(source_url=url)).full_clean()
                self.assertIsNone(source_link(url))

    def test_future_check_and_clinical_review_dates_are_rejected(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        for field in ("source_checked_on", "reviewed_on"):
            with self.assertRaises(ValidationError):
                FirstAidGuide(**guide_values(**{field: tomorrow})).full_clean()
        with self.assertRaises(ValidationError):
            EmergencyHelpline(name="Test", number="112", region="Test", verified_on=tomorrow).full_clean()

    def test_step_order_positive_positions_and_unique_position(self):
        guide = FirstAidGuide.objects.create(**guide_values())
        FirstAidStep.objects.create(guide=guide, position=2, instruction="Second")
        FirstAidStep.objects.create(guide=guide, position=1, instruction="First")
        self.assertEqual(list(guide.steps.values_list("position", flat=True)), [1, 2])
        for position in (0, 1):
            with self.assertRaises(ValidationError):
                FirstAidStep(guide=guide, position=position, instruction="Invalid").full_clean()

    def test_helpline_number_validation_and_region_unique_key(self):
        EmergencyHelpline.objects.create(name="Test", number="112", region="Test region")
        with self.assertRaises(ValidationError):
            EmergencyHelpline(name="Duplicate", number="112", region="Test region").full_clean()
        for number in ("1", "tel:112", "112?body=test", "<script>"):
            with self.assertRaises(ValidationError):
                EmergencyHelpline(name="Test", number=number, region="Other region").full_clean()


class SeedFirstAidTests(TestCase):
    def seed(self):
        output = StringIO()
        call_command("seed_firstaid", stdout=output)
        return output.getvalue()

    def test_seed_creates_five_sourced_adult_guides_and_three_real_helpline_references(self):
        self.assertIn("Created 5 guides and 3 helpline references", self.seed())
        self.assertEqual(FirstAidGuide.objects.count(), 5)
        self.assertEqual(EmergencyHelpline.objects.count(), 3)
        for guide in FirstAidGuide.objects.all():
            guide.full_clean()
            self.assertIsNone(guide.reviewed_on)
            self.assertEqual(guide.source_checked_on, SOURCE_CHECKED_ON)
            self.assertIn("18", guide.audience)
            self.assertEqual(list(guide.steps.values_list("position", flat=True)), list(range(1, guide.steps.count() + 1)))
        for line in EmergencyHelpline.objects.all():
            line.full_clean()
            self.assertEqual(line.verified_on, SOURCE_CHECKED_ON)
        self.assertTrue(EmergencyHelpline.objects.get(number="112").is_nationwide)
        self.assertFalse(EmergencyHelpline.objects.get(number="108").is_nationwide)
        self.assertFalse(EmergencyHelpline.objects.get(number="102").is_nationwide)

    def test_reseed_preserves_edited_or_unpublished_records_and_steps(self):
        self.seed()
        guide = FirstAidGuide.objects.get(slug="adult-cpr")
        guide.summary = "Staff edited summary"
        guide.is_published = False
        guide.source_checked_on = SOURCE_CHECKED_ON - timedelta(days=1)
        guide.save()
        step = guide.steps.first()
        step.instruction = "Staff edited step"
        step.save()
        line = EmergencyHelpline.objects.get(number="108")
        line.is_active = False
        line.description = "Staff edited coverage"
        line.save()
        self.assertIn("Created 0 guides and 0 helpline references", self.seed())
        guide.refresh_from_db(); step.refresh_from_db(); line.refresh_from_db()
        self.assertEqual(guide.summary, "Staff edited summary")
        self.assertFalse(guide.is_published)
        self.assertEqual(guide.source_checked_on, SOURCE_CHECKED_ON - timedelta(days=1))
        self.assertEqual(step.instruction, "Staff edited step")
        self.assertFalse(line.is_active)
        self.assertEqual(line.description, "Staff edited coverage")

    def test_seed_failure_rolls_back_the_whole_new_content_batch(self):
        invalid = deepcopy(GUIDES)
        invalid[-1]["source_url"] = "http://example.com/"
        with patch("firstaid.management.commands.seed_firstaid.GUIDES", invalid):
            with self.assertRaises(CommandError):
                self.seed()
        self.assertEqual(FirstAidGuide.objects.count(), 0)
        self.assertEqual(FirstAidStep.objects.count(), 0)
        self.assertEqual(EmergencyHelpline.objects.count(), 0)

    def test_existing_slug_collision_is_preserved_without_inserting_new_steps(self):
        guide = FirstAidGuide.objects.create(**guide_values(slug=GUIDES[0]["slug"], is_published=False))
        self.seed()
        guide.refresh_from_db()
        self.assertFalse(guide.is_published)
        self.assertFalse(guide.steps.exists())

    def test_content_keeps_key_scope_and_emergency_exceptions(self):
        self.seed()
        cpr = FirstAidGuide.objects.get(slug="adult-cpr")
        self.assertIn("Gasping is not normal breathing", cpr.summary)
        self.assertIn("100–120", " ".join(cpr.steps.values_list("instruction", flat=True)))
        choking = FirstAidGuide.objects.get(slug="adult-choking")
        self.assertIn("Do not use abdominal thrusts in pregnancy", choking.warnings)
        burns = FirstAidGuide.objects.get(slug="thermal-burns")
        self.assertIn("20 minutes", " ".join(burns.steps.values_list("instruction", flat=True)))
        self.assertIn("put it on the face", burns.steps.last().instruction)
        self.assertIn("Patient transport", EmergencyHelpline.objects.get(number="102").name)


class PublicFirstAidTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_firstaid", stdout=StringIO())

    def test_public_library_detail_and_helplines_do_not_require_login(self):
        for name, args in (("guide_list", []), ("guide_detail", ["adult-cpr"]), ("helplines", [])):
            response = self.client.get(reverse(f"firstaid:{name}", args=args))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "This app does not replace calling 112")

    def test_guide_has_numbered_readable_steps_sources_and_honest_review_metadata(self):
        response = self.client.get(reverse("firstaid:guide_detail", args=["adult-cpr"]))
        self.assertContains(response, "Clinical review of this summary is not recorded")
        self.assertContains(response, "Adults (18 years and over)")
        self.assertContains(response, 'class="firstaid-step-number"', count=5)
        self.assertContains(response, "Resuscitation Council UK")
        self.assertContains(response, 'href="tel:112"')
        self.assertNotContains(response, 'href="tel:999"')

    def test_draft_undated_future_empty_and_unsafe_source_guides_are_not_public(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        for index, changes in enumerate(({"is_published": False}, {"source_checked_on": None},
                                        {"source_checked_on": tomorrow}, {"source_url": "javascript:alert(1)"}, {})):
            guide = FirstAidGuide.objects.create(**guide_values(slug=f"hidden-{index}", **changes))
            if index != 4:
                FirstAidStep.objects.create(guide=guide, position=1, instruction="Hidden instruction")
            self.assertNotIn(guide, public_guides())
            for name in ("guide_detail", "guide_detail_api"):
                self.assertEqual(self.client.get(reverse(f"firstaid:{name}", args=[guide.slug])).status_code, 404)

    def test_unknown_guide_is_404_for_html_and_json(self):
        for name in ("guide_detail", "guide_detail_api"):
            self.assertEqual(self.client.get(reverse(f"firstaid:{name}", args=["missing"])).status_code, 404)

    def test_search_validation_empty_state_and_api_consistency(self):
        html = self.client.get(reverse("firstaid:guide_list"), {"q": "  CPR  "})
        api = self.client.get(reverse("firstaid:guide_list_api"), {"q": "  CPR  "})
        self.assertEqual([g.slug for g in html.context["page_obj"]], [g["slug"] for g in api.json()["results"]])
        self.assertEqual(api.json()["count"], 1)
        self.assertContains(self.client.get(reverse("firstaid:guide_list"), {"q": "no-such-guide"}), "No guides found")
        for name in ("guide_list", "guide_list_api"):
            self.assertEqual(self.client.get(reverse(f"firstaid:{name}"), {"q": "x" * 121}).status_code, 400)
            self.assertEqual(self.client.get(reverse(f"firstaid:{name}"), {"page": "bad"}).status_code, 400)

    def test_pagination_keeps_search_and_limits_response(self):
        for index in range(21):
            guide = FirstAidGuide.objects.create(**guide_values(slug=f"extra-{index}", title=f"Test extra {index:02d}"))
            FirstAidStep.objects.create(guide=guide, position=1, instruction="Test instruction")
        response = self.client.get(reverse("firstaid:guide_list"), {"q": "Test extra"})
        self.assertEqual(len(response.context["cards"]), 20)
        self.assertIn("q=Test+extra", response.context["next_query"])
        api = self.client.get(reverse("firstaid:guide_list_api"), {"q": "Test extra", "page": 2}).json()
        self.assertEqual(len(api["results"]), 1)
        self.assertIsNone(api["next"])
        self.assertIn("q=Test+extra", api["previous"])
        self.assertEqual(self.client.get(reverse("firstaid:guide_list"), {"page": 999}).status_code, 404)

    def test_api_details_include_ordered_steps_sources_and_null_clinical_review(self):
        data = self.client.get(reverse("firstaid:guide_detail_api", args=["adult-cpr"])).json()
        self.assertEqual([s["position"] for s in data["steps"]], [1, 2, 3, 4, 5])
        self.assertEqual(len(data["sources"]), 2)
        self.assertEqual(data["source_checked_on"], SOURCE_CHECKED_ON.isoformat())
        self.assertIsNone(data["clinical_reviewed_on"])

    def test_all_public_pages_and_apis_reject_post(self):
        for name, args in (("guide_list", []), ("guide_detail", ["adult-cpr"]), ("helplines", []),
                           ("guide_list_api", []), ("guide_detail_api", ["adult-cpr"]), ("helplines_api", [])):
            self.assertEqual(self.client.post(reverse(f"firstaid:{name}", args=args)).status_code, 405)

    def test_helplines_have_direct_calls_and_explicit_coverage(self):
        response = self.client.get(reverse("firstaid:helplines"))
        for number in ("112", "108", "102"):
            self.assertContains(response, f'href="tel:{number}"')
        self.assertContains(response, "State/UT dependent", count=2)
        self.assertContains(response, "No test calls were made")
        data = self.client.get(reverse("firstaid:helplines_api")).json()["results"]
        self.assertEqual([row["number"] for row in data], ["112", "108", "102"])
        self.assertTrue(data[0]["is_nationwide"])
        self.assertTrue(all(not row["is_nationwide"] for row in data[1:]))

    def test_inactive_unverified_future_unsafe_or_dummy_helplines_are_hidden(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        base = dict(name="Hidden line", number="110", region="Test only", is_active=True,
                    source_url="https://www.mha.gov.in/", verified_on=timezone.localdate())
        for index, changes in enumerate(({"is_active": False}, {"verified_on": None}, {"verified_on": tomorrow},
                                        {"source_url": "javascript:alert(1)"}, {"number": "000"}, {"number": "112?body=bad"})):
            line = EmergencyHelpline.objects.create(**(base | {"region": f"Test {index}"} | changes))
            self.assertNotIn(line, public_helplines())
        self.assertEqual(len(self.client.get(reverse("firstaid:helplines_api")).json()["results"]), 3)

    def test_content_is_escaped_and_unsafe_supporting_links_omitted(self):
        guide = FirstAidGuide.objects.get(slug="adult-cpr")
        guide.title = '<img src=x onerror=alert(1)>'
        guide.supporting_source_url = "javascript:alert(1)"
        guide.save()
        response = self.client.get(reverse("firstaid:guide_detail", args=[guide.slug]))
        self.assertContains(response, "&lt;img src=x onerror=alert(1)&gt;")
        self.assertNotContains(response, '<img src=x onerror=alert(1)>')
        self.assertNotContains(response, 'href="javascript:')
        self.assertEqual(len(response.context["sources"]), 1)

    def test_home_navigation_and_footer_use_real_library_pages(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'href="/first-aid/"')
        self.assertContains(response, 'href="/first-aid/helplines/"')
        self.assertNotContains(response, "First-aid guides are not available")


class FirstAidAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(username="fake-content-admin", password=None, email="")
        cls.staff = User.objects.create_user(username="fake-content-staff", is_staff=True)

    def guide_payload(self, **changes):
        values = {
            "title": "Test admin guide", "slug": "test-admin-guide", "summary": "Educational test only",
            "audience": "Adults", "source_url": "https://www.nhs.uk/conditions/burns-and-scalds/",
            "source_checked_on": timezone.localdate().isoformat(), "is_published": "on",
            "steps-TOTAL_FORMS": "1", "steps-INITIAL_FORMS": "0", "steps-MIN_NUM_FORMS": "0", "steps-MAX_NUM_FORMS": "1000",
            "steps-0-position": "1", "steps-0-heading": "Test heading", "steps-0-instruction": "Test instruction",
        }
        values.update(changes)
        return values

    def test_staff_without_permissions_cannot_manage_content(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("admin:firstaid_firstaidguide_changelist")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:firstaid_emergencyhelpline_changelist")).status_code, 403)

    def test_superuser_can_create_published_guide_with_inline_step(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:firstaid_firstaidguide_add"), self.guide_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FirstAidGuide.objects.get().steps.get().heading, "Test heading")

    def test_empty_or_gapped_published_steps_are_rejected_in_admin(self):
        self.client.force_login(self.admin)
        url = reverse("admin:firstaid_firstaidguide_add")
        response = self.client.post(url, self.guide_payload(**{"steps-TOTAL_FORMS": "0"}))
        self.assertContains(response, "at least one instruction step")
        response = self.client.post(url, self.guide_payload(**{"steps-0-position": "2"}))
        self.assertContains(response, "consecutively from 1")
        self.assertEqual(FirstAidGuide.objects.count(), 0)

    def test_duplicate_step_positions_are_rejected_in_admin(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:firstaid_firstaidguide_add"), self.guide_payload(**{
            "steps-TOTAL_FORMS": "2", "steps-1-position": "1", "steps-1-heading": "Duplicate", "steps-1-instruction": "Second",
        }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FirstAidGuide.objects.count(), 0)

    def test_active_helpline_without_verified_source_is_rejected_in_admin(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:firstaid_emergencyhelpline_add"), {
            "name": "Test invalid line", "number": "112", "region": "Test only", "is_active": "on",
        })
        self.assertContains(response, "official source and its check date")
        self.assertEqual(EmergencyHelpline.objects.count(), 0)
```

Stop here. Say **"next"** for the final mobile UI and accessibility polish pass.
