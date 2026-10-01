# HALA 

> **Hunting Arab Leaks & Assets**
> The first open-source CLI for Arabic-language threat intelligence.

[![CI](https://github.com/Cyber404Man/Hala/actions/workflows/ci.yml/badge.svg)](https://github.com/Cyber404Man/Hala/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

🇵🇸 [اقرأ بالعربي](README.ar.md)

---

## Why HALA?

Global threat intelligence tools were built for the West. They understand English, monitor Twitter and Reddit, and ignore the platforms Arabic speakers actually use.

Meanwhile, **400+ million Arabic speakers** face:

- Localized phishing in Arabic dialects
- Phone number leaks from regional telecoms
- Fake OTP pages targeting Arabic banks
- Scam messages on Telegram, WhatsApp, Facebook

**HALA is built for them.**

---

## Commands

| Command | Description |
|---------|-------------|
| `hala kashif <phone>` | Check if an Arabic phone number appears in known leaks |
| `hala sitr` | Get official opt-out links from Arabic/global data brokers |
| `hala athar @username` | OSINT search across 16 Arabic + global platforms |
| `hala sayyad --brand "jawwal"` | Generate likely phishing domains for Arabic brands |
| `hala nlp --text "..."` | Detect scam indicators in Arabic messages |

---

## Installation

From PyPI :

```bash
pip install hala-arab
```

From source (works now):

```bash
git clone https://github.com/Cyber404Man/Hala.git
cd Hala
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

---

## Quick Start

### Check a phone number

```bash
hala kashif 0599123456 --region PS
hala kashif +967712345678
hala kashif 0501234567 --region SA --json-out
```

### Clean your digital footprint

```bash
hala sitr
hala sitr --country PS
hala sitr --open
```

### OSINT on a username

```bash
hala athar @torvalds
hala athar @username --only-found
```

### Find phishing domains for a brand

```bash
hala sayyad --brand jawwal --dialect ps
hala sayyad --brand "زين" --suspicious-only
```

### Detect scam messages

```bash
hala nlp --text "مبروك! فزت بجائزة 5000 شيكل، اضغط الرابط"
# → SCAM (85/100)
```

---

## Data Sources

HALA uses 100% free, public APIs:

| Source | Data | Cost |
|--------|------|------|
| **XposedOrNot** | Email breaches | Free, no key |
| **LeakCheck.io** | Email + phone | 100 results/month free |
| **urlscan.io** | URL scanning | 100 scans/day free |
| **VirusTotal** | URL + file scanning | 500 req/day free |

**No paid APIs. No hidden costs. No personal data stored.**
---

## Roadmap

- [x] `hala kashif` — phone leak checker
- [x] `hala sitr` — data opt-out links
- [x] `hala athar` — Arabic OSINT
- [x] `hala sayyad` — phishing domain generator
- [x] `hala nlp` — Arabic scam detection (rule-based)
- [ ] **HALA-NLP** — fine-tuned Arabic security LLM
- [ ] **HALA-API** — REST API for banks & telecoms
- [ ] **HALA-Graph** — threat actor relationship graph
- [ ] **HALA-Honeypot** — active scammer tracking
- [ ] **HALA-Vision** — Arabic phishing screenshot detection

---

## Contributing

We welcome contributions from Arabic-speaking security researchers, developers, and OSINT analysts.

Ways to contribute:

- Add new Arabic leak metadata (no personal data!)
- Improve scam patterns in `scam_patterns.json`
- Add opt-out URLs for your country
- Translate the README to more Arabic dialects
- Report false positives / negatives

---

## License

MIT © HALA Community

---

**Built in Gaza. For 400+ million Arabic speakers. 🇵🇸**
