import urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request("https://www.moncallcenter.ma/q-offres/?Ville=Rabat", headers=headers)
html_doc = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8', errors='ignore')
chunks = html_doc.split('<div class="divoffres')
for i in [1, 2, 3]:
    if i < len(chunks):
        print(f"=== CHUNK {i} ===")
        print(chunks[i][:400])
