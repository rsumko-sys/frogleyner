# -*- coding: utf-8 -*-
"""
ROMAN SUMKO — MILTECH / DEFENSE-ADJACENT CV PACK EXPORTER
US defense tech / miltech HR style

Exports:
    1) master_ats_cv.txt
    2) cv_military_liaison_user_liaison.txt
    3) cv_field_validation_testing_specialist.txt
    4) cv_operational_integration_specialist.txt
    5) cv_field_operations_deployment_specialist.txt
    6) cover_letter_template.txt
    7) linkedin_about.txt
    8) interview_prep_sheet.txt

Usage:
- Edit text blocks below
- Run the script
- Files will be created in ./output_cv_pack/

Also used as "data for analysis" by the privacy agent: PROFILE and identifiers
can feed known_accounts / OSINT allowed_identifiers (see profile_identifiers.yaml).
"""

from pathlib import Path
from textwrap import dedent

# Output next to this script so it works from any cwd
OUTPUT_DIR = Path(__file__).resolve().parent / "output_cv_pack"


PROFILE = {
    "name": "ROMAN SUMKO",
    "location": "Kyiv, Ukraine",
    "email": "rsumko@gmail.com",
    "signal": "gnz_trx_2026.25",
    "phone": "+380 96 586 8873",
    "phone_placeholder": "[ADD PHONE]",
    "open_to": "Open to relocation / travel",
    "linkedin": "[ADD LINK]",
    "website": "[OPTIONAL]",
}

AVAILABILITY_BLOCK = [
    "Open to relocation / travel",
    "Available for field assignments and international travel",
]

COMPLIANCE_BLOCK = [
    "[Eligible to work in EU/UK/US: ADD DETAILS]",
    "No security clearance; able to undergo vetting",
]

MASTER_DATA = {
    "headline": "FIELD OPERATIONS / DEPLOYMENT SPECIALIST | Military Liaison | Field Validation | Operational Integration",

    "summary": [
        "Field operations and deployment support professional with 17+ years of experience across logistics, production, and high-pressure execution, including 3+ years working in active combat-zone conditions in Ukraine since 2022.",
        "Experienced in field coordination, movement and access planning, operational logistics, user liaison, field validation, interview support, and practical execution in unstable environments.",
        "Strong at working between end users, local actors, technical teams, and decision-makers under pressure.",
        "Also builds lightweight applied tools and rapid prototypes for operational workflows, including coordinate handling, data parsing, workflow automation, and mapping-oriented support.",
        "Best suited for roles where field reality, deployment friction, user feedback, and practical problem-solving matter more than presentation language.",
    ],

    "core_capabilities": [
        "Field Operations Coordination",
        "Deployment Support",
        "Field Validation",
        "Operational Integration",
        "Military Liaison",
        "User Liaison",
        "Access and Movement Coordination",
        "Field Logistics",
        "Security-Aware Planning",
        "Cross-Functional Coordination",
        "Situational Reporting",
        "Battlefield Information Verification",
        "Product Feedback Collection",
        "End-User Communication",
        "Applied Technical Prototyping",
        "Python",
        "Java",
        "Data Parsing",
        "Coordinate Conversion",
        "Mapping-Oriented Workflows",
        "Workflow Automation",
        "Work in Austere Environments",
    ],

    "experience": [
        {
            "role": "Field Producer / Conflict-Zone Coordinator",
            "company": "DR (Danish Broadcasting Corporation)",
            "dates": "2022–Present",
            "bullets": [
                "Support reporting and documentary teams operating in conflict-affected areas across Ukraine.",
                "Coordinate field movements, access, logistics, timing, and practical execution in high-risk environments.",
                "Support interviews with military personnel, civilians, and local sources.",
                "Provide on-location production support and independent visual capture when needed.",
                "Troubleshoot field constraints including transport, access changes, equipment limits, connectivity issues, and fast-changing local conditions.",
                "Maintain disciplined handling of sensitive information and minimize operational exposure.",
            ],
        },
        {
            "role": "Field Producer (Contract)",
            "company": "The Times",
            "dates": "2024–2025",
            "bullets": [
                "Provided frontline-adjacent field production support for reporting teams in volatile environments.",
                "Coordinated movement planning, local execution, access, and practical logistics.",
                "Supported interviews, field verification, and rapid adaptation under newsroom deadlines.",
                "Helped maintain reliable field delivery in unstable operating conditions.",
            ],
        },
        {
            "role": "Field Operations Coordinator / Military Liaison",
            "company": "Independent / Volunteer",
            "dates": "2022–Present",
            "bullets": [
                "Coordinate with military end users, volunteer networks, local stakeholders, and technical contributors in frontline-related contexts.",
                "Support procurement and delivery coordination for field equipment without disclosing sensitive operational details.",
                "Gather direct user feedback on equipment performance, usability, deployment conditions, and operational constraints.",
                "Translate field needs into actionable requests for suppliers, support teams, and technical contributors.",
                "Support real-world product use shaped by terrain, weather, power limits, maintenance constraints, and urgency.",
            ],
        },
        {
            "role": "Applied Technical Developer / Rapid Prototyping Support",
            "company": "Independent",
            "dates": "2023–Present",
            "bullets": [
                "Build lightweight operational tools and rapid prototypes for military and emergency-use scenarios.",
                "Develop utilities for coordinate parsing, conversion, data structuring, and workflow automation.",
                "Support mapping-oriented workflows and practical task-specific tools.",
                "Use Git-based workflows, debugging, and iterative refinement based on real user feedback and field constraints.",
            ],
        },
    ],

    "previous_experience": [
        "Executive / Creative Producer — Rozetka / 16A Studio | 2018–2022",
        "Line Producer — Heads & Tails | 2018–2022",
        "Creative Producer — Expats / TripMyDream | 2018",
        "Content Manager — Must2Go | 2017–2018",
        "Founder — Cocky Yobbo Production | 2013–2018",
        "Radio Presenter / Reporter — Radio Track 106.4 FM | 2014–2016",
        "Production Assistant — Radioaktive Film / Belka & Strelka | 2004–2007",
    ],

    "technical_skills": [
        "Python",
        "Java",
        "Git",
        "Data Parsing",
        "Coordinate Conversion",
        "Workflow Automation",
        "Mapping-Oriented Support",
        "Field Media Workflow",
        "Camera / Audio Setup",
        "AI-Assisted Development Workflows",
    ],

    "education": [
        "National University of Food Technologies — Marketing & Advertising | 2004–2009",
    ],

    "training": [
        "DW Akademie — Field Producers Training (War Reporting)",
        "Tactical Combat Casualty Care (TCCC)",
        "MARCH Protocol",
        "Stop the Bleed",
    ],

    "languages": [
        "Ukrainian — Native",
        "Russian — Native",
        "English — Professional Working Proficiency (B2)",
    ],
}


