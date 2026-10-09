import json
import re
from typing import Dict, Any, List, Tuple

class AutoTailorEngine:
    def __init__(self, profile_path: str):
        with open(profile_path, 'r', encoding='utf-8') as f:
            self.profile = json.load(f)

    def detect_language(self, text: str) -> str:
        french_markers = [
            "expérience", "poste", "missions", "compétences", "profil", "recherché", "nous recherchons", 
            "connaissance", "développeur", "données", "stage", "société", "équipe", "client", "clientèle",
            "rabat", "maroc", "appels", "chargé", "charge", "conseiller", "téléconseiller", "teleconseiller",
            "relation", "recherche", "salaire", "primes", "formation", "gestion", "traitement", "dossier"
        ]
        english_markers = ["experience", "responsibilities", "qualifications", "requirements", "we are looking for", "developer", "engineer", "skills", "team", "full-time", "opportunity", "data", "customer", "support"]
        
        lower_text = text.lower()
        fr_count = sum(1 for m in french_markers if m in lower_text)
        en_count = sum(1 for m in english_markers if m in lower_text)
        
        return "fr" if fr_count >= en_count and fr_count > 0 else "en"

    def classify_track(self, text: str) -> str:
        lower_text = text.lower()
        
        support_score = sum(1 for k in [
            "support", "incident", "crm", "helpdesk", "technicien", "sla", "customer service", 
            "application support", "analyste support", "ticketing", "back office", "back-office",
            "call center", "centre d'appel", "centre d'appels", "téléconseiller", "charge de clientele",
            "chargé de clientèle", "service client", "relation client", "bpo", "réclamation",
            "téléopérateur", "gestionnaire sinistre", "assistance technique", "customer care", "télévente"
        ] if k in lower_text)
        ai_score = sum(1 for k in ["data scientist", "machine learning", "deep learning", "ia", "ai", "tensorflow", "scikit", "nlp", "predictive", "modélisation", "big data", "pandas"] if k in lower_text)
        web_score = sum(1 for k in ["full-stack", "fullstack", "front-end", "back-end", "react", "javascript", "tailwind", "springboot", "laravel", "web developer", "développeur web"] if k in lower_text)

        scores = {"support_ops": support_score, "ai_ml": ai_score, "web_dev": web_score}
        best_track = max(scores, key=scores.get)
        return best_track if scores[best_track] > 0 else "web_dev"

    def extract_keywords(self, text: str) -> Tuple[List[str], List[str], int]:
        all_candidate_skills = (
            self.profile["skills_bank"]["ai_ml"] +
            self.profile["skills_bank"]["web_dev"] +
            self.profile["skills_bank"]["support_ops"] +
            self.profile["skills_bank"]["tools"]
        )
        
        # Deduplicate preserving order
        unique_skills = []
        for s in all_candidate_skills:
            if s not in unique_skills:
                unique_skills.append(s)

        lower_text = text.lower()
        matched = []
        for skill in unique_skills:
            # Match skill words as patterns
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, lower_text):
                matched.append(skill)

        # Detect tech and operations keywords from job description that might be missing
        potential_job_keywords = [
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "FastAPI", "Django", "Flask",
            "TypeScript", "Node.js", "Express", "GraphQL", "PostgreSQL", "MongoDB",
            "Kafka", "Spark", "PyTorch", "CI/CD", "Next.js", "Vue.js", "Agile", "Scrum",
            "Jira", "Selenium", "Linux", "DevOps", "ITIL", "Power BI", "Tableau",
            "CRM", "Zendesk", "Salesforce", "Ticketing", "SLA", "Excel", "CSAT", "BPO"
        ]
        missing = []
        for kw in potential_job_keywords:
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, lower_text) and kw not in matched:
                missing.append(kw)

        # Calculate ATS score
        total_eval = len(matched) + len(missing)
        if total_eval == 0:
            ats_score = 80
        else:
            base_score = int((len(matched) / total_eval) * 100)
            ats_score = max(55, min(96, base_score + 15))

        return matched, missing, ats_score

    def generate_tailored_summary(self, track: str, lang: str, target_company: str, target_role: str) -> str:
        company_mention = f"chez {target_company}" if target_company and lang == "fr" else (f"at {target_company}" if target_company else "")
        role_mention = target_role if target_role else ("ce poste" if lang == "fr" else "this role")

        if lang == "fr":
            if track == "ai_ml":
                return (
                    f"Data Scientist & Développeur IA diplômé d'une Licence Spécialisée en Big Data (ENSA Kénitra), "
                    f"alliant expertise en modélisation prédictive (TensorFlow, Scikit-learn) et solide socle en ingénierie logicielle. "
                    f"Fort d'expériences concrètes dans la conception de modèles de Deep Learning déployés en production et motivé à apporter une valeur "
                    f"analytique immédiate en tant que {role_mention} {company_mention}."
                )
            elif track == "web_dev":
                return (
                    f"Développeur Full-Stack moderne combinant une expertise pointue en React / Tailwind CSS et architectures back-end (APIs REST, Python, Java/PHP). "
                    f"Titulaire d'un diplôme en développement Full-Stack et d'une Licence Big Data, avec une expérience éprouvée en intégration de systèmes applicatifs "
                    f"et déploiement en production. Dynamique et trilingue, prêt à concevoir des applications web robustes et évolutives pour {company_mention or 'votre équipe'}."
                )
            else:
                return (
                    f"Professionnel trilingue alliant expérience opérationnelle en CDI dans le support d'entreprise et la gestion d'incidents (FedEx / Foundever) "
                    f"avec un solide bagage technique en analyse de données (SQL, Python) et développement logiciel. "
                    f"Spécialiste de la résolution d'anomalies complexes, du respect strict des SLAs et de la traçabilité sous CRM pour {company_mention or 'votre organisation'}."
                )
        else:
            if track == "ai_ml":
                return (
                    f"Results-driven Data Scientist & AI Developer with a Bachelor's in Big Data Engineering (ENSA Kénitra) "
                    f"bridging advanced predictive modeling (TensorFlow, Scikit-learn) with robust software engineering. "
                    f"Proven hands-on experience developing and deploying Deep Learning architectures into live production web environments. "
                    f"Excited to deliver high-impact data solutions as {role_mention} {company_mention}."
                )
            elif track == "web_dev":
                return (
                    f"Full-Stack Software Developer specializing in responsive frontend architectures (React, Tailwind CSS) "
                    f"and robust backend services (REST APIs, Python, SQL, Java/PHP). Backed by dual technical degrees in Full-Stack development and Big Data. "
                    f"Trilingual, proactive, and passionate about shipping clean, accessible, and high-performance software for {company_mention or 'your team'}."
                )
            else:
                return (
                    f"Trilingual Technical Support & Operations Specialist combining enterprise client experience (FedEx / Foundever) "
                    f"with practical computer science and data analytics proficiency (Python, SQL, REST APIs). "
                    f"Experienced in L1/L2 incident triage, root-cause troubleshooting, CRM workflows, and maintaining 99%+ SLA compliance for {company_mention or 'your company'}."
                )

    def generate_cover_letter(self, job_desc: str, target_company: str, target_role: str, track: str, lang: str) -> str:
        company_name = target_company if target_company.strip() else ("l'équipe de recrutement" if lang == "fr" else "the Hiring Team")
        role_name = target_role if target_role.strip() else ("ce poste" if lang == "fr" else "this position")

        p = self.profile
        portfolio_url = p.get('portfolio', 'https://portfolio-showcase-psi-sooty.vercel.app')

        if track == "support_ops":
            if lang == "fr":
                return f"""Abderrahmane El Idrissi Slimani
Rabat, Maroc | +212 762 609 561
elidrissislimaniabderrahmane@gmail.com
LinkedIn: linkedin.com/in/abderrahmane-el-idrissi-slimani | Portfolio: {portfolio_url}

Objet : Candidature au poste de {role_name}

Madame, Monsieur,

C’est avec un vif intérêt que je vous soumets ma candidature pour le poste de **{role_name}** au sein de **{company_name}**.

Actuellement en poste en CDI chez Foundever à Rabat en tant que Customer Service Representative (projet FedEx), j'assure au quotidien le traitement rigoureux de dossiers Back-Office, la gestion d'appels clients et partenaires, la résolution d'escalades complexes et le respect strict des indicateurs de performance (SLA 99%+, FCR, CSAT). Cette expérience m'a conféré une maîtrise approfondie des outils CRM, des workflows de ticketing et de la rigueur opérationnelle exigée dans les centres d'excellence.

Parallèlement, ma formation supérieure (Licence en Big Data à l'ENSA Kénitra et Diplôme en Développement Full-Stack) m'apporte une parfaite aisance avec les outils numériques, le traitement et la saisie de données, ainsi qu'une capacité rapide d'assimilation des logiciels métiers et processus internes.

Parfaitement trilingue (Français C1, Anglais C1, Arabe maternel) et reconnu pour mon écoute active, mon sens aigu de la relation client et ma fiabilité, je suis immédiatement disponible pour contribuer au succès de vos opérations chez {company_name}.

Je serais honoré d'échanger avec vous lors d'un entretien afin de vous exposer de vive voix ma motivation.

Je vous remercie pour l'attention portée à ma candidature et vous prie d'agréer, Madame, Monsieur, mes salutations distinguées.

Abderrahmane El Idrissi Slimani
"""
            else:
                return f"""Abderrahmane El Idrissi Slimani
Rabat, Morocco | +212 762 609 561
elidrissislimaniabderrahmane@gmail.com
LinkedIn: linkedin.com/in/abderrahmane-el-idrissi-slimani | Portfolio: {portfolio_url}

Subject: Application for {role_name}

Dear Hiring Team at {company_name},

I am writing to express my strong interest in the **{role_name}** opportunity at **{company_name}**.

Currently employed as a Customer Service Representative (permanent CDI) at Foundever Rabat on the FedEx project, I manage daily front and back-office customer operations, complex complaint resolutions, CRM ticketing workflows, and strict compliance with SLA and customer satisfaction (CSAT) metrics. This role has honed my attention to detail, interpersonal communication, and problem-resolution skills.

Additionally, my technical background—holding a Bachelor’s in Big Data Engineering from ENSA Kénitra alongside Full-Stack training—enables me to navigate corporate software, data management systems, and specialized business applications with speed and precision.

Fluent in English (C1), French (C1), and native in Arabic, I excel in high-tempo customer care and back-office environments. I am enthusiastic about the opportunity to bring my operational dedication and strong work ethic to {company_name}.

I would welcome the opportunity to speak with you in an interview to discuss how my qualifications align with your requirements.

Thank you for your consideration.

Sincerely,

Abderrahmane El Idrissi Slimani
"""

        if lang == "fr":
            return f"""Abderrahmane El Idrissi Slimani
Rabat, Maroc | +212 762 609 561
elidrissislimaniabderrahmane@gmail.com
LinkedIn: linkedin.com/in/abderrahmane-el-idrissi-slimani | Portfolio: {portfolio_url}

Objet : Candidature au poste de {role_name}

Madame, Monsieur,

C’est avec un vif enthousiasme que je vous adresse ma candidature pour le poste de **{role_name}** au sein de **{company_name}**. Titulaire d'une Licence Spécialisée en Big Data de l'ENSA Kénitra et d'un Diplôme de Technicien Spécialisé en Développement Full-Stack, mon parcours combine une rigueur logicielle approfondie et une capacité éprouvée à délivrer des solutions à fort impact.

Lors de mes récentes expériences, j’ai notamment conçu et déployé un système complet de détection de malwares par Deep Learning chez 3D Smart Factory (projet MalwaresInspector avec inférence optimisée LiteRT), intégrant un modèle TensorFlow à une interface web réactive (React, Tailwind CSS) via des APIs REST sécurisées. Vous pouvez d'ailleurs retrouver mes projets déployés et démonstrations interactives sur mon portfolio : {portfolio_url}. Parallèlement, mon expérience opérationnelle chez Foundever pour le compte de FedEx m’a permis de développer une réactivité exemplaire face aux incidents critiques, un sens aigu de la relation client internationale et une maîtrise rigoureuse des engagements SLA.

Rejoindre **{company_name}** représente pour moi l'opportunité de mettre au service de vos projets ma polyvalence technique, mon autonomie et mon enthousiasme à résoudre des problématiques complexes. Parfaitement trilingue (Français, Anglais, Arabe), je m'intègre avec agilité au sein d'équipes pluridisciplinaires et internationales.

Je serais honoré d'échanger avec vous lors d'un entretien afin de vous détailler en quoi mon profil répond aux exigences de vos défis actuels.

Je vous remercie par avance pour l'intérêt que vous porterez à ma démarche et vous prie d'agréer, Madame, Monsieur, mes salutations distinguées.

Abderrahmane El Idrissi Slimani
"""
        else:
            return f"""Abderrahmane El Idrissi Slimani
Rabat, Morocco | +212 762 609 561
elidrissislimaniabderrahmane@gmail.com
LinkedIn: linkedin.com/in/abderrahmane-el-idrissi-slimani | Portfolio: {portfolio_url}

Subject: Application for {role_name}

Dear Hiring Team at {company_name},

I am writing to express my strong enthusiasm for the **{role_name}** position at **{company_name}**. Holding a Bachelor’s in Big Data Engineering from ENSA Kénitra alongside an Associate Degree in Full-Stack Web Development, my background uniquely bridges production-grade software engineering with advanced predictive analytics.

During my work at 3D Smart Factory, I architected and deployed an end-to-end Deep Learning malware detection engine (MalwaresInspector project, live with optimized LiteRT inference), serving inference models through RESTful APIs into a modern React and Tailwind CSS user interface. You can explore my full portfolio of live production projects at {portfolio_url}. Furthermore, my operational experience managing high-priority client incidents for FedEx at Foundever has honed my capacity to troubleshoot under pressure, analyze systemic bottlenecks, and adhere strictly to high-standard SLAs.

{company_name}’s commitment to engineering excellence strongly resonates with my goals. Trilingual in English, French, and Arabic, I bring proven adaptability, solid code hygiene (Git, clean APIs), and a proactive problem-solving mindset that enables me to contribute value from day one.

I would welcome the opportunity to discuss how my technical skills and operational dedication align with your team's objectives in an interview.

Thank you for your time and consideration.

Sincerely,

Abderrahmane El Idrissi Slimani
"""

    def tailor_application(self, job_desc: str, target_company: str = "", target_role: str = "", lang_choice: str = "auto", forced_track: str = None) -> Dict[str, Any]:
        lang = self.detect_language(job_desc) if lang_choice == "auto" else lang_choice
        track = forced_track if forced_track else self.classify_track(job_desc)
        matched_skills, missing_skills, ats_score = self.extract_keywords(job_desc)
        summary = self.generate_tailored_summary(track, lang, target_company, target_role)
        cover_letter = self.generate_cover_letter(job_desc, target_company, target_role, track, lang)

        # Assemble tailored experiences
        tailored_experiences = []
        for exp in self.profile["experiences"]:
            exp_data = exp[lang]
            title = None
            bullets = None
            if track == "support_ops":
                title = exp_data.get("title_support") or exp_data.get("title_general") or exp_data.get("title_web") or exp_data.get("title_ai")
                bullets = exp_data.get("bullets_support") or exp_data.get("bullets_tech") or exp_data.get("bullets_web") or exp_data.get("bullets_ai")
            elif track == "ai_ml":
                title = exp_data.get("title_ai") or exp_data.get("title_general") or exp_data.get("title_web")
                bullets = exp_data.get("bullets_ai") or exp_data.get("bullets_tech") or exp_data.get("bullets_web")
            else: # web_dev
                title = exp_data.get("title_web") or exp_data.get("title_general") or exp_data.get("title_ai")
                bullets = exp_data.get("bullets_web") or exp_data.get("bullets_tech") or exp_data.get("bullets_ai")

            if not bullets:
                for k, v in exp_data.items():
                    if k.startswith("bullets_") and isinstance(v, list):
                        bullets = v
                        break
            if not bullets:
                bullets = []

            if not title:
                for k, v in exp_data.items():
                    if k.startswith("title_") and isinstance(v, str):
                        title = v
                        break
            if not title:
                title = "Software & Systems Specialist"

            tailored_experiences.append({
                "company": exp["company"],
                "period": exp["period"],
                "location": exp["location"],
                "title": title,
                "bullets": bullets
            })

        # Assemble Markdown resume
        md_resume = self._build_markdown_resume(summary, tailored_experiences, matched_skills, track, lang)
        html_resume = self._build_html_resume(summary, tailored_experiences, matched_skills, track, lang, target_role)

        return {
            "lang": lang,
            "track": track,
            "ats_score": ats_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "summary": summary,
            "tailored_experiences": tailored_experiences,
            "markdown_resume": md_resume,
            "html_resume": html_resume,
            "cover_letter": cover_letter
        }

    def _build_markdown_resume(self, summary: str, experiences: List[Dict[str, Any]], matched_skills: List[str], track: str, lang: str) -> str:
        p = self.profile
        skills_sec = "COMPÉTENCES TECHNIQUES" if lang == "fr" else "TECHNICAL SKILLS"
        exp_sec = "EXPÉRIENCES PROFESSIONNELLES" if lang == "fr" else "PROFESSIONAL EXPERIENCE"
        edu_sec = "FORMATION ACADÉMIQUE" if lang == "fr" else "EDUCATION"
        cert_sec = "CERTIFICATIONS" if lang == "fr" else "CERTIFICATIONS"
        lang_sec = "LANGUES" if lang == "fr" else "LANGUAGES"

        # Organize skills
        skills_list = matched_skills if len(matched_skills) >= 6 else (p["skills_bank"]["web_dev"][:5] + p["skills_bank"]["ai_ml"][:5])

        lines = [
            f"# {p['name'].upper()}",
            f"**{p['location']}** | **{p['phone']}** | **{p['email']}**",
            f"[LinkedIn]({p['linkedin']}) | [GitHub]({p['github']}) | [Portfolio]({p.get('portfolio', 'https://portfolio-showcase-psi-sooty.vercel.app')})\n",
            "---",
            f"### {summary}\n",
            f"## {skills_sec}",
            f"- **Core Tech:** {', '.join(skills_list)}",
            f"- **Frameworks & Libs:** React, Tailwind CSS, TensorFlow, Scikit-learn, REST APIs, Pandas, NumPy",
            f"- **Dev & DevOps:** Git, GitHub, Linux, Jupyter, Power BI, SQL\n",
            f"## {exp_sec}"
        ]

        for exp in experiences:
            lines.append(f"### {exp['title']} — **{exp['company']}** ({exp['period']})")
            for b in exp['bullets']:
                lines.append(f"- {b}")
            lines.append("")

        portfolio_url = p.get('portfolio', 'https://portfolio-showcase-psi-sooty.vercel.app')
        proj_sec = "PROJETS EN PRODUCTION & PORTFOLIO" if lang == "fr" else "LIVE PRODUCTION PROJECTS & PORTFOLIO"
        lines.append(f"## {proj_sec}")
        lines.append(f"- **MalwaresInspector (AI Cybersecurity):** Détection de malwares par Deep Learning (CNN VGG-16 quantifié LiteRT, <150ms de latence cloud) — [Démo Live](https://malwares-detector.vercel.app/) | [Code GitHub](https://github.com/slimanix/MalwersDetector)")
        lines.append(f"- **Auto-Tailor Engine (Full-Stack & ATS):** Radar multi-plateformes d'offres et moteur d'adaptation de CVs vectoriels A4 — [Démo Live](https://autotailorengine.vercel.app) | [Code GitHub](https://github.com/slimanix/auto-tailor-engine)")
        lines.append(f"- **Portfolio & Showcase Hub:** Vitrine d'ingénierie et projets déployés — [Accéder au Portfolio]({portfolio_url})\n")

        lines.append(f"## {edu_sec}")
        for edu in p["education"][lang]:
            lines.append(f"- **{edu['degree']}** — {edu['institution']} *({edu['period']})*")
            lines.append(f"  *{edu['highlights']}*")
        lines.append("")

        lines.append(f"## {cert_sec}")
        for cert in p["certifications"]:
            lines.append(f"- **{cert['name']}** — {cert['issuer']} (ID: `{cert['credential_id']}`)")
        lines.append("")

        lines.append(f"## {lang_sec}")
        lines.append(f"- {', '.join(p['languages'][lang])}")

        return "\n".join(lines)

    def _clean_target_role(self, target_role: str, track: str, lang: str) -> str:
        """Sanitizes raw ad titles into elegant, ATS-friendly professional subtitles."""
        if not target_role or not target_role.strip():
            if track == "support_ops":
                return "Customer Service & Operations Specialist" if lang == "en" else "Chargé de Clientèle & Opérations Back-Office"
            elif track == "ai_ml":
                return "Data Engineer & AI Specialist" if lang == "en" else "Ingénieur Données & Spécialiste IA"
            else:
                return "Full-Stack Software Engineer" if lang == "en" else "Ingénieur Développeur Full-Stack"

        clean = target_role.strip()
        # Remove recruitment prefixes & commercial marketing noise
        clean = re.sub(r'^(urgent\s*[:-]?\s*|recrutement\s*[:-]?\s*|nous recrutons\s*[:-]?\s*|dans l\s*immediat\s*!*[:-]?\s*)', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'(\s*[-|–/]\s*(package|salaire|primes|prime|cdi|h/f|f/h|weekend|shift|urgent|rabat|salé|sale|maroc|télétravail|teletravail).*)$', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s*\([^)]*(dh|mad|salaire|primes|prime|h/f|f/h|cdi)[^)]*\)', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s*[-|–]\s*$', '', clean).strip()

        # If title is still too long (> 50 chars), standardize nicely
        if len(clean) > 50:
            if track == "support_ops":
                return "Customer Service & Operations Specialist" if lang == "en" else "Chargé de Clientèle & Support Opérationnel"
            elif track == "ai_ml":
                return "Data & Machine Learning Engineer" if lang == "en" else "Ingénieur Big Data & IA"
            else:
                return "Full-Stack Software Engineer" if lang == "en" else "Développeur Full-Stack"

        clean = clean[0].upper() + clean[1:] if clean else ""
        return clean if len(clean) >= 3 else ("Customer Service & Operations Specialist" if track == "support_ops" else "Software & Data Engineer")

    def _build_html_resume(self, summary: str, experiences: List[Dict[str, Any]], matched_skills: List[str], track: str, lang: str, target_role: str) -> str:
        p = self.profile
        skills_list = matched_skills if len(matched_skills) >= 5 else (p["skills_bank"]["web_dev"][:4] + p["skills_bank"]["ai_ml"][:4])
        
        display_title = self._clean_target_role(target_role, track, lang)

        exp_html = ""
        for i, exp in enumerate(experiences):
            # 3 bullets for primary role, 2 for subsequent to guarantee strict 1-page A4
            bullets_to_show = exp['bullets'][:3] if i < 2 else exp['bullets'][:2]
            bullets_html = "".join([f"<li>{b}</li>" for b in bullets_to_show])
            
            tag_badge = ""
            if "Foundever" in exp['company']:
                tag_badge = '<span class="exp-tag">Contrat CDI — Projet FedEx</span>' if lang == "fr" else '<span class="exp-tag">Permanent CDI — FedEx Project</span>'
            elif "3D Smart" in exp['company']:
                tag_badge = '<span class="exp-tag">R&D Deep Learning</span>'

            exp_html += f"""
            <div class="exp-item">
                <div class="exp-header">
                    <span class="exp-role">{exp['title']}</span>
                    <span class="exp-date">{exp['period']}</span>
                </div>
                <div class="exp-sub">
                    <span class="exp-company">{exp['company']}</span>
                    <span class="exp-loc">• {exp['location']}</span>
                    {tag_badge}
                </div>
                <ul class="bullets">{bullets_html}</ul>
            </div>
            """

        edu_html = ""
        for edu in p["education"][lang]:
            edu_html += f"""
            <div class="edu-item">
                <div class="edu-header">
                    <span class="edu-degree">{edu['degree']}</span>
                    <span class="edu-date">{edu['period']}</span>
                </div>
                <div class="edu-inst">{edu['institution']}</div>
            </div>
            """

        cert_html = ""
        for cert in p["certifications"][:3]:
            cert_html += f"<li><strong>{cert['name']}</strong> — {cert['issuer']}</li>"

        languages_str = " • ".join(p['languages'][lang])

        # Categorized skills adapted to track
        if track == "support_ops":
            skill_row_1_label = "Relation Client & BPO" if lang == "fr" else "Customer Operations"
            skill_row_1_val = "Traitement Back-Office, Gestion d'appels & réclamations, Escalades complexes, SLAs (99%+), CSAT, FCR"
            skill_row_2_label = "Outils CRM & Bureautique" if lang == "fr" else "CRM & Productivity"
            skill_row_2_val = "Systèmes CRM & Ticketing, Excel & Google Sheets avancé, Outils collaboratifs, ERP"
            skill_row_3_label = "Compétences Techniques" if lang == "fr" else "Technical Foundation"
            skill_row_3_val = "Développement Full-Stack (React, Python), Bases SQL, Big Data, Automatisation informatique"
        else:
            skill_row_1_label = "Technologies Cibles" if lang == "fr" else "Targeted Stack"
            skill_row_1_val = ", ".join(skills_list)
            skill_row_2_label = "Développement & Données" if lang == "fr" else "Development & Data"
            skill_row_2_val = "React, Tailwind CSS, Python, TensorFlow, Scikit-learn, REST APIs, SQL, TypeScript, Pandas"
            skill_row_3_label = "DevOps & Méthodes" if lang == "fr" else "DevOps & Methods"
            skill_row_3_val = "Git, GitHub, Linux, Docker, CRM Ticketing, Power BI, Jupyter, Méthodes Agiles"

        lang_label = "Langues de Travail" if lang == "fr" else "Languages"
        portfolio_url = p.get('portfolio', 'https://portfolio-showcase-psi-sooty.vercel.app')
        portfolio_display = portfolio_url.replace("https://", "").replace("http://", "").rstrip("/")

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{p['name']} - Curriculum Vitae</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 6.5mm 12mm 5mm 12mm;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        font-size: 11px;
        line-height: 1.34;
        padding: 4px 14px;
        -webkit-font-smoothing: antialiased;
    }}

    /* Executive Classic Header */
    .header {{
        text-align: center;
        border-bottom: 2px solid #0f2942;
        padding-bottom: 4px;
        margin-bottom: 6px;
    }}
    .header h1 {{
        font-size: 21px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #0f2942;
        margin-bottom: 1.5px;
    }}
    .header .subtitle {{
        font-size: 11px;
        font-weight: 700;
        color: #1e40af;
        letter-spacing: 1.4px;
        text-transform: uppercase;
        margin-bottom: 3.5px;
    }}
    .header .contact-line {{
        font-size: 9.8px;
        font-weight: 500;
        color: #475569;
        line-height: 1.4;
    }}
    .header .contact-line a {{
        color: #1e40af;
        text-decoration: none;
        font-weight: 600;
    }}

    /* Section Headers */
    .section-title {{
        font-size: 10.4px;
        font-weight: 800;
        color: #0f2942;
        border-bottom: 1.5px solid #0f2942;
        padding-bottom: 2px;
        margin-top: 5.5px;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Professional Summary */
    .summary {{
        font-size: 10.4px;
        color: #334155;
        line-height: 1.36;
        text-align: justify;
        margin-bottom: 4px;
    }}

    /* Competencies Table */
    .skills-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 10.2px;
        margin-bottom: 3px;
    }}
    .skills-table td {{
        padding: 1.2px 0;
        vertical-align: top;
        line-height: 1.3;
    }}
    .skills-table .skill-cat {{
        width: 25%;
        font-weight: 700;
        color: #0f2942;
        white-space: nowrap;
    }}
    .skills-table .skill-val {{
        color: #334155;
    }}

    /* Experience */
    .exp-item {{
        margin-bottom: 4.5px;
    }}
    .exp-header {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }}
    .exp-role {{
        font-size: 11.2px;
        font-weight: 700;
        color: #0f172a;
    }}
    .exp-date {{
        font-size: 9.8px;
        font-weight: 600;
        color: #64748b;
        font-variant-numeric: tabular-nums;
    }}
    .exp-sub {{
        font-size: 10.4px;
        margin-bottom: 2px;
    }}
    .exp-company {{
        font-weight: 700;
        color: #1e40af;
    }}
    .exp-loc {{
        color: #64748b;
        font-weight: 500;
    }}
    .exp-tag {{
        display: inline-block;
        background: #f1f5f9;
        color: #0f766e;
        border: 1px solid #cbd5e1;
        padding: 0 4px;
        border-radius: 3px;
        font-size: 9.2px;
        font-weight: 600;
        margin-left: 6px;
    }}
    ul.bullets {{
        margin: 1px 0 2px 14px;
        padding: 0;
    }}
    ul.bullets li {{
        font-size: 10.1px;
        color: #334155;
        line-height: 1.31;
        margin-bottom: 1.5px;
    }}
    ul.bullets li strong {{
        color: #0f172a;
        font-weight: 600;
    }}

    /* Two Columns (Education & Certifications) */
    .bottom-grid {{
        display: flex;
        gap: 16px;
        margin-top: 2px;
    }}
    .col-left {{
        flex: 1.1;
    }}
    .col-right {{
        flex: 0.9;
    }}
    .edu-item {{
        margin-bottom: 3.5px;
    }}
    .edu-header {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }}
    .edu-degree {{
        font-size: 10.3px;
        font-weight: 700;
        color: #0f172a;
    }}
    .edu-date {{
        font-size: 9.5px;
        font-weight: 600;
        color: #64748b;
    }}
    .edu-inst {{
        font-size: 9.8px;
        color: #475569;
        font-weight: 500;
    }}
    .cert-list {{
        list-style: none;
        margin: 0;
        padding: 0;
    }}
    .cert-list li {{
        font-size: 9.8px;
        color: #334155;
        line-height: 1.3;
        margin-bottom: 2px;
        position: relative;
        padding-left: 10px;
    }}
    .cert-list li::before {{
        content: "•";
        position: absolute;
        left: 0;
        color: #1e40af;
        font-weight: bold;
    }}

    @media print {{
        body {{ padding: 0; margin: 0; }}
        @page {{ margin: 6mm 10mm 4mm 10mm; }}
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>{p['name']}</h1>
        <div class="subtitle">{display_title}</div>
        <div class="contact-line">
            {p['location']} &nbsp;•&nbsp; {p['phone']} &nbsp;•&nbsp; {p['email']}<br>
            LinkedIn: <a href="{p['linkedin']}">linkedin.com/in/abderrahmane-el-idrissi-slimani</a> &nbsp;•&nbsp; GitHub: <a href="{p['github']}">github.com/slimanix</a> &nbsp;•&nbsp; Portfolio: <a href="{portfolio_url}">{portfolio_display}</a>
        </div>
    </div>

    <div class="section-title">{"PROFIL PROFESSIONNEL" if lang == "fr" else "PROFESSIONAL PROFILE"}</div>
    <div class="summary">{summary}</div>

    <div class="section-title">{"COMPÉTENCES CLÉS & TECHNIQUES" if lang == "fr" else "CORE COMPETENCIES & EXPERTISE"}</div>
    <table class="skills-table">
        <tr>
            <td class="skill-cat">{skill_row_1_label} :</td>
            <td class="skill-val">{skill_row_1_val}</td>
        </tr>
        <tr>
            <td class="skill-cat">{skill_row_2_label} :</td>
            <td class="skill-val">{skill_row_2_val}</td>
        </tr>
        <tr>
            <td class="skill-cat">{skill_row_3_label} :</td>
            <td class="skill-val">{skill_row_3_val}</td>
        </tr>
        <tr>
            <td class="skill-cat">{lang_label} :</td>
            <td class="skill-val">{languages_str}</td>
        </tr>
    </table>

    <div class="section-title">{"EXPÉRIENCES PROFESSIONNELLES" if lang == "fr" else "PROFESSIONAL EXPERIENCE"}</div>
    {exp_html}

    <div class="bottom-grid">
        <div class="col-left">
            <div class="section-title" style="margin-top: 0;">{"FORMATION ACADÉMIQUE" if lang == "fr" else "EDUCATION"}</div>
            {edu_html}
        </div>
        <div class="col-right">
            <div class="section-title" style="margin-top: 0;">{"CERTIFICATIONS" if lang == "fr" else "CERTIFICATIONS"}</div>
            <ul class="cert-list">
                {cert_html}
            </ul>
        </div>
    </div>
</body>
</html>
"""
