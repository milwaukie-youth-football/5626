#!/usr/bin/env python3
"""Fail if any internal-link href in the built public/ dir doesn't resolve to a real page."""
import re
import sys
import html
import pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")

def resolves(page_dir: pathlib.Path, href: str) -> bool:
    href = href.split("#")[0]
    if href in ("", "/", "."):
        return True
    target = (page_dir / href).resolve()
    try:
        rel = target.relative_to(root.resolve())
    except ValueError:
        return False
    return (
        (root / rel).exists()
        or (root / f"{rel}.html").exists()
        or (root / rel / "index.html").exists()
    )

broken = []
for page in root.rglob("*.html"):
    text = page.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'<a[^>]*class="[^"]*internal-link[^"]*"[^>]*href="([^"]*)"', text):
        href = html.unescape(m.group(1))
        if not resolves(page.parent, href):
            broken.append((str(page.relative_to(root)), href))

if broken:
    print(f"BROKEN internal links: {len(broken)}")
    for src, href in broken:
        print(f"  {src} -> {href}")
    sys.exit(1)

print(f"OK: all internal wikilinks resolve ({sum(1 for _ in root.rglob('*.html'))} pages checked).")
