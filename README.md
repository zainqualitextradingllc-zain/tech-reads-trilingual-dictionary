<div align="center">

<img src="./app/assets/tech_reads_logo.jpg" alt="Tech Reads Logo" width="380" style="border-radius: 12px; margin-bottom: 12px;" />

# Tech Reads™ Trilingual Dictionary
### Professional English • 日本語 (Japanese) • اردو (Urdu) Terminology Suite

[![React Native](https://img.shields.io/badge/React_Native-Expo_SDK_52-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactnative.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL_Mode-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Ollama Swarm](https://img.shields.io/badge/Ollama_Swarm-Multi--Model-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai/)
[![Live Web App](https://img.shields.io/badge/Live_App-GitHub_Pages-brightgreen?style=for-the-badge&logo=github&logoColor=white)](https://zainqualitextradingllc-zain.github.io/tech-reads-trilingual-dictionary/)
[![License: Qualitex Trading LLC](https://img.shields.io/badge/License-Qualitex_Trading_LLC-00E5FF?style=for-the-badge)](./LICENSE)

<br/>

### 🌐 [Click Here to Open the Live Web Application](https://zainqualitextradingllc-zain.github.io/tech-reads-trilingual-dictionary/)

**A mission-critical trilingual professional dictionary and flashcard learning suite engineered by Qualitex Trading LLC under the Tech Reads™ brand.** Designed specifically for international trade, cross-border commerce, skilled technical workers, healthcare professionals, automotive engineers, and software developers operating between English, Japanese, and Urdu.

[🚀 Open Live App](https://zainqualitextradingllc-zain.github.io/tech-reads-trilingual-dictionary/) • [Download & Clone](#-download--quickstart) • [Features](#-key-features) • [Domain Coverage](#-professional-domains) • [Swarm Miner](#-ollama-swarm-miner-daemon) • [Legal & Disclaimer](#-copyright--legal-disclaimer)

---

</div>

## 🌟 Key Features

- **🔍 Unified 3-Way Instant Search**  
  Search seamlessly across all three languages simultaneously. Accepts:
  - English terms & definitions
  - Japanese Kanji (`変速機`), Kana (`とらんすみっしょん`), or Hepburn Romaji (`toransumisshon`)
  - Urdu Nastaliq (`ٹرانسمیشن`) or Phonetic Roman Urdu (`transmission / gearbox`)

- **🔊 Dialect-Accurate Text-to-Speech (TTS)**  
  Instant offline audio playback for both Japanese (`ja-JP`) and Urdu (`ur-PK`) with pitch normalization and phonetic fallback.

- **🎴 Interactive Flashcard Training Mode**  
  Built-in spaced repetition study mode with smooth 3D flip card animations, audio pronunciations, domain categorization, and self-assessment mastery counters.

- **📱 True Cross-Platform (Mobile & Web)**  
  Runs natively on Android and iOS via the free **Expo Go** app, and as a responsive desktop web application in any modern browser.

- **💾 100% Offline-Ready & Pre-Bundled**  
  Ships with 432+ comprehensively audited, high-precision technical terms embedded directly into `app/assets/dictionary.json` and backed by `data/dictionary.db` in high-concurrency SQLite WAL mode.

- **🤖 Autonomous Ollama Swarm Miner**  
  Background multi-agent Python daemon orchestrating local LLM workers (`qwen2.5:7b`, `deepseek-r1:8b`, `qwen2.5-coder:7b`, and `qwen3.5:4b`) to continuously discover, translate, phonetically audit, and auto-sync new terminology.

---

## 📚 Professional Domains (432+ Verified Terms)

| Domain | Verified Entries | Key Terminology Examples |
| :--- | :---: | :--- |
| **🚗 Automotive Engineering** | **82** | Transmission, Alternator, Camshaft, Catalytic Converter, Hybrid Inverter |
| **💻 Software & IT** | **72** | Kubernetes, CI/CD Pipeline, Pull Request, Latency, Containerization |
| **🏦 Banking & Finance** | **63** | Letter of Credit, Bill of Lading, Escrow, Forex Spread, Collateral |
| **💼 Workplace & Corporate** | **60** | Overtime Pay, Performance Appraisal, NDA, Resignation, Grievance |
| **📈 Business & Trade** | **60** | Incoterms, Free on Board (FOB), Tariff, Customs Declaration, Bill of Exchange |
| **⚖️ Legal & Contracts** | **32** | Power of Attorney, Indemnification, Arbitration, Jurisdiction, Tort |
| **🏥 Medical & Healthcare** | **32** | Myocardial Infarction, Hypertension, Biopsy, Intravenous, Prophylaxis |
| **📦 Logistics & Supply Chain** | **31** | Bill of Lading, Consignee, Demurrage, Intermodal Freight, Manifest |

---

## 🚀 Download & Quickstart

### Prerequisites
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (v18 or newer)
- [Python 3.10+](https://www.python.org/) *(Optional, only required if running the Ollama miner)*

### 1. Clone the Repository
```bash
git clone https://github.com/zainqualitextradingllc-zain/tech-reads-trilingual-dictionary.git
cd tech-reads-trilingual-dictionary
```

### 2. Install App Dependencies
```bash
cd app
npm install
cd ..
```

### 3. Launch the Application

#### On Windows (One-Click PowerShell Launcher):
```powershell
.\Start-App.ps1
```

#### On Any OS (Standard Terminal):
```bash
cd app
npx expo start
```

### How to View the App:
- **Web Browser:** Press <kbd>w</kbd> in your terminal to open immediately at `http://localhost:8081`.
- **Android / iPhone:** Install **Expo Go** from Google Play or the iOS App Store, then scan the QR code displayed in your terminal.
- **Android Emulator:** Press <kbd>a</kbd> with an active Android Virtual Device.

---

## 🤖 Ollama Swarm Miner Daemon

The repository includes a background terminology mining engine located in `/miner`. It uses local Ollama models to auto-mine, validate script encoding (Hiragana/Katakana regex & Nastaliq Arabic Unicode blocks), and sync the SQLite database directly with the mobile app bundle.

### Start the Miner Daemon:
```powershell
.\Start-Miner.ps1
```
Or directly via Python:
```bash
cd miner
python miner.py --all --loop
```

### Check Live Swarm Status:
```powershell
.\Show-Status.ps1
```

---

## 📁 Repository Structure

```text
tech-reads-trilingual-dictionary/
├── app/                              # React Native / Expo Mobile & Web App
│   ├── assets/                       # Brand logos, icons, and bundled dictionary
│   │   ├── dictionary.json           # 432+ audited entries (offline bundle)
│   │   ├── tech_reads_logo.jpg       # Tech Reads™ 3D neon emblem
│   │   ├── tech_reads_icon.jpg       # Tech Reads™ brand icon
│   │   └── qualitex_logo.jpg         # Qualitex Trading LLC corporate seal
│   ├── App.tsx                       # Full application UI (Search, TTS, Flashcards, Modal)
│   ├── app.json                      # Expo application manifest
│   └── package.json                  # React Native & Expo dependencies
│
├── data/                             # Data persistence layer
│   └── dictionary.db                 # Master SQLite database (WAL mode)
│
├── miner/                            # Swarm Intelligence & LLM Mining System
│   ├── miner.py                      # Multi-model Ollama swarm miner with auto-retry
│   ├── seeds.json                    # Seed keywords across all 8 domains
│   ├── audio_audit.py                # Phonetic & TTS pronunciation auditing
│   └── clean_audio.py                # Glitch removal & Nastaliq normalization
│
├── .gitignore                        # Standard Node, Python, and SQLite ignore rules
├── LICENSE                           # Official Qualitex Trading LLC Software License
├── DISCLAIMER.md                     # Legal, Lexicographical & Medical/Legal Disclaimers
├── README.md                         # Product documentation (this file)
├── Show-Status.ps1                   # Live database & Ollama status monitor
├── Start-App.ps1                     # One-click app launcher
└── Start-Miner.ps1                   # One-click Ollama miner launcher
```

---

## ⚖️ Copyright & Legal Disclaimer

- **Copyright © 2026 Qualitex Trading LLC. All rights reserved.**
- **Tech Reads™** and the Tech Reads 3D emblem are registered trademarks / proprietary branding of **Qualitex Trading LLC**.
- Medical, legal, automotive, and financial terminology provided in this application is for linguistic translation and educational reference only. For detailed disclaimers regarding professional liability, trade compliance, and AI generation notices, please review [DISCLAIMER.md](./DISCLAIMER.md).

For licensing inquiries, corporate partnerships, or custom enterprise linguistic datasets:
- **Corporate Entity:** Qualitex Trading LLC
- **Brand:** Tech Reads™
- **Email:** `zain_qualitex@outlook.com`
- **GitHub:** [@zainqualitextradingllc-zain](https://github.com/zainqualitextradingllc-zain)
