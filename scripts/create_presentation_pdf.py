"""Build a presentation-content handout. PDF libraries are authoring tools only."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "MEDTAP_Presentation_Guide_Ashish_Raj.pdf"
SOURCE = ROOT / "docs" / "MEDTAP_Presentation_Content.md"
PRESENTER = "Ashish Raj"
DATE = "19 November 2026"
DJANGO_TESTS = 219
JS_CHECKS = 41

SLIDES = [
    {
        "title": "MEDTAP: Medical Emergency App", "seconds": 20,
        "bullets": [
            "Presented by Ashish Raj",
            "Nearby healthcare discovery and emergency location sharing",
            "A Django web application with maps, private profiles and educational resources",
        ],
        "notes": "Good morning. I am Ashish Raj, and my project is MEDTAP, a medical emergency support web application. It brings nearby healthcare search, emergency contacts and location sharing into one interface. I will explain its design, demonstrate the main workflow and describe how the application runs locally with Django and SQLite.",
        "visual": "Use the project name and one clear subtitle. Open the home page after the introduction.",
        "evidence": "README.md; templates/core/home.html",
    },
    {
        "title": "Problem statement and objectives", "seconds": 35,
        "bullets": [
            "Project motivation: bring facility lookup, contacts and emergency information together",
            "Find mapped healthcare facilities around a chosen location",
            "Keep personal emergency information available through an authenticated account",
            "Help users save and manually share an SOS location",
        ],
        "notes": "The problem I chose is the need to move between separate resources when looking for care or preparing to share an emergency location. MEDTAP groups these tasks in one application. Its objectives are to make nearby facilities easier to find, keep a user's profile and contacts organized, and offer a clear SOS sharing flow. These are design objectives. I have not measured a reduction in emergency response time.",
        "visual": "Use a short problem statement followed by the three product objectives. Avoid unsupported statistics.",
        "evidence": "README.md; accounts/models.py; emergency/views.py",
    },
    {
        "title": "Users and application modules", "seconds": 35,
        "bullets": [
            "Visitors: facility search, maps, first-aid guides and helpline references",
            "Registered users: medical profile, emergency contacts and private SOS records",
            "Authorized operators: ambulance-request queue and status updates",
            "Administrators: controlled management of listings, content and permissions",
        ],
        "notes": "There are different access levels. A visitor can use the public healthcare directory and educational pages. A signed-in user can manage their own medical profile, emergency contacts and SOS records. An authorized operator can work with the project ambulance queue. Administrators manage data and permissions. This separation matters because private medical and location records must not become public directory data.",
        "visual": "Show the main navigation and identify which pages require an account or operator permission.",
        "evidence": "accounts/views.py; facilities/views.py; emergency/permissions.py; firstaid/views.py",
    },
    {
        "title": "Technology stack and architecture", "seconds": 45,
        "bullets": [
            "Frontend: Django templates, HTML, CSS, Bootstrap and JavaScript",
            "Maps: Leaflet with OpenStreetMap tiles",
            "Backend: Python, Django 6.1.3 and Django REST Framework",
            "Storage: SQLite for accounts, profiles, contacts and SOS records",
        ],
        "notes": "The application follows Django's model, template and view structure. The browser sends requests to Django views. Forms validate input, service functions implement search and workflow logic, and models store persistent records in SQLite. Public JSON endpoints also expose selected information. The facility service contacts Overpass on the server and sends normalized results to both the list and the map. The project runs locally using Django's development server.",
        "visual": "Explain the sequence verbally: browser request, Django view and service, database or directory, rendered response. A simple architecture slide can use those labels.",
        "evidence": "requirements.txt; config/urls.py; config/settings.py; facilities/services.py",
    },
    {
        "title": "Database design", "seconds": 35,
        "bullets": [
            "One user has one medical profile and can keep multiple emergency contacts",
            "A user can create multiple SOS records",
            "One SOS record can have one ambulance request with multiple status events",
            "Facilities can have multiple specialities; first-aid guides contain ordered steps",
        ],
        "notes": "The data model connects a user to one medical profile. Each profile can have several contacts, with a database constraint allowing only one primary contact. SOS records belong to their user. A one-to-one relationship prevents multiple ambulance requests for the same SOS, and status-event records preserve progress history. Facility specialities use a many-to-many relationship. Educational guides and helplines have their own source and publication fields.",
        "visual": "Use a relationship list or a small ER diagram based on these exact model relationships.",
        "evidence": "accounts/models.py; emergency/models.py; facilities/models.py; firstaid/models.py",
    },
    {
        "title": "How real facility search works", "seconds": 55,
        "bullets": [
            "Choose GPS permission, enter coordinates or search the map's centre",
            "Search real OpenStreetMap data through an Overpass provider and fallback",
            "Filter results and sort approximate distances using the Haversine formula",
            "Show source links, available contact details and transparent cache/outage status",
        ],
        "notes": "After validating coordinates, the backend sends a rounded area centre to the provider. The default radius is five kilometres, with live searches limited to 25 kilometres. The parser recognizes hospitals, clinics, pharmacies and blood banks. Search then applies filters, removes nearby duplicates and sorts by Haversine distance. Fresh snapshots last 15 minutes. During an outage, labelled older snapshots can remain available for up to 24 hours. Distance is straight-line distance. A listing does not verify beds, stock, current opening or emergency capacity.",
        "visual": "Show one facility card, its source link and its numbered map pin. Explain that missing phone or opening details remain unknown.",
        "evidence": "facilities/live.py; facilities/services.py; facilities/forms.py; static/js/facilities.js",
    },
    {
        "title": "Private profile and SOS sharing", "seconds": 45,
        "bullets": [
            "Store blood group, recorded allergies, medical conditions and emergency contacts",
            "Require sign-in and check ownership for private records",
            "Save an SOS coordinate snapshot with a timestamp",
            "Offer WhatsApp, SMS or copy links for the user to send manually",
        ],
        "notes": "The profile provides a place to record personal emergency information. The SOS workflow saves a location snapshot for the signed-in user and prepares sharing links. The user chooses a recipient and sends the message themselves. The app does not automatically alert every contact, and it does not insert the medical profile into the share message. Coordinates can appear in search URLs or saved SOS records, so the interface explains this. In the demonstration I will use fictional details and will not send a real message.",
        "visual": "Show a fictional profile and the SOS sharing controls. Stop before placing a call or sending a message.",
        "evidence": "accounts/models.py; accounts/views.py; emergency/services.py; static/js/sos.js",
    },
    {
        "title": "Ambulance workflow and educational resources", "seconds": 45,
        "bullets": [
            "Ambulance statuses: Requested, Accepted, On the way and Completed",
            "Operator permissions, status history and protection against stale edits",
            "Adult first-aid guides with source links and source-check dates",
            "Helpline references include their region or service coverage",
        ],
        "notes": "The ambulance module demonstrates a controlled request workflow. An authorized operator advances a request one step at a time, and the system records the change. A version check prevents an older edit from overwriting a newer update. This is a project workflow, and no ambulance provider is connected for real dispatch. The educational module stores adult first-aid summaries and helpline references with source information. A source-check date is separate from a clinical-review date.",
        "visual": "Show an existing demonstration status timeline or the first-aid library. Explain the dispatch limitation visibly.",
        "evidence": "emergency/ambulance_services.py; emergency/models.py; firstaid/models.py; FIRST_AID_SOURCES.md",
    },
    {
        "title": "Testing and reliability", "seconds": 40,
        "bullets": [
            f"Project verification covers {DJANGO_TESTS} Django tests and {JS_CHECKS} JavaScript checks",
            "Tests cover validation, ownership, permissions, CSRF and workflow consistency",
            "Directory tests cover malformed responses, fallback, caching and provider outages",
            "A documented live test returned 787 mapped listings within 5 km of central Bengaluru",
        ],
        "notes": "The verification script runs system checks, migration checks, Django tests and the frontend checks. Automated directory tests use mocks so an external outage does not make the test suite unpredictable. A separate real-data check on 18 November 2026 returned 787 listings and successful HTML and API responses. That number describes one area and time. It is not a benchmark, a guarantee of complete coverage or proof that the public provider is always available.",
        "visual": "Use the test totals as implementation evidence. Label the live example with its area, radius and date.",
        "evidence": "scripts/check_project.py; core/test_workflows.py; facilities/test_live.py; README.md verification record",
    },
    {
        "title": "Local setup and demonstration environment", "seconds": 45,
        "bullets": [
            "Run the application locally using Python and Django",
            "Store persistent records in the local db.sqlite3 database",
            "Use management commands to initialize the database and educational resources",
            "Demonstrate browser location permission or enter a public sample location manually",
        ],
        "notes": "This version runs locally with SQLite and does not require a separate database server. The setup creates a Python environment, installs the three application dependencies and applies Django migrations. Management commands add educational references and the operator permission group. I start the application on localhost and use fictional records for the demonstration. Facility searches still need an internet connection to reach the external directory and map services. I can enter a public sample location manually if device location is unavailable.",
        "visual": "Show the local application's home page at http://127.0.0.1:8000/. Keep the .env file and real personal records out of view.",
        "evidence": "README.md local setup; requirements.txt; config/settings.py; manage.py",
    },
    {
        "title": "Live demonstration", "seconds": 90,
        "bullets": [
            "Open the home page and a rehearsed facility search",
            "Match a facility card with its map pin and original source",
            "Show a fictional user's profile and an SOS record without sending a message",
            "Open a project ambulance timeline or a first-aid guide, then return to the presentation",
        ],
        "notes": "For the first 30 seconds I will show facility results, a map pin and the source link. For the next 30 seconds I will show a fictional profile and the saved SOS sharing page. I will use the final 30 seconds for the ambulance timeline if an operator account is configured, or a first-aid guide otherwise. I will rehearse the search beforehand. If the provider fails, I will explain the outage message and show a dated screenshot or available labelled cached results instead of presenting invented data.",
        "visual": "Before presenting, open the relevant tabs and sign in to a fictional demo account. A public sample search can use 12.9716, 77.5946 with a 5 km radius.",
        "evidence": "README.md main pages; templates/facilities/nearby.html; templates/emergency/detail.html; templates/firstaid/guide_list.html",
    },
    {
        "title": "Limitations, future work and conclusion", "seconds": 40,
        "bullets": [
            "Current limits: public-provider availability, map coverage and location accuracy",
            "No verified stock, bed availability, automatic alerts or real ambulance dispatch",
            "Future work: managed data access, verified provider partnerships and shared caching",
            "MEDTAP combines nearby-care discovery with private emergency preparation in one web app",
        ],
        "notes": "The main limitations are incomplete map data, occasional provider outages and uncertainty in device location. Real dispatch and verified hospital capacity would require operational partnerships, not just an extra screen. My next steps would be dependable directory access, shared caching for more users, and independently reviewed educational content. MEDTAP demonstrates an integrated Django application for finding mapped care and preparing emergency information, while making these limits clear. Thank you. I am ready for questions.",
        "visual": "End with the project name, two or three next steps and a simple Questions heading.",
        "evidence": "README.md scope and privacy; facilities/live.py; emergency/ambulance_services.py",
    },
]

VIVA = [
    ("Why did you choose Django?", "Django supplies authentication, forms, ORM models, migrations, admin and CSRF protection. Its app structure also keeps accounts, facilities, emergency workflows and educational content organized."),
    ("Is the healthcare data real?", "Facility searches read OpenStreetMap records through Overpass. The app links to the original listing and keeps missing details unknown. Generated sample facilities are excluded from normal public search."),
    ("Why use the Haversine formula?", "It estimates great-circle distance from latitude and longitude without requiring a paid routing API. It gives a portable way to sort nearby results, but it does not estimate road distance or travel time."),
    ("Does SOS automatically contact someone?", "No. SOS saves a signed-in user's coordinate snapshot and prepares sharing controls. The user selects the recipient and sends the WhatsApp or SMS message themselves."),
    ("Does the ambulance module book a real ambulance?", "No. It records a project request and an operator-controlled status timeline. Real booking would require a connected provider and an operational dispatch process."),
    ("Why does this project use SQLite?", "SQLite stores the project's records in a local database file and works with Django without a separate database server. This makes local setup and a small demonstration straightforward."),
    ("What happens when the directory provider fails?", "The service tries a configured fallback, briefly cools down failed hosts and can show clearly labelled cached snapshots. If no usable results exist, it reports unavailability rather than a successful empty search."),
    ("What would you improve for a public launch?", "I would add dependable data-provider capacity, shared caching and rate limiting, tested backup and retention procedures, and reviewed content. Real dispatch and verified capacity need provider partnerships."),
]

REFERENCES = [
    ("Project implementation", "README.md; requirements.txt; accounts/models.py; facilities/live.py; facilities/services.py; emergency/ambulance_services.py; firstaid/models.py; config/settings.py; core/test_workflows.py"),
    ("Local setup and verification", "README.md local setup and verification sections; scripts/check_project.py; facilities/test_live.py; core/test_database.py"),
    ("OpenStreetMap attribution", "https://www.openstreetmap.org/copyright"),
    ("Project source provenance", "FIRST_AID_SOURCES.md and THIRD_PARTY.md in the repository. Medical source dates remain those recorded by the project. This guide does not claim a new clinical review."),
]


def minute_label(seconds):
    return f"{seconds // 60}:{seconds % 60:02d}"


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    font_root = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Body", str(font_root / "calibri.ttf")))
    pdfmetrics.registerFont(TTFont("BodyBold", str(font_root / "calibrib.ttf")))
    pdfmetrics.registerFont(TTFont("BodyItalic", str(font_root / "calibrii.ttf")))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold", italic="BodyItalic", boldItalic="BodyBold")
    ink = colors.HexColor("#15333F")
    teal = colors.HexColor("#17665D")
    muted = colors.HexColor("#526375")
    styles = {
        "title": ParagraphStyle("title", fontName="BodyBold", fontSize=29, leading=34, textColor=ink, spaceAfter=19),
        "cover": ParagraphStyle("cover", fontName="BodyBold", fontSize=54, leading=60, textColor=ink, spaceAfter=18),
        "subtitle": ParagraphStyle("subtitle", fontName="Body", fontSize=23, leading=29, textColor=teal, spaceAfter=18),
        "section": ParagraphStyle("section", fontName="BodyBold", fontSize=10.5, leading=14, textColor=teal, spaceBefore=18, spaceAfter=8),
        "body": ParagraphStyle("body", fontName="Body", fontSize=12.2, leading=18, textColor=ink, spaceAfter=10),
        "bullet": ParagraphStyle("bullet", fontName="Body", fontSize=13.2, leading=18.5, textColor=ink, leftIndent=12, firstLineIndent=-12, spaceAfter=9),
        "small": ParagraphStyle("small", fontName="Body", fontSize=10, leading=14, textColor=muted, spaceAfter=8),
        "table": ParagraphStyle("table", fontName="Body", fontSize=11.2, leading=14, textColor=ink),
        "qa": ParagraphStyle("qa", fontName="Body", fontSize=11.1, leading=15, textColor=ink, spaceAfter=13),
    }
    def p(text, style="body"):
        return Paragraph(escape(text), styles[style])

    width, height = A4
    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(muted)
        canvas.setFont("Body", 9)
        canvas.drawString(48, height - 31, "MEDTAP / PRESENTATION CONTENT")
        canvas.drawRightString(width - 48, height - 31, PRESENTER)
        canvas.drawString(48, 26, DATE)
        canvas.drawRightString(width - 48, 26, f"{doc.page:02d}")
        canvas.restoreState()

    document = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=48, rightMargin=48,
                              topMargin=54, bottomMargin=47, title="MEDTAP Presentation Guide",
                              author=PRESENTER, subject="8-10 minute project presentation with speaker notes")
    frame = Frame(48, 47, width - 96, height - 101, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    document.addPageTemplates(PageTemplate(id="guide", frames=frame, onPage=decorate))
    story = []
    story += [Spacer(1, 73), p("PROJECT PRESENTATION GUIDE", "section"), p("MEDTAP", "cover"),
              p("Medical Emergency App", "subtitle"), p(PRESENTER, "subtitle"), Spacer(1, 20),
              p("12 slides for an 8-10 minute presentation. Includes ready-to-use slide points, speaking notes, a live-demo sequence and viva answers."),
              Spacer(1, 16), p("PRESENTATION FOCUS", "section"),
              p("Explain the problem, show the working application, describe the technology and data flow, and distinguish implemented features from future operational integrations."),
              p("Demonstration environment: the local Django application with SQLite. This guide focuses on implemented features and the local demo workflow.", "small"),
              PageBreak()]
    total = sum(slide["seconds"] for slide in SLIDES)
    story += [p("Presentation sequence", "title"), p(f"Target speaking time: {minute_label(total)}. Allow questions after the presentation. The live demo has a 90-second allowance."), Spacer(1, 8)]
    rows = [[p("SLIDE", "small"), p("TOPIC", "small"), p("TIME", "small")]]
    for index, slide in enumerate(SLIDES, 1):
        rows.append([p(f"{index:02d}", "table"), p(slide["title"], "table"), p(minute_label(slide["seconds"]), "table")])
    table = Table(rows, colWidths=[45, width - 201, 60])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, 0), .5, colors.HexColor("#D8E3E7")),
    ]))
    story += [table, p("How to use this guide", "section"), p("Copy only the 'On the slide' points into your slides. Rehearse the speaking notes in your own words. Treat the visual suggestions as optional aids. Use the appendices for preparation and questions, rather than reading them during the timed talk.", "small"), PageBreak()]
    markdown = [f"# MEDTAP presentation content\n\nPresenter: {PRESENTER}\n\nDuration: 8-10 minutes (planned {minute_label(total)}).\n\nPrepared: {DATE}\n"]
    for index, slide in enumerate(SLIDES, 1):
        story += [p(f"SLIDE {index:02d} / {len(SLIDES):02d}    -    {slide['seconds']} SECONDS", "section"),
                  p(slide["title"], "title"), p("ON THE SLIDE", "section")]
        story.extend(p("- " + bullet, "bullet") for bullet in slide["bullets"])
        story += [p("SPEAKING NOTES", "section"), p(slide["notes"]),
                  p("VISUAL OR DEMO SUGGESTION", "section"), p(slide["visual"], "small"),
                  p("Implementation evidence: " + slide["evidence"], "small"), PageBreak()]
        markdown += [f"\n## Slide {index}: {slide['title']} ({slide['seconds']} seconds)\n",
                     "\n".join("- " + bullet for bullet in slide["bullets"]),
                     "\n\nSpeaking notes: " + slide["notes"],
                     "\n\nVisual/demo: " + slide["visual"], "\n\nEvidence: " + slide["evidence"] + "\n"]
    story += [p("Viva and discussion", "title"), p("These answers describe the implemented project and its local demonstration environment.", "small")]
    for question, answer in VIVA:
        story.append(Paragraph(f"<b>{escape(question)}</b><br/>{escape(answer)}", styles["qa"]))
    story.append(PageBreak())
    story += [p("Local demonstration checklist", "title"), p("Use the existing Django application and SQLite database for the presentation. Prepare the browser tabs before the timed demonstration."),
              p("PREPARATION SEQUENCE", "section")]
    steps = [
        "Follow the local setup steps in README.md. Keep the local .env file and its secret key private.",
        "Apply database migrations with python manage.py migrate. The application stores its records in db.sqlite3.",
        "If needed, add educational references with python manage.py seed_firstaid and prepare the operator group with python manage.py setup_ambulance_operators.",
        "Start the app with python manage.py runserver 127.0.0.1:8000 and open http://127.0.0.1:8000/ in the browser.",
        "Sign in with a fictional demonstration account and open the profile, SOS page and a rehearsed facility search in separate tabs.",
        "Show facility sources and the map, then demonstrate an SOS record without sending a message. Finish with a first-aid guide or a prepared operator timeline.",
    ]
    story.extend(p(f"{index}. {step}") for index, step in enumerate(steps, 1))
    story += [p("DEMO FALLBACK", "section"),
              p("Internet access is required for directory lookups and map tiles. If the provider is unavailable, show the application's outage message, a clearly labelled cached result or a dated screenshot. Use fictional records and stop before making calls or sending messages.", "small"),
              p("The application runs locally with Django and SQLite. The presentation makes no claim of a live hosted service.", "small"), PageBreak()]
    story += [p("References and rehearsal", "title"), p("Repository evidence supports the feature descriptions. The documented live facility example is from 18 November 2026. This guide describes the local application.", "small")]
    for name, target in REFERENCES:
        story += [p(name, "section"), p(target, "small")]
    story += [p("FINAL REHEARSAL", "section"),
              p("Keep the talk near nine minutes. Open the demo tabs in advance. Never display credentials or real medical records. Present cached data with its retrieval time and use fictional details for the local demonstration.", "small")]
    document.build(story)
    markdown += ["\n## Viva questions\n"]
    markdown.extend(f"\n### {question}\n\n{answer}\n" for question, answer in VIVA)
    markdown += ["\n## Local demonstration\n\nFollow the local setup in README.md. Run the Django application with SQLite at http://127.0.0.1:8000/ and rehearse with fictional records.\n"]
    SOURCE.write_text("\n".join(markdown), encoding="utf-8")
    print(f"Created {OUTPUT}")
    print(f"Created editable content {SOURCE}")


if __name__ == "__main__":
    build()
