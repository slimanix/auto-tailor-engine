import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from flask import Flask, render_template, request, jsonify, Response
from engine import AutoTailorEngine
from job_hunter import JobHunter
from auto_applier import AutoApplier

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))

env_file = os.path.join(base_dir, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

profile_path = os.path.join(base_dir, "profile_data.json")
engine = AutoTailorEngine(profile_path)
hunter = JobHunter(profile_path)
applier = AutoApplier(profile_path)

# ── Tailor ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tailor", methods=["POST"])
def tailor_job():
    data = request.json or {}
    job_desc = data.get("job_desc", "").strip()
    company  = data.get("company",  "").strip()
    role     = data.get("role",     "").strip()
    lang     = data.get("lang",     "auto").strip()

    if not job_desc:
        return jsonify({"error": "Job description cannot be empty"}), 400

    result = engine.tailor_application(job_desc, company, role, lang)
    is_fr  = result["lang"] == "fr"

    portfolio_url = "https://portfolio-showcase-psi-sooty.vercel.app"
    recruiter_dm = (
        f"Bonjour,\n\nJe me permets de vous contacter suite à la publication de votre offre pour le poste de {role or 'Développeur'}"
        f"{' chez ' + company if company else ''}. Diplômé en Big Data (ENSA Kénitra) et Full-Stack, mon parcours allie expertise "
        f"technique (React, Python, Deep Learning) et rigueur opérationnelle. Vous pouvez consulter mon portfolio et démos de projets ici : {portfolio_url}\n\n"
        f"Je serais ravi d'échanger brièvement avec vous !\n\n"
        f"Bien cordialement,\nAbderrahmane El Idrissi Slimani"
        if is_fr else
        f"Hi there,\n\nI noticed the {role or 'Software Engineer'} opening{' at ' + company if company else ''} and wanted to reach out "
        f"directly. With a Bachelor's in Big Data (ENSA Kénitra) and hands-on experience in Full-Stack (React, Python, REST APIs) and "
        f"Deep Learning, I'm confident I can make an immediate impact. You can review my live production projects on my portfolio: {portfolio_url}\n\n"
        f"Would love to connect!\n\n"
        f"Best regards,\nAbderrahmane El Idrissi Slimani"
    )
    result["recruiter_dm"] = recruiter_dm
    return jsonify(result)

def sort_jobs(jobs, sort_key="ats_desc"):
    """Helper to sort jobs by various criteria."""
    if sort_key == "ats_desc":
        return sorted(jobs, key=lambda j: j.get("ats_score", 0), reverse=True)
    elif sort_key == "ats_asc":
        return sorted(jobs, key=lambda j: j.get("ats_score", 0))
    elif sort_key == "company_asc":
        return sorted(jobs, key=lambda j: (j.get("company") or "").lower())
    elif sort_key == "company_desc":
        return sorted(jobs, key=lambda j: (j.get("company") or "").lower(), reverse=True)
    elif sort_key == "title_asc":
        return sorted(jobs, key=lambda j: (j.get("title") or "").lower())
    elif sort_key == "location_asc":
        return sorted(jobs, key=lambda j: (j.get("location") or "").lower())
    elif sort_key == "source_asc":
        return sorted(jobs, key=lambda j: (j.get("source") or "").lower())
    return jobs

def sort_applications(apps, sort_key="date_desc"):
    """Helper to sort application records by date, score, company, status, etc."""
    if sort_key == "date_desc":
        return sorted(apps, key=lambda a: a.get("applied_at", ""), reverse=True)
    elif sort_key == "date_asc":
        return sorted(apps, key=lambda a: a.get("applied_at", ""))
    elif sort_key == "ats_desc":
        return sorted(apps, key=lambda a: a.get("ats_score", 0), reverse=True)
    elif sort_key == "ats_asc":
        return sorted(apps, key=lambda a: a.get("ats_score", 0))
    elif sort_key == "company_asc":
        return sorted(apps, key=lambda a: (a.get("company") or "").lower())
    elif sort_key == "company_desc":
        return sorted(apps, key=lambda a: (a.get("company") or "").lower(), reverse=True)
    elif sort_key == "title_asc":
        return sorted(apps, key=lambda a: (a.get("title") or "").lower())
    elif sort_key == "followup_asc":
        return sorted(apps, key=lambda a: a.get("followup_date", "") or "9999")
    elif sort_key == "status_asc":
        return sorted(apps, key=lambda a: (a.get("status") or "").lower())
    return apps

# ── Hunter ───────────────────────────────────────────────────────────────────

@app.route("/api/hunter/jobs", methods=["GET"])
def get_hunted_jobs():
    jobs = hunter.load_cached_jobs()
    sort_key = request.args.get("sort", "ats_desc")
    jobs = sort_jobs(jobs, sort_key)
    return jsonify({"jobs": jobs, "count": len(jobs), "sorted_by": sort_key})

@app.route("/api/hunter/scan", methods=["POST"])
def scan_jobs():
    try:
        data = request.json or {}
        mode = data.get("mode", "all")
        min_score = int(data.get("min_score", 65))
        jobs = hunter.scan_and_tailor(min_ats_score=min_score, mode=mode)
        return jsonify({"jobs": jobs, "count": len(jobs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/hunter/scan_bpo", methods=["POST"])
def scan_bpo_jobs():
    """Dedicated live scanner for Call Centers & Back-Office in Rabat, Salé, and Remote Morocco."""
    try:
        data = request.json or {}
        min_score = int(data.get("min_score", 55))
        jobs = hunter.scan_bpo(min_ats_score=min_score)
        bpo_jobs = [j for j in jobs if j.get("category") == "bpo"]
        return jsonify({"jobs": jobs, "bpo_jobs": bpo_jobs, "count": len(jobs), "bpo_count": len(bpo_jobs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Auto-Apply ────────────────────────────────────────────────────────────────

@app.route("/api/apply/run", methods=["POST"])
def run_auto_apply():
    """Auto-package applications for all high-scoring jobs and generate report."""
    data       = request.json or {}
    min_score  = int(data.get("min_score", 70))
    scan_first = bool(data.get("scan_first", False))
    mode       = data.get("mode", "all")

    try:
        if scan_first:
            if mode == "bpo":
                jobs = hunter.scan_bpo(min_ats_score=55)
            else:
                jobs = hunter.scan_and_tailor(min_ats_score=65, mode=mode)
        else:
            jobs = hunter.load_cached_jobs()

        if mode == "bpo":
            target_jobs = [j for j in jobs if j.get("category") == "bpo" or j.get("track") == "support_ops"]
        elif mode == "tech":
            target_jobs = [j for j in jobs if j.get("category") != "bpo" and j.get("track") != "support_ops"]
        else:
            target_jobs = jobs

        result = applier.run_auto_apply(target_jobs, min_score=min_score)
        result["scanned_live"] = scan_first
        result["mode"] = mode
        result["total_jobs_scanned"] = len(target_jobs)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/apply/log", methods=["GET"])
def get_applications_log():
    """Return full applications log with optional sorting."""
    log = applier.load_applied_log()
    sort_key = request.args.get("sort", "date_desc")
    log = sort_applications(log, sort_key)
    return jsonify({"applications": log, "count": len(log), "sorted_by": sort_key})

@app.route("/api/apply/update_status", methods=["POST"])
def update_application_status():
    """Update status of a specific application (e.g. 'Interview Scheduled', 'Rejected')."""
    data   = request.json or {}
    job_id = data.get("job_id", "")
    status = data.get("status", "")
    notes  = data.get("notes", "")

    if not job_id or not status:
        return jsonify({"error": "job_id and status required"}), 400

    log = applier.load_applied_log()
    updated = False
    for entry in log:
        if entry.get("job_id") == job_id:
            entry["status"] = status
            if notes:
                entry["notes"] = notes
            updated = True
            break

    if updated:
        applier.save_applied_log(log)
        applier.generate_reports(log)
        return jsonify({"success": True, "updated_job_id": job_id})
    else:
        return jsonify({"error": "Job ID not found"}), 404

@app.route("/api/apply/report/md", methods=["GET"])
def get_report_md():
    """Return the Markdown report as plain text."""
    tmp_path = os.path.join("/tmp", "Application_Report.md")
    md_path = tmp_path if os.path.exists(tmp_path) else os.path.join(base_dir, "Application_Report.md")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/plain")
    return Response("No report generated yet.", mimetype="text/plain")

@app.route("/api/apply/report/csv", methods=["GET"])
def get_report_csv():
    """Download the CSV report."""
    tmp_path = os.path.join("/tmp", "Application_Report.csv")
    csv_path = tmp_path if os.path.exists(tmp_path) else os.path.join(base_dir, "Application_Report.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            return Response(
                f.read(),
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=Applications_Abderrahmane.csv"}
            )
    return Response("No report available.", mimetype="text/plain")

@app.route("/api/apply/send_email", methods=["POST"])
def send_application_email():
    """Send an application email using the candidate's Gmail credentials stored in env."""
    data         = request.json or {}
    job_id       = data.get("job_id", "")
    recipient    = data.get("recipient_email", "")
    subject      = data.get("subject", "")
    body         = data.get("body", "")
    sender_email = os.environ.get("GMAIL_SENDER", "elidrissislimaniabderrahmane@gmail.com")
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not recipient:
        return jsonify({"error": "Recipient email is required"}), 400
    if not app_password:
        return jsonify({"error": "GMAIL_APP_PASSWORD env variable not set. See setup instructions."}), 400

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject or "Candidature — Abderrahmane El Idrissi Slimani"
        msg["From"]    = sender_email
        msg["To"]      = recipient

        # Find and attach tailored 1-page PDF CV
        app_dir = os.path.join(base_dir, "applications")
        if os.path.exists(app_dir):
            for folder in os.listdir(app_dir):
                if folder.startswith(job_id):
                    pdf_candidate = os.path.join(app_dir, folder, "CV_1Page.pdf")
                    html_candidate = os.path.join(app_dir, folder, "CV_1Page.html")
                    if not os.path.exists(pdf_candidate) and os.path.exists(html_candidate):
                        applier.convert_html_to_pdf(html_candidate, pdf_candidate)
                    if os.path.exists(pdf_candidate):
                        with open(pdf_candidate, "rb") as f:
                            att = MIMEApplication(f.read(), _subtype="pdf")
                            att.add_header("Content-Disposition", "attachment", filename="CV_Abderrahmane_El_Idrissi_Slimani.pdf")
                            msg.attach(att)
                        break

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient, msg.as_string())

        # Update log status
        log = applier.load_applied_log()
        for entry in log:
            if entry.get("job_id") == job_id:
                entry["status"] = "Email Sent"
                entry["email_sent_to"] = recipient
                break
        applier.save_applied_log(log)
        applier.generate_reports(log)

        return jsonify({"success": True, "sent_to": recipient})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Export & PDF ─────────────────────────────────────────────────────────────

@app.route("/api/apply/pdf/<job_id>", methods=["GET"])
def get_application_pdf(job_id):
    """Download the 1-page A4 PDF CV for a given job, with graceful HTML print fallback on serverless."""
    app_dir = os.path.join(base_dir, "applications")
    if os.path.exists(app_dir):
        for folder in os.listdir(app_dir):
            if folder.startswith(job_id):
                pdf_path = os.path.join(app_dir, folder, "CV_1Page.pdf")
                html_path = os.path.join(app_dir, folder, "CV_1Page.html")
                if not os.path.exists(pdf_path) and os.path.exists(html_path):
                    applier.convert_html_to_pdf(html_path, pdf_path)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        return Response(
                            f.read(),
                            mimetype="application/pdf",
                            headers={"Content-Disposition": f"attachment;filename=CV_Abderrahmane_{job_id}.pdf"}
                        )
                elif os.path.exists(html_path):
                    with open(html_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    print_script = "<script>window.onload = function() { window.print(); }</script></body>"
                    content = content.replace("</body>", print_script)
                    return Response(content, mimetype="text/html")

    # Fallback to cached jobs if applications directory is empty (e.g. serverless bundle)
    jobs = hunter.load_cached_jobs()
    for j in jobs:
        if j.get("id") == job_id and j.get("html_resume"):
            content = j["html_resume"]
            print_script = "<script>window.onload = function() { window.print(); }</script></body>"
            content = content.replace("</body>", print_script)
            return Response(content, mimetype="text/html")

    return jsonify({"error": "Application not found"}), 404

@app.route("/export/html", methods=["POST"])
def export_html():
    data         = request.json or {}
    html_content = data.get("html", "")
    return Response(
        html_content,
        mimetype="text/html",
        headers={"Content-Disposition": "attachment;filename=CV_Abderrahmane_El_Idrissi.html"}
    )

if __name__ == "__main__":
    print("Auto-Tailor Engine + Job Hunter + Auto-Applier running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
