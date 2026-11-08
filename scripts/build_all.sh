#!/usr/bin/env bash
# Rebuild every artifact from results/ in order.  bash scripts/build_all.sh
set -e
cd "$(dirname "$0")/.."
python tests/test_core.py
python -m planted.replay
python -m planted.analyze > /dev/null
python -m planted.monitors | tail -3
python scripts/fill_report.py
python scripts/build_report.py
python scripts/fill_slides.py
python scripts/build_slides.py
for id in cover finding monitors; do python scripts/render.py scripts/social.final.html docs/img/social-$id.png --selector "#$id" --width 1300 --height 2200 --scale 2 > /dev/null; done
python scripts/export_viewer.py > /dev/null
rm -f docs/video/_build/pitch_*
python scripts/build_videos.py pitch
python scripts/finalize.py
