import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-rabat-b309-m7.html'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=8) as resp:
    page_html = resp.read().decode('utf-8', errors='ignore')

# Print snippet containing 10375542
idx = page_html.find('10375542')
if idx != -1:
    print("Found! Snippet:")
    print(page_html[idx-100:idx+200])
else:
    print("Not found")
