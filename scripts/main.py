from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import shutil
import re
from re import Match

MD_DIR = Path("md")
if MD_DIR.exists():
    shutil.rmtree(MD_DIR)


SITE_URL = "https://arapiraca.ufal.br/graduacao/"
PROJECT_DIR = Path.home() / "httrack-websites/ufal/"
SITE_NAME = "arapiraca.ufal.br/graduacao"
SITE_DIR = PROJECT_DIR / SITE_NAME
shutil.copytree(SITE_DIR, MD_DIR)


def pages_to_mdx():
    for page in MD_DIR.rglob("*"):
        if page.is_dir():
            continue
        if page.suffix != ".html":
            page.unlink()
            continue
        html = page.read_text("utf-8")
        soup = BeautifulSoup(html, features="html.parser")
        content = soup.select_one("#content")
        if not content:
            page.unlink()
            continue
        for header in content.select("header>div"):
            header.clear()
        markdown = "---\nlayout: '@/layouts/Layout.astro'\n---\n\n" + md(str(content))
        mdf = page.parent / (page.stem + ".mdx")
        mdf.write_text(markdown, "utf-8")
        page.unlink()


def clean_directories():
    for glob in [
        "++plone++ufalprofile",
        "@@download",
        "@@images",
    ]:
        for directory in MD_DIR.rglob(glob):
            shutil.rmtree(directory)


def relative_to_url(x: Match):
    d = x.groupdict()
    desc, link, alt = d["desc"], d["link"], d["alt"]
    url = str(link)
    if not link.startswith("http"):
        url = str(SITE_URL / Path(url))
    return f'![{desc}]({url} "{alt}")'


def update_relative_links():
    XP = r"!\[(?P<desc>.*?)\]\((?P<link>.+?)(?:[ ]\"(?P<alt>.+?)\")?\)"
    for md in MD_DIR.rglob("*.mdx"):
        text = md.read_text("utf-8")
        if re.search(XP, text):
            text = re.sub(XP, relative_to_url, text)
        md.write_text(text, "utf-8")


pages_to_mdx()
clean_directories()
update_relative_links()

# TODO mover para src/pages/
# o arquivo ciencia-da-computacao.md é o index
# o diretório ciencia-da-computacao/ terá seu conteúdo movido a src/pages/
