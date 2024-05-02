from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from urllib.parse import unquote
import shutil
import re
from re import Match

MD_DIR = Path("md")
PUBLIC = Path("public")

if PUBLIC.exists():
    shutil.rmtree(PUBLIC)
if MD_DIR.exists():
    shutil.rmtree(MD_DIR)

IMG_SUFFIXES = list(
    map(lambda e: f".{e}", ["png", "jpg", "jpeg", "gif", "webp", "svg"])
)
IMG_DIR, FILES_DIR = PUBLIC / "images", PUBLIC / "file"
for p in [PUBLIC, IMG_DIR, FILES_DIR]:
    p.mkdir(exist_ok=True)

PROJECT_DIR = Path.home() / "httrack-websites/ufal/"
SITE_NAME = "arapiraca.ufal.br/graduacao"

SITE_DIR = PROJECT_DIR / SITE_NAME
shutil.copytree(SITE_DIR, MD_DIR)


def to_md():
    for page in MD_DIR.rglob("*.html"):
        if page.is_dir():
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


def populate_public():
    PLONE = "++plone++ufalprofile"
    for i, p in enumerate(MD_DIR.rglob(PLONE)):
        if i == 0:
            shutil.move(p / "favicons", "public")
        shutil.rmtree(p)
    move_dir_content()
    for directory in MD_DIR.rglob("@@download"):
        shutil.rmtree(directory)
    for directory in MD_DIR.rglob("@@images"):
        shutil.rmtree(directory)


def move_dir_content():
    for file in MD_DIR.rglob("*"):
        if file.is_dir() or file.suffix == ".md":
            continue
        target_dir = IMG_DIR if file.suffix in IMG_SUFFIXES else FILES_DIR
        target_file = target_dir / file.name
        if target_file.exists():
            target_file = target_dir / (file.parent.parent.name + file.suffix)
        shutil.move(file, target_file)


def update_links():
    XP = r"!\[(?P<desc>.*?)\]\((?P<link>.+?)(?:[ ]\"(?P<alt>.+?)\")?\)"
    for md in MD_DIR.rglob("*.md"):
        text = md.read_text("utf-8")

        def parse(x: Match):
            d = x.groupdict()
            desc, link, alt = d["desc"], d["link"], d["alt"]
            path = md.parent / unquote(link)
            path = Path("/images") / path.name
            return f'![{desc}]({path} "{alt}")'

        if re.search(XP, text):
            text = re.sub(XP, parse, text)
        md.write_text(text, "utf-8")


to_md()
update_links()
populate_public()
