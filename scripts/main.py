from src.scrape import main as scrape
from src.convert_to_mdx import main as to_mdx
from src.create_sitemap import main as create_sitemap


opt = input("scrape (0), to_mdx (1), create_sitemap (2)\n\t-> ")
if "0" in opt:
    scrape()
if "1" in opt:
    to_mdx()
if "2" in opt:
    create_sitemap()
