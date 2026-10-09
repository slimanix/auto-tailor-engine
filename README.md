# ⚡ Auto-Tailor Engine & Moroccan Job Hunter Bot

> **Autonomous multi-platform job scraper, ATS-optimized CV tailoring engine, classy 1-page vector PDF generator, and automated application bot.**  
> Built for **Abderrahmane El Idrissi Slimani** | Rabat, Morocco.

---

## 🌟 Key Features

### 1. 🤖 Multi-Platform Moroccan Job Hunter (`job_hunter.py`)
Live autonomous scrapers targeting Moroccan recruitment platforms and global remote boards:
- **MonCallCenter.ma**: Direct streams for Rabat (`/q-offres/?Ville=Rabat`), Salé Technopolis (`/q-offres/?Ville=Salé`), and keyword-based filtering (`back office`, `télétravail`).
- **Rekrute.com**: Full extraction of IT, Tech, and BPO listings in Rabat, Salé, Casablanca, and Remote Morocco.
- **Marocannonces.com**: Dedicated scraping across Tech/IT and Call Center/Back-Office categories.
- **LinkedIn Jobs (Guest API)**: Real-time queries for Customer Care, Support Operations, Full-Stack, and AI across Rabat-Salé-Kénitra and Morocco Remote.
- **Public & Remote Portals**: Emploi-Public (Concours Rabat), Alwadifa-Maroc, Remotive, and WeWorkRemotely.

---

### 2. 🎯 Dual-Track ATS Auto-Tailor Engine (`engine.py`)
Automatically classifies job descriptions and dynamically pivots between two career tracks:
1. **🎧 Support & Operations Track (`support_ops`)**:
   - Prioritizes Abderrahmane's **permanent CDI at Foundever in Rabat on the FedEx project**.
   - Highlights front/back-office operations, CRM ticketing, SLA compliance (99%+), complex escalation handling, and customer satisfaction metrics (CSAT, FCR).
   - Emphasizes trilingual fluency: **French (C1)**, **English (C1)**, and **Native Arabic**.
2. **💻 Tech & AI Track (`web_dev` / `ai_ml`)**:
   - Highlights the Bachelor’s in Big Data (ENSA Kénitra) & Full-Stack Web Development certification.
   - Highlights the Deep Learning malware detection engine at **3D Smart Factory** and data pipelines at **HubbleMind**.
   - Emphasizes Python, React, Tailwind CSS, TensorFlow, Scikit-learn, REST APIs, and SQL.

---

### 3. 📄 Classy & ATS-Compliant 1-Page Vector PDF (`engine.py` & `auto_applier.py`)
- **Executive Typography & Palette**: Oxford Midnight Navy (`#0f2942`), Royal Sapphire accents (`#1e40af`), and crisp contrast.
- **Strict ATS Parsing Compatibility**: Clean semantic markup, standard section headers (`PROFIL PROFESSIONNEL`, `COMPÉTENCES CLÉS`, `EXPÉRIENCES PROFESSIONNELLES`, `FORMATION ACADÉMIQUE`), plain-text contact information with zero unparseable graphics.
- **Guaranteed Single-Page A4 Geometry**: Automatically calibrated line heights and bullet allocations to produce a strict 1-page A4 vector PDF (`CV_1Page.pdf`) via Chromium/Edge headless without page spillover.
- **Tailored Deliverables**: Generates `CV_1Page.pdf`, `CV_1Page.html`, `Cover_Letter.txt`, and high-converting `Recruiter_DM.txt` messages.

---

### 4. 📬 Automated Multi-Channel Application Bot (`auto_applier.py`)
- **Aggressive Contact Extraction**: Parses recruiter and HR email addresses directly from job postings.
- **Direct SMTP Email Dispatch**: Automatically dispatches personalized application emails via Gmail SMTP with the 1-page PDF CV attached.
- **Direct Portal Links**: Instant one-click application URLs for Rekrute, MonCallCenter, LinkedIn, and Emploi-Public.
- **Audit Reports**: Continuously writes comprehensive markdown logs (`Application_Report.md`) and spreadsheet exports (`Application_Report.csv`).

