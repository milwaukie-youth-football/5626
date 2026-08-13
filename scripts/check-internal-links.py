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
checked = 0
# Match each <a ...> tag as a whole first, then pull class/href out of it independently -
# attribute order in Quartz's output isn't guaranteed (href often comes before class),
# so a single ordered regex silently matches nothing and the check passes vacuously.
tag_re = re.compile(r"<a\b[^>]*>")
class_re = re.compile(r'class="([^"]*)"')
href_re = re.compile(r'href="([^"]*)"')

for page in root.rglob("*.html"):
    text = page.read_text(encoding="utf-8", errors="ignore")
    for tag in tag_re.finditer(text):
        tag_text = tag.group(0)
        class_m = class_re.search(tag_text)
        href_m = href_re.search(tag_text)
        if not class_m or not href_m:
            continue
        if "internal-link" not in class_m.group(1).split():
            continue
        checked += 1
        href = html.unescape(href_m.group(1))
        if not resolves(page.parent, href):
            broken.append((str(page.relative_to(root)), href))

if checked == 0:
    print("ERROR: matched 0 internal-link anchors - the check regex is broken, not the site.")
    sys.exit(1)

if broken:
    print(f"BROKEN internal links: {len(broken)}")
    for src, href in broken:
        print(f"  {src} -> {href}")
    sys.exit(1)

print(f"OK: all internal wikilinks resolve ({checked} links checked across {sum(1 for _ in root.rglob('*.html'))} pages).")
