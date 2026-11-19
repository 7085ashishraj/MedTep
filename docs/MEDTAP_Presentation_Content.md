# MEDTAP presentation content

Presenter: Ashish Raj

Duration: 8-10 minutes (planned 8:50).

Prepared: 19 November 2026


## Slide 1: MEDTAP: Medical Emergency App (20 seconds)

- Presented by Ashish Raj
- Nearby healthcare discovery and emergency location sharing
- A Django web application with maps, private profiles and educational resources


Speaking notes: Good morning. I am Ashish Raj, and my project is MEDTAP, a medical emergency support web application. It brings nearby healthcare search, emergency contacts and location sharing into one interface. I will explain its design, demonstrate the main workflow and describe how the application runs locally with Django and SQLite.


Visual/demo: Use the project name and one clear subtitle. Open the home page after the introduction.


Evidence: README.md; templates/core/home.html


## Slide 2: Problem statement and objectives (35 seconds)

- Project motivation: bring facility lookup, contacts and emergency information together
- Find mapped healthcare facilities around a chosen location
- Keep personal emergency information available through an authenticated account
- Help users save and manually share an SOS location


Speaking notes: The problem I chose is the need to move between separate resources when looking for care or preparing to share an emergency location. MEDTAP groups these tasks in one application. Its objectives are to make nearby facilities easier to find, keep a user's profile and contacts organized, and offer a clear SOS sharing flow. These are design objectives. I have not measured a reduction in emergency response time.


Visual/demo: Use a short problem statement followed by the three product objectives. Avoid unsupported statistics.


Evidence: README.md; accounts/models.py; emergency/views.py


## Slide 3: Users and application modules (35 seconds)

- Visitors: facility search, maps, first-aid guides and helpline references
- Registered users: medical profile, emergency contacts and private SOS records
- Authorized operators: ambulance-request queue and status updates
- Administrators: controlled management of listings, content and permissions


Speaking notes: There are different access levels. A visitor can use the public healthcare directory and educational pages. A signed-in user can manage their own medical profile, emergency contacts and SOS records. An authorized operator can work with the project ambulance queue. Administrators manage data and permissions. This separation matters because private medical and location records must not become public directory data.


Visual/demo: Show the main navigation and identify which pages require an account or operator permission.


Evidence: accounts/views.py; facilities/views.py; emergency/permissions.py; firstaid/views.py


## Slide 4: Technology stack and architecture (45 seconds)

- Frontend: Django templates, HTML, CSS, Bootstrap and JavaScript
- Maps: Leaflet with OpenStreetMap tiles
- Backend: Python, Django 6.1.3 and Django REST Framework
- Storage: SQLite for accounts, profiles, contacts and SOS records


Speaking notes: The application follows Django's model, template and view structure. The browser sends requests to Django views. Forms validate input, service functions implement search and workflow logic, and models store persistent records in SQLite. Public JSON endpoints also expose selected information. The facility service contacts Overpass on the server and sends normalized results to both the list and the map. The project runs locally using Django's development server.


Visual/demo: Explain the sequence verbally: browser request, Django view and service, database or directory, rendered response. A simple architecture slide can use those labels.


Evidence: requirements.txt; config/urls.py; config/settings.py; facilities/services.py


## Slide 5: Database design (35 seconds)

- One user has one medical profile and can keep multiple emergency contacts
- A user can create multiple SOS records
- One SOS record can have one ambulance request with multiple status events
- Facilities can have multiple specialities; first-aid guides contain ordered steps


Speaking notes: The data model connects a user to one medical profile. Each profile can have several contacts, with a database constraint allowing only one primary contact. SOS records belong to their user. A one-to-one relationship prevents multiple ambulance requests for the same SOS, and status-event records preserve progress history. Facility specialities use a many-to-many relationship. Educational guides and helplines have their own source and publication fields.


Visual/demo: Use a relationship list or a small ER diagram based on these exact model relationships.


