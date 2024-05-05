from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from urllib.parse import unquote
import shutil
import re
from re import Match

MD_DIR = Path("md")
if MD_DIR.exists():
    shutil.rmtree(MD_DIR)

PROJECT_DIR = Path.home() / "httrack-websites/ufal/"
SITE_NAME = "arapiraca.ufal.br/graduacao"

SITE_DIR = PROJECT_DIR / SITE_NAME
shutil.copytree(SITE_DIR, MD_DIR)


def to_md():
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
        markdown = md(str(content))
        mdf = page.parent / (page.stem + ".md")
        mdf.write_text(markdown, "utf-8")
        page.unlink()
    clean_directories()


def clean_directories():
    for glob in [
        "++plone++ufalprofile",
        "@@download",
        "@@images",
    ]:
        for directory in MD_DIR.rglob(glob):
            shutil.rmtree(directory)


def update_links():
    XP = r"!\[(?P<desc>.*?)\]\((?P<link>.+?)(?:[ ]\"(?P<alt>.+?)\")?\)"
    for md in MD_DIR.rglob("*.md"):
        text = md.read_text("utf-8")

        def parse(x: Match):
            d = x.groupdict()
            desc, link, alt = d["desc"], d["link"], d["alt"]
            # TODO apenas urls relativas
            path = "https://arapiraca.ufal.br/graduacao/" / Path(link)
            return f'![{desc}]({path} "{alt}")'

        if re.search(XP, text):
            text = re.sub(XP, parse, text)
        md.write_text(text, "utf-8")


to_md()
clean_directories()
update_links()
# TODO mover para src/pages
# TODO adicionar layout (frontmatter)
