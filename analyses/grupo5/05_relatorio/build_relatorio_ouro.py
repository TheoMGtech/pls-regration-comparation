from __future__ import annotations

import base64
import html
import json
import re
from io import BytesIO
from pathlib import Path

import markdown
from PIL import Image, ImageChops


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = ROOT / "docs" / "relatorios" / "grupo5"
NOTEBOOK = REPORT / "relatorio_ouro.ipynb"
OUTPUT = REPORT / "relatorio_ouro.html"


CSS = r"""
:root{--navy:#17324d;--gold:#b88917;--ink:#1d2730;--muted:#5b6670;--paper:#fff;--soft:#f2f5f7;--red:#a33d34}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#e8ecef;color:var(--ink);font-family:Inter,"Segoe UI",Arial,sans-serif;line-height:1.55}
nav{position:sticky;top:0;z-index:10;display:flex;gap:14px;overflow:auto;padding:10px 20px;background:rgba(23,50,77,.97);box-shadow:0 2px 10px #0003}
nav a{color:#fff;text-decoration:none;white-space:nowrap;font-size:12px}nav a:hover{color:#f2cf6f}
main{width:min(1120px,calc(100% - 32px));margin:24px auto 60px;background:var(--paper);box-shadow:0 8px 36px #24384a24}
section{padding:36px 54px 14px}.cover{min-height:72vh;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(135deg,var(--navy),#255d72);color:white;border-bottom:8px solid var(--gold)}
.cover h1{font-size:48px;margin:0 0 8px}.cover h2{font-size:25px;color:#f5d77f;border:0}.cover p{font-size:17px}
h2{color:var(--navy);font-size:28px;border-bottom:3px solid var(--gold);padding-bottom:8px;margin:0 0 18px}h3{color:var(--navy)}
p{max-width:92ch}blockquote{margin:22px 0;padding:14px 18px;background:#fff7dd;border-left:5px solid var(--gold)}code{background:#eef1f3;padding:2px 5px;border-radius:3px}
.outputs{padding:8px 54px 30px}.execution-note{font-size:12px;color:var(--muted);background:var(--soft);padding:8px 12px;margin-bottom:12px}
.flow{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;margin:28px 0;padding:22px;background:linear-gradient(135deg,#f2f5f7,#fff7dd);border:1px solid #d8dee3;border-radius:10px}
.flow span{padding:12px 16px;background:white;border:2px solid var(--navy);border-radius:8px;font-weight:700;color:var(--navy)}.flow b{font-size:24px;color:var(--gold)}
.formula{text-align:center;font-family:"Cambria Math",Cambria,serif;font-size:22px;margin:24px auto;padding:14px;background:#f6f8f9;border-left:4px solid var(--gold);max-width:70ch}
.teoria-pls{min-height:620px;background:linear-gradient(180deg,#fff,#fbfcfd)}.estudo-caso-ouro{background:#fffaf0}.comparacao-futura,.conclusao-global-futura{background:#f7fafc}
table{border-collapse:collapse;width:100%;margin:14px 0 24px;font-size:13px}th{background:var(--navy);color:white;text-align:left}th,td{padding:8px 9px;border:1px solid #d8dee3}tr:nth-child(even) td{background:#f6f8f9}
figure{margin:22px auto;text-align:center}img{max-width:100%;height:auto}pre{white-space:pre-wrap;background:var(--soft);padding:12px}ul{max-width:92ch}
footer{padding:24px 54px;color:var(--muted);border-top:1px solid #ddd;font-size:12px}
@media print{@page{size:A4;margin:16mm 14mm 17mm}body{background:white;font-size:10.5pt}nav{display:none}main{width:100%;margin:0;box-shadow:none}.cover{min-height:245mm}.section{break-before:page;padding:0 0 6mm}.teoria-pls,.estudo-caso-ouro,.comparacao-futura,.conclusao-global-futura{min-height:auto}.outputs{padding:0 0 5mm}h2{font-size:20pt}table{font-size:8.5pt}figure,.flow,table,blockquote{break-inside:avoid}img{max-height:165mm;object-fit:contain}tr{break-inside:avoid}a{color:inherit;text-decoration:none}}
"""


def convert_markdown(source: str) -> str:
    def formula(match: re.Match[str]) -> str:
        raw = match.group(1).strip()
        if raw == r"t_k = X w_k":
            value = "t<sub>k</sub> = X w<sub>k</sub>"
        elif raw == r"z = \frac{x - \mu_{treino}}{\sigma_{treino}}":
            value = "z = (x - μ<sub>treino</sub>) / σ<sub>treino</sub>"
        else:
            value = html.escape(raw)
        return f'<div class="formula">{value}</div>'

    source = re.sub(r"\$\$(.*?)\$\$", formula, source, flags=re.S)
    return markdown.markdown(source, extensions=["tables", "fenced_code", "md_in_html"])


def output_html(output: dict) -> str:
    data = output.get("data", {})
    if "text/html" in data:
        return "".join(data["text/html"])
    if "image/png" in data:
        payload = data["image/png"]
        if isinstance(payload, list):
            payload = "".join(payload)
        image = Image.open(BytesIO(base64.b64decode(payload))).convert("RGB")
        background = Image.new("RGB", image.size, "white")
        if ImageChops.difference(image, background).getbbox() is None:
            return ""
        return f'<figure><img src="data:image/png;base64,{payload}" alt="Visualização do relatório"></figure>'
    if output.get("output_type") == "stream":
        return ""
    if "text/plain" in data:
        text = "".join(data["text/plain"])
        return f"<pre>{html.escape(text)}</pre>"
    return ""


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    cover = convert_markdown("".join(cells[0]["source"]))
    nav: list[str] = []
    body: list[str] = [f'<section class="cover">{cover}</section>']
    section_index = 0

    for cell in cells[1:]:
        if cell["cell_type"] == "markdown":
            section_index += 1
            source = "".join(cell.get("source", []))
            heading = re.search(r"^##\s+(.+)$", source, flags=re.M)
            label = heading.group(1).strip() if heading else f"Seção {section_index}"
            anchor = f"sec-{section_index}"
            tags = cell.get("metadata", {}).get("tags", [])
            classes = " ".join(["section", *tags])
            nav.append(f'<a href="#{anchor}">{html.escape(label)}</a>')
            body.append(f'<section class="{classes}" id="{anchor}">{convert_markdown(source)}</section>')
        elif cell["cell_type"] == "code":
            rendered = "".join(output_html(output) for output in cell.get("outputs", []))
            if rendered:
                body.append(f'<div class="outputs">{rendered}</div>')

    document = (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Grupo 5 - Estudo de caso da Base Ouro</title>'
        f"<style>{CSS}</style></head><body><nav>{''.join(nav)}</nav><main>"
        f"{''.join(body)}"
        '<footer>Grupo 5 - estudo de caso da Base Ouro. V1 oficial; V2 complementar.</footer>'
        "</main></body></html>"
    )
    OUTPUT.write_text(document, encoding="utf-8", newline="\n")
    print(f"generated={OUTPUT}")
    print(f"sections={section_index}")


if __name__ == "__main__":
    main()