Evidence: accounts/models.py; emergency/models.py; facilities/models.py; firstaid/models.py


## Slide 6: How real facility search works (55 seconds)

- Choose GPS permission, enter coordinates or search the map's centre
- Search real OpenStreetMap data through an Overpass provider and fallback
- Filter results and sort approximate distances using the Haversine formula
- Show source links, available contact details and transparent cache/outage status


Speaking notes: After validating coordinates, the backend sends a rounded area centre to the provider. The default radius is five kilometres, with live searches limited to 25 kilometres. The parser recognizes hospitals, clinics, pharmacies and blood banks. Search then applies filters, removes nearby duplicates and sorts by Haversine distance. Fresh snapshots last 15 minutes. During an outage, labelled older snapshots can remain available for up to 24 hours. Distance is straight-line distance. A listing does not verify beds, stock, current opening or emergency capacity.


Visual/demo: Show one facility card, its source link and its numbered map pin. Explain that missing phone or opening details remain unknown.


Evidence: facilities/live.py; facilities/services.py; facilities/forms.py; static/js/facilities.js


## Slide 7: Private profile and SOS sharing (45 seconds)

- Store blood group, recorded allergies, medical conditions and emergency contacts
- Require sign-in and check ownership for private records
- Save an SOS coordinate snapshot with a timestamp
- Offer WhatsApp, SMS or copy links for the user to send manually


Speaking notes: The profile provides a place to record personal emergency information. The SOS workflow saves a location snapshot for the signed-in user and prepares sharing links. The user chooses a recipient and sends the message themselves. The app does not automatically alert every contact, and it does not insert the medical profile into the share message. Coordinates can appear in search URLs or saved SOS records, so the interface explains this. In the demonstration I will use fictional details and will not send a real message.


Visual/demo: Show a fictional profile and the SOS sharing controls. Stop before placing a call or sending a message.


Evidence: accounts/models.py; accounts/views.py; emergency/services.py; static/js/sos.js


## Slide 8: Ambulance workflow and educational resources (45 seconds)

- Ambulance statuses: Requested, Accepted, On the way and Completed
- Operator permissions, status history and protection against stale edits
- Adult first-aid guides with source links and source-check dates
- Helpline references include their region or service coverage


Speaking notes: The ambulance module demonstrates a controlled request workflow. An authorized operator advances a request one step at a time, and the system records the change. A version check prevents an older edit from overwriting a newer update. This is a project workflow, and no ambulance provider is connected for real dispatch. The educational module stores adult first-aid summaries and helpline references with source information. A source-check date is separate from a clinical-review date.


Visual/demo: Show an existing demonstration status timeline or the first-aid library. Explain the dispatch limitation visibly.


Evidence: emergency/ambulance_services.py; emergency/models.py; firstaid/models.py; FIRST_AID_SOURCES.md


## Slide 9: Testing and reliability (40 seconds)

- Project verification covers 219 Django tests and 41 JavaScript checks
- Tests cover validation, ownership, permissions, CSRF and workflow consistency
- Directory tests cover malformed responses, fallback, caching and provider outages
- A documented live test returned 787 mapped listings within 5 km of central Bengaluru


Speaking notes: The verification script runs system checks, migration checks, Django tests and the frontend checks. Automated directory tests use mocks so an external outage does not make the test suite unpredictable. A separate real-data check on 18 November 2026 returned 787 listings and successful HTML and API responses. That number describes one area and time. It is not a benchmark, a guarantee of complete coverage or proof that the public provider is always available.


Visual/demo: Use the test totals as implementation evidence. Label the live example with its area, radius and date.


Evidence: scripts/check_project.py; core/test_workflows.py; facilities/test_live.py; README.md verification record


## Slide 10: Local setup and demonstration environment (45 seconds)

- Run the application locally using Python and Django
- Store persistent records in the local db.sqlite3 database
- Use management commands to initialize the database and educational resources
- Demonstrate browser location permission or enter a public sample location manually


