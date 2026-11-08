"""Render an HTML file (or one element of it) to PNG with headless Chromium.

  python scripts/render.py scripts/fig1_design.html docs/img/fig1_design.png --selector "#fig"
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html")
ap.add_argument("png")
ap.add_argument("--selector", default=None)
ap.add_argument("--width", type=int, default=1360)
ap.add_argument("--height", type=int, default=900)
ap.add_argument("--scale", type=float, default=2)
a = ap.parse_args()

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": a.width, "height": a.height}, device_scale_factor=a.scale)
    pg.goto(Path(a.html).resolve().as_uri())
    pg.wait_for_timeout(400)
    (pg.locator(a.selector) if a.selector else pg).screenshot(path=a.png, **({} if a.selector else {"full_page": True}))
    b.close()
print("wrote", a.png)
