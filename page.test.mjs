import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

async function read(path) {
  return readFile(new URL(path, import.meta.url), 'utf8');
}

test('project uses Vue, Vite, and Vue Router entry wiring', async () => {
  const [pkgRaw, html, main, router] = await Promise.all([
    read('./package.json'),
    read('./index.html'),
    read('./src/main.js'),
    read('./src/router.js'),
  ]);

  const pkg = JSON.parse(pkgRaw);

  assert.equal(pkg.type, 'module');
  assert.equal(pkg.scripts.dev, 'vite');
  assert.equal(pkg.scripts.build, 'vite build');
  assert.equal(pkg.dependencies.vue, '^3.5.0');
  assert.ok(pkg.dependencies['vue-router']);
  assert.equal(pkg.devDependencies.vite, '^7.0.0');

  assert.match(html, /<div id="app"><\/div>/);
  assert.match(html, /location\.protocol === 'file:'/);
  assert.match(html, /'\.\/dist\/index\.html'/);
  assert.match(main, /createApp\(App\)/);
  assert.match(main, /\.use\(router\)\.mount\('#app'\)/);
  assert.match(router, /createRouter/);
  assert.match(router, /createWebHistory/);
});

test('router splits the restaurant site into independent page roots', async () => {
  const [app, router] = await Promise.all([
    read('./src/App.vue'),
    read('./src/router.js'),
  ]);

  assert.match(app, /RouterView/);
  assert.match(app, /SiteHeader/);
  assert.match(app, /SiteFooter/);
  assert.doesNotMatch(app, /OrderingSection/);

  assert.match(router, /path:\s*'\/'/);
  assert.match(router, /path:\s*'\/story'/);
  assert.match(router, /path:\s*'\/dishes'/);
  assert.match(router, /path:\s*'\/space'/);
  assert.match(router, /path:\s*'\/contact'/);
  assert.match(router, /path:\s*'\/ordering'/);
});

test('shared styles and ui helper still provide interactivity', async () => {
  const [css, { isScrolled }] = await Promise.all([
    read('./src/styles.css'),
    import(new URL('./src/ui.js', import.meta.url)),
  ]);

  assert.match(css, /\.site-nav\.is-scrolled/);
  assert.match(css, /\.button:hover/);
  assert.match(css, /\.page-hero/);
  assert.match(css, /\.feature-card/);
  assert.match(css, /@media\s*\(max-width:\s*900px\)/);

  assert.equal(isScrolled(0), false);
  assert.equal(isScrolled(80), true);
  assert.equal(isScrolled(40, 60), false);
  assert.equal(isScrolled(61, 60), true);
});

test('page components and ordering section are split by route responsibility', async () => {
  const [
    home,
    story,
    dishes,
    space,
    contact,
    orderingPage,
    orderingSection,
    helpers,
  ] = await Promise.all([
    read('./src/pages/HomePage.vue'),
    read('./src/pages/StoryPage.vue'),
    read('./src/pages/DishesPage.vue'),
    read('./src/pages/SpacePage.vue'),
    read('./src/pages/ContactPage.vue'),
    read('./src/pages/OrderingPage.vue'),
    read('./src/features/ordering/OrderingSection.vue'),
    import(new URL('./src/features/ordering/state.js', import.meta.url)),
  ]);

  const dish = { id: 7, name: 'test dish', price: '36.00' };
  const once = helpers.addCartItem([], dish);
  const twice = helpers.addCartItem(once, dish);

  assert.equal(twice[0].quantity, 2);
  assert.equal(helpers.updateCartItemQuantity(twice, 7, 0).length, 0);
  assert.deepEqual(
    helpers.validateOrderDraft({ customerName: '', phone: '', note: '' }, []),
    {
      customerName: helpers.validateOrderDraft({ customerName: '', phone: '1', note: '' }, []).customerName,
      phone: helpers.validateOrderDraft({ customerName: 'a', phone: '', note: '' }, []).phone,
      items: helpers.validateOrderDraft({ customerName: 'a', phone: '1', note: '' }, []).items,
    }
  );
  assert.deepEqual(
    helpers.buildOrderPayload(
      { customerName: 'name', phone: '13800138000', note: 'note' },
      [{ dishId: 7, quantity: 2 }]
    ),
    {
      customer_name: 'name',
      phone: '13800138000',
      note: 'note',
      items: [{ dish_id: 7, quantity: 2 }],
    }
  );

  assert.match(home, /hero-social-bistro/);
  assert.match(home, /RouterLink/);
  assert.match(story, /story-/);
  assert.match(dishes, /dish-roasted-chicken/);
  assert.match(dishes, /dish-braised-beef/);
  assert.match(space, /space-window-seating/);
  assert.match(contact, /tel:/);
  assert.match(orderingPage, /OrderingSection/);
  assert.match(orderingSection, /id="ordering"/);
});