Speaking notes: This version runs locally with SQLite and does not require a separate database server. The setup creates a Python environment, installs the three application dependencies and applies Django migrations. Management commands add educational references and the operator permission group. I start the application on localhost and use fictional records for the demonstration. Facility searches still need an internet connection to reach the external directory and map services. I can enter a public sample location manually if device location is unavailable.


Visual/demo: Show the local application's home page at http://127.0.0.1:8000/. Keep the .env file and real personal records out of view.


Evidence: README.md local setup; requirements.txt; config/settings.py; manage.py


## Slide 11: Live demonstration (90 seconds)

- Open the home page and a rehearsed facility search
- Match a facility card with its map pin and original source
- Show a fictional user's profile and an SOS record without sending a message
- Open a project ambulance timeline or a first-aid guide, then return to the presentation


Speaking notes: For the first 30 seconds I will show facility results, a map pin and the source link. For the next 30 seconds I will show a fictional profile and the saved SOS sharing page. I will use the final 30 seconds for the ambulance timeline if an operator account is configured, or a first-aid guide otherwise. I will rehearse the search beforehand. If the provider fails, I will explain the outage message and show a dated screenshot or available labelled cached results instead of presenting invented data.


Visual/demo: Before presenting, open the relevant tabs and sign in to a fictional demo account. A public sample search can use 12.9716, 77.5946 with a 5 km radius.


Evidence: README.md main pages; templates/facilities/nearby.html; templates/emergency/detail.html; templates/firstaid/guide_list.html


## Slide 12: Limitations, future work and conclusion (40 seconds)

- Current limits: public-provider availability, map coverage and location accuracy
- No verified stock, bed availability, automatic alerts or real ambulance dispatch
- Future work: managed data access, verified provider partnerships and shared caching
- MEDTAP combines nearby-care discovery with private emergency preparation in one web app


Speaking notes: The main limitations are incomplete map data, occasional provider outages and uncertainty in device location. Real dispatch and verified hospital capacity would require operational partnerships, not just an extra screen. My next steps would be dependable directory access, shared caching for more users, and independently reviewed educational content. MEDTAP demonstrates an integrated Django application for finding mapped care and preparing emergency information, while making these limits clear. Thank you. I am ready for questions.


Visual/demo: End with the project name, two or three next steps and a simple Questions heading.


Evidence: README.md scope and privacy; facilities/live.py; emergency/ambulance_services.py


## Viva questions


### Why did you choose Django?

Django supplies authentication, forms, ORM models, migrations, admin and CSRF protection. Its app structure also keeps accounts, facilities, emergency workflows and educational content organized.


### Is the healthcare data real?

Facility searches read OpenStreetMap records through Overpass. The app links to the original listing and keeps missing details unknown. Generated sample facilities are excluded from normal public search.


### Why use the Haversine formula?

It estimates great-circle distance from latitude and longitude without requiring a paid routing API. It gives a portable way to sort nearby results, but it does not estimate road distance or travel time.


### Does SOS automatically contact someone?

No. SOS saves a signed-in user's coordinate snapshot and prepares sharing controls. The user selects the recipient and sends the WhatsApp or SMS message themselves.


### Does the ambulance module book a real ambulance?

No. It records a project request and an operator-controlled status timeline. Real booking would require a connected provider and an operational dispatch process.


### Why does this project use SQLite?

SQLite stores the project's records in a local database file and works with Django without a separate database server. This makes local setup and a small demonstration straightforward.


### What happens when the directory provider fails?

The service tries a configured fallback, briefly cools down failed hosts and can show clearly labelled cached snapshots. If no usable results exist, it reports unavailability rather than a successful empty search.


### What would you improve for a public launch?

I would add dependable data-provider capacity, shared caching and rate limiting, tested backup and retention procedures, and reviewed content. Real dispatch and verified capacity need provider partnerships.


## Local demonstration

Follow the local setup in README.md. Run the Django application with SQLite at http://127.0.0.1:8000/ and rehearse with fictional records.
