# Third-party assets

First-aid text consists of original brief educational summaries with direct source
links; no external medical illustrations or complete articles are redistributed.
See [FIRST_AID_SOURCES.md](FIRST_AID_SOURCES.md) for the NHS, St John Ambulance,
Resuscitation Council UK, ERC, MHA and NHM references checked on 12 November 2026.
A source-check date does not claim a clinical review of MEDTAP's wording.

SOS sharing uses links rather than an external messaging API. Link construction
follows [WhatsApp click-to-chat documentation](https://faq.whatsapp.com/5913398998672934),
[Google Maps URL documentation](https://developers.google.com/maps/documentation/urls/get-started)
and the [SMS URI scheme, RFC 5724](https://www.rfc-editor.org/rfc/rfc5724).
WhatsApp direct-recipient links require an international number; we do not guess
a country code from a local contact number. SMS composer/body support varies by
device and app, so a copyable message remains available. No third-party request is
made by the server to deliver a message. Users choose whether to open a sharing link.

Core Bootstrap assets are served locally so the layout and navigation do not depend
on a CDN during use. Keep the supplied licenses when redistributing the project.

- Leaflet 1.9.4 stable: https://leafletjs.com/reference-1.9.4.html — BSD-2-Clause;
  license at `static/vendor/leaflet/LICENSE`. JS, CSS and supporting images are
  vendored from the official `leaflet@1.9.4` npm package via jsDelivr. The beta 2.0
  release is not used. Leaflet positions markers with runtime styles; our custom
  templates and scripts contain no inline styling.
- OpenStreetMap tiles: https://tile.openstreetmap.org/{z}/{x}/{y}.png. Data ©
  OpenStreetMap contributors (https://www.openstreetmap.org/copyright). The page
  follows https://operations.osmfoundation.org/policies/tiles/: visible attribution,
  ordinary browser caching, origin-only cross-domain Referer, no bulk download,
  offline cache feature or prefetch. This community tile service has no uptime
  guarantee. Review provider terms and capacity before a larger public deployment.

- Bootstrap 5.3.8: https://getbootstrap.com/ — MIT; license at
  `static/vendor/bootstrap/LICENSE`. CSS and bundle from the official npm package,
  downloaded via jsDelivr.
- Bootstrap Icons 1.13.1: https://icons.getbootstrap.com/ — MIT; license at
  `static/vendor/bootstrap-icons/LICENSE`. SVG sprite from the official npm package,
  downloaded via jsDelivr. The ambulance action uses Bootstrap's truck-front icon.
- Inter: https://fonts.google.com/specimen/Inter — SIL Open Font License. The base
  template requests the Google Fonts stylesheet. If it cannot load, the page falls
  back to system fonts. No external photos or hospital branding are used.

Design references: NHS Design System (https://service-manual.nhs.uk/design-system),
Apollo 24|7 (https://www.apollo247.com/) and Cleveland Clinic
(https://my.clevelandclinic.org/). The layout and copy are original to this project;
there is no affiliation with those organisations.

The current visual redesign is principally inspired by Mediso by Muzamal Hussain:
https://www.framer.com/marketplace/templates/mediso/. VitalCare and Healthio were
also considered. The project uses an original Django layout and stylesheet; it
does not distribute a Framer template or its source assets.

`static/img/care-professional-v2.png` is an original AI-generated illustrative
portrait made with the built-in imagegen tool. It is not a listed provider or a
depiction of an identified doctor. The prompt and asset details are recorded in
UI_REDESIGN.md. Framer preview images in the ignored tooling cache were used only
for reference and are not served by the app.
