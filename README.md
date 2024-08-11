# ddeltree.github.io/cpt

Frontend independente para o site do curso de [Ciência da Computação](https://arapiraca.ufal.br/graduacao/ciencia-da-computacao) @ UFAL - Campus Arapiraca.

### Features & objetivos

- NoJS, com um mínimo e opcional JavaScript.
- Carregamento rápido.
- Melhor experiência de navegação entre páginas, com transições e sem recarregamento total.
- Barra lateral com um mapa do site em árvore.
- Responsividade.
- Capacidade de espelhar o site original de forma automatizada.

<br/>

## Dependências e execução

### Dependências

O projeto é um monorepo de um projeto Python com Poetry, que realiza o scraping do [site do curso](https://arapiraca.ufal.br/graduacao/ciencia-da-computacao), com o frontend Astro. Logo, é preciso:

1. Instalar o [Poetry](https://python-poetry.org/)
2. Instalar as dependências do clone usando
   `pnpm install` ou `npm install`

### Scraping

Para espelhar o site do curso, use os comandos:

```bash
cd scripts
poetry shell
python3 main.py # com os argumentos 0, 1 e 2
```

### Servir o front

```bash
pnpm run dev
# ou
npm run dev
```

<br/>

_Construído com [Astro](https://astro.build/)._
