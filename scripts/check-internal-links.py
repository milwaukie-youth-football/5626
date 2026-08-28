#!/usr/bin/env python3
"""Fail if any internal link in the built public/ dir doesn't resolve.

Checks three things, all against the emitted HTML:
  - internal-link hrefs resolve to a real page (a link that escapes the site
    root is broken, even though it resolves on a local filesystem)
  - #anchors on those links exist on the target page
  - <img src> assets resolve
"""
import re
import sys
import html
import pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")

def target_page(page_dir: pathlib.Path, href: str):
    """Return the emitted file a href points at, or None if it doesn't resolve."""
    href = href.split("#")[0]
    if href in ("", "/", "."):
        return None
    target = (page_dir / href).resolve()
    try:
        rel = target.relative_to(root.resolve())
    except ValueError:
        return None                      # escaped the site root
    for cand in ((root / rel), (root / f"{rel}.html"), (root / rel / "index.html")):
        if cand.exists():
            return cand
    return None


def ids_on(page: pathlib.Path) -> set:
    if page.suffix != ".html":
        return set()
    if page not in _ids:
        text = page.read_text(encoding="utf-8", errors="ignore")
        _ids[page] = set(re.findall(r'id="([^"]+)"', text))
    return _ids[page]


_ids: dict = {}

broken = []
checked = 0
# Match each <a ...> tag as a whole first, then pull class/href out of it independently -
# attribute order in Quartz's output isn't guaranteed (href often comes before class),
# so a single ordered regex silently matches nothing and the check passes vacuously.
tag_re = re.compile(r"<a\b[^>]*>")
class_re = re.compile(r'class="([^"]*)"')
href_re = re.compile(r'href="([^"]*)"')
img_re = re.compile(r'<img\b[^>]*\bsrc="([^"]*)"')

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
        if href.startswith("#"):
            dest = page                      # same-page anchor
        else:
            dest = target_page(page.parent, href)
        if dest is None:
            broken.append((str(page.relative_to(root)), href))
            continue
        frag = href.partition("#")[2]
        if frag and frag not in ids_on(dest):
            broken.append((str(page.relative_to(root)), f"{href}  (no such anchor)"))

    for src in img_re.findall(text):
        src = html.unescape(src)
        if re.match(r"^(https?:|data:|//)", src):
            continue
        checked += 1
        if target_page(page.parent, src) is None:
            broken.append((str(page.relative_to(root)), src))

if checked == 0:
    print("ERROR: matched 0 internal-link anchors - the check regex is broken, not the site.")
    sys.exit(1)

if broken:
    print(f"BROKEN internal links: {len(broken)}")
    for src, href in broken:
        print(f"  {src} -> {href}")
    sys.exit(1)

print(f"OK: all internal links, anchors and images resolve "
      f"({checked} checked across {sum(1 for _ in root.rglob('*.html'))} pages).")
