import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  site: 'https://ddeltree.github.io',
  base: 'cpt',
  integrations: [
    tailwind(),
    mdx({
      optimize: true,
    }),
  ],
});
