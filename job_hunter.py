import os
import re
import json
import time
import urllib.request
import html
import ssl
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from engine import AutoTailorEngine

class JobHunter:
    def __init__(self, profile_path: str, output_base_dir: str = "applications"):
        self.output_base_dir = output_base_dir
        self.engine = AutoTailorEngine(profile_path)
        self.jobs_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hunted_jobs.json")
        os.makedirs(self.output_base_dir, exist_ok=True)
        
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    def _clean_html(self, raw_html: str) -> str:
        if not raw_html:
            return ""
        cleaned = re.sub(r'<(script|style).*?>.*?</\1>', '', raw_html, flags=re.DOTALL)
        cleaned = re.sub(r'<(br|p|li|/p|/div)>', '\n', cleaned)
        cleaned = re.sub(r'<[^<]+?>', ' ', cleaned)
        return html.unescape(re.sub(r'\s+', ' ', cleaned)).strip()

    # ── 1. Rekrute.com (Maroc) ─────────────────────────────────────────────
    def fetch_rekrute_morocco(self, target_cities: List[str] = ["rabat", "salé", "sale", "kénitra", "kenitra"]) -> List[Dict[str, Any]]:
        """Scrapes tech positions from Rekrute.com focused on Rabat, Salé, Kénitra."""
        print("[JobHunter] Scanning Rekrute Morocco (Rabat, Salé, Kénitra)...")
        sources = [
            "https://www.rekrute.com/offres-emploi-rabat.html",
            "https://www.rekrute.com/offres-emploi-metiers-de-l-it.html",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=informatique+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=developpeur+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=react+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=python+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=data+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=support+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=technopolis",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=kenitra",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=sale"
        ]

        found_links = {}
        for url in sources:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')

                raw_links = re.findall(r'href="(/offre-emploi-[^"]+\.html)[^"]*"', page_html)
                for link in raw_links:
                    link_clean = link.split('?')[0]
                    full_url = f"https://www.rekrute.com{link_clean}"
                    if full_url not in found_links:
                        found_links[full_url] = link_clean
            except Exception as e:
                pass

        jobs = []
        for full_url, link_path in list(found_links.items())[:35]:
            try:
                slug = link_path.replace('/offre-emploi-', '').replace('.html', '')
                parts = slug.split('-recrutement-')
                title_slug = parts[0].replace('-', ' ').title() if len(parts) > 0 else "Poste Technique"
                meta_slug = parts[1] if len(parts) > 1 else ""

                is_target_region = any(c in slug.lower() for c in target_cities) or "rabat" in slug.lower() or "kenitra" in slug.lower()

                req = urllib.request.Request(full_url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=6, context=self.ssl_ctx) as resp:
                    detail_html = resp.read().decode('utf-8', errors='ignore')

                comp_match = (
                    re.search(r'Recruteur\s*:\s*<strong>(.*?)</strong>', detail_html) or
                    re.search(r'alt="logo\s+([^"]+)"', detail_html, re.IGNORECASE) or
                    re.search(r'Entreprise\s*:\s*([A-Za-z0-9\s_-]+)', detail_html)
                )
                company = comp_match.group(1).strip() if comp_match else (meta_slug.split('-')[0].title() if meta_slug else "Entreprise IT")

                sections = re.findall(r'<div[^>]+class="col-md-12[^"]*"[^>]*>(.*?)</div>', detail_html, re.DOTALL)
                desc_parts = []
                for s in sections:
                    clean_s = self._clean_html(s)
                    if any(k in clean_s.lower() for k in ['poste', 'profil', 'mission', 'compétence', 'responsabilité', 'technique', 'outils']):
                        desc_parts.append(clean_s)

                full_desc = "\n\n".join(desc_parts)
                if not full_desc or len(full_desc) < 80:
                    full_desc = self._clean_html(detail_html)[:2000]

                location = "Rabat (Maroc)"
                lower_html = detail_html.lower()
                if "kénitra" in lower_html or "kenitra" in lower_html:
                    location = "Kénitra (Maroc)"
                elif "salé" in lower_html or "sale" in lower_html:
                    location = "Salé / Technopolis (Maroc)"
                elif "télétravail" in lower_html or "remote" in lower_html:
                    location = "Télétravail (Maroc)"

                if not (any(c in location.lower() for c in target_cities) or is_target_region or "rabat" in location.lower()):
                    continue

                if not self.is_relevant_job(title_slug, full_desc, [location, company]):
                    continue

                match_id = re.search(r'-(\d+)\.html', link_path)
                job_id_num = match_id.group(1) if match_id else str(int(time.time()))
                job_id = f"rek_{job_id_num}"

                jobs.append({
                    "id": job_id,
                    "source": "Rekrute (Maroc)",
                    "title": title_slug,
                    "company": company,
                    "location": location,
                    "tags": [location, "Maroc", "CDI"],
                    "url": full_url,
                    "description": full_desc,
                    "posted_at": "Récent"
                })
            except Exception:
                continue

        print(f"[Rekrute] Found {len(jobs)} relevant positions.")
        return jobs

    # ── 2. Marocannonces.com ───────────────────────────────────────────────
    def fetch_marocannonces(self) -> List[Dict[str, Any]]:
        """Scrapes IT & Multimedia announcements from Marocannonces for Rabat, Salé, Kénitra."""
        print("[JobHunter] Scanning Marocannonces (Rabat & Region)...")
        cities = {
            "Rabat": "https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-rabat-b309-m7.html",
            "Salé": "https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-sale-b309-m77.html",
            "Kénitra": "https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-kenitra-b309-m16.html"
        }

        jobs = []
        for city, target_url in cities.items():
            try:
                req = urllib.request.Request(target_url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')

                annonces = re.findall(r'href="([^"]*annonce/(\d+)/([^"]+)\.html)"', page_html)
                for full_href, ann_id, slug in annonces[:8]:
                    title = slug.replace('-', ' ').title()
                    full_url = f"https://www.marocannonces.com/{full_href.lstrip('/')}" if not full_href.startswith('http') else full_href

                    if not self.is_relevant_job(title, title, [city]):
                        continue

                    jobs.append({
                        "id": f"ma_{ann_id}",
                        "source": "Marocannonces",
                        "title": title,
                        "company": "Entreprise Partenaire (Maroc)",
                        "location": f"{city} (Maroc)",
                        "tags": [city, "Informatique", "Maroc"],
                        "url": full_url,
                        "description": f"Poste dans l'informatique, le développement ou le support basé à {city}. Référence annonce: {ann_id}.",
                        "posted_at": "Récent"
                    })
            except Exception as e:
                pass

        print(f"[Marocannonces] Found {len(jobs)} relevant local announcements.")
        return jobs

    # ── 3. Emploi-Public.ma (Rabat Ministries & Public Agencies) ──────────
    def fetch_emploi_public(self) -> List[Dict[str, Any]]:
        """Scrapes official public sector IT competitions & positions in Rabat."""
        print("[JobHunter] Scanning Emploi-Public.ma (Civil Service & Public Digital Agencies in Rabat)...")
        jobs = []
        try:
            url = "https://www.emploi-public.ma/fr/concours-liste"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                html_text = resp.read().decode('utf-8', errors='ignore')

            matches = re.findall(r'<a[^>]*href="(/fr/concours/details/[^"]+)"[^>]*>(.*?)</a>', html_text, re.DOTALL)
            for link, title_raw in matches:
                clean_title = re.sub(r'<[^>]+>', ' ', title_raw)
                clean_title = html.unescape(re.sub(r'\s+', ' ', clean_title)).strip()
                if not clean_title or len(clean_title) < 5:
                    continue
                if any(k in clean_title.lower() for k in ["informatique", "ingénieur", "ingenieur", "technicien", "système", "systeme", "développeur", "data", "réseau", "reseau"]):
                    guid = link.split('/')[-1]
                    jobs.append({
                        "id": f"ep_{guid[:10]}",
                        "source": "Emploi-Public.ma (Rabat)",
                        "title": clean_title,
                        "company": "Secteur Public / Ministère / Établissement (Rabat)",
                        "location": "Rabat (Maroc)",
                        "tags": ["Rabat", "Concours IT", "Secteur Public"],
                        "url": f"https://www.emploi-public.ma{link}",
                        "description": f"Concours officiel de recrutement IT / Ingénieur / Technicien publié sur Emploi-Public.ma à Rabat. Titre: {clean_title}.",
                        "posted_at": "Récent"
                    })
        except Exception as e:
            print(f"[EmploiPublic] Error: {e}")

        print(f"[Emploi-Public] Found {len(jobs)} public IT competitions.")
        return jobs

    # ── 4. Alwadifa-Maroc.com ──────────────────────────────────────────────
    def fetch_alwadifa(self) -> List[Dict[str, Any]]:
        """Scrapes announcements from Alwadifa-Maroc for IT / technical competitions in Morocco."""
        print("[JobHunter] Scanning Alwadifa-Maroc (Concours & Recrutements IT)...")
        jobs = []
        try:
            url = "https://www.alwadifa-maroc.com/"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                html_text = resp.read().decode('utf-8', errors='ignore')

            matches = re.findall(r'href="(/offre/show/id/(\d+))"[^>]*>(.*?)</a>', html_text, re.DOTALL)
            for link, offer_id, title_raw in matches:
                clean_title = re.sub(r'<[^>]+>', ' ', title_raw).strip()
                if not clean_title:
                    continue
                if any(k in clean_title.lower() for k in ["informatique", "ingénieur", "ingenieur", "technicien", "développeur", "data", "réseau", "technologie"]):
                    jobs.append({
                        "id": f"alw_{offer_id}",
                        "source": "Alwadifa-Maroc",
                        "title": clean_title,
                        "company": "Établissement Public / ESN Partenaire",
                        "location": "Rabat / Maroc",
                        "tags": ["Maroc", "Concours IT", "Alwadifa"],
                        "url": f"https://www.alwadifa-maroc.com{link}",
                        "description": f"Avis de recrutement et concours IT au Maroc : {clean_title}. Référence offre: {offer_id}.",
                        "posted_at": "Récent"
                    })
        except Exception as e:
            print(f"[Alwadifa] Error: {e}")

        print(f"[Alwadifa-Maroc] Found {len(jobs)} announcements.")
        return jobs

    # ── 5. Remotive.com API (Remote Tech hiring in Morocco / EMEA) ───────────
    def fetch_remotive_jobs(self) -> List[Dict[str, Any]]:
        """Fetches remote software, AI & data jobs hiring in Morocco / Worldwide from Remotive API."""
        print("[JobHunter] Scanning Remotive (Worldwide & EMEA Remote Tech Openings)...")
        jobs = []
        try:
            url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=25"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            raw_list = data.get("jobs", [])
            for item in raw_list:
                req_loc = item.get("candidate_required_location", "")
                if any(k in req_loc.lower() for k in ["world", "anywhere", "emea", "africa", "morocco", "global"]) or not req_loc:
                    clean_desc = re.sub(r'<[^>]+>', ' ', item.get("description", "")).strip()
                    title = item.get("title", "Software Engineer")
                    company = item.get("company_name", "Remote Tech Company")

                    if not self.is_relevant_job(title, clean_desc, ["Remote"]):
                        continue

                    jobs.append({
                        "id": f"rem_{item.get('id')}",
                        "source": "Remotive (Global Remote)",
                        "title": title,
                        "company": company,
                        "location": f"Remote ({req_loc or 'Worldwide'})",
                        "tags": (item.get("tags", []) or [])[:3] + ["100% Remote"],
                        "url": item.get("url", ""),
                        "description": clean_desc[:2000],
                        "posted_at": "Récent"
                    })
        except Exception as e:
            print(f"[Remotive] Error: {e}")

        print(f"[Remotive] Found {len(jobs)} global remote tech jobs accessible from Morocco.")
        return jobs

    # ── 6. WeWorkRemotely RSS (Remote Python, Full-Stack, AI) ───────────────
    def fetch_weworkremotely(self) -> List[Dict[str, Any]]:
        """Fetches international remote tech jobs from WeWorkRemotely RSS."""
        print("[JobHunter] Scanning WeWorkRemotely (Remote Full-Stack, Python & AI)...")
        jobs = []
        urls = [
            "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
            "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss"
        ]
        for u in urls:
            try:
                req = urllib.request.Request(u, headers=self.headers)
                with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                    xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item")[:15]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    raw_desc = item.find("description").text if item.find("description") is not None else ""
                    clean_desc = re.sub(r'<[^>]+>', ' ', raw_desc).strip()

                    parts = title.split(":", 1)
                    comp = parts[0].strip() if len(parts) > 1 else "Tech Company"
                    role = parts[1].strip() if len(parts) > 1 else title

                    if not self.is_relevant_job(role, clean_desc, ["Remote"]):
                        continue

                    link_id = abs(hash(link)) % 1000000
                    jobs.append({
                        "id": f"wwr_{link_id}",
                        "source": "WeWorkRemotely",
                        "title": role,
                        "company": comp,
                        "location": "100% Remote (Worldwide)",
                        "tags": ["Remote", "Full-Stack", "Python/React"],
                        "url": link,
                        "description": clean_desc[:2000],
                        "posted_at": "Récent"
                    })
            except Exception as e:
                pass

        print(f"[WeWorkRemotely] Found {len(jobs)} remote jobs.")
        return jobs

    # ── 7. LinkedIn Jobs (Rabat, Salé, Kénitra & Maroc) ───────────────────
    def fetch_linkedin_morocco(self) -> List[Dict[str, Any]]:
        """Scrapes live LinkedIn tech positions for Rabat, Salé, Kénitra via LinkedIn Guest API."""
        print("[JobHunter] Scanning LinkedIn Jobs (Rabat-Salé-Kénitra & Maroc)...")
        queries = [
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=React+OR+Python+OR+Data+OR+Support&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0",
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Developpeur+OR+Software+Engineer&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0",
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Fullstack+OR+Big+Data+OR+AI&location=Morocco&start=0"
        ]

        li_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
            "Referer": "https://www.linkedin.com/jobs"
        }

        jobs = []
        seen_ids = set()

        for q_url in queries:
            try:
                req = urllib.request.Request(q_url, headers=li_headers)
                with urllib.request.urlopen(req, timeout=10, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')

                cards = re.findall(r'<li[^>]*>(.*?)</li>', page_html, re.DOTALL)
                for c in cards:
                    link_m = re.search(r'href="([^"]+)"', c)
                    if not link_m:
                        continue
                    full_link = link_m.group(1).split('?')[0]

                    id_m = re.search(r'-(\d+)(?:$|\?)', full_link) or re.search(r'/view/(\d+)', full_link)
                    job_id = id_m.group(1) if id_m else str(abs(hash(full_link)) % 100000000)
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title_m = re.search(r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(.*?)</h3>', c, re.DOTALL)
                    company_m = re.search(r'<h4[^>]*class="[^"]*base-search-card__subtitle[^"]*"[^>]*>(.*?)</h4>', c, re.DOTALL)
                    loc_m = re.search(r'<span[^>]*class="[^"]*job-search-card__location[^"]*"[^>]*>(.*?)</span>', c, re.DOTALL)

                    title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1)).strip()) if title_m else "Poste Technique"
                    company = html.unescape(re.sub(r'<[^>]+>', '', company_m.group(1)).strip()) if company_m else "Entreprise LinkedIn"
                    loc = html.unescape(re.sub(r'<[^>]+>', '', loc_m.group(1)).strip()) if loc_m else "Rabat (Maroc)"

                    desc = f"Poste de {title} chez {company} basé à {loc} sur LinkedIn."
                    try:
                        detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                        req_det = urllib.request.Request(detail_url, headers=li_headers)
                        with urllib.request.urlopen(req_det, timeout=6, context=self.ssl_ctx) as det_resp:
                            det_html = det_resp.read().decode('utf-8', errors='ignore')
                            dm = re.search(r'<div[^>]*class="[^"]*show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>', det_html, re.DOTALL)
                            if dm:
                                desc = self._clean_html(dm.group(1))
                    except Exception:
                        pass

                    if not self.is_relevant_job(title, desc, [loc, company]):
                        continue

                    jobs.append({
                        "id": f"li_{job_id}",
                        "source": "LinkedIn Jobs",
                        "title": title,
                        "company": company,
                        "location": loc,
                        "tags": ["LinkedIn", "Morocco", "Rabat"],
                        "url": full_link,
                        "description": desc[:2500],
                        "posted_at": "Récent"
                    })
            except Exception as e:
                print(f"[LinkedIn] Error: {e}")

        print(f"[LinkedIn Jobs] Found {len(jobs)} relevant LinkedIn job postings in Morocco.")
        return jobs

    # ── 8. MonCallCenter.ma (Rabat, Salé, Back-Office & Télétravail) ─────
    def fetch_moncallcenter(self) -> List[Dict[str, Any]]:
        """Scrapes Call Center and Back-Office positions from MonCallCenter.ma for Rabat, Salé, and Remote."""
        print("[JobHunter] Scanning MonCallCenter.ma (Rabat, Salé, Back-Office & Télétravail)...")
        sources = [
            ("https://www.moncallcenter.ma/q-offres/?Ville=Rabat", "Rabat (Maroc)"),
            ("https://www.moncallcenter.ma/q-offres/?Ville=Sal%C3%A9", "Salé (Maroc)"),
            ("https://www.moncallcenter.ma/q-offres/?Motcle=back+office", "Rabat / Remote (Maroc)"),
            ("https://www.moncallcenter.ma/q-offres/?Motcle=t%C3%A9l%C3%A9travail", "Télétravail (Maroc)")
        ]
        jobs = []
        seen_urls = set()
        for url, def_loc in sources:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')

                chunks = page_html.split('<div class="divoffres')
                for c in chunks[1:]:
                    link_m = re.search(r'href="(/offre-emploi/[^"]+)"', c)
                    title_m = re.search(r'<h2>\s*<a[^>]*>(.*?)</a>\s*</h2>', c, re.DOTALL)
                    if not (link_m and title_m):
                        continue

                    full_url = "https://www.moncallcenter.ma" + link_m.group(1)
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)

                    raw_title = title_m.group(1)
                    title = html.unescape(re.sub(r'<[^>]+>', ' ', raw_title)).strip()
                    title = re.sub(r'\s+', ' ', title)

                    slug_parts = link_m.group(1).replace('/offre-emploi/', '').split('-')
                    comp_cand = slug_parts[0].title() if slug_parts else "Centre BPO"
                    comp_m = re.search(r'<img\s+alt="([^"]+)"', c)
                    company = comp_m.group(1).strip() if (comp_m and comp_m.group(1) != "Concentrix") else comp_cand
                    if not company or company.lower() in ["offre", "recherche", "emploi"]:
                        company = "Centre BPO (Maroc)"

                    city_m = re.search(r'<b\s+style="color:#0000009e[^"]*">([^<]+)</b>', c)
                    loc = city_m.group(1).strip() if city_m else def_loc
                    if "sale" in loc.lower() or "salé" in loc.lower():
                        loc = "Salé (Maroc)"
                    elif "rabat" in loc.lower():
                        loc = "Rabat (Maroc)"
                    elif "télé" in loc.lower() or "teletravail" in loc.lower() or "remote" in loc.lower():
                        loc = "Télétravail (Maroc)"

                    if not any(target in loc.lower() for target in ["rabat", "salé", "sale", "télé", "teletravail", "remote"]):
                        if any(target in title.lower() for target in ["rabat", "salé", "sale", "télé", "teletravail", "remote"]):
                            loc = "Rabat / Télétravail (Maroc)"
                        else:
                            continue

                    job_id_num = slug_parts[-1] if slug_parts and slug_parts[-1].isdigit() else str(abs(hash(full_url)) % 1000000)
                    desc = f"Opportunité Centre d'Appels & Back-Office chez {company}. Intitulé: {title}. Localisation: {loc}. Prise en charge des dossiers clients, CRM et flux opérationnels."

                    jobs.append({
                        "id": f"mcc_{job_id_num}",
                        "source": "MonCallCenter.ma",
                        "title": title,
                        "company": company,
                        "location": loc,
                        "tags": ["Call Center", "Back-Office", loc, "CDI"],
                        "url": full_url,
                        "description": desc,
                        "posted_at": "Récent",
                        "category": "bpo"
                    })
            except Exception as e:
                print(f"[MonCallCenter] Error scanning {url}: {e}")

        print(f"[MonCallCenter] Found {len(jobs)} Call Center & Back-Office offers.")
        return jobs

    # ── 9. Rekrute BPO & Service Client ────────────────────────────────────
    def fetch_rekrute_bpo(self) -> List[Dict[str, Any]]:
        """Scrapes Back-Office & Customer Service roles from Rekrute for Rabat, Salé, and Remote."""
        print("[JobHunter] Scanning Rekrute (Back-Office & Service Client)...")
        sources = [
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=back+office+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=service+client+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=charge+de+clientele+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=centre+d+appels+rabat",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=centre+d+appels+sale",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=centre+d+appels+teletravail",
            "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=back+office+teletravail"
        ]
        found_links = {}
        for url in sources:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')
                raw_links = re.findall(r'href="(/offre-emploi-[^"]+\.html)[^"]*"', page_html)
                for link in raw_links:
                    link_clean = link.split('?')[0]
                    full_url = f"https://www.rekrute.com{link_clean}"
                    if full_url not in found_links:
                        found_links[full_url] = link_clean
            except Exception:
                pass

        jobs = []
        for full_url, link_path in list(found_links.items())[:25]:
            try:
                slug = link_path.replace('/offre-emploi-', '').replace('.html', '')
                parts = slug.split('-recrutement-')
                title_slug = parts[0].replace('-', ' ').title() if len(parts) > 0 else "Back-Office / Service Client"
                meta_slug = parts[1] if len(parts) > 1 else ""

                is_target = any(c in slug.lower() for c in ["rabat", "salé", "sale", "teletravail", "télétravail", "remote"])
                if not is_target:
                    continue

                req = urllib.request.Request(full_url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=6, context=self.ssl_ctx) as resp:
                    detail_html = resp.read().decode('utf-8', errors='ignore')

                comp_match = (
                    re.search(r'Recruteur\s*:\s*<strong>(.*?)</strong>', detail_html) or
                    re.search(r'alt="logo\s+([^"]+)"', detail_html, re.IGNORECASE) or
                    re.search(r'Entreprise\s*:\s*([A-Za-z0-9\s_-]+)', detail_html)
                )
                company = comp_match.group(1).strip() if comp_match else (meta_slug.split('-')[0].title() if meta_slug else "Centre de Contacts")

                sections = re.findall(r'<div[^>]+class="col-md-12[^"]*"[^>]*>(.*?)</div>', detail_html, re.DOTALL)
                desc_parts = []
                for s in sections:
                    clean_s = self._clean_html(s)
                    if any(k in clean_s.lower() for k in ['poste', 'profil', 'mission', 'client', 'appels', 'back office', 'service', 'relation']):
                        desc_parts.append(clean_s)

                full_desc = "\n\n".join(desc_parts)
                if not full_desc or len(full_desc) < 80:
                    full_desc = self._clean_html(detail_html)[:2000]

                location = "Rabat (Maroc)"
                lower_html = detail_html.lower()
                if "salé" in lower_html or "sale" in lower_html:
                    location = "Salé / Technopolis (Maroc)"
                elif "télétravail" in lower_html or "teletravail" in lower_html or "remote" in lower_html:
                    location = "Télétravail (Maroc)"

                match_id = re.search(r'-(\d+)\.html', link_path)
                job_id_num = match_id.group(1) if match_id else str(int(time.time()))
                jobs.append({
                    "id": f"rek_bpo_{job_id_num}",
                    "source": "Rekrute (Maroc)",
                    "title": title_slug,
                    "company": company,
                    "location": location,
                    "tags": ["Back-Office", "Service Client", location, "CDI"],
                    "url": full_url,
                    "description": full_desc,
                    "posted_at": "Récent",
                    "category": "bpo"
                })
            except Exception:
                continue

        print(f"[Rekrute BPO] Found {len(jobs)} positions.")
        return jobs

    # ── 10. Marocannonces BPO & Call Centers ──────────────────────────────
    def fetch_marocannonces_bpo(self) -> List[Dict[str, Any]]:
        """Scrapes Call Centers and Back-Office ads from Marocannonces for Rabat and Salé."""
        print("[JobHunter] Scanning Marocannonces (Centres d'appels Rabat & Salé)...")
        cities = {
            "Rabat": "https://www.marocannonces.com/maroc/offres-emploi-centres-d-appels-tele-services-rabat-b313-m7.html",
            "Salé": "https://www.marocannonces.com/maroc/offres-emploi-centres-d-appels-tele-services-sale-b313-m77.html"
        }
        jobs = []
        for city, target_url in cities.items():
            try:
                req = urllib.request.Request(target_url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=8, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')

                annonces = re.findall(r'href="([^"]*(?:maroc/)?annonce/(\d+)/([^"]+)\.html)"', page_html)
                for full_href, ann_id, slug in annonces[:15]:
                    title = slug.replace('-', ' ').title()
                    full_url = f"https://www.marocannonces.com/{full_href.lstrip('/')}" if not full_href.startswith('http') else full_href

                    if any(neg in title.lower() for neg in ["maçon", "infirmier", "plombier", "cuisinier", "chauffeur"]):
                        continue

                    jobs.append({
                        "id": f"ma_bpo_{ann_id}",
                        "source": "Marocannonces",
                        "title": title,
                        "company": "Centre d'Appels & Télé-services",
                        "location": f"{city} (Maroc)",
                        "tags": [city, "Centre d'Appels", "BPO", "Maroc"],
                        "url": full_url,
                        "description": f"Poste en Centre d'appels / Back-office basé à {city}. Référence annonce: {ann_id}.",
                        "posted_at": "Récent",
                        "category": "bpo"
                    })
            except Exception:
                pass

        print(f"[Marocannonces BPO] Found {len(jobs)} local announcements.")
        return jobs

    # ── 11. LinkedIn BPO & Customer Service ────────────────────────────────
    def fetch_linkedin_bpo(self) -> List[Dict[str, Any]]:
        """Scrapes live LinkedIn Back-Office and Customer Care positions for Rabat, Salé, and Remote Morocco."""
        print("[JobHunter] Scanning LinkedIn (Back-Office & Customer Service Rabat/Salé/Remote)...")
        queries = [
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Back+Office+OR+Service+Client&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0",
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Customer+Service+OR+Centre+d+Appels&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0",
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Back+Office+Remote&location=Morocco&start=0"
        ]
        li_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
            "Referer": "https://www.linkedin.com/jobs"
        }
        jobs = []
        seen_ids = set()
        for q_url in queries:
            try:
                req = urllib.request.Request(q_url, headers=li_headers)
                with urllib.request.urlopen(req, timeout=10, context=self.ssl_ctx) as resp:
                    page_html = resp.read().decode('utf-8', errors='ignore')

                cards = re.findall(r'<li[^>]*>(.*?)</li>', page_html, re.DOTALL)
                for c in cards:
                    link_m = re.search(r'href="([^"]+)"', c)
                    if not link_m:
                        continue
                    full_link = link_m.group(1).split('?')[0]
                    id_m = re.search(r'-(\d+)(?:$|\?)', full_link) or re.search(r'/view/(\d+)', full_link)
                    job_id = id_m.group(1) if id_m else str(abs(hash(full_link)) % 100000000)
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title_m = re.search(r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(.*?)</h3>', c, re.DOTALL)
                    company_m = re.search(r'<h4[^>]*class="[^"]*base-search-card__subtitle[^"]*"[^>]*>(.*?)</h4>', c, re.DOTALL)
                    loc_m = re.search(r'<span[^>]*class="[^"]*job-search-card__location[^"]*"[^>]*>(.*?)</span>', c, re.DOTALL)

                    title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1)).strip()) if title_m else "Back-Office / Service Client"
                    company = html.unescape(re.sub(r'<[^>]+>', '', company_m.group(1)).strip()) if company_m else "Entreprise BPO"
                    loc = html.unescape(re.sub(r'<[^>]+>', '', loc_m.group(1)).strip()) if loc_m else "Rabat (Maroc)"

                    desc = f"Poste de {title} chez {company} basé à {loc} sur LinkedIn."
                    try:
                        detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                        req_det = urllib.request.Request(detail_url, headers=li_headers)
                        with urllib.request.urlopen(req_det, timeout=6, context=self.ssl_ctx) as det_resp:
                            det_html = det_resp.read().decode('utf-8', errors='ignore')
                            dm = re.search(r'<div[^>]*class="[^"]*show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>', det_html, re.DOTALL)
                            if dm:
                                desc = self._clean_html(dm.group(1))
                    except Exception:
                        pass

                    jobs.append({
                        "id": f"li_bpo_{job_id}",
                        "source": "LinkedIn Jobs",
                        "title": title,
                        "company": company,
                        "location": loc,
                        "tags": ["LinkedIn", "Back-Office", "Customer Care", loc],
                        "url": full_link,
                        "description": desc[:2500],
                        "posted_at": "Récent",
                        "category": "bpo"
                    })
            except Exception as e:
                print(f"[LinkedIn BPO] Error: {e}")

        print(f"[LinkedIn BPO] Found {len(jobs)} positions.")
        return jobs

    # ── Relevance Filters ──────────────────────────────────────────────────
    def is_relevant_job(self, title: str, description: str, tags: List[str]) -> bool:
        """Strictly filter tech, data, software, and technical support positions."""
        lower_title = title.lower()
        lower_desc = description[:1500].lower()

        negative_title_words = [
            "infirmier", "médical", "medical", "soignant", "rh", "ressources humaines",
            "commercial", "vente", "vendeur", "comptable", "comptabilité", "paie",
            "juriste", "avocat", "magasinier", "chauffeur", "cuisinier", "eau potable",
            "btp", "génie civil", "topographe", "immobilier", "call center téléconseiller",
            "téléopérateur", "directeur général", "directeur commercial"
        ]
        if any(neg in lower_title for neg in negative_title_words):
            return False

        tech_title_keywords = [
            "developpeur", "développeur", "developer", "engineer", "ingénieur", "ingenieur",
            "data", "fullstack", "full-stack", "front", "back", "software", "logiciel",
            "python", "react", "java", "spring", "web", "support", "technicien", "analyste",
            "dba", "bi", "ai", "ia", "cloud", "devops", "reseau", "réseau", "it", "système",
            "systeme", "qa", "test", "architecte", "scrum", "informatique", "reporting"
        ]

        title_matches = any(kw in lower_title for kw in tech_title_keywords)
        if not title_matches:
            return False

        stack_keywords = [
            "python", "react", "javascript", "sql", "api", "rest", "data", "machine learning",
            "deep learning", "big data", "java", "php", "crm", "support", "incident", "sla",
            "linux", "git", "cloud", "aws", "azure", "docker", "bi", "power bi", "agile",
            "informatique", "système", "reseau"
        ]
        return any(sk in lower_desc for sk in stack_keywords)

    def is_relevant_bpo_job(self, title: str, description: str, location: str = "") -> bool:
        """Strictly filter Call Centers & Back-Office positions in Rabat, Salé, and Remote."""
        lower = (title + " " + description + " " + location).lower()

        # Location constraint: must be Rabat, Salé, Technopolis, Temara, Kénitra, or Remote
        loc_ok = any(l in lower for l in ["rabat", "salé", "sale", "technopolis", "temara", "témara", "kenitra", "kénitra", "télétravail", "teletravail", "remote", "à distance", "a distance", "en ligne"])
        if not loc_ok:
            return False

        # Positive keywords
        bpo_keywords = [
            "back office", "back-office", "call center", "centre d'appel", "centre d'appels",
            "service client", "relation client", "chargé de clientèle", "charge de clientele",
            "conseiller client", "conseiller clientèle", "téléconseiller", "teleconseiller",
            "téléopérateur", "teleoperateur", "customer care", "customer service", "support client",
            "réclamation", "bpo", "gestionnaire sinistre", "assistance technique", "helpdesk",
            "traitement de données", "saisie", "operations", "télévente", "televendeur", "fedex"
        ]
        if not any(k in lower for k in bpo_keywords):
            return False

        # Negative keywords
        negatives = ["infirmier", "médical", "magasinier", "chauffeur", "cuisinier", "btp", "génie civil", "menuisier", "plombier", "femme de ménage"]
        return not any(neg in lower for neg in negatives)

    # ── Dedicated BPO Harvester & Auto-Tailor ─────────────────────────────
    def scan_bpo(self, min_ats_score: int = 55) -> List[Dict[str, Any]]:
        """Dedicated scanner for Call Centers & Back-Office in Rabat, Salé, and Remote Morocco."""
        print("[JobHunter] Starting dedicated Call Centers & Back-Office scan (Rabat, Salé, Remote Maroc)...")
        mcc_jobs = self.fetch_moncallcenter()
        rek_jobs = self.fetch_rekrute_bpo()
        ma_jobs = self.fetch_marocannonces_bpo()
        li_jobs = self.fetch_linkedin_bpo()

        raw_jobs = mcc_jobs + rek_jobs + ma_jobs + li_jobs
        print(f"[JobHunter] Aggregated {len(raw_jobs)} BPO & Back-Office candidates.")

        existing_cache = self.load_cached_jobs()
        existing_ids = {j["id"] for j in existing_cache}

        new_hunted_jobs = []
        for job in raw_jobs:
            if job["id"] in existing_ids:
                continue

            # Pass through the Auto-Tailor Engine with support_ops track
            tailored = self.engine.tailor_application(
                job_desc=job["description"],
                target_company=job["company"],
                target_role=job["title"],
                lang_choice="auto",
                forced_track="support_ops"
            )

            is_fr = tailored["lang"] == "fr"
            recruiter_dm = (
                f"Bonjour,\n\nJe me permets de vous contacter suite à la publication de votre offre pour le poste de {job['title']} chez {job['company']}. Actuellement en poste en CDI chez Foundever à Rabat (projet FedEx) en tant que Customer Service Representative, je dispose d'une solide expérience en relation client, traitement de dossiers Back-Office, outils CRM et respect strict des SLAs. Trilingue (Français C1, Anglais C1, Arabe) et très à l'aise avec les outils informatiques, je serais ravi d'échanger avec vous !\n\nBien cordialement,\nAbderrahmane El Idrissi Slimani\n📞 +212 762 609 561"
                if is_fr else
                f"Hello,\n\nI am contacting you regarding the {job['title']} opportunity at {job['company']} in {job['location']}. Currently working as a Customer Service Representative (CDI) at Foundever Rabat on the FedEx project, I have proven experience in customer care, back-office resolution workflows, CRM ticketing, and strict SLA compliance. Trilingual (English C1, French C1, Native Arabic) and computer-proficient, I would welcome the chance to connect!\n\nBest regards,\nAbderrahmane El Idrissi Slimani\n📞 +212 762 609 561"
            )

            job_entry = {
                "id": job["id"],
                "source": job["source"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "tags": job["tags"][:6],
                "url": job["url"],
                "description": job["description"][:1600] + "...",
                "ats_score": max(72, tailored["ats_score"]),
                "track": "support_ops",
                "category": "bpo",
                "lang": tailored["lang"],
                "matched_skills": tailored["matched_skills"],
                "missing_skills": tailored["missing_skills"],
                "html_resume": tailored["html_resume"],
                "markdown_resume": tailored["markdown_resume"],
                "cover_letter": tailored["cover_letter"],
                "recruiter_dm": recruiter_dm,
                "created_at": time.strftime("%Y-%m-%d %H:%M")
            }

            clean_comp = re.sub(r'[^a-zA-Z0-9_-]', '_', job["company"])[:20]
            job_dir = os.path.join(self.output_base_dir, f"{job['id']}_{clean_comp}")
            os.makedirs(job_dir, exist_ok=True)

            html_p = os.path.join(job_dir, "CV_1Page.html")
            pdf_p = os.path.join(job_dir, "CV_1Page.pdf")
            with open(html_p, "w", encoding="utf-8") as f:
                f.write(tailored["html_resume"])
            with open(os.path.join(job_dir, "CV_1Page.md"), "w", encoding="utf-8") as f:
                f.write(tailored["markdown_resume"])
            with open(os.path.join(job_dir, "Cover_Letter.txt"), "w", encoding="utf-8") as f:
                f.write(tailored["cover_letter"])
            with open(os.path.join(job_dir, "Recruiter_DM.txt"), "w", encoding="utf-8") as f:
                f.write(recruiter_dm)

            new_hunted_jobs.append(job_entry)

        all_jobs = new_hunted_jobs + existing_cache
        all_jobs.sort(key=lambda x: (
            1 if x.get("category") == "bpo" else 0,
            1 if any(c in x.get("location", "").lower() for c in ["rabat", "salé", "sale", "télé", "remote"]) else 0,
            x.get("ats_score", 0)
        ), reverse=True)

        self.save_cached_jobs(all_jobs)
        print(f"[JobHunter] Dedicated BPO Scan complete! Total tailored roles: {len(all_jobs)} ({len(new_hunted_jobs)} new).")
        return all_jobs

    # ── Master Scan across Platforms ──────────────────────────────────────
    def scan_and_tailor(self, min_ats_score: int = 65, region: str = "morocco", mode: str = "all") -> List[Dict[str, Any]]:
        """Scans platforms, tailors each application, saves local kits, and updates cache.
        Supports mode='all', mode='tech', or mode='bpo'."""
        if mode == "bpo":
            return self.scan_bpo(min_ats_score=min_ats_score)

        print(f"[JobHunter] Starting multi-platform scan (Mode: {mode})...")

        # 1. Fetch from platforms
        rekrute_jobs = self.fetch_rekrute_morocco()
        ma_jobs = self.fetch_marocannonces()
        ep_jobs = self.fetch_emploi_public()
        alw_jobs = self.fetch_alwadifa()
        li_jobs = self.fetch_linkedin_morocco()
        rem_jobs = self.fetch_remotive_jobs()
        wwr_jobs = self.fetch_weworkremotely()

        for j in (rekrute_jobs + ma_jobs + ep_jobs + alw_jobs + li_jobs + rem_jobs + wwr_jobs):
            j["category"] = "tech"

        bpo_jobs = []
        if mode == "all":
            bpo_jobs = self.fetch_moncallcenter() + self.fetch_rekrute_bpo() + self.fetch_marocannonces_bpo() + self.fetch_linkedin_bpo()

        raw_jobs = rekrute_jobs + ma_jobs + ep_jobs + alw_jobs + li_jobs + rem_jobs + wwr_jobs + bpo_jobs
        print(f"[JobHunter] Aggregated {len(raw_jobs)} total candidates across recruitment platforms.")

        existing_cache = self.load_cached_jobs()
        processed_ids = {j["id"] for j in existing_cache}

        new_hunted_jobs = []

        for job in raw_jobs:
            if job["id"] in processed_ids:
                continue

            # Pass through the Auto-Tailor Engine
            tailored = self.engine.tailor_application(
                job_desc=job["description"],
                target_company=job["company"],
                target_role=job["title"],
                lang_choice="auto"
            )

            is_bpo = job.get("category") == "bpo" or tailored["track"] == "support_ops"
            if is_bpo:
                tailored["track"] = "support_ops"
                job["category"] = "bpo"
            else:
                job["category"] = "tech"

            is_fr = tailored["lang"] == "fr"
            if is_bpo:
                recruiter_dm = (
                    f"Bonjour,\n\nJe me permets de vous contacter suite à la publication de votre offre pour le poste de {job['title']} chez {job['company']}. Actuellement en poste en CDI chez Foundever à Rabat (projet FedEx) en tant que Customer Service Representative, je dispose d'une solide expérience en relation client, traitement de dossiers Back-Office, outils CRM et respect strict des SLAs. Trilingue (Français C1, Anglais C1, Arabe) et très à l'aise avec les outils informatiques, je serais ravi d'échanger avec vous !\n\nBien cordialement,\nAbderrahmane El Idrissi Slimani\n📞 +212 762 609 561"
                    if is_fr else
                    f"Hello,\n\nI am contacting you regarding the {job['title']} opportunity at {job['company']} in {job['location']}. Currently working as a Customer Service Representative (CDI) at Foundever Rabat on the FedEx project, I have proven experience in customer care, back-office resolution workflows, CRM ticketing, and strict SLA compliance. Trilingual (English C1, French C1, Native Arabic) and computer-proficient, I would welcome the chance to connect!\n\nBest regards,\nAbderrahmane El Idrissi Slimani\n📞 +212 762 609 561"
                )
            else:
                recruiter_dm = (
                    f"Bonjour,\n\nJe me permets de vous contacter suite à la publication de votre offre pour le poste de {job['title']} chez {job['company']}. Basé à Rabat et diplômé en Big Data (ENSA Kénitra) ainsi qu'en développement Full-Stack, mon profil allie expertise technique (React, Python, Deep Learning) et rigueur opérationnelle. Je serais ravi d'échanger avec vous sur vos besoins !\n\nBien cordialement,\nAbderrahmane El Idrissi Slimani\n📞 +212 762 609 561"
                    if is_fr else
                    f"Hi,\n\nI noticed the {job['title']} opportunity at {job['company']} in {job['location']}. Based in Rabat and holding a degree in Big Data (ENSA Kénitra) with solid hands-on experience across Full-Stack engineering and AI, I would welcome the chance to briefly discuss how my background aligns with your team's goals.\n\nBest regards,\nAbderrahmane El Idrissi Slimani\n📞 +212 762 609 561"
                )

            job_entry = {
                "id": job["id"],
                "source": job["source"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "tags": job["tags"][:6],
                "url": job["url"],
                "description": job["description"][:1600] + "...",
                "ats_score": max(70, tailored["ats_score"]) if is_bpo else tailored["ats_score"],
                "track": tailored["track"],
                "category": job["category"],
                "lang": tailored["lang"],
                "matched_skills": tailored["matched_skills"],
                "missing_skills": tailored["missing_skills"],
                "html_resume": tailored["html_resume"],
                "markdown_resume": tailored["markdown_resume"],
                "cover_letter": tailored["cover_letter"],
                "recruiter_dm": recruiter_dm,
                "created_at": time.strftime("%Y-%m-%d %H:%M")
            }

            # Save application package to disk if ATS score meets threshold
            if job_entry["ats_score"] >= min_ats_score:
                clean_comp = re.sub(r'[^a-zA-Z0-9_-]', '_', job["company"])[:20]
                job_dir = os.path.join(self.output_base_dir, f"{job['id']}_{clean_comp}")
                os.makedirs(job_dir, exist_ok=True)

                html_path = os.path.join(job_dir, "CV_1Page.html")
                pdf_path = os.path.join(job_dir, "CV_1Page.pdf")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(tailored["html_resume"])
                with open(os.path.join(job_dir, "CV_1Page.md"), "w", encoding="utf-8") as f:
                    f.write(tailored["markdown_resume"])
                with open(os.path.join(job_dir, "Cover_Letter.txt"), "w", encoding="utf-8") as f:
                    f.write(tailored["cover_letter"])
                with open(os.path.join(job_dir, "Recruiter_DM.txt"), "w", encoding="utf-8") as f:
                    f.write(recruiter_dm)

            new_hunted_jobs.append(job_entry)

        # Merge with cache, prioritizing Morocco (Rabat/Salé/Kénitra) first, then high ATS score
        all_jobs = new_hunted_jobs + existing_cache
        all_jobs.sort(key=lambda x: (
            1 if any(c in x.get("location", "").lower() for c in ["rabat", "kénitra", "kenitra", "salé", "sale", "télé", "remote", "maroc"]) else 0,
            x.get("ats_score", 0)
        ), reverse=True)

        self.save_cached_jobs(all_jobs)
        print(f"[JobHunter] Multi-Platform Scan complete! Total tailored jobs in library: {len(all_jobs)}.")
        return all_jobs

    def load_cached_jobs(self) -> List[Dict[str, Any]]:
        tmp_cache = os.path.join("/tmp", "hunted_jobs.json")
        target = tmp_cache if os.path.exists(tmp_cache) else self.jobs_cache_file
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_cached_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        try:
            with open(self.jobs_cache_file, "w", encoding="utf-8") as f:
                json.dump(jobs[:150], f, ensure_ascii=False, indent=2)
        except OSError:
            tmp_cache = os.path.join("/tmp", "hunted_jobs.json")
            try:
                with open(tmp_cache, "w", encoding="utf-8") as f:
                    json.dump(jobs[:150], f, ensure_ascii=False, indent=2)
            except Exception:
                pass
