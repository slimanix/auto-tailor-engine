import os
import sys
import json
import time
import re
import ssl
import smtplib
import subprocess
import urllib.request
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Dict, Any, Optional

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


class AutoApplier:
    def __init__(self, profile_path: str, log_file: str = "applications_log.json", base_app_dir: str = "applications"):
        self.profile_path = profile_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(self.base_dir, log_file)
        self.base_app_dir = os.path.join(self.base_dir, base_app_dir)
        os.makedirs(self.base_app_dir, exist_ok=True)

        # Load .env if present
        env_file = os.path.join(self.base_dir, ".env")
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.strip().split("=", 1)
                        os.environ[k.strip()] = v.strip()

        # Load profile for email body generation
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)

    # ── Log Management ─────────────────────────────────────────────────────

    def load_applied_log(self) -> List[Dict[str, Any]]:
        tmp_log = os.path.join("/tmp", "applications_log.json")
        target = tmp_log if os.path.exists(tmp_log) else self.log_file
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_applied_log(self, log_entries: List[Dict[str, Any]]) -> None:
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(log_entries, f, ensure_ascii=False, indent=2)
        except OSError:
            tmp_log = os.path.join("/tmp", "applications_log.json")
            try:
                with open(tmp_log, "w", encoding="utf-8") as f:
                    json.dump(log_entries, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    # ── Email Sending ──────────────────────────────────────────────────────

    def _build_application_email(self, job: Dict[str, Any], lang: str = "fr") -> Dict[str, str]:
        """Build personalized email subject and body for a job application."""
        title = job.get("title", "Poste Technique")
        company = job.get("company", "votre entreprise")
        name = self.profile.get("name", "Abderrahmane El Idrissi Slimani")
        email = self.profile.get("email", "elidrissislimaniabderrahmane@gmail.com")
        phone = self.profile.get("phone", "+212 762 609 561")
        track = job.get("track", "")

        is_support_bpo = track == "support_ops" or any(kw in (title + " " + job.get("description", "")).lower() for kw in [
            "back office", "back-office", "call center", "centre d'appel", "clientèle", "service client", 
            "téléconseiller", "téléopérateur", "chargé de clientèle", "support client", "customer service", "customer care"
        ])

        if is_support_bpo:
            if lang == "fr":
                subject = f"Candidature — {title} | {name}"
                body = (
                    f"Madame, Monsieur,\n\n"
                    f"Je vous adresse ma candidature pour le poste de {title} au sein de {company}.\n\n"
                    f"Actuellement Customer Service Representative (CDI) chez Foundever à Rabat (projet FedEx), "
                    f"j'assure au quotidien le traitement rigoureux de dossiers Back-Office, la gestion des réclamations, "
                    f"le support client et le respect strict des indicateurs SLA et de satisfaction (CSAT).\n\n"
                    f"Trilingue (Français C1, Anglais C1, Arabe maternel) et fort d'un cursus supérieur (Licence Big Data à l'ENSA Kénitra et Développement Full-Stack), "
                    f"je maîtrise parfaitement les outils CRM, les systèmes de ticketing, le traitement de données et l'environnement numérique d'entreprise.\n\n"
                    f"Vous trouverez ci-joint mon CV d'une page au format PDF détaillant mon parcours.\n"
                    f"Je reste à votre entière disposition pour un entretien afin de convenir d'une opportunité d'échange.\n\n"
                    f"Bien cordialement,\n"
                    f"{name}\n"
                    f"{phone} | {email}\n"
                    f"LinkedIn: https://www.linkedin.com/in/abderrahmane-el-idrissi-slimani/"
                )
            else:
                subject = f"Application — {title} | {name}"
                body = (
                    f"Dear Hiring Team,\n\n"
                    f"I am writing to submit my application for the {title} position at {company}.\n\n"
                    f"Currently working as a Customer Service Representative (permanent CDI) at Foundever Rabat on the FedEx project, "
                    f"I bring proven experience in front and back-office operations, CRM ticketing, escalations resolution, and maintaining 99%+ SLA and CSAT targets.\n\n"
                    f"Trilingual in English (C1), French (C1), and native in Arabic, with a solid background in data analysis and computer tools (Big Data at ENSA Kénitra), "
                    f"I am fast-learning, dependable, and immediately operational.\n\n"
                    f"Please find my tailored 1-page PDF CV attached. I would welcome the opportunity to discuss this role further.\n\n"
                    f"Best regards,\n"
                    f"{name}\n"
                    f"{phone} | {email}\n"
                    f"LinkedIn: https://www.linkedin.com/in/abderrahmane-el-idrissi-slimani/"
                )
            return {"subject": subject, "body": body}

        if lang == "fr":
            subject = f"Candidature — {title} | {name}"
            body = (
                f"Madame, Monsieur,\n\n"
                f"Je me permets de vous adresser ma candidature pour le poste de {title} "
                f"chez {company}.\n\n"
                f"Diplômé en Big Data de l'ENSA Kénitra et Technicien Spécialisé en "
                f"Développement Full-Stack (ISTA), je dispose d'une expérience concrète en :\n"
                f"  • Développement web Full-Stack (React, Python, REST APIs)\n"
                f"  • Data Science & Deep Learning (TensorFlow, Computer Vision)\n"
                f"  • Support applicatif & gestion d'incidents (CRM, SLA, ticketing)\n\n"
                f"Actuellement en poste en tant que Customer Service Representative chez "
                f"Foundever (projet FedEx), je suis à la recherche d'une opportunité qui me "
                f"permettrait de mettre davantage à profit mes compétences techniques.\n\n"
                f"Vous trouverez ci-joint mon CV personnalisé pour cette offre. "
                f"Je reste disponible pour un entretien à votre convenance.\n\n"
                f"Bien cordialement,\n"
                f"{name}\n"
                f"{phone} | {email}\n"
                f"LinkedIn: https://www.linkedin.com/in/abderrahmane-el-idrissi-slimani/"
            )
        else:
            subject = f"Application — {title} | {name}"
            body = (
                f"Dear Hiring Manager,\n\n"
                f"I am writing to express my interest in the {title} position "
                f"at {company}.\n\n"
                f"With a Bachelor's in Big Data (ENSA Kénitra) and a Full-Stack "
                f"Development diploma, I bring hands-on experience in:\n"
                f"  • Full-Stack Web Development (React, Python, REST APIs)\n"
                f"  • Data Science & Deep Learning (TensorFlow, Computer Vision)\n"
                f"  • Application Support & Incident Management (CRM, SLA, ticketing)\n\n"
                f"I am currently working as a Customer Service Representative at "
                f"Foundever (FedEx project) and am looking for an opportunity that "
                f"better leverages my technical skills.\n\n"
                f"Please find my tailored CV attached. "
                f"I would welcome the opportunity to discuss this role further.\n\n"
                f"Best regards,\n"
                f"{name}\n"
                f"{phone} | {email}\n"
                f"LinkedIn: https://www.linkedin.com/in/abderrahmane-el-idrissi-slimani/"
            )

        return {"subject": subject, "body": body}

    def convert_html_to_pdf(self, html_path: str, pdf_path: str) -> bool:
        """Converts an HTML 1-page CV to a crisp vector PDF using headless Edge/Chrome."""
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            return True

        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ]
        browser_exe = next((p for p in edge_paths if os.path.exists(p)), None)
        if not browser_exe or not os.path.exists(html_path):
            return False

        try:
            abs_html = os.path.abspath(html_path)
            abs_pdf = os.path.abspath(pdf_path)
            cmd = [
                browser_exe,
                "--headless",
                "--disable-gpu",
                "--run-all-compositor-stages-before-draw",
                "--no-pdf-header-footer",
                f"--print-to-pdf={abs_pdf}",
                f"file:///{abs_html.replace(os.sep, '/')}"
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 1000
        except Exception as e:
            print(f"[AutoApplier] PDF conversion error: {e}")
            return False

    def send_application_email(self, recipient: str, subject: str, body: str,
                                cv_pdf_path: Optional[str] = None,
                                cv_html_path: Optional[str] = None) -> Dict[str, Any]:
        """Send an actual application email via Gmail SMTP attaching the 1-page PDF CV."""
        sender = os.environ.get("GMAIL_SENDER", "elidrissislimaniabderrahmane@gmail.com")
        app_password = os.environ.get("GMAIL_APP_PASSWORD", "")

        if not app_password:
            return {"success": False, "error": "GMAIL_APP_PASSWORD not set"}

        # If PDF is not explicitly given, try to convert from HTML
        if not cv_pdf_path and cv_html_path and os.path.exists(cv_html_path):
            candidate_pdf = cv_html_path.replace(".html", ".pdf")
            if self.convert_html_to_pdf(cv_html_path, candidate_pdf):
                cv_pdf_path = candidate_pdf

        try:
            msg = MIMEMultipart("mixed")
            msg["Subject"] = subject
            msg["From"] = f"Abderrahmane El Idrissi Slimani <{sender}>"
            msg["To"] = recipient

            # Email body
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Attach 1-Page PDF CV (Strictly .pdf)
            if cv_pdf_path and os.path.exists(cv_pdf_path):
                with open(cv_pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
                attachment.add_header("Content-Disposition", "attachment",
                                     filename="CV_Abderrahmane_El_Idrissi_Slimani.pdf")
                msg.attach(attachment)

            # Send
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender, app_password)
                server.sendmail(sender, recipient, msg.as_string())

            print(f"[AutoApplier] [SUCCESS] Email SENT to {recipient}: {subject}")
            return {"success": True, "sent_to": recipient}

        except Exception as e:
            print(f"[AutoApplier] [FAILED] Email FAILED to {recipient}: {e}")
            return {"success": False, "error": str(e)}

    # ── Rekrute Direct Apply ───────────────────────────────────────────────

    def _extract_rekrute_apply_url(self, job_url: str) -> Optional[str]:
        """Try to extract the direct 'Postuler' (Apply) link from a Rekrute job page."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            req = urllib.request.Request(job_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                page = resp.read().decode("utf-8", errors="ignore")

            # Rekrute apply links look like: /cv/postuler-...-xxx.html or data-url="/cv/..."
            apply_match = re.search(r'href="(/cv/[^"]+)"', page)
            if apply_match:
                return f"https://www.rekrute.com{apply_match.group(1)}"

            # Alternative: look for "Postuler" button with onclick or data attributes
            postuler_match = re.search(r'data-url="(/[^"]*postul[^"]*)"', page, re.IGNORECASE)
            if postuler_match:
                return f"https://www.rekrute.com{postuler_match.group(1)}"

            # Fallback: open the job page itself
            return job_url

        except Exception:
            return job_url

    def _extract_emails_from_page(self, job_url: str, description: str) -> List[str]:
        """Extract valid recruiter email addresses from the job posting text."""
        all_text = description or ""
        raw_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', all_text)

        # Filter out junk emails & platform administrative contacts
        ignore_domains = [
            "example.com", "rekrute.com", "domain.com", "sentry.io",
            "w3.org", "schema.org", "google.com", "facebook.com",
            "twitter.com", "jquery.com", "mozilla.org", "cloudflare.com",
            "placeholder.com", "test.com", "email.com", "yourdomain.com",
            "tinyboards.co", "weworkremotely.com", "remotive.com",
            "png", "jpg", "jpeg", "gif", "svg", "webp", "js", "css"
        ]
        ignore_prefixes = [
            "exemple@", "example@", "noreply@", "no-reply@", "support@",
            "abuse@", "mailer-daemon@", "privacy@", "legal@", "gdpr@",
            "dpo@", "compliance@", "security@", "billing@", "press@",
            "webmaster@", "admin@", "hostmaster@"
        ]
        asset_exts = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".js", ".css", ".ico")

        valid_emails = []
        for em in raw_emails:
            em_lower = em.lower().strip()
            if any(em_lower.endswith(ext) for ext in asset_exts) or "@1x" in em_lower or "@2x" in em_lower or "@3x" in em_lower:
                continue
            if any(em_lower.startswith(p) for p in ignore_prefixes):
                continue
            domain_part = em_lower.split('@')[-1] if '@' in em_lower else ''
            if not domain_part or any(ign in domain_part for ign in ignore_domains):
                continue
            # Must look like a real domain with valid TLD (.com, .ma, .fr, .org, .net, .io, etc.)
            if not re.search(r'\.[a-zA-Z]{2,6}$', domain_part):
                continue
            if em_lower not in valid_emails:
                valid_emails.append(em_lower)

        return valid_emails

    # ── Core Apply Logic ───────────────────────────────────────────────────

    def apply_to_job(self, job: Dict[str, Any], auto_send: bool = True) -> Dict[str, Any]:
        """Full auto-application pipeline for a single job:
        1. Package CV, cover letter, recruiter DM
        2. Extract contact emails aggressively
        3. Auto-send email if possible
        4. Auto-extract Rekrute apply link
        5. Log everything
        """
        job_id = job.get("id", str(int(time.time())))
        company = job.get("company", "Entreprise IT")
        title = job.get("title", "Poste Technique")
        location = job.get("location", "Rabat (Maroc)")
        url = job.get("url", "")
        ats_score = job.get("ats_score", 85)
        description = job.get("description", "")
        lang = job.get("lang", "fr")

        # Aggressive email extraction
        emails = self._extract_emails_from_page(url, description)
        contact_email = emails[0] if emails else ""

        # Build application folder
        clean_comp = re.sub(r'[^a-zA-Z0-9_-]', '_', company)[:20]
        app_folder = os.path.join(self.base_app_dir, f"{job_id}_{clean_comp}")
        os.makedirs(app_folder, exist_ok=True)

        cv_html_path = os.path.join(app_folder, "CV_1Page.html")
        cv_pdf_path = os.path.join(app_folder, "CV_1Page.pdf")
        cv_md_path = os.path.join(app_folder, "CV_1Page.md")
        cover_letter_path = os.path.join(app_folder, "Cover_Letter.txt")
        recruiter_dm_path = os.path.join(app_folder, "Recruiter_DM.txt")

        # Save files
        if not os.path.exists(cv_html_path) and job.get("html_resume"):
            with open(cv_html_path, "w", encoding="utf-8") as f:
                f.write(job["html_resume"])

        # Convert to strict 1-page A4 PDF
        if os.path.exists(cv_html_path) and not os.path.exists(cv_pdf_path):
            self.convert_html_to_pdf(cv_html_path, cv_pdf_path)

        if not os.path.exists(cv_md_path) and job.get("markdown_resume"):
            with open(cv_md_path, "w", encoding="utf-8") as f:
                f.write(job["markdown_resume"])
        if not os.path.exists(cover_letter_path) and job.get("cover_letter"):
            with open(cover_letter_path, "w", encoding="utf-8") as f:
                f.write(job["cover_letter"])
        if not os.path.exists(recruiter_dm_path) and job.get("recruiter_dm"):
            with open(recruiter_dm_path, "w", encoding="utf-8") as f:
                f.write(job["recruiter_dm"])

        # ── Determine method and ACTUALLY apply ────────────────────────────

        method = "Packaged Only"
        status = "Packaged & Logged"
        apply_url = url
        email_sent_to = ""

        if contact_email and auto_send:
            # ACTUALLY SEND THE EMAIL with PDF ATTACHMENT
            email_data = self._build_application_email(job, lang)
            result = self.send_application_email(
                recipient=contact_email,
                subject=email_data["subject"],
                body=email_data["body"],
                cv_pdf_path=cv_pdf_path if os.path.exists(cv_pdf_path) else None
            )
            if result.get("success"):
                method = "Email Auto-Sent"
                status = "✅ Email Sent"
                email_sent_to = contact_email
            else:
                method = "Email Failed"
                status = f"❌ Email Failed: {result.get('error', 'Unknown')}"
                email_sent_to = contact_email

        elif "rekrute" in url.lower():
            apply_url = self._extract_rekrute_apply_url(url) or url
            method = "Rekrute Direct"
            status = "🔗 Apply Link Ready"
        elif "emploi-public" in url.lower():
            method = "Emploi-Public (Concours)"
            status = "🏛️ Concours Postuler"
        elif "alwadifa" in url.lower():
            method = "Alwadifa-Maroc"
            status = "📋 Concours Postuler"
        elif "linkedin" in url.lower():
            method = "LinkedIn Direct Apply"
            status = "💼 Apply on LinkedIn"
        elif "moncallcenter" in url.lower():
            method = "MonCallCenter Direct"
            status = "🎧 Apply on MonCallCenter"
        elif "remotive" in url.lower():
            method = "Remotive (Remote)"
            status = "🌐 Global Apply Link"
        elif "weworkremotely" in url.lower():
            method = "WeWorkRemotely (Remote)"
            status = "🌐 Global Apply Link"
        else:
            method = "Marocannonces / Portail"
            status = "🔗 Apply Link Ready"

        now_str = time.strftime("%Y-%m-%d %H:%M")
        followup_time = time.strftime("%Y-%m-%d", time.localtime(time.time() + 5 * 86400))

        record = {
            "job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "apply_url": apply_url,
            "ats_score": ats_score,
            "method": method,
            "contact_email": contact_email,
            "email_sent_to": email_sent_to,
            "status": status,
            "applied_at": now_str,
            "followup_date": followup_time,
            "folder": os.path.relpath(app_folder, self.base_dir),
            "cv_pdf": os.path.relpath(cv_pdf_path, self.base_dir) if os.path.exists(cv_pdf_path) else ""
        }

        return record

    # ── Batch Auto-Apply ───────────────────────────────────────────────────

    def run_auto_apply(self, hunted_jobs: List[Dict[str, Any]], min_score: int = 70, limit: Optional[int] = None) -> Dict[str, Any]:
        """Automatically apply to all eligible jobs:
        - Sends email where HR email is found
        - Generates Rekrute apply links
        - Packages all materials
        - Generates reports
        """
        current_log = self.load_applied_log()
        already_applied_ids = {entry["job_id"] for entry in current_log}

        new_applications = []
        emails_sent = 0
        links_ready = 0

        for job in hunted_jobs:
            if limit and len(new_applications) >= limit:
                break

            if job.get("id") in already_applied_ids:
                continue

            score = job.get("ats_score", 0)
            if score >= min_score:
                rec = self.apply_to_job(job, auto_send=True)
                new_applications.append(rec)
                current_log.insert(0, rec)

                if "Sent" in rec.get("status", ""):
                    emails_sent += 1
                elif "Link" in rec.get("status", ""):
                    links_ready += 1

        self.save_applied_log(current_log)
        self.generate_reports(current_log)

        return {
            "new_count": len(new_applications),
            "total_count": len(current_log),
            "emails_sent": emails_sent,
            "links_ready": links_ready,
            "new_applications": new_applications,
            "all_applications": current_log
        }

    # ── Report Generation ──────────────────────────────────────────────────

    def generate_reports(self, log_entries: List[Dict[str, Any]]) -> None:
        """Generates Application_Report.md and Application_Report.csv."""
        md_file = os.path.join(self.base_dir, "Application_Report.md")
        csv_file = os.path.join(self.base_dir, "Application_Report.csv")

        total_sent = sum(1 for e in log_entries if "Sent" in e.get("status", ""))
        total_links = sum(1 for e in log_entries if "Link" in e.get("status", ""))

        md_lines = [
            "# 📊 Automated Applications Report — Abderrahmane El Idrissi Slimani",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M')} | "
            f"**Total:** {len(log_entries)} | "
            f"**Emails Sent:** {total_sent} | "
            f"**Apply Links Ready:** {total_links}\n",
            "| Date & Time | Job Title | Company | Location | ATS | Method | Status | Follow-Up |",
            "| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: |"
        ]

        csv_lines = ["Job ID,Job Title,Company,Location,ATS Score,Method,Status,Email Sent To,Applied At,Follow-Up Due,URL,Apply URL"]

        for entry in log_entries:
            md_lines.append(
                f"| {entry['applied_at']} | **{entry['title']}** | {entry['company']} "
                f"| {entry['location']} | **{entry['ats_score']}%** | {entry['method']} "
                f"| `{entry['status']}` | {entry['followup_date']} |"
            )
            c_title = f'"{entry["title"]}"'
            c_comp = f'"{entry["company"]}"'
            c_loc = f'"{entry["location"]}"'
            c_status = f'"{entry["status"]}"'
            apply_url = entry.get("apply_url", entry.get("url", ""))
            email_sent = entry.get("email_sent_to", "")
            csv_lines.append(
                f'{entry["job_id"]},{c_title},{c_comp},{c_loc},{entry["ats_score"]},'
                f'{entry["method"]},{c_status},{email_sent},{entry["applied_at"]},'
                f'{entry["followup_date"]},{entry["url"]},{apply_url}'
            )

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("\n".join(csv_lines))

        print(f"[AutoApplier] Reports saved - {total_sent} emails sent, {total_links} apply links ready.")
