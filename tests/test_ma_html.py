import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-rabat-b309-m7.html'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print("Marocannonces status:", resp.status, "Length:", len(html))
        # Find any links
        links = re.findall(r'href="([^"]+)"', html)
        job_links = [l for l in links if 'emploi' in l or 'marocannonces' in l or '.html' in l]
        print(f"Total matching links: {len(job_links)}")
        for l in job_links[:10]:
            print(" -", l)
except Exception as e:
    print("Error:", e)
