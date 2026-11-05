# Recherche de bruitages CC0 sur Openverse (gratuit, sans clé) avec relances.
# usage : python openverse.py "requête" [max_duree_ms] [n]
import sys, json, time, urllib.request, urllib.parse

q = sys.argv[1]
maxd = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
url = "https://api.openverse.org/v1/audio/?" + urllib.parse.urlencode({"q": q, "license": "cc0", "page_size": 40})
data = None
for essai in range(4):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cutora-video)"})
        data = json.load(urllib.request.urlopen(req, timeout=45))
        break
    except Exception as e:
        time.sleep(4 + 4 * essai)
if data is None:
    print(f"## {q}: Openverse ne répond pas"); sys.exit(0)
print(f"## {q} ({data.get('result_count')} résultats)")
k = 0
for r in data.get("results", []):
    d = r.get("duration") or 0
    if not d or d > maxd:
        continue
    print(f"  {r['id'][:8]} {d/1000:5.2f}s | {r['title'][:50]} | {r.get('url')}")
    k += 1
    if k >= n:
        break
