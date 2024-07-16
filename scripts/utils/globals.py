import shutil
from pathlib import Path


UTILS_DIR = Path("utils")
DEAD_LINKS_PATH = UTILS_DIR / "dead_links.txt"

DATA_DIR = Path("data")
HTML_DIR = DATA_DIR / "html"
MD_DIR = DATA_DIR / "md"

ROOT_URL = "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao"


# TMP
SITE_URL = "https://arapiraca.ufal.br/graduacao/"
PROJECT_DIR = Path.home() / "httrack-websites/ufal/"
SITE_NAME = "arapiraca.ufal.br/graduacao"
SITE_DIR = PROJECT_DIR / SITE_NAME
