import urllib.request
import ssl
import re
import html

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def test_harvest():
    mcc_jobs = []
    urls = [
        ("https://www.moncallcenter.ma/q-offres/?Ville=Rabat", "Rabat"),
        ("https://www.moncallcenter.ma/q-offres/?Ville=Sal%C3%A9", "Salé"),
        ("https://www.moncallcenter.ma/q-offres/?Motcle=back+office", "Morocco"),
        ("https://www.moncallcenter.ma/q-offres/?Motcle=t%C3%A9l%C3%A9travail", "Télétravail / Remote")
    ]
    for url, def_loc in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
            
            chunks = content.split('<div class="divoffres')
            found_this_url = 0
            for c in chunks[1:]:
                link_m = re.search(r'href="(/offre-emploi/[^"]+)"', c)
                title_m = re.search(r'<h2>\s*<a[^>]*>(.*?)</a>\s*</h2>', c, re.DOTALL)
                comp_m = re.search(r'<img\s+alt="([^"]+)"', c)
                if link_m and title_m:
                    link = "https://www.moncallcenter.ma" + link_m.group(1)
                    title = html.unescape(re.sub(r'<[^>]+>', ' ', title_m.group(1))).strip()
                    comp = comp_m.group(1).strip() if comp_m else "Centre d'Appels"
                    # Try to extract city from badge
                    city_m = re.search(r'<b\s+style="color:#0000009e[^"]*">([^<]+)</b>', c)
                    loc = city_m.group(1).strip() if city_m else def_loc
                    mcc_jobs.append({
                        "title": title,
                        "company": comp,
                        "location": loc,
                        "url": link
                    })
                    found_this_url += 1
            print(f"[MonCallCenter] {url} -> {found_this_url} jobs")
        except Exception as e:
            print(f"[MonCallCenter] Error on {url}: {e}")

    print(f"Total MCC Jobs: {len(mcc_jobs)}")
    for j in mcc_jobs[:10]:
        print(" ", j['company'], "|", j['title'], "|", j['location'])

test_harvest()
