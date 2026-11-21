"""Render REPORT.md as one self-contained styled HTML page (figures as separate files next to it), for sharing.

    python report_html.py --out /path/report.html        # also writes report_files.json: published path -> source file
The page is what `build_report.py` produced, converted with python-markdown; image paths are rewritten to
fig/<folder>/<name>.png and listed in report_files.json so the Artifact publish can attach them."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent

CSS = """
<title>Query Routing Representations</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Space+Grotesk:wght@500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* layout: one reading column, section nav on top, tables scroll inside their own frame */
:root {
  --bg: #fbfaf7; --surface: #f2f0ea; --fg: #1b1a17; --muted: #5d5a52; --line: #d8d5cc;
  --accent: #2a78d6; --accent-ink: #1c5cab; --warm: #eb6834; --good: #1baf7a;
  --font-body: "Source Serif 4", Georgia, "Times New Roman", serif;
  --font-head: "Space Grotesk", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "IBM Plex Mono", "SFMono-Regular", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #15161a; --surface: #1e2026; --fg: #ebe9e2; --muted: #a39f94; --line: #353840;
  --accent: #6aa6ef; --accent-ink: #9cc4f5; --warm: #f08a5e; --good: #3fcf98; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #15161a; --surface: #1e2026; --fg: #ebe9e2; --muted: #a39f94; --line: #353840;
  --accent: #6aa6ef; --accent-ink: #9cc4f5; --warm: #f08a5e; --good: #3fcf98; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 17px; line-height: 1.55;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 0 4rem; }
main { max-width: 900px; margin: 0 auto; }
header.top { padding-block: 2.5rem 1rem; border-bottom: 1px solid var(--line); margin-bottom: 1.5rem; }
header.top h1 { font-family: var(--font-head); font-size: clamp(1.7rem, 4vw, 2.5rem); line-height: 1.15; margin: 0 0 .6rem; text-wrap: balance; letter-spacing: -.01em; }
header.top p.meta { color: var(--muted); font-size: .95rem; margin: 0; font-family: var(--font-mono); }
nav.toc { display: flex; flex-wrap: wrap; gap: .4rem .9rem; margin: 1rem 0 0; padding: 0; list-style: none; font-family: var(--font-head); font-size: .9rem; }
nav.toc a { color: var(--accent-ink); text-decoration: none; border-bottom: 1px solid transparent; }
nav.toc a:hover, nav.toc a:focus-visible { border-bottom-color: var(--accent); outline: none; }
h2 { font-family: var(--font-head); font-size: 1.55rem; margin: 2.6rem 0 .8rem; line-height: 1.2; text-wrap: balance; letter-spacing: -.01em; }
h3 { font-family: var(--font-head); font-size: 1.15rem; margin: 2rem 0 .6rem; line-height: 1.3; text-wrap: balance; }
h2 + h3 { margin-top: 1rem; }
p { margin: 0 0 1rem; max-width: 68ch; }
li { margin: 0 0 .5rem; max-width: 68ch; }
ol, ul { padding-left: 1.4rem; }
strong { font-weight: 600; }
em { color: var(--muted); }
code { font-family: var(--font-mono); font-size: .86em; background: var(--surface); padding: .05em .3em; border-radius: 3px; }
pre { background: var(--surface); border: 1px solid var(--line); padding: .8rem 1rem; overflow-x: auto; font-family: var(--font-mono); font-size: .82rem; line-height: 1.5; }
pre code { background: none; padding: 0; }
a { color: var(--accent-ink); }
.table-wrap { overflow-x: auto; margin: 0 0 1.4rem; border: 1px solid var(--line); border-radius: 4px; }
table { border-collapse: collapse; width: 100%; font-size: .84rem; font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
th, td { padding: .42rem .6rem; text-align: left; border-bottom: 1px solid var(--line); white-space: nowrap; vertical-align: top; }
th { font-family: var(--font-head); font-weight: 600; background: var(--surface); position: sticky; top: 0; font-size: .8rem; letter-spacing: .01em; }
tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: color-mix(in srgb, var(--accent) 7%, transparent); }
figure { margin: 1.2rem 0 1.6rem; }
figure img { max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fcfcfb; }
figure figcaption { font-size: .85rem; color: var(--muted); margin-top: .4rem; font-family: var(--font-head); }
.callout { border-left: 3px solid var(--accent); background: var(--surface); padding: .8rem 1rem; margin: 0 0 1.2rem; max-width: 72ch; }
.callout p:last-child { margin-bottom: 0; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
@media (max-width: 560px) { body { font-size: 16px; } table { font-size: .78rem; } }
</style>
"""


def convert(md_path: Path, fig_prefix="fig"):
    text = md_path.read_text()
    files = {}

    def rewrite(m):
        src = m.group(2)
        if not src.endswith(".png"):
            return m.group(0)
        source = (md_path.parent / src).resolve()
        key = f"{fig_prefix}/" + "/".join(p for p in Path(src).parts if p not in ("..", "figures", "analysis", "analysis_compare"))
        files[key] = str(source)
        return f"{m.group(1)}({key})"
    text = re.sub(r"(!?\[[^\]]*\])\(([^)]+)\)", rewrite, text)
    # title and meta line become the header
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip()
    meta = lines[2].strip("_ ") if len(lines) > 2 and lines[2].startswith("_") else ""
    body_md = "\n".join(lines[3:])
    html = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"])
    html = html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    html = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" /></p>', r'<figure><img alt="\1" src="\2" loading="lazy"><figcaption>\1</figcaption></figure>', html)
    html = re.sub(r'<p><em>\((.*?)\)</em></p>', r'<div class="callout"><p>\1</p></div>', html, flags=re.S)
    # section nav from the h2 headings
    heads = re.findall(r"<h2>(.*?)</h2>", html)
    ids = []
    for i, h in enumerate(heads):
        slug = "s" + re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")[:40]
        ids.append((slug, h))
        html = html.replace(f"<h2>{h}</h2>", f'<h2 id="{slug}">{h}</h2>', 1)
    nav = "".join(f'<a href="#{slug}">{re.sub(r"^[0-9]+[.] ", "", h)}</a>' for slug, h in ids)
    page = (CSS + "<main><header class=\"top\">" + f"<h1>{title}</h1>" + (f'<p class="meta">{meta}</p>' if meta else "")
            + f'<nav class="toc" aria-label="Sections">{nav}</nav></header>' + html + "</main>")
    return page, files


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", default=str(HERE / "REPORT.md"))
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    page, files = convert(Path(args.report))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    (out.parent / "report_files.json").write_text(json.dumps(files, indent=1))
    missing = [k for k, v in files.items() if not Path(v).exists()]
    print(f"wrote {out} ({len(page) // 1024} KB), {len(files)} figures" + (f", MISSING: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
