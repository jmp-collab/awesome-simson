#!/usr/bin/env python3
"""Baut docs/index.html (GitHub Pages) aus README.md.

Keine Abhängigkeiten, nur Python 3.8+. Aufruf aus dem Repo-Root:
    python3 scripts/build_page.py

README.md bleibt die einzige Quelle; die HTML-Seite nie von Hand bearbeiten.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "README.md"
OUT = ROOT / "docs" / "index.html"

# Wird als canonical und og:url genutzt. Bei eigener Domain hier anpassen.
SITE_URL = "https://jmp-collab.github.io/awesome-simson/"
TITLE = "Awesome Simson & Moped-Tuning: Foren, Anleitungen, Rechner"
DESCRIPTION = (
    "Kuratierte Liste für Simson, DDR-Mopeds, Mofas und klassische Roller: Foren, "
    "Reparaturanleitungen, BVF-Vergaser, Zweitakt-Rechner, 60-km/h-Regel, Museen und Treffen."
)

# Link-Ziel mit bis zu einer Ebene balancierter Klammern, z. B. Wikipedia-Titel
DEST = r"((?:[^()\s]|\([^()\s]*\))+)"


def slug(text):
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


def plain(text):
    """Markdown-Links und -Markierungen zu reinem Text (für Suche und JSON-LD)."""
    text = re.sub(r"\[([^\]]+)\]\(" + DEST + r"\)", r"\1", text)
    return re.sub(r"\s+", " ", text.replace("`", "").replace("*", "")).strip()


def inline(text):
    """Minimales Inline-Markdown: Links, fett, kursiv, Code."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", out)

    def link(m):
        label, href = m.group(1), html.unescape(m.group(2))
        if href.startswith("#"):
            pass
        elif not href.startswith("http"):
            href = "https://github.com/jmp-collab/awesome-simson/blob/main/" + href
        ext = href.startswith("http")
        attrs = ' target="_blank" rel="noopener"' if ext else ""
        return f'<a href="{html.escape(href)}"{attrs}>{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(" + DEST + r"\)", link, out)


ITEM_RE = re.compile(r"^- \[([^\]]+)\]\(" + DEST + r"\)\s*[-–—]\s*(.*)$")


def convert(md):
    lines = md.splitlines()
    body, nav, items = [], [], []
    h2 = h3 = ""
    i = 0
    skip_section = False
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            body.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):  # H1 kommt aus dem Template
            i += 1
            continue
        if line.startswith("## "):
            close_list()
            h2 = line[3:].strip()
            h3 = ""
            skip_section = h2 == "Inhalt"
            if not skip_section:
                nav.append((slug(h2), h2))
                body.append(f'<h2 id="{slug(h2)}">{inline(h2)}</h2>')
            i += 1
            continue
        if skip_section:
            i += 1
            continue
        if line.startswith("### "):
            close_list()
            h3 = line[4:].strip()
            body.append(f'<h3 id="{slug(h3)}">{inline(h3)}</h3>')
        elif line.startswith("|"):
            close_list()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            head, *rest = rows
            t = ['<div class="table"><table><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rest:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            body.append("".join(t))
            continue
        elif line.startswith(">"):
            close_list()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> ").rstrip())
                i += 1
            text = " ".join(q for q in quote if q)
            cls = "tip" if "💡" in text else "lead"
            body.append(f'<aside class="{cls}">{inline(text)}</aside>')
            continue
        elif ITEM_RE.match(line):
            m = ITEM_RE.match(line)
            name, url, desc = m.groups()
            if not in_list:
                body.append('<ul class="tools">')
                in_list = True
            eu = "🇪🇺" in desc
            oss = "OSS`" in desc or "`OSS" in desc
            cat = h3 or h2
            body.append(
                f'<li data-eu="{int(eu)}" data-oss="{int(oss)}" '
                f'data-search="{html.escape(plain(" ".join([name, desc, h2, h3])).lower())}">'
                f'<a class="name" href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(name)}</a>'
                f'<span class="desc">{inline(desc)}</span></li>'
            )
            clean = plain(re.sub(r"🇪🇺|\[`OSS`\]\([^)]*\)|`OSS`", " ", desc))
            items.append({"name": name, "url": url, "description": clean, "category": cat})
        elif re.match(r"^\d+\. ", line) or line.startswith("- "):
            close_list()
            tag = "ol" if line[0].isdigit() else "ul"
            buf = []
            while i < len(lines) and (re.match(r"^\d+\. ", lines[i]) or lines[i].startswith("- ")) and not ITEM_RE.match(lines[i]):
                text = re.sub(r"^(\d+\.|-) ", "", lines[i])
                buf.append(f"<li>{inline(text)}</li>")
                i += 1
            body.append(f"<{tag} class=\"plain\">{''.join(buf)}</{tag}>")
            continue
        elif line.strip() == "---":
            close_list()
        elif line.strip():
            close_list()
            para = [line.strip()]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||>|- |\d+\. |---)", lines[i + 1]):
                i += 1
                para.append(lines[i].strip())
            body.append(f"<p>{inline(' '.join(para))}</p>")
        else:
            close_list()
        i += 1
    close_list()
    return "\n".join(body), nav, items


