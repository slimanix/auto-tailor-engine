import urllib.request
import re
import html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-rabat-b309-m7.html'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=8) as resp:
    page_html = resp.read().decode('utf-8', errors='ignore')

# Match annonces: categorie/309/Offres-emploi/annonce/...
matches = re.findall(r'<a[^>]+href="([^"]*annonce/(\d+)/([^"]+)\.html)"[^>]*>(.*?)</a>', page_html)
print(f"Total matching announcements: {len(matches)}")
for link, ann_id, slug, inner_text in matches[:8]:
    clean_title = slug.replace('-', ' ').title()
    print(f" - ID: {ann_id} | Title: {clean_title} | URL: https://www.marocannonces.com/{link.lstrip('/')}")
