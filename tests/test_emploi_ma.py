import urllib.request

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

url = 'https://www.emploi.ma/recherche-jobs-maroc?f%5B0%5D=im_field_offre_metiers%3A31&f%5B1%5D=im_field_offre_region%3A74'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        print("Emploi.ma success! Status:", resp.status)
        content = resp.read().decode('utf-8', errors='ignore')
        print("Length:", len(content))
except Exception as e:
    print("Emploi.ma error:", e)
