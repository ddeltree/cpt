from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import shutil

MD_DIR = Path("md")
PUBLIC = Path("public")

if PUBLIC.exists():
    shutil.rmtree(PUBLIC)
if MD_DIR.exists():
    shutil.rmtree(MD_DIR)

IMAGES, FILES = PUBLIC / "images", PUBLIC / "file"
for p in [PUBLIC, IMAGES, FILES]:
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


def move_dir_content(directory: Path, target_dir: Path):
    for file in directory.rglob("*"):
        if file.is_dir():
            continue
        target_file = target_dir / file.name
        if target_file.exists():
            target_file = target_dir / directory.parent.name
        shutil.move(file, target_file)


def populate_public():
    PLONE = "++plone++ufalprofile"
    for i, p in enumerate(MD_DIR.rglob(PLONE)):
        if i == 0:
            shutil.move(p / "favicons", "public")
        shutil.rmtree(p)
    for directory in MD_DIR.rglob("@@download"):
        move_dir_content(directory, FILES)
        shutil.rmtree(directory)
    for directory in MD_DIR.rglob("@@images"):
        move_dir_content(directory, IMAGES)
        shutil.rmtree(directory)


to_md()
populate_public()
