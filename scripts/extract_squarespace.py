"""One-time migration: Squarespace JSON exports (raw/*.json) -> markdown/JSON content.

Usage: python3 scripts/extract_squarespace.py
Outputs:
  content/blog/*.md          old blog posts (frontmatter + markdown body)
  content/art.json           art gallery metadata
  content/papers.json        papers parsed from the Squarespace papers page
  content/articles.json      essays/articles parsed from the articles page
"""
import json, re, html, datetime, pathlib
from bs4 import BeautifulSoup
from markdownify import markdownify as md

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "raw", ROOT / "content"
(OUT / "blog").mkdir(parents=True, exist_ok=True)

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "untitled"

def clean_html(body):
    soup = BeautifulSoup(body, "html.parser")
    for t in soup.find_all(["script", "style"]):
        t.decompose()
    # Squarespace image blocks -> plain <img>
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if src:
            img.attrs = {"src": src, "alt": img.get("alt", "")}
    for tag in soup.find_all(True):
        for a in ["style", "class", "data-block-type", "id", "data-block-json", "data-layout-label", "data-type"]:
            tag.attrs.pop(a, None)
    return str(soup)

def to_md(body):
    text = md(clean_html(body), heading_style="ATX", bullets="-")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = text.replace("\xa0", " ")
    return text

# ---- blog ----
posts = []
for f in ["blog.json", "blog2.json", "blog3.json"]:
    posts += json.load(open(RAW / f))["items"]
seen = set()
for p in posts:
    if p["id"] in seen: continue
    seen.add(p["id"])
    date = datetime.datetime.utcfromtimestamp(p["publishOn"] / 1000).date()
    title = html.unescape(p["title"]).strip()
    body_md = to_md(p["body"])
    if not title:
        # untitled posts: derive title from first sentence
        first = re.sub(r"[#*_\[\]()>]", "", body_md.split("\n")[0])[:70].strip()
        title = first.rsplit(" ", 1)[0] + "…" if len(first) >= 70 else first
    slug = f"{date.isoformat()}-{slugify(title)}"[:90]
    excerpt = BeautifulSoup(p.get("excerpt") or "", "html.parser").get_text(" ", strip=True)[:300]
    fm = {
        "title": title,
        "date": date.isoformat(),
        "categories": p.get("categories", []),
        "tags": p.get("tags", []),
        "excerpt": excerpt,
        "legacyUrl": "/blog/" + p["urlId"],
    }
    fm_txt = "---\n" + "".join(
        f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items()
    ) + "---\n\n"
    (OUT / "blog" / f"{slug}.md").write_text(fm_txt + body_md + "\n")
print("blog posts:", len(seen))

# ---- art ----
art = json.load(open(RAW / "art.json"))["items"]
art_meta = []
for i, it in enumerate(sorted(art, key=lambda x: x["displayIndex"])):
    w, h = map(int, it["originalSize"].split("x"))
    art_meta.append({"file": f"{i+1:02d}.jpg", "title": html.unescape(it["title"]).strip(), "width": w, "height": h})
json.dump(art_meta, open(OUT / "art.json", "w"), indent=2, ensure_ascii=False)
print("art:", len(art_meta))

# ---- papers & articles (parse the h3-led blocks) ----
def parse_list_page(name):
    soup = BeautifulSoup(json.load(open(RAW / f"{name}.json"))["mainContent"], "html.parser")
    entries = []
    for h3 in soup.find_all("h3"):
        a = h3.find("a")
        entry = {"title": h3.get_text(" ", strip=True), "url": a["href"] if a else None}
        meta, abstract = [], []
        for sib in h3.find_next_siblings():
            if sib.name == "h3" or sib.name == "hr": break
            txt = sib.get_text(" ", strip=True)
            if not txt: continue
            (meta if len(meta) < 2 else abstract).append(str(sib))
        entry["meta_html"] = meta
        entry["abstract_html"] = abstract
        entries.append(entry)
    return entries

for name in ["papers", "articles"]:
    e = parse_list_page(name)
    json.dump(e, open(OUT / f"{name}_raw.json", "w"), indent=2, ensure_ascii=False)
    print(name, len(e))
