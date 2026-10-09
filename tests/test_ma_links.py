import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-rabat-b309-m7.html'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=8) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Find job cards: Usually <div class="holder"> or <li ...>
links = re.findall(r'href="([^"]*emploi-maroc/[^"]*)"', html)
if not links:
    # Try finding any href with id or title
    links = [l for l in re.findall(r'href="([^"]+)"', html) if 'offre' in l or 'annonce' in l or 'informatique' in l]

print(f"Candidate job links on Marocannonces: {len(links)}")
for l in list(set(links))[:10]:
    print(" -", l)
