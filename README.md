# Shortoff Dashboard Demo

Public Streamlit demo dashboard for Shortoff Mountain Retreats sample data.

This repository is safe to deploy publicly because it uses sample/demo data only. Do not add real guest records, live revenue exports, API keys, payment data, or private platform exports to this repo.

## What This Tracks

- Booking revenue, nights, ADR, direct-booking share, and channel mix.
- Website sessions, booking CTA clicks, inquiries, and booking-start conversion.
- SEO clicks, impressions, position, and top search queries.
- Review ratings, topics, and guest-experience themes.
- Data freshness and missing-field checks.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app loads sample data from `data/sample/`. For live business data, use the private `shortoff-live-dashboard` repo instead.

## Sample Data Files

The demo includes these sample CSVs:

- `reservations.csv`
- `web_analytics.csv`
- `seo_queries.csv`
- `reviews.csv`
- `issues.csv`

## Streamlit Cloud

1. Create a new public GitHub repository.
2. Push this folder as the repo.
3. In Streamlit Community Cloud, create a new app from the public demo repo.
4. Set the main file path to `app.py`.
5. Deploy. No secrets are required for the demo.

## Public Repo Rules

- Keep this repo sample-data only.
- Do not add `data/private/`.
- Do not add `.streamlit/secrets.toml`.
- Do not add platform exports from Airbnb, Lodgify, Stripe, Google Search Console, or booking systems.
