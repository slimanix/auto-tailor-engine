import urllib.request, ssl, re, html

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = 'https://www.moncallcenter.ma/offre-emploi/concentrix-conseiller-clientele-gestion-sinistre-habitation-rabat-sale-teletravail-possible-165628'
req = urllib.request.Request(url, headers=headers)
html_doc = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')

# Check company, ville, description
print("Length:", len(html_doc))
company = re.search(r'class="[^"]*company[^"]*"[^>]*>(.*?)<', html_doc, re.I)
print("Company:", company.groups() if company else "Not found")

meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html_doc, re.I)
print("Meta desc:", meta_desc.group(1) if meta_desc else "Not found")

# Find main content div
content_match = re.search(r'<(div|section)[^>]+class=["\'][^"\']*(?:offre-content|description|detail)[^"\']*["\'][^>]*>(.*?)</\1>', html_doc, re.DOTALL | re.I)
if content_match:
    print("Content match length:", len(content_match.group(2)))
else:
    print("Content match not found, looking for generic text...")
