# Elias CRM

Elias CRM is a Python-based customer relationship management suite designed to streamline lead generation and outreach campaigns for sales teams. It combines web scraping utilities, contact enrichment, phone dialing, and email automation into a single desktop application.

## Features

- **Company sourcing** &ndash; scrape potential leads from sites such as Clutch via the Apify API.
- **Contact enrichment** &ndash; gather contact data using a local Cognism scraper and other utilities.
- **Campaign management** &ndash; create and run email or phone campaigns from an intuitive PyQt5 interface.
- **Phone dialer** &ndash; automate calling workflows with optional Selenium and PyAutoGUI support.
- **Email outreach** &ndash; send personalized messages using built‑in templates.
- **CSV import** &ndash; load existing lead lists directly into the CRM database.

## Use Cases

- Building a prospect database for business development.
- Enriching existing contact lists with additional data points.
- Running targeted email or phone campaigns at scale.
- Organizing and tracking company interactions in one place.

## Tech Stack

- **Python 3** with **PyQt5** for the graphical user interface.
- **SQLite** for local data storage.
- Scraping and automation libraries such as **Apify**, **BeautifulSoup**, **Selenium**, and **pyautogui**.
- Data analysis with **pandas** and **numpy**.

## Integrations

- **Apify API** for company and website scraping.
- **Cognism** for contact data extraction.
- Optional browser automation via **Selenium** and desktop automation with **pyautogui**.
- Email delivery using standard SMTP settings.

## Getting Started

1. Install dependencies from `requirements.txt`.
2. Copy `example.env` to `.env` and adjust any environment variables.
3. Run the application:
   ```bash
   python -X utf8 main.py
   ```

See the [`docs`](docs/) directory for additional documentation and [`examples`](examples/) for sample scripts.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms of the [Apache 2.0 License](LICENSE).
