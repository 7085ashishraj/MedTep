# First-aid and helpline source notes

Sources checked on **12 November 2026**. This is a source-check date, not a clinical
review of MEDTAP's text. All five seeded guides have `reviewed_on = None` and say
that clinical review of the summary is not recorded. The text is an original,
brief educational summary of the linked guidance, scoped to adults aged 18+.
No source diagrams, photographs, logos or complete articles are reproduced.

## Guide provenance

| Guide | Main and supporting references |
| --- | --- |
| Adult CPR | [Resuscitation Council UK: adult BLS, 2025](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/adult-basic-life-support-guidelines), [RCUK public CPR guide](https://www.resus.org.uk/public-resource/how-do-cpr), [ERC adult BLS, 2025](https://www.erc.edu/media/wrhj5sye/gl2025-04-bls-e.pdf) |
| Severe external bleeding | [St John Ambulance: severe bleeding](https://www.sja.org.uk/first-aid-advice/severe-bleeding/), [RCUK first-aid guidelines, 2025](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines) |
| Thermal burns/scalds | [NHS: burns and scalds](https://www.nhs.uk/conditions/burns-and-scalds/), [St John Ambulance: burns/scalds](https://www.sja.org.uk/first-aid-advice/burns-and-scalds/), [Queen Victoria Hospital NHS: burn first aid](https://www.qvh.nhs.uk/our-services/plastic-surgery-and-burns/burns/burns-first-aid-and-prevention/) |
| Adult choking | [St John Ambulance: choking](https://www.sja.org.uk/first-aid-advice/choking/), [RCUK BLS FAQs](https://www.resus.org.uk/professional-library/faqs/faqs-basic-life-support-cpr), [RCUK first-aid guidelines, 2025](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines) |
| Recovery position | [St John Ambulance: recovery position](https://www.sja.org.uk/first-aid-advice/recovery-position/), [RCUK first-aid guidelines, 2025](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/first-aid-guidelines) |

The two primary/supporting links are also stored on each guide and shown publicly.
The additional references above document cross-checks and specific qualifications.
RCUK's pregnancy/choking FAQ carries a July 2026 update. NHS's burns page reports
a March 2026 review. Those organisations' review dates are not imported as clinical
review dates for our own summaries.

## Scope and localisation

The seeded pages cover adult CPR, severe external bleeding, thermal burns/scalds,
adult choking and the recovery position. They distinguish abnormal breathing from
normal breathing, include choking exceptions for pregnancy, and explicitly avoid
presenting the thermal-burn guide as treatment for chemical/electrical injury.
Infant/child, drowning and other specialist protocols are outside these summaries.
The pages direct the user to the emergency dispatcher and original guidance.

UK source articles may use 999 or 111. MEDTAP displays India's 112 emergency
shortcut instead, based on the Ministry of Home Affairs reference below. This
localisation is explicit in the UI; it does not imply NHS/RCUK endorsement or a
connection between MEDTAP and any government dispatch system.

## Indian helpline references

- **112:** [Ministry of Home Affairs ERSS](https://www.mha.gov.in/emergency-response-support-system-erss)
  describes nationwide unified emergency access, including health emergencies.
- **108 and 102:** [National Health Mission: ERS/patient transport](https://nhm.gov.in/nhm/index1.php?lang=1&level=2&lid=189&sublinkid=1217)
  describes 108 primarily as emergency response and 102 as basic patient transport,
  particularly for pregnant women/children. Its statement about participating
  states/UTs concerns availability of 108 **or** 102; it does not establish that
  both numbers operate identically everywhere. Both cards are labelled state/UT
  dependent, with no promise of capacity, response time or successful connection.

No test call was made. These are real official helpline references, not FAKE
facility phone numbers. The facility sample-data rules remain unchanged.

## Maintaining the content

`seed_firstaid` uses a fixed evidence date from `firstaid/content.py`. Running it
later does not claim that a fresh source check happened. Existing guides, steps,
publication flags, dates and helpline entries are preserved on repeat runs.
The command does not scrape sources, overwrite staff edits, automatically expire
content or perform clinical review. Publication/source dates must be maintained
deliberately in admin after checking the underlying references. Changes in clinical
guidance require content review; passing software tests is not medical validation.
Only record a clinical review date when a qualified clinician actually reviewed
this app's wording. No such review is recorded for this seeded release.
