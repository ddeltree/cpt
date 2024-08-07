from pathlib import Path


UTILS_DIR = Path("utils")
DEAD_LINKS_PATH = UTILS_DIR / "dead_links.txt"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
HTML_DIR = DATA_DIR / "html"
MD_DIR = DATA_DIR / "md"
REDIRECTS_CSV_PATH = DATA_DIR / "redirects.csv"
SITEMAP_PATH = DATA_DIR / "sitemap.json"
LINKS_PATH = DATA_DIR / "links.txt"
RESOURCES_PATH = UTILS_DIR / "resources.txt"

ROOT_URL = "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao"

PUBLIC_DIR = Path("../public").resolve()
PAGES_DIR = Path("../src/pages").resolve()
SKIP_URLS = DEAD_LINKS_PATH.read_text().splitlines()

HEADERS = {
    # Exigido por http://lattes.cnpq.br/...
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}
