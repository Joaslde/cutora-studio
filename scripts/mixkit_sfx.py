# Liste les sons Mixkit d'une catégorie : python mixkit_audio.py sfx|music cat1 cat2 ...
import sys, re, html, urllib.request
kind = sys.argv[1]
base = "free-sound-effects" if kind == "sfx" else "free-stock-music/tag"
for tag in sys.argv[2:]:
    try:
        req = urllib.request.Request(f"https://mixkit.co/{base}/{tag}/", headers={"User-Agent": "Mozilla/5.0"})
        p = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"## {tag}: {e}"); continue
    urls = list(dict.fromkeys(re.findall(r'https://assets\.mixkit\.co/[^"\']+\.mp3', p)))
    titles = [html.unescape(t.strip()) for t in re.findall(r'item-grid-card__title[^>]*>\s*([^<]+)', p)]
    print(f"## {tag} ({len(urls)})")
    for u, t in zip(urls, titles):
        sid = re.search(r"/(\d+)/", u).group(1)
        print(f"  {sid:>5} {t[:52]}")
