from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup

ROOT_DIR = Path.home() / "httrack-websites/ufal/arapiraca.ufal.br/graduacao"
MD_DIR = ROOT_DIR / "md"
MD_DIR.mkdir(exist_ok=True)

for page in ROOT_DIR.rglob("*.html"):
    if page.is_dir():
        continue
    html = page.read_text("utf-8")
    soup = BeautifulSoup(html, features="html.parser")
    content = soup.select_one("#content")
    if not content:
        continue
    for header in content.select("header>div"):
        header.clear()
    markdown = md(str(content))
    md_dir = MD_DIR / page.parent.relative_to(ROOT_DIR)
    for parent in list(page.relative_to(ROOT_DIR).parents)[1::-1]:
        (MD_DIR / parent).mkdir(exist_ok=True)
    mdf = md_dir / (page.stem + ".md")
    mdf.write_text(markdown, "utf-8")
