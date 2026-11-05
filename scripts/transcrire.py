# Transcription française avec le minutage de chaque mot (faster-whisper, gratuit, hors ligne).
# usage : python transcrire.py audio.wav mots.json [modele] ["noms propres : Marie, Cutora, HyperFrames"]
#   modele : small (défaut, bon compromis), base (plus rapide), medium (plus précis, 1,5 Go à télécharger).
# Préparer l'audio : ffmpeg -i video.mp4 -vn -ac 1 -ar 16000 audio.wav
import sys, json
from faster_whisper import WhisperModel

audio, out = sys.argv[1], sys.argv[2]
model = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "small", device="cpu", compute_type="int8")
prompt = sys.argv[4] if len(sys.argv) > 4 else None  # aide à bien écrire les noms propres
segs, info = model.transcribe(audio, language="fr", word_timestamps=True, beam_size=5, initial_prompt=prompt,
                              condition_on_previous_text=False)
words = []
for s in segs:
    print(f"[{s.start:6.2f} - {s.end:6.2f}] {s.text}")
    for w in s.words:
        words.append({"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)})
json.dump(words, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(words), "mots ->", out)