TARGETED_CVS = {
    "military_liaison_user_liaison": {
        "headline": "MILITARY LIAISON / USER LIAISON",
        "summary": [
            "Field-based coordination professional with deep experience working between military end users, civilian teams, local actors, and international stakeholders in Ukraine since 2022.",
            "Strong in communication, trust-building, access coordination, and translating real user needs into usable operational requirements.",
        ],
        "core_strengths": [
            "Military Liaison",
            "User Liaison",
            "Stakeholder Coordination",
            "Field Operations",
            "Access Coordination",
            "Operational Feedback",
            "Cross-Functional Communication",
        ],
        "experience": [
            {
                "role": "Field Operations Coordinator / Military Liaison",
                "company": "Independent / Volunteer",
                "dates": "2022–Present",
                "bullets": [
                    "Coordinated with military end users, volunteer networks, and technical contributors in frontline-related contexts.",
                    "Gathered user needs, field concerns, and equipment feedback.",
                    "Translated real-world constraints into actionable requirements for support teams and partners.",
                    "Maintained effective communication across different stakeholder groups under pressure.",
                ],
            },
            {
                "role": "Field Producer / Conflict-Zone Coordinator",
                "company": "DR",
                "dates": "2022–Present",
                "bullets": [
                    "Coordinated field access, movement, logistics, and interview support in conflict-affected environments.",
                    "Worked with military personnel, civilians, and international teams in high-pressure conditions.",
                ],
            },
        ],
    },

    "field_validation_testing_specialist": {
        "headline": "FIELD VALIDATION / TESTING SPECIALIST",
        "summary": [
            "Field-oriented validation specialist experienced in observing how tools, equipment, and workflows behave under real-world stress.",
            "Identifies usability and reliability problems and translates field feedback into clear findings for operational or technical teams.",
        ],
        "core_strengths": [
            "Field Validation",
            "Field Testing",
            "User Feedback",
            "Real-World Constraints",
            "Reliability Feedback",
            "Operational Observation",
            "Usability Assessment",
        ],
        "experience": [
            {
                "role": "Field Operations Coordinator / Military Liaison",
                "company": "Independent / Volunteer",
                "dates": "2022–Present",
                "bullets": [
                    "Gathered direct user feedback on equipment performance, usability, and deployment conditions.",
                    "Identified recurring field problems caused by environment, urgency, terrain, power constraints, and workflow mismatch.",
                    "Converted observations from real use cases into practical recommendations for suppliers and technical contributors.",
                ],
            },
            {
                "role": "Applied Technical Developer / Rapid Prototyping Support",
                "company": "Independent",
                "dates": "2023–Present",
                "bullets": [
                    "Built lightweight support tools shaped by user needs and iterative feedback.",
                    "Refined utilities based on practical constraints and real operator use.",
                ],
            },
        ],
    },

    "operational_integration_specialist": {
        "headline": "OPERATIONAL INTEGRATION SPECIALIST",
        "summary": [
            "Operational integration professional with strong field awareness and experience aligning users, workflows, equipment, logistics, and constraints in real environments.",
            "Useful where products need to survive contact with reality, not just pass internal review.",
        ],
        "core_strengths": [
            "Operational Integration",
            "Deployment Workflow",
            "Product Adoption",
            "Field Constraints",
            "Implementation Support",
            "User Feedback",
            "Cross-Team Coordination",
        ],
        "experience": [
            {
                "role": "Field Operations Coordinator / Military Liaison",
                "company": "Independent / Volunteer",
                "dates": "2022–Present",
                "bullets": [
                    "Supported practical integration of field equipment into real working environments.",
                    "Identified barriers to effective use including environment, access, power, logistics, and training issues.",
                    "Helped connect user behavior, mission context, and technical limitations into actionable implementation feedback.",
                ],
            },
            {
                "role": "Field Producer / Conflict-Zone Coordinator",
                "company": "DR",
                "dates": "2022–Present",
                "bullets": [
                    "Coordinated practical execution in unstable environments with constant changes in timing, access, and conditions.",
                    "Maintained structured delivery despite incomplete information and operational pressure.",
                ],
            },
        ],
    },

    "field_operations_deployment_specialist": {
        "headline": "FIELD OPERATIONS / DEPLOYMENT SPECIALIST",
        "summary": [
            "Field operations professional experienced in deployment support in high-risk and infrastructure-limited environments.",
            "Skilled in movement planning, access coordination, field logistics, user communication, and practical support during rollout in unstable conditions.",
        ],
        "core_strengths": [
            "Deployment Support",
            "Field Operations",
            "Movement Planning",
            "Access Coordination",
            "Field Logistics",
            "Rollout Support",
            "Operational Execution",
        ],
        "experience": [
            {
                "role": "Field Producer / Conflict-Zone Coordinator",
                "company": "DR",
                "dates": "2022–Present",
                "bullets": [
                    "Coordinated field movements, access, logistics, and practical execution in conflict-affected environments.",
                    "Solved field bottlenecks involving transport, timing, permissions, equipment, and route changes.",
                    "Supported reliable execution under pressure and changing constraints.",
                ],
            },
            {
                "role": "Field Operations Coordinator / Military Liaison",
                "company": "Independent / Volunteer",
                "dates": "2022–Present",
                "bullets": [
                    "Supported deployment and field use of equipment in real conditions shaped by weather, terrain, urgency, and maintenance realities.",
                    "Gathered field observations and user feedback to improve deployment effectiveness.",
                ],
            },
        ],
    },
}


