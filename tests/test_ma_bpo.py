import urllib.request, ssl, re, html

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9"
}

urls = [
    ("https://www.marocannonces.com/maroc/offres-emploi-centres-d-appels-tele-services-rabat-b313-m7.html", "Rabat"),
    ("https://www.marocannonces.com/maroc/offres-emploi-centres-d-appels-tele-services-sale-b313-m77.html", "Salé")
]

for url, loc in urls:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
    
    annonces = re.findall(r'href="([^"]*(?:maroc/)?annonce/(\d+)/([^"]+)\.html)"', content)
    print(f"[{loc}] Found {len(annonces)} announcements")
    for full_href, ann_id, slug in annonces[:5]:
        title = slug.replace('-', ' ').title()
        print(f"  - {title} (ID: {ann_id})")