def main():
    md = SRC.read_text(encoding="utf-8")
    body, nav, items = convert(md)
    # Tools, die in mehreren Kategorien stehen, nur einmal zählen
    seen = set()
    items = [it for it in items if not (it["url"] in seen or seen.add(it["url"]))]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": SITE_URL,
                "url": SITE_URL,
                "name": TITLE,
                "description": DESCRIPTION,
                "inLanguage": "de-DE",
            },
            {
                "@type": "ItemList",
                "name": "Awesome Simson & Moped-Tuning",
                "numberOfItems": len(items),
                "itemListElement": [
                    {"@type": "ListItem", "position": n, "name": it["name"], "url": it["url"],
                     "description": it["description"]}
                    for n, it in enumerate(items, 1)
                ],
            },
        ],
    }
    nav_html = "".join(f'<a href="#{a}">{inline(t)}</a>' for a, t in nav)
    page = TEMPLATE.format(
        title=html.escape(TITLE),
        description=html.escape(DESCRIPTION),
        url=SITE_URL,
        count=len(items),
        nav=nav_html,
        body=body,
        ld=json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(items)} Einträge, {len(nav)} Abschnitte")


TEMPLATE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{ld}</script>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1b18;--muted:#6b665d;--line:#e6e1d6;--card:#fff;--accent:#c8102e;--accent-ink:#9e0c24;--cta:#c8102e;--tip:#fdeef0}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141311;--fg:#ece8e1;--muted:#a39d92;--line:#2c2a26;--card:#1c1b18;--accent:#e5484d;--accent-ink:#ff8a8f;--cta:#b3132a;--tip:#2a1618}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
a{{color:var(--accent-ink)}}
header{{padding:48px 16px 24px;max-width:1080px;margin:auto}}
header h1{{font-size:clamp(28px,5vw,44px);line-height:1.1;margin:0 0 12px;letter-spacing:-.02em}}
header p{{color:var(--muted);max-width:720px;margin:0 0 16px}}
.cta{{display:inline-block;background:var(--cta);color:#fff;text-decoration:none;font-weight:600;padding:10px 16px;border-radius:8px;margin:4px 8px 4px 0}}
.cta.ghost{{background:transparent;color:var(--accent-ink);border:1px solid var(--accent)}}
.bar{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px}}
.bar .in{{max-width:1080px;margin:auto;display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
.bar input[type=search]{{flex:1 1 260px;font:inherit;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}}
.bar label{{font-size:14px;color:var(--muted);white-space:nowrap}}
#count{{font-size:14px;color:var(--muted)}}
nav{{max-width:1080px;margin:12px auto 0;padding:0 16px;display:flex;gap:6px;flex-wrap:wrap}}
nav a{{font-size:13px;text-decoration:none;color:var(--fg);border:1px solid var(--line);border-radius:999px;padding:4px 10px;background:var(--card)}}
main{{max-width:1080px;margin:auto;padding:8px 16px 64px}}
h2{{margin:48px 0 8px;font-size:26px;scroll-margin-top:70px}}
h3{{margin:28px 0 8px;font-size:18px;color:var(--muted);scroll-margin-top:70px}}
ul.tools{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}}
ul.tools li{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}}
ul.tools .name{{display:block;font-weight:650;text-decoration:none;color:var(--fg);margin-bottom:2px}}
ul.tools .name:hover{{color:var(--accent-ink)}}
ul.tools .desc{{font-size:14.5px;color:var(--muted)}}
code{{font-size:12px;background:var(--line);padding:1px 5px;border-radius:4px}}
aside{{margin:12px 0 16px;padding:12px 14px;border-radius:10px}}
aside.tip{{background:var(--tip);border-left:4px solid var(--accent)}}
aside.lead{{color:var(--muted)}}
.table{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:14.5px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
.hidden{{display:none!important}}
footer{{max-width:1080px;margin:auto;padding:24px 16px 48px;color:var(--muted);font-size:14px;border-top:1px solid var(--line)}}
</style>
</head>
<body>
<header>
<h1>Awesome Simson &amp; Moped-Tuning</h1>
<p>{count} geprüfte Quellen für Simson, DDR-Mopeds, Mofas und klassische Roller: Foren, Anleitungen, Vergaser, Rechner, Recht, Museen und Treffen.</p>
<a class="cta" href="https://github.com/jmp-collab/awesome-simson" target="_blank" rel="noopener">Auf GitHub ergänzen</a>
</header>
<div class="bar"><div class="in">
<input type="search" id="q" placeholder="Suchen, z. B. Vergaser, Schwalbe, Führerschein" aria-label="Liste durchsuchen">
<span id="count" aria-live="polite"></span>
</div></div>
<nav aria-label="Kategorien">{nav}</nav>
<main>
{body}
</main>
<footer>Generiert aus <a href="https://github.com/jmp-collab/awesome-simson/blob/main/README.md">README.md</a>. MIT-Lizenz.</footer>
<script>
(function(){{
var q=document.getElementById('q'),count=document.getElementById('count');
var items=[].slice.call(document.querySelectorAll('ul.tools li'));
function run(){{
  var s=q.value.trim().toLowerCase();
  items.forEach(function(li){{
    var ok=!s||li.dataset.search.indexOf(s)>-1;
    li.classList.toggle('hidden',!ok);
  }});
  // Beim Filtern nur Überschriften und Listen mit Treffern zeigen, sonst alles
  var kids=[].slice.call(document.querySelector('main').children);
  kids.forEach(function(el){{el.classList.toggle('hidden',!!s&&!(el.matches('ul.tools')&&el.querySelector('li:not(.hidden)')));}});
  if(s){{
    kids.forEach(function(el,i){{
      if(!/^H[23]$/.test(el.tagName))return;
      var lvl=+el.tagName[1];
      for(var j=i+1;j<kids.length;j++){{
        var k=kids[j]; if(/^H[23]$/.test(k.tagName)&&+k.tagName[1]<=lvl)break;
        if(k.matches('ul.tools')&&!k.classList.contains('hidden')){{el.classList.remove('hidden');break;}}
      }}
    }});
  }}
  // Einträge, die in mehreren Kategorien stehen, nur einmal zählen
  function uniq(list){{var u={{}};list.forEach(function(li){{u[li.querySelector('a.name').href]=1;}});return Object.keys(u).length;}}
  count.textContent=uniq(items.filter(function(li){{return !li.classList.contains('hidden');}}))+' von '+uniq(items)+' Einträgen';
}}
q.addEventListener('input',run);
run();
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
