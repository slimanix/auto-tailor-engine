import urllib.request, ssl, re, html

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
li_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
    "Referer": "https://www.linkedin.com/jobs"
}

urls = [
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Back+Office+OR+Service+Client&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0",
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Customer+Service+OR+Centre+d+Appels&location=Rabat-Sal%C3%A9-K%C3%A9nitra%2C+Morocco&start=0",
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Back+Office+Remote&location=Morocco&start=0"
]

for url in urls:
    req = urllib.request.Request(url, headers=li_headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
    
    cards = re.findall(r'<li[^>]*>(.*?)</li>', content, re.DOTALL)
    print(f"URL: {url.split('keywords=')[1][:30]} -> {len(cards)} raw cards")
    for c in cards[:4]:
        title_m = re.search(r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(.*?)</h3>', c, re.DOTALL)
        company_m = re.search(r'<h4[^>]*class="[^"]*base-search-card__subtitle[^"]*"[^>]*>(.*?)</h4>', c, re.DOTALL)
        loc_m = re.search(r'<span[^>]*class="[^"]*job-search-card__location[^"]*"[^>]*>(.*?)</span>', c, re.DOTALL)
        if title_m:
            t = title_m.group(1).strip()
            cp = company_m.group(1).strip() if company_m else "N/A"
            l = loc_m.group(1).strip() if loc_m else "N/A"
            print(f"   -> {t} | {cp} | {l}")
