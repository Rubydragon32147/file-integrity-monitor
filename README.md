# File Integrity Monitoring System (FIMS)

A lightweight **Host Intrusion Detection System (HIDS)** built in Python. Monitors folders in real time using SHA-256 hashing and alerts you when files are modified, deleted, or created.

---

## Features

- Real-time file monitoring with instant alerts
- SHA-256 cryptographic hashing
- Severity-tagged alerts — `CRITICAL`, `HIGH`, `MEDIUM`
- Summary reports and full alert history
- File restore — revert any file to its baseline state
- Email alerts for critical changes
- Structured timestamped logging

---

## Setup

```bash
git clone https://github.com/yourusername/fims.git
cd fims
python -m venv venv
venv\Scripts\activate
pip install watchdog rich schedule
```

Edit `config.json` with your folder paths before running.

---

## Usage

```bash
python main.py --baseline        # snapshot current file state
python main.py --watch           # start live monitoring
python main.py --scan            # one-time manual check
python main.py --report          # view summary stats
python main.py --history         # view alert timeline
python main.py --restore "path"  # revert file to baseline
```

---

## Tech Stack

`Python` `watchdog` `rich` `schedule` `SHA-256` `smtplib`

---

## Skills Demonstrated

Cryptography · Endpoint Security · Incident Detection · CLI Design · Structured Logging

---

Built by [Your Name](https://github.com/yourusername) as a cybersecurity portfolio project.
