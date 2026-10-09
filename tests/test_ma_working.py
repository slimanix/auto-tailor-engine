import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-rabat-b309-m7.html'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=8) as resp:
    page_html = resp.read().decode('utf-8', errors='ignore')

matches = re.findall(r'href="((?:https://www\.marocannonces\.com/)?(?:categorie/\d+/Offres-emploi/)?annonce/(\d+)/([^"]+)\.html)"', page_html)
print(f"Total annonces found: {len(matches)}")
seen = set()
for full_href, ann_id, slug in matches:
    if ann_id not in seen:
        seen.add(ann_id)
        title = slug.replace('-', ' ').title()
        full_url = f"https://www.marocannonces.com/{full_href.lstrip('/')}" if not full_href.startswith('http') else full_href
        print(f" - [{ann_id}] {title[:50]} -> {full_url}")
