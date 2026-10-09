import urllib.request
import re

urls = [
    'https://www.rekrute.com/offres-emploi-metiers-de-l-it.html',
    'https://www.rekrute.com/offres-emploi-rabat.html'
]

for url in urls:
    print(f"\n=== FETCHING: {url} ===")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')

    # Job links
    job_links = re.findall(r'<a[^>]+href="(/offre-emploi-[^"]+\.html)[^"]*"[^>]*>(.*?)</a>', content, re.DOTALL)
    print(f"Found {len(job_links)} job links")
    for link, title_html in job_links[:10]:
        clean_title = re.sub(r'<[^>]+>', '', title_html).strip()
        if clean_title and len(clean_title) > 3:
            print(f" - Title: {clean_title}")
            print(f"   URL: https://www.rekrute.com{link}")