COVER_LETTER_TEMPLATE = {
    "subject": "Application for [ROLE TITLE]",
    "body": [
        "Dear Hiring Team,",
        "",
        "I am applying for the [ROLE TITLE] position.",
        "",
        "My background combines field operations, conflict-zone coordination, logistics-heavy execution, and user-facing work in high-pressure environments in Ukraine since 2022. I have supported international reporting and documentary teams in unstable operating conditions, coordinated access and movement, worked with military and civilian stakeholders, and handled practical execution where plans often change fast.",
        "",
        "Alongside that field work, I also build lightweight applied tools and support utilities for operational workflows, including coordinate handling, data structuring, workflow automation, and mapping-oriented tasks. I do not position myself as a conventional software engineer. My value is different: I understand real operating conditions, user friction, deployment constraints, and how to translate those realities into useful feedback and practical support for teams.",
        "",
        "I believe I am a strong fit for roles that require field realism, disciplined communication, deployment support, operational integration, and structured user feedback.",
        "",
        "I would be glad to discuss how I could contribute to your team.",
        "",
        "Best regards,",
        "Roman Sumko",
        "Kyiv, Ukraine",
        "rsumko@gmail.com",
        "Signal: gnz_trx_2026.25",
        "Phone: +380 96 586 8873",
    ],
}


