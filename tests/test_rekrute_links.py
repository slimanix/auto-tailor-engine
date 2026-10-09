import urllib.request
import re

url = 'https://www.rekrute.com/offres-emploi-rabat.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Search for hrefs with "emploi" or "offre" or "recrutement"
links = re.findall(r'href="([^"]*(?:offre|emploi|job)[^"]*)"', content, re.IGNORECASE)
unique_links = list(set(links))[:20]
for l in unique_links:
    print(l)
