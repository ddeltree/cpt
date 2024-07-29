import fs from 'fs'

const redirects = fs
  .readFileSync('scripts/utils/redirects.csv', 'utf-8')
  .split('\n')
  .map((x) => x.trim())
  .filter((x) => x !== '')
  .map((x) => x.split(',')[0])
  .map(encodeURI)

const rootURL = 'https://arapiraca.ufal.br/graduacao/ciencia-da-computacao'

const links = fs
  .readFileSync('scripts/utils/links.txt', 'utf-8')
  .split('\n')
  .map((x) => x.trim())
  .filter((x) => x !== '')
  .map(encodeURI)
  .map((x) => (redirects.includes(x) ? x : x.replace(rootURL, '/cpt')))
export default links
