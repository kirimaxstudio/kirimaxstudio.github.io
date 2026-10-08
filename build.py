"""Render the public privacy policy. Uses Python's standard library."""
import argparse
import html
import json
from pathlib import Path


def render(data):
    esc = html.escape
    contact = ["Название студии — " + data["brand"] + "."]
    if data.get("developer_name", "").strip():
        contact.append("Оператор персональных данных: " + data["developer_name"] + ".")
    if data.get("developer_status", "").strip():
        contact.append("Статус: " + data["developer_status"])
    if data.get("developer_inn", "").strip():
        contact.append("ИНН: " + data["developer_inn"])
    if data.get("developer_address", "").strip():
        contact.append("Адрес для обращений: " + data["developer_address"])
    if data.get("support_email", "").strip():
        contact.append("Обращения по вопросам данных: " + data["support_email"])
    draft = not data.get("developer_name", "").strip() or not data.get("support_email", "").strip()
    parts = []
    if draft:
        parts.append('<aside class="draft">Черновик: сведения об ответственном разработчике ещё не заполнены. Документ подготовлен для проверки, а не для выпуска игры.</aside>')
    parts.extend([
        "<h1>Политика конфиденциальности</h1>",
        "<p>" + esc(data["game"] + " · " + data["brand"]) + "</p>",
        "<p>" + esc("Дата последнего изменения: " + data["date"]) + "</p>",
        "<p>" + "<br>".join(map(esc, contact)) + "</p>",
    ])
    for section in data["sections"]:
        parts.append("<section><h2>" + esc(section["title"]) + "</h2>")
        parts.extend("<p>" + esc(p) + "</p>" for p in section["text"].split("\n\n"))
        parts.append("</section>")
    parts.append("<h2>Документы сервисов</h2><ul>")
    for link in data["links"]:
        if not link["url"].startswith("https://"):
            raise ValueError("Service links must use HTTPS")
        parts.append('<li><a href="' + esc(link["url"], quote=True) + '">' + esc(link["label"]) + '</a></li>')
    parts.append("</ul>")
    robots = '<meta name="robots" content="noindex">' if draft else ""
    return ('<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="referrer" content="no-referrer">' + robots +
            '<title>' + esc(data["game"]) + ' — политика конфиденциальности</title>'
            '<style>body{margin:0;background:#dbeafe;color:#1f2937;font:17px/1.65 system-ui,sans-serif}'
            'main{max-width:780px;margin:24px auto;padding:28px;background:#eff6ff;border-radius:20px}'
            'h1{font-size:28px;line-height:1.25}h2{font-size:21px;line-height:1.35}'
            'a{color:#2563eb}p,a{overflow-wrap:anywhere}.draft{padding:14px;background:#fef3c7;border-radius:10px}'
            '@media(max-width:600px){main{margin:0;padding:22px;border-radius:0}}</style>'
            '</head><body><main>' + "\n".join(parts) + '</main></body></html>\n')


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=root / "docs/privacy/policy.json")
    parser.add_argument("--output", type=Path, default=root / "docs/privacy/index.html")
    parser.add_argument("--require-contact", action="store_true",
                        help="Fail instead of publishing a draft with missing developer contact")
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    missing = [k for k in ("developer_name", "support_email", "public_url") if not data.get(k, "").strip()]
    if args.require_contact and any(k in missing for k in ("developer_name", "support_email")):
        parser.error("Fill developer_name and support_email in policy.json before publishing.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")
    print("Generated:", args.output)
    if missing:
        print("Before the game release, fill:", ", ".join(missing))


if __name__ == "__main__":
    main()