LINKEDIN_ABOUT = [
    "Field operations and coordination professional working at the intersection of conflict-zone execution, deployment support, user liaison, and practical problem-solving.",
    "Since 2022, I have worked in active combat-zone conditions in Ukraine, supporting international reporting and documentary teams with field coordination, movement and access planning, local logistics, interview support, and on-location execution in unstable environments.",
    "In parallel, I support field-facing operational workflows through lightweight applied tooling and rapid prototyping — including coordinate handling, data structuring, workflow automation, and mapping-oriented support.",
    "My strongest value is in roles where products, workflows, or teams need to function in real-world conditions rather than controlled environments. I work well between end users, field reality, and technical or operational teams.",
    "Areas of fit: Field Operations, Deployment Support, Military / User Liaison, Field Validation, Operational Integration, Product Operations, Applied Technical Support.",
]


INTERVIEW_PREP = {
    "positioning": "I am a field operations and liaison person with real conflict-zone experience, strong coordination skills, and enough applied technical literacy to support deployment, validation, and user feedback loops.",

    "core_message": "I reduce the gap between field reality and team assumptions.",

    "what_i_am": [
        "field operations / coordination",
        "military / user liaison",
        "deployment / integration support",
        "field validation / feedback collection",
        "practical operator in unstable environments",
        "applied technical support / rapid prototyping layer",
    ],

    "what_i_am_not": [
        "not a founder",
        "not a senior defense engineer",
        "not a weapons designer",
        "not a battlefield systems architect",
        "not pretending to be a pure software engineer",
    ],

    "top_answers": {
        "Tell me about yourself.":
            "I come from a long production and field operations background. Since 2022, I have worked in conflict-zone conditions in Ukraine, coordinating movements, logistics, access, field execution, and communication between different stakeholders. In parallel, I also build lightweight practical tools when needed. My value is in connecting field reality, user needs, and execution.",

        "Why this role?":
            "Because this is where my experience is directly useful. I understand real conditions, user friction, deployment constraints, and how to help a team adapt a product or workflow to reality.",

        "Why should we hire you?":
            "Because I can help your team avoid the gap between internal assumptions and real-world use. I can support field deployment, gather usable feedback, and improve coordination with actual users.",

        "What is your biggest strength?":
            "Operational adaptability under pressure. I can enter messy conditions, identify the real bottleneck, keep communication clean, and move execution forward.",

        "What are your technical limits?":
            "I am not a deep engineer. My technical value is applied: lightweight tools, workflow support, coordinate handling, parsing, and practical prototyping driven by user needs.",

        "How do you handle sensitive information?":
            "Need-to-know basis. I avoid unnecessary specifics and treat information discipline as part of operational hygiene.",
    },

    "phrases_to_repeat": [
        "real operating conditions",
        "user needs",
        "deployment constraints",
        "structured feedback",
        "practical execution",
        "operational friction",
        "fast adaptation",
        "cross-functional communication",
    ],

    "what_to_avoid": [
        "heroic war stories",
        "unit names",
        "tactical details",
        "exaggerated miltech claims",
        "sounding like you are applying to be CEO of NATO",
    ],

    "best_closing_line":
        "I am most useful where a company needs someone who can take a product or workflow into reality, understand why it works or fails there, and help the team adjust fast and intelligently.",
}


def bullets(items):
    return "\n".join(f"- {item}" for item in items)


def simple_lines(items):
    return "\n".join(items)


def section(title, content):
    return f"{title}\n{content}".strip()


def join_sections(sections):
    return "\n\n".join(s for s in sections if s.strip())


def render_header(profile, headline):
    header_lines = [
        profile["name"],
        profile["location"],
        profile["email"],
        f"Phone: {profile['phone']}",
        f"Signal: {profile['signal']}",
    ]

    if profile.get("open_to"):
        header_lines.append(profile["open_to"])

    if profile.get("linkedin") and profile["linkedin"] != "[ADD LINK]":
        header_lines.append(f"LinkedIn: {profile['linkedin']}")

    if profile.get("website") and profile["website"] != "[OPTIONAL]":
        header_lines.append(f"Website: {profile['website']}")

    header_text = "\n".join(header_lines)

    return dedent(f"""
    {header_text}

    {headline}
    """).strip()


