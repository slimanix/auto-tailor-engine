import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8"
}

sources = {
    "moncallcenter_search": "https://www.moncallcenter.ma/offres-emploi.html?keyword=back+office",
    "moncallcenter_rabat": "https://www.moncallcenter.ma/offres-emploi-rabat.html",
    "rekrute_backoffice": "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=back+office+rabat",
    "rekrute_callcenter_remote": "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=centre+d+appels+teletravail",
    "marocannonces_callcenter_rabat": "https://www.marocannonces.com/maroc/offres-emploi-centres-d-appels-tele-services-rabat-b313-m7.html",
    "marocannonces_callcenter_sale": "https://www.marocannonces.com/maroc/offres-emploi-centres-d-appels-tele-services-sale-b313-m77.html",
    "linkedin_backoffice_rabat": "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Back+Office+OR+Service+Client&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0"
}

for name, url in sources.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            print(f"[{name}] HTTP {resp.status} - Length: {len(body)}")
            # Sample matches
            if "linkedin" in name:
                cards = re.findall(r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(.*?)</h3>', body)
                print(f"  -> LinkedIn titles: {[c.strip() for c in cards[:3]]}")
            elif "rekrute" in name:
                links = re.findall(r'href="(/offre-emploi-[^"]+\.html)"', body)
                print(f"  -> Rekrute job links found: {len(links)}")
            elif "marocannonces" in name:
                ann = re.findall(r'href="([^"]*annonce/\d+/[^"]+\.html)"', body)
                print(f"  -> Marocannonces ads found: {len(ann)}")
            elif "moncallcenter" in name:
                m_links = re.findall(r'href="(/offre-emploi-[^"]+\.html)"', body)
                if not m_links:
                    m_links = re.findall(r'href="(/emploi-[^"]+\.html)"', body)
                print(f"  -> Moncallcenter links found: {len(m_links)}")
    except Exception as e:
        print(f"[{name}] Error: {e}")
