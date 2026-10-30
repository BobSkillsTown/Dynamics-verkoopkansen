"""Build the GitHub Pages site from site/.

site/index.html is written as an artifact page: it has no <!doctype>, <html>, <head> or <body>
of its own. This script wraps it in a complete document and copies the images to _site/.

Run from the repository root:  python3 tools/build_pages.py
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"
OUT = ROOT / "_site"

# Same base the artifact viewer adds around the page
BASE_STYLE = """<style>
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>"""


def main():
    page = (SRC / "index.html").read_text(encoding="utf-8")
    split = page.index("</style>") + len("</style>")
    head, body = page[:split], page[split:]
    head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    html = (
        "<!doctype html>\n<html lang=\"nl\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        f"{BASE_STYLE}\n{head}\n</head>\n<body>\n{body.strip()}\n</body>\n</html>\n"
    )
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "img", OUT / "img")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
