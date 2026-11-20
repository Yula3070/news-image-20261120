#!/usr/bin/env python3
"""Entry program for the news-image-20261120 competition.

Writes the 20 November 2026 world-news front page to <output>/entry.png.
When PIL and suitable fonts are available it renders the image with
render.py (fully deterministic: no randomness, no clock reads). If
rendering is not possible in the sandbox, it copies the committed
entry.png instead, which is the same image render.py produces.
Standard library only; the output directory comes from
MAKEFUN_OUTPUT_DIR, defaulting to /output.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    try:
        sys.path.insert(0, here)
        import render

        img = render.build()
        tmp = dest + ".tmp"
        img.save(tmp, "PNG", optimize=True)
        os.replace(tmp, dest)
    except Exception:
        # No PIL/fonts in this sandbox: ship the committed render.
        shutil.copyfile(os.path.join(here, "entry.png"), dest)


if __name__ == "__main__":
    main()
