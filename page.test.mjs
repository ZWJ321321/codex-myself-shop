import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('project uses a Vue + Vite entry', async () => {
  const [pkgRaw, html, main] = await Promise.all([
    readFile(new URL('./package.json', import.meta.url), 'utf8'),
    readFile(new URL('./index.html', import.meta.url), 'utf8'),
    readFile(new URL('./src/main.js', import.meta.url), 'utf8'),
  ]);

  const pkg = JSON.parse(pkgRaw);

  assert.equal(pkg.type, 'module');
  assert.equal(pkg.scripts.dev, 'vite');
  assert.equal(pkg.scripts.build, 'vite build');
  assert.equal(pkg.dependencies.vue, '^3.5.0');
  assert.equal(pkg.devDependencies.vite, '^7.0.0');

  assert.match(html, /<div id="app"><\/div>/);
  assert.match(html, /location\.protocol === 'file:'/);
  assert.match(html, /'\.\/dist\/index\.html'/);
  assert.match(main, /createApp\(App\)\.mount\('#app'\)/);
});

test('app component keeps the restaurant sections', async () => {
  const app = await readFile(new URL('./src/App.vue', import.meta.url), 'utf8');

  assert.match(app, /id="hero"/);
  assert.match(app, /id="story"/);
  assert.match(app, /id="dishes"/);
  assert.match(app, /id="space"/);
  assert.match(app, /id="highlights"/);
  assert.match(app, /id="contact"/);
  assert.match(app, /立即预订/);
  assert.match(app, /招牌菜/);
});

test('shared styles and ui helper still provide interactivity', async () => {
  const [css, distHtml, { isScrolled }] = await Promise.all([
    readFile(new URL('./src/styles.css', import.meta.url), 'utf8'),
    readFile(new URL('./dist/index.html', import.meta.url), 'utf8'),
    import(new URL('./src/ui.js', import.meta.url)),
  ]);

  assert.match(css, /\.site-nav\.is-scrolled/);
  assert.match(css, /\.dish-card:hover/);
  assert.match(css, /\.button:hover/);
  assert.match(css, /@media\s*\(max-width:\s*900px\)/);
  assert.match(distHtml, /src="\.\/assets\//);
  assert.match(distHtml, /href="\.\/assets\//);

  assert.equal(isScrolled(0), false);
  assert.equal(isScrolled(80), true);
  assert.equal(isScrolled(40, 60), false);
  assert.equal(isScrolled(61, 60), true);
});
