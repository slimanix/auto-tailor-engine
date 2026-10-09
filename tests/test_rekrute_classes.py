import urllib.request
import re

url = 'https://www.rekrute.com/offre-emploi-reporting-programmer-clinical-data-recrutement-alten-maroc-rabat-187316.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Print classes in the HTML
classes = set(re.findall(r'class="([^"]+)"', content))
print("Classes matching 'job' or 'content' or 'desc' or 'detail':")
for c in classes:
    if any(k in c.lower() for k in ['job', 'content', 'desc', 'detail', 'info', 'text', 'box', 'post']):
        print(" -", c)
