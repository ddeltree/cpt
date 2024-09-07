from pathlib import Path


UTILS_DIR = Path("utils")
DEAD_LINKS_PATH = UTILS_DIR / "dead_links.txt"

PUBLIC_DIR = Path("../public").resolve()
PAGES_DIR = Path("../src/pages").resolve()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
HTML_DIR = DATA_DIR / "html"
MD_DIR = DATA_DIR / "md"
REDIRECTS_CSV_PATH = UTILS_DIR / "redirects.csv"
LINKS_PATH = UTILS_DIR / "links.txt"
RESOURCES_PATH = UTILS_DIR / "resources.txt"
FRONTMATTER_PATH = UTILS_DIR / "frontmatter.mdx"
SITEMAP_PATH = PUBLIC_DIR / "sitemap.json"
LINK_TAGS_PATH = UTILS_DIR / "link-tags.json"

ROOT_URL = "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao"

SKIP_URLS = DEAD_LINKS_PATH.read_text().splitlines()

HEADERS = {
    # Exigido por http://lattes.cnpq.br/...
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}
