import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.optioncarriere.ma/emploi-rabat.html?s=informatique'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=8) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Print hrefs
hrefs = set(re.findall(r'href="([^"]+)"', html))
for h in hrefs:
    if 'job' in h or 'emploi' in h or 'offre' in h:
        print(h)