def render_summary(lines):
    return "\n".join(lines)


def render_experience(experience_items):
    blocks = []
    for item in experience_items:
        block = (
            f"{item['role']}\n"
            f"{item['company']} | {item['dates']}\n"
            f"{bullets(item['bullets'])}"
        )
        blocks.append(block)
    return "\n\n".join(blocks)


def render_master_cv():
    return join_sections([
        render_header(PROFILE, MASTER_DATA["headline"]),
        section("AVAILABILITY", simple_lines(AVAILABILITY_BLOCK)),
        section("COMPLIANCE / VETTING", simple_lines(COMPLIANCE_BLOCK)),
        section("PROFILE", render_summary(MASTER_DATA["summary"])),
        section("CORE CAPABILITIES", simple_lines(MASTER_DATA["core_capabilities"])),
        section("PROFESSIONAL EXPERIENCE", render_experience(MASTER_DATA["experience"])),
        section("SELECTED PREVIOUS EXPERIENCE", simple_lines(MASTER_DATA["previous_experience"])),
        section("TECHNICAL SKILLS", simple_lines(MASTER_DATA["technical_skills"])),
        section("EDUCATION", simple_lines(MASTER_DATA["education"])),
        section("TRAINING", simple_lines(MASTER_DATA["training"])),
        section("LANGUAGES", simple_lines(MASTER_DATA["languages"])),
    ])


def render_targeted_cv(key):
    data = TARGETED_CVS[key]
    return join_sections([
        render_header(PROFILE, data["headline"]),
        section("AVAILABILITY", simple_lines(AVAILABILITY_BLOCK)),
        section("COMPLIANCE / VETTING", simple_lines(COMPLIANCE_BLOCK)),
        section("PROFILE", render_summary(data["summary"])),
        section("CORE STRENGTHS", simple_lines(data["core_strengths"])),
        section("RELEVANT EXPERIENCE", render_experience(data["experience"])),
        section("TECHNICAL SKILLS", simple_lines(MASTER_DATA["technical_skills"])),
        section("EDUCATION", simple_lines(MASTER_DATA["education"])),
        section("TRAINING", simple_lines(MASTER_DATA["training"])),
        section("LANGUAGES", simple_lines(MASTER_DATA["languages"])),
    ])


def render_cover_letter():
    subject = f"SUBJECT: {COVER_LETTER_TEMPLATE['subject']}"
    body = "\n".join(COVER_LETTER_TEMPLATE["body"])
    return f"{subject}\n\n{body}"


def render_linkedin_about():
    return "\n\n".join(LINKEDIN_ABOUT)


def render_interview_prep():
    top_answers = []
    for question, answer in INTERVIEW_PREP["top_answers"].items():
        top_answers.append(f"{question}\n{answer}")

    return join_sections([
        section("POSITIONING", INTERVIEW_PREP["positioning"]),
        section("CORE MESSAGE", INTERVIEW_PREP["core_message"]),
        section("WHAT I AM", bullets(INTERVIEW_PREP["what_i_am"])),
        section("WHAT I AM NOT", bullets(INTERVIEW_PREP["what_i_am_not"])),
        section("TOP ANSWERS", "\n\n".join(top_answers)),
        section("PHRASES TO REPEAT", bullets(INTERVIEW_PREP["phrases_to_repeat"])),
        section("WHAT TO AVOID", bullets(INTERVIEW_PREP["what_to_avoid"])),
        section("BEST CLOSING LINE", INTERVIEW_PREP["best_closing_line"]),
    ])


def write_text_file(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def export_all():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = {
        "master_ats_cv.txt": render_master_cv(),
        "cv_military_liaison_user_liaison.txt": render_targeted_cv("military_liaison_user_liaison"),
        "cv_field_validation_testing_specialist.txt": render_targeted_cv("field_validation_testing_specialist"),
        "cv_operational_integration_specialist.txt": render_targeted_cv("operational_integration_specialist"),
        "cv_field_operations_deployment_specialist.txt": render_targeted_cv("field_operations_deployment_specialist"),
        "cover_letter_template.txt": render_cover_letter(),
        "linkedin_about.txt": render_linkedin_about(),
        "interview_prep_sheet.txt": render_interview_prep(),
    }

    for filename, content in files.items():
        write_text_file(OUTPUT_DIR / filename, content)

    print(f"Done. Exported {len(files)} files to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    export_all()
