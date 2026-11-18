"""Render reports/EDA_checkpoint_report.md to PDF (needs Google Chrome; run after the notebooks)."""
import subprocess
from pathlib import Path

import mistune

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: Letter; margin: 0.6in 0.7in; }
body { font: 11px/1.45 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #0b0b0b; }
h1 { font-size: 21px; margin: 0 0 4px; }
h2 { font-size: 14px; margin: 18px 0 6px; padding-bottom: 3px; border-bottom: 1px solid #e4e3df; }
p { margin: 5px 0; }
ul, ol { margin: 4px 0; padding-left: 20px; }
table { border-collapse: collapse; margin: 6px 0; }
th, td { border-bottom: 1px solid #e4e3df; padding: 3px 10px; text-align: left; }
th { color: #52514e; font-weight: 600; }
img { display: block; margin: 4px auto 10px; break-inside: avoid; }
img:not([width]) { width: 78%; }
table { break-inside: avoid; }
p:has(> strong:first-child) { break-after: avoid; }
"""


def main():
    md = (HERE / "EDA_checkpoint_report.md").read_text()
    body = mistune.create_markdown(plugins=["table"], escape=False)(md)
    html = HERE / "EDA_checkpoint_report.html"
    html.write_text(f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{body}")
    pdf = HERE / "EDA_checkpoint_report.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True)
    html.unlink()
    print("wrote", pdf)


if __name__ == "__main__":
    main()
