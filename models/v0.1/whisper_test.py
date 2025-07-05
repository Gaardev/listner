from datetime import date
import os
import whisper
import json

today = date.today()
print(today)

os.makedirs(f"mp3/{today}", exist_ok=True)

if not os.path.exists(r"C:\Users\edu8136622\OneDrive\discord-bot\models\v0.1\rec.mp3"):
    raise FileNotFoundError("rec.mp3 not found!")

model=whisper.load_model("small") # tiny, base, small, medium, large
result = model.transcribe(r"C:\Users\edu8136622\OneDrive\discord-bot\models\v0.1\rec.mp3", language="no", fp16=False)

with open(f"mp3/{today}/transcribed.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

with open(f"mp3/{today}/transcribed.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])