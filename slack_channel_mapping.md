# Slack Workspace Configuration — Gmail Label to Channel Mapping

**Author:** Angel Evans  
**Date:** 2026-02-13  
**Description:** Configuration document for mapping Gmail Organizer labels to Slack channels for real-time email notification routing.

---

## Overview

This document defines the Slack workspace channel structure that mirrors the Gmail Organizer label hierarchy. Each Gmail label maps to a Slack channel where notifications about new or re-categorized emails can be routed using a Slack integration (such as a Zapier zap, Google Apps Script trigger, or custom webhook).

The design philosophy is to keep channels focused and manageable: deeply nested Gmail labels are consolidated into broader Slack channels to avoid channel sprawl while maintaining clear routing.

---

## Channel Definitions

### Critical Channels (High Priority)

These channels receive notifications that require immediate attention or action.

| Slack Channel | Gmail Labels Routed Here | Purpose | Priority |
| :--- | :--- | :--- | :--- |
| `#legal-court` | TIMELINE-EVIDENCE/Legal-Court/* | All legal correspondence, court notices, attorney emails | URGENT |
| `#government-irs` | TIMELINE-EVIDENCE/Government/IRS | IRS notices and tax correspondence | URGENT |
| `#credentials` | API-KEYS-CREDENTIALS/* | API keys, tokens, passwords, licenses (private channel) | HIGH |
| `#flagged-review` | FLAGGED-REVIEW | Uncategorized emails needing manual review | HIGH |
| `#medical-appointments` | TIMELINE-EVIDENCE/Medical/Appointments | Upcoming medical appointments | HIGH |

### Standard Channels

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#timeline-evidence` | TIMELINE-EVIDENCE (top-level catch) | General timeline evidence |
| `#timeline-location` | TIMELINE-EVIDENCE/Location-Activity/* | Location and travel activity |
| `#timeline-comms` | TIMELINE-EVIDENCE/Communications-Sent/* | Sent communications log |
| `#government` | TIMELINE-EVIDENCE/Government/SSA, Medicaid-Medicare, Other-Gov | Government correspondence |
| `#finance` | TIMELINE-EVIDENCE/Financial-Transactions (general) | General financial |
| `#finance-banking` | TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase | Chase banking alerts |
| `#finance-investments` | TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments | Investment notifications |
| `#finance-bills` | TIMELINE-EVIDENCE/Financial-Transactions/Bills-Utilities | Bill and utility reminders |
| `#medical` | TIMELINE-EVIDENCE/Medical/* (except Appointments) | Medical correspondence |
| `#housing` | TIMELINE-EVIDENCE/Housing/* | Housing, vouchers, inspections |

### Music Channels

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#music` | MUSIC (top-level) | General music activity |
| `#music-collabs` | MUSIC/Collaborations/* | Collaboration emails (Caresse, others) |
| `#music-platforms` | MUSIC/Platforms/* | SoundCloud, Spotify, Suno, Donna |
| `#music-creative` | MUSIC/Lyrics-Drafts | Lyrics and draft notifications |
| `#music-legal` | MUSIC/Copyright-Legal | Copyright and licensing |
| `#music-distribution` | MUSIC/Distribution | Distribution platform emails |

### Projects Channels

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#projects` | PROJECTS (top-level, Other-Projects) | General project activity |
| `#projects-ssrn` | PROJECTS/SSRN-Academic/* | SSRN academic papers and submissions |
| `#projects-dev` | PROJECTS/GitHub-Dev, YumYumCode, Universal-OZ, MCT-InTheWild, Tiki-Washbot, Neurooz | Development project notifications |
| `#projects-web` | PROJECTS/Meetaudreyevans | Website project updates |
| `#projects-accessibility` | PROJECTS/Alt-Text-ADA | ADA and accessibility project |
| `#projects-ideas` | PROJECTS/App-Ideas | New app ideas and brainstorms |

### Job Search Channels

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#job-search` | JOB-SEARCH (top-level) | General job search activity |
| `#job-alerts` | JOB-SEARCH/Alerts/* | Indeed, LinkedIn, other job alerts |
| `#job-applications` | JOB-SEARCH/Applications | Application confirmations |
| `#job-responses` | JOB-SEARCH/Responses | Employer responses |
| `#job-interviews` | JOB-SEARCH/Interviews | Interview scheduling |

### Contacts Channels

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#contacts` | CONTACTS (top-level, Other-Important) | General important contacts |
| `#contacts-personal` | CONTACTS/Caresse-Lopez | Personal contact notifications |
| `#contacts-church` | CONTACTS/Church-One20 | Church community |
| `#contacts-medical` | CONTACTS/Medical-Team | Medical team correspondence |
| `#contacts-legal` | CONTACTS/Legal-Team | Legal team correspondence |
| `#contacts-housing` | CONTACTS/Housing-Contacts | Housing contacts |

### Commerce and Subscriptions

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#orders-receipts` | ORDERS-RECEIPTS (general, Google-Play, eBay, Etsy, Other) | Purchase confirmations |
| `#orders-amazon` | ORDERS-RECEIPTS/Amazon | Amazon order tracking |
| `#orders-subscriptions` | ORDERS-RECEIPTS/Subscriptions | Subscription renewals and charges |

### Information Channels

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#newsletters` | NEWSLETTERS (general, Other) | Newsletter digests |
| `#newsletters-tech` | NEWSLETTERS/Tech | Tech newsletters |
| `#newsletters-finance` | NEWSLETTERS/Finance | Finance newsletters |
| `#newsletters-business` | NEWSLETTERS/Business | Business newsletters |
| `#software` | SOFTWARE-TRACKING/* | Software purchases, trials, licenses |

### Social Media

| Slack Channel | Gmail Labels Routed Here | Purpose |
| :--- | :--- | :--- |
| `#social-media` | SOCIAL-MEDIA (general, Other) | General social media notifications |
| `#social-tiktok` | SOCIAL-MEDIA/TikTok | TikTok notifications |
| `#social-linkedin` | SOCIAL-MEDIA/LinkedIn | LinkedIn notifications |
| `#social-reddit` | SOCIAL-MEDIA/Reddit | Reddit notifications |
| `#social-nextdoor` | SOCIAL-MEDIA/Nextdoor | Nextdoor notifications |

---

## Integration Setup

### Option 1: Zapier (No-Code)

1. Create a new Zap with trigger: "Gmail — New Email Matching Search"
2. Set the search query to match the Gmail label (e.g., `label:TIMELINE-EVIDENCE/Legal-Court`)
3. Set the action to: "Slack — Send Channel Message"
4. Map the channel to the corresponding Slack channel from the table above
5. Repeat for each label-to-channel mapping

### Option 2: Google Apps Script (Free)

Create a time-driven trigger in Google Apps Script that checks for new emails in each label and posts to the corresponding Slack webhook URL. A template script is available in the project repository.

### Option 3: Custom Python Script

Extend the `gmail_organizer.py` to include a Slack notification module using the Slack Web API. This approach provides the most control and can be scheduled via cron.

```python
# Example Slack notification snippet
import requests

def notify_slack(channel, message, webhook_url):
    payload = {
        "channel": channel,
        "text": message,
        "username": "Gmail Organizer",
        "icon_emoji": ":email:",
    }
    requests.post(webhook_url, json=payload)
```

---

## Channel Summary

| Category | Channel Count |
| :--- | :--- |
| Critical / High Priority | 5 |
| Timeline & Evidence | 5 |
| Finance | 3 |
| Medical & Housing | 2 |
| Music | 6 |
| Projects | 6 |
| Job Search | 5 |
| Contacts | 6 |
| Commerce | 3 |
| Information | 5 |
| Social Media | 5 |
| **Total Channels** | **51** |
