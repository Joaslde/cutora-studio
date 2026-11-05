# Voix off française gratuite (edge-tts), une piste par scène, avec le minutage de chaque mot.
# usage : python voix.py script.txt dossier_sortie [voix] [vitesse]
#   script.txt : un paragraphe par scène, séparés par une ligne vide.
#   voix par défaut : fr-FR-RemyMultilingualNeural (homme). Femme : fr-FR-VivienneMultilingualNeural.
#   vitesse : "+0%", "+8%", "-5%"...
# Sortie : s1.mp3, s1.words.json, s2.mp3... puis fusionner en UNE piste avant le montage.
import asyncio, json, sys, os
import edge_tts

script, outdir = sys.argv[1], sys.argv[2]
VOICE = sys.argv[3] if len(sys.argv) > 3 else "fr-FR-RemyMultilingualNeural"
RATE = sys.argv[4] if len(sys.argv) > 4 else "+0%"
paras = [p.strip() for p in open(script, encoding="utf-8").read().split("\n\n") if p.strip()]
os.makedirs(outdir, exist_ok=True)

async def one(key, text):
    com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    words = []
    with open(f"{outdir}/{key}.mp3", "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": round(s, 3), "end": round(s + chunk["duration"] / 1e7, 3)})
    with open(f"{outdir}/{key}.words.json", "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)
    print(key, "ok", len(words), "mots")

async def main():
    for i, t in enumerate(paras, 1):
        await one(f"s{i}", t)

asyncio.run(main())
