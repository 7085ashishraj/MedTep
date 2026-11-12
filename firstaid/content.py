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
