import fs from 'fs'

const rootURL = 'https://arapiraca.ufal.br/graduacao/ciencia-da-computacao'

const links = fs
  .readFileSync('scripts/utils/links.txt', 'utf-8')
  .split('\n')
  .map((x) => x.trim())
  .filter((x) => x !== '')
  .map((x) => encodeURI(x))
  .map((x) => x.replace(rootURL, '/cpt'))
export default links
