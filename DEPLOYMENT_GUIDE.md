# Deployment Guide

## Overview
This repository ships a Gmail Organizer automation script plus an S2M website artifact for validation and go-to-market packaging.

## Runtime Components
- Python CLI: `gmail_organizer.py`
- Website in test: `website/index.html`
- Validation scripts: `scripts/test-baseline.sh`, `scripts/build-baseline.sh`

## Local Validation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run baseline test command:
   ```bash
   npm test
   ```
3. Run baseline build command:
   ```bash
   npm run build
   ```

## Vercel Deployment (Website in Test)
1. Import this repository in Vercel.
2. Set output directory to `website`.
3. Deploy with the default static build profile.
4. Record the deployment URL in `README.md` under "Website in Test".

## Operational Notes
- Python Gmail API credentials must never be committed.
- Run baseline scripts before release merges.
