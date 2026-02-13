# Email Directory Structure — Full Label Tree with Slack Channel Mappings

**Author:** Angel Evans  
**Date:** 2026-02-13  
**Description:** Complete hierarchical tree of all Gmail labels created by Gmail Organizer, with corresponding Slack channel mappings for team notification routing.

---

## Directory Tree

```
GMAIL ORGANIZER LABEL HIERARCHY
================================

TIMELINE-EVIDENCE/                          → #timeline-evidence
├── Location-Activity/                      → #timeline-location
│   ├── Google-Maps                         → #timeline-location
│   ├── Redfin-Property                     → #timeline-location
│   ├── Travel-Transport                    → #timeline-location
│   └── Check-Ins                           → #timeline-location
├── Communications-Sent/                    → #timeline-comms
│   ├── Self-Emails                         → #timeline-comms
│   ├── To-Contacts                         → #timeline-comms
│   └── Replies                             → #timeline-comms
├── Legal-Court/                            → #legal-court
│   ├── Case-Files                          → #legal-court
│   ├── Attorney-Correspondence             → #legal-court
│   └── Court-Notices                       → #legal-court
├── Government/                             → #government
│   ├── IRS                                 → #government-irs
│   ├── SSA                                 → #government
│   ├── Medicaid-Medicare                   → #government
│   └── Other-Gov                           → #government
├── Financial-Transactions/                 → #finance
│   ├── Banking-Chase                       → #finance-banking
│   ├── Credit-Cards                        → #finance
│   ├── Robinhood-Investments               → #finance-investments
│   ├── Payment-Processors                  → #finance
│   └── Bills-Utilities                     → #finance-bills
├── Medical/                                → #medical
│   ├── UC-Health                           → #medical
│   ├── Colorado-In-Motion                  → #medical
│   ├── Insurance                           → #medical
│   ├── Appointments                        → #medical-appointments
│   └── Prescriptions                       → #medical
└── Housing/                                → #housing
    ├── HQS-Inspections                     → #housing
    ├── Vouchers                            → #housing
    ├── Rent-Payments                       → #housing
    └── Property-Search                     → #housing

MUSIC/                                      → #music
├── Collaborations/                         → #music-collabs
│   ├── Caresse-Rae-Edna                    → #music-collabs
│   └── Other-Collabs                       → #music-collabs
├── Platforms/                              → #music-platforms
│   ├── SoundCloud                          → #music-platforms
│   ├── Spotify                             → #music-platforms
│   ├── Suno                                → #music-platforms
│   └── Donna                               → #music-platforms
├── Lyrics-Drafts                           → #music-creative
├── Copyright-Legal                         → #music-legal
└── Distribution                            → #music-distribution

PROJECTS/                                   → #projects
├── SSRN-Academic/                          → #projects-ssrn
│   ├── Paper-Generation                    → #projects-ssrn
│   ├── Submissions                         → #projects-ssrn
│   └── eJournals                           → #projects-ssrn
├── YumYumCode                              → #projects-dev
├── GitHub-Dev                              → #projects-dev
├── Universal-OZ                            → #projects-dev
├── MCT-InTheWild                           → #projects-dev
├── Meetaudreyevans                         → #projects-web
├── Tiki-Washbot                            → #projects-dev
├── Neurooz                                 → #projects-dev
├── Alt-Text-ADA                            → #projects-accessibility
├── App-Ideas                               → #projects-ideas
└── Other-Projects                          → #projects

JOB-SEARCH/                                 → #job-search
├── Applications                            → #job-applications
├── Alerts/                                 → #job-alerts
│   ├── Indeed                              → #job-alerts
│   ├── LinkedIn                            → #job-alerts
│   └── Other                               → #job-alerts
├── Responses                               → #job-responses
└── Interviews                              → #job-interviews

API-KEYS-CREDENTIALS/                       → #credentials (private)
├── API-Keys                                → #credentials (private)
├── Bot-Tokens                              → #credentials (private)
├── Passwords                               → #credentials (private)
└── Licenses                                → #credentials (private)

CONTACTS/                                   → #contacts
├── Caresse-Lopez                           → #contacts-personal
├── Church-One20                            → #contacts-church
├── Medical-Team                            → #contacts-medical
├── Legal-Team                              → #contacts-legal
├── Housing-Contacts                        → #contacts-housing
└── Other-Important                         → #contacts

ORDERS-RECEIPTS/                            → #orders-receipts
├── Amazon                                  → #orders-amazon
├── Google-Play                             → #orders-receipts
├── eBay                                    → #orders-receipts
├── Etsy                                    → #orders-receipts
├── Subscriptions                           → #orders-subscriptions
└── Other-Purchases                         → #orders-receipts

NEWSLETTERS/                                → #newsletters
├── Tech                                    → #newsletters-tech
├── Finance                                 → #newsletters-finance
├── Business                                → #newsletters-business
└── Other                                   → #newsletters

SOFTWARE-TRACKING/                          → #software
├── Purchases                               → #software
├── Trials                                  → #software
├── Licenses                                → #software
└── Cancellations                           → #software

SOCIAL-MEDIA/                               → #social-media
├── TikTok                                  → #social-tiktok
├── LinkedIn                                → #social-linkedin
├── Reddit                                  → #social-reddit
├── Nextdoor                                → #social-nextdoor
└── Other                                   → #social-media

FLAGGED-REVIEW/                             → #flagged-review
```

---

## Label Count Summary

| Top-Level Category | Sub-Labels | Total | Slack Channel |
| :--- | :--- | :--- | :--- |
| TIMELINE-EVIDENCE | 26 | 27 | #timeline-evidence |
| MUSIC | 10 | 11 | #music |
| PROJECTS | 12 | 13 | #projects |
| JOB-SEARCH | 6 | 7 | #job-search |
| API-KEYS-CREDENTIALS | 4 | 5 | #credentials |
| CONTACTS | 6 | 7 | #contacts |
| ORDERS-RECEIPTS | 6 | 7 | #orders-receipts |
| NEWSLETTERS | 4 | 5 | #newsletters |
| SOFTWARE-TRACKING | 4 | 5 | #software |
| SOCIAL-MEDIA | 5 | 6 | #social-media |
| FLAGGED-REVIEW | 0 | 1 | #flagged-review |
| **TOTAL** | **83** | **94** | **30+ channels** |
