import urllib.request, ssl, re, html

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8"
}

sources = [
    "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=back+office+rabat",
    "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=service+client+rabat",
    "https://www.rekrute.com/offres-emploi-maroc.html?s=3&p=1&o=1&keyword=centre+d+appels+teletravail"
]

for url in sources:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        page_html = resp.read().decode('utf-8', errors='ignore')
    
    links = re.findall(r'href="(/offre-emploi-[^"]+\.html)[^"]*"', page_html)
    kw = url.split('keyword=')[1]
    print(f"Rekrute [{kw}]: {len(set(links))} job links found")
    for l in list(set(links))[:4]:
        title = l.replace('/offre-emploi-', '').replace('.html', '').split('-recrutement-')[0].replace('-', ' ').title()
        print(f"  -> {title}")
