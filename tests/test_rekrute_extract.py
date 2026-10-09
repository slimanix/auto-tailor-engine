import urllib.request
import re
import html

url = 'https://www.rekrute.com/offre-emploi-reporting-programmer-clinical-data-recrutement-alten-maroc-rabat-187316.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Match contentbloc
blocs = re.findall(r'<div[^>]+class="[^"]*contentbloc[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL)
print(f"Found {len(blocs)} contentblocs")
for i, b in enumerate(blocs):
    clean = re.sub(r'<[^>]+>', ' ', b)
    clean = html.unescape(re.sub(r'\s+', ' ', clean)).strip()
    print(f"\n--- Bloc {i+1} ---")
    print(clean[:300])
