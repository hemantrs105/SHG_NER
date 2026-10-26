#!/usr/bin/env python3
"""Experiments to raise BODHAN IndicOCR accuracy on the register pages, one change at a time.

Run with the OCR venv:
    ~/claude_demo/.venv-indicocr/bin/python ocr_lab.py <variant> [--split dev|test|all]
then score:
    /usr/bin/python3 -I eval_ocr.py ocr/lab_<variant> lab_<variant>

Every variant reads the same upright photos (pages_ocr/) on the Mac GPU in float32, through one read
cache (ocr/lab_cache.json): a crop two variants share is read once, and read identically. The layout is
detected once per page and kept (ocr/layout/), so a variant differs from its base only in what it names.

Variants (base + one change):
    plain              BODHAN's own pipeline (the harness with every component off)
    harness            Bhavish's harness, default settings
    plain_px2048       plain, with the crop pixel budget raised from 1536² to 2048² (tables are not shrunk)
    harness_tab1       harness, tables cut into strips at native resolution (scale 1.0), header band
                       stacked above each strip (the harness's own strip reader)
    harness_tab15      the same at 1.5× native
    harness_tab2       the same at 2× native
    harness_enhance    harness, on photos with flattened lighting and stretched contrast
    plain_enhance      plain, on the same enhanced photos
Modifiers, added with "+" (e.g. harness_tab15+enhance):
    enhance            the enhanced photos
    pad24              every layout box grown by 24 px on each side (tight boxes clip glyph edges)
    beam3              beam search with 3 beams instead of BODHAN's greedy decoding (cached separately)
"""
import argparse, csv, json, math, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages_ocr"
LAYOUT = ROOT / "ocr" / "layout"
CACHE = ROOT / "ocr" / "lab_cache.json"


def enhance(img):
    """Flatten uneven lighting (divide by a heavily blurred copy), then stretch contrast per channel.
    Colour is kept: the ink is blue, the notebook rules are pale blue and pink."""
    import cv2
    import numpy as np
    from PIL import Image
    a = np.asarray(img).astype(np.float32)
    small = cv2.resize(a, (a.shape[1] // 8, a.shape[0] // 8), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 12), (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR)
    flat = np.clip(a / np.maximum(bg, 1) * 235.0, 0, 255)
    lo, hi = np.percentile(flat, 1, axis=(0, 1)), np.percentile(flat, 99.5, axis=(0, 1))
    out = np.clip((flat - lo) / np.maximum(hi - lo, 1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant")
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    a = ap.parse_args()
    parts = a.variant.split("+")
    base, extra = parts[0], set(parts[1:])
    if base.endswith("_enhance"):
        base, extra = base[: -len("_enhance")], extra | {"enhance"}

    from PIL import Image
    import indic_ocr_harness.api as api
    from indic_ocr_harness import Harness, HarnessConfig
    from indic_ocr_harness.pipeline import page as pg

    table_scale = {"harness_tab1": 1.0, "harness_tab15": 1.5, "harness_tab2": 2.0}.get(base)
    px_side = 2048 if base == "plain_px2048" else None
    cfg = HarnessConfig.plain() if base.startswith("plain") else HarnessConfig()
    if not (base in ("plain", "harness") or table_scale or px_side) or not all(
            m == "enhance" or (m.startswith(("pad", "beam")) and m.lstrip("padbem").isdigit()) for m in extra):
        sys.exit(f"unknown variant {a.variant}")

    class LabPageRun(pg.PageRun):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            if px_side:
                self.crop_cfg = self.rt.CropConfig(max_px_side=px_side)

        def read_scaled(self, arr, prompt, kind):
            if kind != "table" or not table_scale:
                return super().read_scaled(arr, prompt, kind)
            import cv2
            s = table_scale
            z = cv2.resize(arr, (max(1, round(arr.shape[1] * s)), max(1, round(arr.shape[0] * s))),
                           interpolation=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA)
            info = {"line_px": None, "card_scale": round(min(1.0, math.sqrt(self.crop_cfg.max_px / arr.size * 3)), 3),
                    "scale": s}
            if z.shape[0] * z.shape[1] <= self.crop_cfg.max_px:
                texts, pieces = self.read_crops([z], prompt, kind)
                return texts[0], dict(info, mode="lab: forced scale", pieces=pieces)
            t, inf = self.read_strips(z, prompt, kind)
            return t, dict(info, mode="lab: forced strips", **inf)

    api.run_page = lambda image, layout, c, reader, rt: LabPageRun(image, layout, c, reader, rt).run()

    pages = [r for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))
             if a.split == "all" or r["split"] == a.split]
    out = ROOT / "ocr" / f"lab_{a.variant}"
    out.mkdir(parents=True, exist_ok=True)
    LAYOUT.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    with Harness(cfg, device="mps", dtype="float32", cache=str(CACHE)) as h:
        beams = next((int(m[4:]) for m in extra if m.startswith("beam")), 0)
        if beams:
            rec = h.recognizer
            rec.tag += f"|beam{beams}"                     # never mixed with greedy reads in the cache
            rec.batch_size = 2
            gen = rec.backend.model.generate
            rec.backend.model.generate = lambda **kw: gen(**kw, num_beams=beams)
        for p in pages:
            img = Image.open(PAGES / f"{p['page']}.jpg").convert("RGB")
            lay_path = LAYOUT / f"{p['page']}.json"
            if not lay_path.exists():
                lay_path.write_text(json.dumps(h.detect_layout(img), ensure_ascii=False), encoding="utf-8")
            layout = json.loads(lay_path.read_text(encoding="utf-8"))
            for m in extra:
                if m.startswith("pad"):
                    d = int(m[3:])
                    for b in layout["blocks"]:
                        x0, y0, x1, y1 = b["bbox_xyxy"]
                        b["bbox_xyxy"] = [max(0, x0 - d), max(0, y0 - d), min(layout["width"], x1 + d),
                                          min(layout["height"], y1 + d)]
            if "enhance" in extra:
                img = enhance(img)
            t = time.time()
            page = h.read(img, layout=layout, name=p["page"])
            (out / f"{p['page']}.md").write_text(page.text + "\n", encoding="utf-8")
            (out / f"{p['page']}.json").write_text(page.to_json(indent=1), encoding="utf-8")
            print(f"{a.variant} {p['page']}: {time.time() - t:.0f}s", flush=True)
    print(f"{a.variant}: {len(pages)} pages in {time.time() - t_all:.0f}s")


if __name__ == "__main__":
    main()
