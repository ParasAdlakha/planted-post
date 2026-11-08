"""Fill submission texts and copy ready-to-attach deliverables to the parent folder.

  python scripts/finalize.py
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent
nums = json.loads((ROOT / "results" / "report_numbers.json").read_text())
src = (ROOT / "report" / "report.final.md").read_text(encoding="utf-8")
abstract = [l for l in src.splitlines() if l.startswith("abstract:")][0].split(":", 1)[1].strip()


def dur(p):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        s = float(r.stdout.strip())
        return f"{int(s // 60)}:{int(s % 60):02d}"
    except Exception:
        return "[length]"


subs = {"__EPS__": nums["__EPS__"], "__NMODELS__": nums["__NMODELS__"], "__ABSTRACT__": abstract,
        "__ABSWORDS__": str(len(abstract.split())), "__PITCHLEN__": dur(ROOT / "docs" / "video" / "PlantedPost-pitch.mp4")}
for name in ["SUBMISSION TEXTS", "FUNDING FORM"]:
    t = (ROOT / "docs" / f"{name}.template.md").read_text(encoding="utf-8")
    for k, v in subs.items():
        t = t.replace(k, v)
    left = re.findall(r"__[A-Z]+__", t)
    (ROOT / "docs" / f"{name}.md").write_text(t, encoding="utf-8")
    (OUT / f"{name}.md").write_text(t, encoding="utf-8")
    print(name, "leftover:", left)

copies = {
    "report/PlantedPost-report.pdf": "The Planted Post - report.pdf",
    "report/PlantedPost-report.docx": "The Planted Post - report.docx",
    "docs/slides/PlantedPost-slides.pdf": "The Planted Post - slides.pdf",
    "docs/slides/PlantedPost-slides.pptx": "The Planted Post - slides.pptx",
    "docs/video/PlantedPost-pitch.mp4": "The Planted Post - pitch.mp4",
    "docs/video/PlantedPost-demo.mp4": "The Planted Post - demo.mp4",
    "docs/img/social-cover.png": "LinkedIn 1 cover.png",
    "docs/img/social-finding.png": "LinkedIn 2 finding.png",
    "docs/img/social-monitors.png": "LinkedIn 3 monitors.png",
    "docs/research-brief.html": "research-brief.html",
}
for a, b in copies.items():
    p = ROOT / a
    if p.exists():
        shutil.copy2(p, OUT / b)
        print("copied", b)
    else:
        print("MISSING", a)
# the project page links report/ under docs/
(ROOT / "docs" / "report").mkdir(exist_ok=True)
shutil.copy2(ROOT / "report" / "PlantedPost-report.pdf", ROOT / "docs" / "report" / "PlantedPost-report.pdf")
