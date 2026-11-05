# Sert la page de découverte du style (choix/index.html) et enregistre les choix dans le profil.
# Usage : python choix_serveur.py --profil "<atelier>/profils/<nom>" [--style <nom-du-style>] [--port 8765] [--sans-navigateur]
#   --style : rouvre la page préremplie avec ce style existant, pour le modifier (l'ancien choix.json est gardé à côté).
# À lancer en arrière-plan : le script s'arrête tout seul quand la personne clique « Enregistrer mon style »,
# et affiche alors le chemin du fichier écrit puis son contenu (Claude le lit dans la sortie de la commande).
# Écrit : <profil>/styles/<nom-du-style>/choix.json
import argparse, json, re, sys, threading, unicodedata, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent / "choix"

ap = argparse.ArgumentParser()
ap.add_argument("--profil", required=True)
ap.add_argument("--style", default="")
ap.add_argument("--port", type=int, default=8765)
ap.add_argument("--sans-navigateur", action="store_true")
args = ap.parse_args()
PROFIL = Path(args.profil)
PROFIL.mkdir(parents=True, exist_ok=True)


def slug(t):
    t = unicodedata.normalize("NFKD", t or "mon-style").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "mon-style"


class Page(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ICI), **k)

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.split("?")[0] == "/etat.json":
            f = PROFIL / "styles" / slug(args.style) / "choix.json" if args.style else None
            if f and f.exists():
                corps = f.read_bytes()
                self.send_response(200); self.send_header("content-type", "application/json"); self.end_headers()
                self.wfile.write(corps)
            else:
                self.send_error(404)
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/enregistrer":
            self.send_error(404); return
        data = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))).decode("utf-8"))
        dossier = PROFIL / "styles" / slug(data.get("nom_style"))
        dossier.mkdir(parents=True, exist_ok=True)
        f = dossier / "choix.json"
        if f.exists():  # jamais écraser un choix précédent : on garde l'ancien à côté
            f.rename(dossier / f"choix-{data.get('date', 'ancien')}-{len(list(dossier.glob('choix-*.json')))}.json")
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.send_response(200); self.send_header("content-type", "application/json"); self.end_headers()
        self.wfile.write(b'{"ok": true}')
        print("CHOIX ENREGISTRES :", f, flush=True)
        print(json.dumps({k: v for k, v in data.items() if k != "parcours"}, ensure_ascii=False, indent=2), flush=True)
        threading.Thread(target=serveur.shutdown, daemon=True).start()


port = args.port
for essai in range(10):
    try:
        serveur = ThreadingHTTPServer(("127.0.0.1", port), Page)
        break
    except OSError:
        port += 1
else:
    sys.exit("Aucun port libre entre %d et %d" % (args.port, port))

url = f"http://localhost:{port}/"
print("Page de choix ouverte :", url, flush=True)
if not args.sans_navigateur:
    webbrowser.open(url)
serveur.serve_forever()
