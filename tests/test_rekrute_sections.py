import urllib.request
import re
import html

url = 'https://www.rekrute.com/offre-emploi-reporting-programmer-clinical-data-recrutement-alten-maroc-rabat-187316.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Search for headings like "Poste :", "Profil recherché :", "Missions :"
sections = re.findall(r'<div[^>]+class="col-md-12[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL)
for s in sections:
    text = re.sub(r'<[^>]+>', ' ', s)
    text = html.unescape(re.sub(r'\s+', ' ', text)).strip()
    if any(k in text.lower() for k in ['poste', 'profil', 'mission', 'compétence', 'responsabilité', 'alten', 'projet']):
        print("--- Section Found ---")
        print(text[:400])