---

### 5. 💻 Interactive Dashboard & Control Panel (`templates/index.html`)
- **Radar Switcher**: One-click toggling between:
  - 🎧 *Centres d'Appels & Back-Office Radar* (Rabat / Salé / Télétravail)
  - 💻 *Tech, IT & Data Radar* (React, Python, Cloud)
  - 🌐 *Global Overview*
- **Multi-Criteria Sorting & Live Search**:
  - Sort by **ATS Score** (High to Low / Low to High), **Company** (A-Z / Z-A), **Job Title** (A-Z / Z-A), **Location**, or **Source Platform**.
  - Real-time instant search bar for keywords, companies, or stacks.
  - Interactive clickable column headers with dynamic arrow indicators in the Applications Log table.
- **1-Click Actions**:
  - `📂 Pack & CV`: Modal preview of the tailored CV, Cover Letter, and Recruiter DM.
  - `📥 PDF`: Instant on-demand download of the vector A4 PDF CV.
  - `🌐 Postuler ↗`: Opens the job portal link directly.

---

## 🏗️ Project Architecture

```
auto_tailor_engine/
├── app.py                      # Flask REST API & Web Dashboard Server
├── engine.py                   # Core ATS optimization & executive resume generator
├── job_hunter.py               # Autonomous scrapers (MonCallCenter, Rekrute, LinkedIn, etc.)
├── auto_applier.py             # Packaging pipeline, PDF compiler & Gmail SMTP dispatcher
├── profile_data.json           # Centralized candidate master profile
├── hunted_jobs.json            # Cached database of hunted jobs
├── applications_log.json       # Real-time application tracking log
├── Application_Report.md       # Markdown summary report of sent applications
├── Application_Report.csv      # CSV export for spreadsheet tracking
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── templates/
│   └── index.html              # Responsive dark-theme dashboard UI
└── tests/                      # Verification and scraper exploration tests
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Google Chrome or Microsoft Edge installed (for headless vector PDF compilation)

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/slimanix/auto-tailor-engine.git
cd auto-tailor-engine
pip install -r requirements.txt
```

### 3. Configuration (Optional for Email Sending)
Copy the template configuration file:
```bash
copy .env.example .env
```
Edit `.env` to provide your Gmail sender address and 16-character Google App Password:
```env
GMAIL_SENDER=elidrissislimaniabderrahmane@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
```

### 4. Running the Dashboard
Launch the server:
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 📊 Endpoints & API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Main interactive web dashboard |
| `GET` | `/api/hunter/jobs?sort=ats_desc` | Returns hunted jobs with multi-criteria sorting |
| `POST`| `/api/hunter/scan_bpo` | Runs live scanner for Call Centers & Back-Office (Rabat/Salé/Remote) |
| `POST`| `/api/hunter/scan` | Runs live scanner for Tech & IT or all jobs (`mode: "tech" \| "all"`) |
| `POST`| `/api/apply/run` | Batch auto-packages applications, builds PDFs, and sends emails |
| `GET` | `/api/apply/log?sort=date_desc` | Returns full application history log with sorting |
| `GET` | `/api/apply/pdf/<job_id>` | Compiles and downloads 1-page vector A4 PDF CV on demand |
| `POST`| `/api/tailor` | Custom ATS analysis on any user-provided job description |

---

## 👤 Author
**Abderrahmane El Idrissi Slimani**  
- **Location**: Rabat, Morocco  
- **Portfolio Showcase**: [portfolio-showcase-psi-sooty.vercel.app](https://portfolio-showcase-psi-sooty.vercel.app)
- **LinkedIn**: [linkedin.com/in/abderrahmane-el-idrissi-slimani](https://www.linkedin.com/in/abderrahmane-el-idrissi-slimani/)  
- **GitHub**: [github.com/slimanix](https://github.com/slimanix)  
- **Email**: `elidrissislimaniabderrahmane@gmail.com`
