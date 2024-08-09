import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import icon from 'astro-icon';

import react from "@astrojs/react";

// https://astro.build/config
export default defineConfig({
  site: 'https://ddeltree.github.io',
  base: 'cpt',
  integrations: [tailwind(), mdx({
    optimize: true
  }), icon(), react()]
});