test('ordering route exposes the new two-step ordering flow', async () => {
  const [pkgRaw, orderingPage, orderingSection, previewPanel, receiptCard, api] = await Promise.all([
    read('./package.json'),
    read('./src/pages/OrderingPage.vue'),
    read('./src/features/ordering/OrderingSection.vue'),
    read('./src/features/ordering/OrderPreviewPanel.vue'),
    read('./src/features/ordering/OrderReceiptCard.vue'),
    read('./src/features/ordering/api.js'),
  ]);

  const pkg = JSON.parse(pkgRaw);

  assert.equal(pkg.scripts.test, 'node --test page.test.mjs src/features/ordering/state.test.mjs');
  assert.match(orderingPage, /先确认价格，再正式下单/);
  assert.match(orderingSection, /previewOrder\(/);
  assert.match(orderingSection, /createOrder\(/);
  assert.match(orderingSection, /requestSignature/);
  assert.match(orderingSection, /previewSummary\.value = null/);
  assert.match(orderingSection, /订单信息已变更，请重新确认价格/);
  assert.match(orderingSection, /取餐时间/);
  assert.match(orderingSection, /用餐方式/);
  assert.match(previewPanel, /确认订单信息/);
  assert.match(previewPanel, /正式下单/);
  assert.match(receiptCard, /订单回执/);
  assert.match(api, /order-previews/);
  assert.match(api, /正式下单失败/);
});

test('critical user-facing copy is not corrupted', async () => {
  const [header, home, story, dishes, space, contact, orderingPage, orderingSection, state, api] = await Promise.all([
    read('./src/components/SiteHeader.vue'),
    read('./src/pages/HomePage.vue'),
    read('./src/pages/StoryPage.vue'),
    read('./src/pages/DishesPage.vue'),
    read('./src/pages/SpacePage.vue'),
    read('./src/pages/ContactPage.vue'),
    read('./src/pages/OrderingPage.vue'),
    read('./src/features/ordering/OrderingSection.vue'),
    read('./src/features/ordering/state.js'),
    read('./src/features/ordering/api.js'),
  ]);

  for (const source of [header, home, story, dishes, space, contact, orderingPage]) {
    assert.doesNotMatch(source, /\?{2,}/);
  }

  assert.match(header, /\u6728\u820d\u98df\u5802/);
  assert.match(header, /\u5728\u7ebf\u70b9\u9910/);
  assert.match(home, /\u4eca\u665a\u60f3\u5403\u5f97\u8ba4\u771f\u4e00\u70b9/);
  assert.match(story, /\u54c1\u724c\u6545\u4e8b|Brand Story/);
  assert.match(dishes, /\u7099\u70e4\u5357\u74dc\u5976\u6cb9\u9e21\u817f\u6392/);
  assert.match(space, /\u7a97\u8fb9\u5ea7\u4f4d/);
  assert.match(contact, /\u7535\u8bdd\u9884\u7ea6/);
  assert.match(orderingPage, /\u5148\u786e\u8ba4\u4ef7\u683c\uff0c\u518d\u6b63\u5f0f\u4e0b\u5355/);
  assert.match(orderingSection, /\u5728\u7ebf\u70b9\u9910/);
  assert.match(state, /\u8bf7\u8f93\u5165\u59d3\u540d/);
  assert.match(api, /\u52a0\u8f7d\u83dc\u54c1\u5931\u8d25/);
});

test('ordering api gracefully handles empty or non-json responses', async () => {
  const originalFetch = globalThis.fetch;
  const { fetchCategories, submitOrder } = await import(new URL('./src/features/ordering/api.js', import.meta.url));

  try {
    globalThis.fetch = async () => ({
      ok: false,
      status: 500,
      text: async () => '',
      json: async () => { throw new SyntaxError('Unexpected end of JSON input'); },
    });

    await assert.rejects(fetchCategories(), /加载分类失败/);
    await assert.rejects(
      submitOrder({ customer_name: 'a', phone: '1', items: [] }),
      /提交订单失败/
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});