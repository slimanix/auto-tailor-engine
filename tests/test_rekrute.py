import urllib.request
import re
import html

url = 'https://www.rekrute.com/offres-emploi-rabat.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Find job post blocks
# Rekrute jobs usually look like: <li class="post-id-... or <div class="section">
items = re.findall(r'<a[^>]+href="(/offre-recrutement-[^"]+)"[^>]*>(.*?)</a>', content)
print(f"Total matching links found: {len(items)}")
for link, text in items[:10]:
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if clean_text:
        print(f"Link: https://www.rekrute.com{link} | Title: {clean_text}")
