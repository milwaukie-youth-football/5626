#!/usr/bin/env python3
"""Check every internal link in the built site under `public`.

Run after any content move: rebuild, then `python3 scripts/check-links.py`.
Reports links whose target page/asset is missing, and #anchors that don't
exist on the target page. Exit code 1 if anything is broken.
"""
import pathlib, re, sys
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "public"

# baseUrl in quartz.config.yaml may carry a path prefix (e.g. .../5626), which
# absolute links in the built HTML include but the local public/ tree does not
m = re.search(r"baseUrl:\s*(\S+)", (REPO / "quartz.config.yaml").read_text())
PREFIX = ("/" + m.group(1).split("/", 1)[1].strip("/") + "/") if m and "/" in m.group(1) else "/"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if tag in ("a", "img", "iframe", "link", "script") and a.get(key):
                self.refs.append(a[key])


def parse(path):
    p = Links()
    p.feed(path.read_text(errors="ignore"))
    return p


pages = {p: parse(p) for p in ROOT.rglob("*.html")}
anchors = {p.relative_to(ROOT).as_posix(): v.ids for p, v in pages.items()}
broken = []

for page, data in pages.items():
    here = "/" + page.relative_to(ROOT).as_posix()
    for ref in data.refs:
        if re.match(r"^(https?:|mailto:|data:|#|//)", ref) or not ref:
            continue
        target, _, frag = ref.partition("#")
        if not target:
            continue                       # same-page anchor
        abs_url = unquote(urljoin(here, target))
        if PREFIX != "/":
            if abs_url == PREFIX.rstrip("/"):
                abs_url = "/"
            elif abs_url.startswith(PREFIX):
                abs_url = "/" + abs_url[len(PREFIX):]
        rel = abs_url.lstrip("/")
        cand = ROOT / rel
        if cand.is_dir():
            cand = cand / "index.html"
            rel = rel.rstrip("/") + "/index.html"
        if not cand.exists() and not rel.endswith(".html"):
            alt = ROOT / (rel + ".html")   # extensionless page link
            if alt.exists():
                cand, rel = alt, rel + ".html"
        if not cand.exists():
            broken.append((here, ref, "missing target"))
        elif frag and rel in anchors and frag not in anchors[rel]:
            broken.append((here, ref, f"missing anchor #{frag}"))

print(f"checked {len(pages)} pages, {sum(len(d.refs) for d in pages.values())} refs")
for page, ref, why in sorted(broken):
    print(f"BROKEN  {page}  ->  {ref}   ({why})")
print(f"{len(broken)} broken")
sys.exit(1 if broken else 0)
