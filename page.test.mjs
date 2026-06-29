import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

test('page includes the planned sections and actions', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');

  assert.match(html, /id="hero"/);
  assert.match(html, /id="story"/);
  assert.match(html, /id="dishes"/);
  assert.match(html, /id="space"/);
  assert.match(html, /id="highlights"/);
  assert.match(html, /id="contact"/);
  assert.match(html, /立即预订/);
  assert.match(html, /招牌菜/);
});

test('styles define warm interactive states', async () => {
  const css = await readFile(new URL('./styles.css', import.meta.url), 'utf8');

  assert.match(css, /\.site-nav\.is-scrolled/);
  assert.match(css, /\.dish-card:hover/);
  assert.match(css, /\.button:hover/);
  assert.match(css, /@media\s*\(max-width:\s*900px\)/);
});

test('script exposes the scroll helper without requiring module loading', async () => {
  const source = await readFile(new URL('./script.js', import.meta.url), 'utf8');
  const context = { window: {} };

  vm.createContext(context);
  vm.runInContext(source, context);

  assert.equal(typeof context.window.isScrolled, 'function');
  assert.equal(context.window.isScrolled(0), false);
  assert.equal(context.window.isScrolled(80), true);
  assert.equal(context.window.isScrolled(40, 60), false);
  assert.equal(context.window.isScrolled(61, 60), true);
});
