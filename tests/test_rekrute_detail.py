import urllib.request
import re
import html

url = 'https://www.rekrute.com/offre-emploi-reporting-programmer-clinical-data-recrutement-alten-maroc-rabat-187316.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Company logo or name
comp_match = re.search(r'alt="logo\s+([^"]+)"', content, re.IGNORECASE) or re.search(r'Recruteur\s*:\s*<strong>(.*?)</strong>', content)
company = comp_match.group(1).strip() if comp_match else "Alten Maroc"

# Details blocks
blcs = re.findall(r'<div[^>]+class="blc"[^>]*>(.*?)</div>', content, re.DOTALL)
full_desc = " ".join([re.sub(r'<[^>]+>', ' ', b) for b in blcs])
clean_desc = html.unescape(re.sub(r'\s+', ' ', full_desc)).strip()

print(f"Company: {company}")
print(f"Description length: {len(clean_desc)}")
print(f"Sample: {clean_desc[:400]}")
