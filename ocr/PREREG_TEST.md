# Pre-registration: BODHAN OCR levers, before the held-out test pages

Written 2026-10-26 16:43 IST, after the dev runs and before any test-page run of a new variant.

## Frozen code (SHA-256)

```
7c72a642ff50a79f4cbcdce5a00f79c3d64e81d38911bd021e94522c3513c43d  ocr_post.py
1611b1e6f44b7cacc050f89d0a2997b8b9dd51c07f876532bc0b03eda8d20a61  ocr_lab.py
2129045bd3ac33e660589161f3d3503da4dd4ac80b82a413d0aef7994ce4b347  eval_ocr.py
4a584ce55a04d4dccfda33ab8662177eab84b14d6472d2e0c64def4c12b7c723  resolve.py
aedfa2a5944a2603c90bb4ef4705de845ff2319fd9ef5297558b69e4c028cbd2  crosscheck.py
```

## Variants carried to the test pages

- `plain+post`, `harness+post`: BODHAN (without / with the harness), then `ocr_post.py`.
- `harness_tab1+post`: big tables read in strips at native resolution, then `ocr_post.py`.

Not carried: beam search (no gain on dev, 2.3x slower), 2048 px budget (neutral), enhanced photos (worse),
1.5x and 2x upscaled tables (worse, and real wrong links on dev).

## Predictions (test pages, 208 name mentions)

1. `+post` links more names to the right person and leaves fewer unread than its base, with 0 wrong links
   and no new link-audit flags.
2. `+post` finds at least as many numbers as its base.
3. `harness_tab1+post` links more names to the right person than `harness+post`, and finds the same number
   of numbers or fewer.

## Caveat

The cleanup rules in `ocr_post.py` were written after looking at BODHAN's output on all 19 pages (for
example the glued "C.M" on IMG_0118, a test page). Their test result is a check, not a blind test. The
tiling variant was never run on a test page before this file.
