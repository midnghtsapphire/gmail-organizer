# Gmail Organizer v2.0.0

**Automated Email Labeling, Sorting & Migration Tool**

A modular Python application that scans, categorizes, and organizes your Gmail inbox into a clean, hierarchical label structure. Built with security, performance, and extensibility in mind.

## Features

- **Modular Architecture** — Clean package structure (auth, categorizer, operations, migrator, reporter)
- **Encrypted Credential Storage** — Fernet symmetric encryption for OAuth tokens
- **Token Bucket Rate Limiter** — Proactive API rate limiting with burst support
- **Compiled Regex Patterns** — Case-insensitive matching with pre-compiled patterns
- **Exponential Backoff** — Automatic retry on API rate limits (429, 500, 503)
- **Label Migration** — Migrate old labels to new hierarchy automatically
- **Label Cleanup** — Remove empty/obsolete labels
- **Dry Run Mode** — Preview all changes before executing (default)
- **Comprehensive Reporting** — JSON and Markdown export

## Label Hierarchy

All labels are **active** — no archiving, no catch-all buckets.

```
TIMELINE-EVIDENCE/
├── Communications-Sent/{Self-Emails, To-Contacts}
├── Financial-Transactions/{Banking-Chase, Robinhood, Venmo-CashApp, Crypto}
├── Location-Activity/{Google-Maps, Redfin-Property, Travel-Transport}
├── Medical/{UC-Health, Insurance-Claims, Prescriptions}
├── Government/{IRS, SSA, Medicaid-Medicare, SNAP-Benefits, Unemployment}
├── Housing/{Rent-Payments, Lease-Agreements, HQS-Inspections, Utilities}
└── Legal-Court

MUSIC/
├── Platforms/{SoundCloud, Spotify, Apple-Music, YouTube-Music, TikTok-Sounds}
├── Distribution/{DistroKid, TuneCore, CDBaby}
├── Collaborations/Caresse-Rae-Edna
├── Copyright-Legal/{ASCAP-BMI, Registrations}
├── Royalties
└── Prompts-Templates

PROJECTS/
├── SSRN-Academic/{eJournals, Downloads}
├── GitHub-Dev, YumYumCode, Tiki-Washbot, Neurooz
├── Alt-Text-ADA, App-Ideas, Meetaudreyevans
└── ...

JOB-SEARCH/{Applications, Interviews, Alerts/{Indeed,LinkedIn,Glassdoor}, Offers, Rejections}
API-KEYS-CREDENTIALS/{API-Keys, Bot-Tokens, Passwords, Licenses}
CONTACTS/{Caresse-Lopez, Church-One20, Family, Professional}
ORDERS-RECEIPTS/{Amazon, eBay, Etsy, Google-Play, Subscriptions}
NEWSLETTERS/{Tech, Music-Industry, Business}
SOFTWARE-TRACKING/{Trials, Cancellations, Updates}
SOCIAL-MEDIA/{TikTok, LinkedIn, Reddit, Nextdoor, Instagram, Facebook}
FLAGGED-REVIEW
```

## Installation

```bash
pip install -e .
```

### Prerequisites

1. Python 3.9+
2. Google Cloud project with Gmail API enabled
3. OAuth 2.0 credentials (`credentials.json`)

## Usage

### Create Label Hierarchy Only
```bash
python -m gmail_organizer --labels-only
```

### Dry Run (preview categorization)
```bash
python -m gmail_organizer --dry-run --max-messages 100
```

### Execute Categorization
```bash
python -m gmail_organizer --execute --max-messages 500
```

### Migrate Old Labels
```bash
python -m gmail_organizer --migrate --execute
```

### Cleanup Empty Labels
```bash
python -m gmail_organizer --cleanup --execute
```

## Before/After Example

**Before (flat labels):**
```
bank, legal, music, job, ssrn, orders, random, misc
```

**After (hierarchical):**
```
TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase
TIMELINE-EVIDENCE/Legal-Court
MUSIC/Platforms/SoundCloud
JOB-SEARCH/Alerts/Indeed
PROJECTS/SSRN-Academic
ORDERS-RECEIPTS/Amazon
FLAGGED-REVIEW
```

## Security Considerations

- **Encrypted Tokens** — OAuth tokens encrypted at rest using Fernet (AES-128-CBC)
- **File Permissions** — Token and key files set to `0600`
- **No Hardcoded Secrets** — All credentials externalized
- **Secure Refresh** — Automatic token refresh with encrypted re-storage

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v --cov=gmail_organizer --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass with 90%+ coverage
5. Submit a pull request

## Troubleshooting

| Error Code | Description | Solution |
|-----------|-------------|----------|
| `403` | Insufficient permissions | Re-run OAuth flow, ensure Gmail API scope |
| `429` | Rate limit exceeded | Reduce `api_calls_per_second` in config |
| `500` | Server error | Automatic retry with backoff |
| `FATAL: credentials.json not found` | Missing OAuth credentials | Download from Google Cloud Console |

## License

MIT License

Copyright (c) 2025-2026 Angel Evans

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
