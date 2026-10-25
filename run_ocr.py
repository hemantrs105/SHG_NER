#!/usr/bin/env python3
"""Offline OCR leg: transcribe each page photo with a local vision model via Ollama.

The output is the realistic input the name resolver would get on a laptop with no
internet. Compare it with text/clean/, which is a careful reading checked by a person.

Usage: python run_ocr.py [ollama-model] [page-stem ...]
"""
import base64, json, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen3-vl:8b"
OUT = ROOT / "text" / ("ocr_" + MODEL.split(":")[0].replace("-", ""))
OUT.mkdir(parents=True, exist_ok=True)
stems = sys.argv[2:] or sorted(p.stem for p in (ROOT / "pages").glob("*.jpg"))

PROMPT = ("Transcribe all handwritten text on this page exactly as written, line by line, "
          "top to bottom. Keep Devanagari as Devanagari and English as English. For tables, "
          "write one row per line with cells separated by ' | '. Do not translate, summarise "
          "or correct spellings. Write [?] for an illegible word.")

log = open(OUT / "_run.log", "a", encoding="utf-8")
for stem in stems:
    dest = OUT / f"{stem}.txt"
    if dest.exists() and dest.stat().st_size > 0:
        print(f"skip {stem} (done)", flush=True)
        continue
    img = base64.b64encode((ROOT / "pages" / f"{stem}.jpg").read_bytes()).decode()
    # The Ollama qwen3-vl:8b tag is the *thinking* variant: it ignores think=false and
    # reasons before answering. Give it room to finish thinking, then keep only the
    # answer. With a small budget it returned an empty transcript.
    # num_ctx: the default 4096 cannot hold a ~1900-token page image plus output.
    payload = {"model": MODEL, "stream": False,
               "messages": [{"role": "user", "content": PROMPT, "images": [img]}],
               "options": {"temperature": 0, "num_predict": 10000, "num_ctx": 16384}}
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=3600) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        msg = f"{stem}: HTTP {e.code} {e.read()[:300]!r}"
        print(msg, flush=True); log.write(msg + "\n"); log.flush()
        continue
    txt = d["message"].get("content", "")
    secs = time.time() - t0
    dest.write_text(txt, encoding="utf-8")
    msg = (f"{stem}: {secs:.0f}s, answer {len(txt)} chars, thinking "
           f"{len(d['message'].get('thinking') or '')} chars, tokens out {d.get('eval_count')}")
    print(msg, flush=True); log.write(msg + "\n"); log.flush()
