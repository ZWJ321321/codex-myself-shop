<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { createRevealObserver, isScrolled, revealVisible } from './ui.js';

const navRef = ref(null);

const navItems = [
  { label: '故事', href: '#story' },
  { label: '招牌菜', href: '#dishes' },
  { label: '环境', href: '#space' },
  { label: '到店', href: '#contact' },
];

const heroNotes = ['现做热食', '适合约会聚餐', '晚间氛围感'];

const dishes = [
  {
    title: '炙烤奶油南瓜鸡腿排',
    tag: 'Chef Pick',
    copy: '适合放在第一张卡片，用来承接首屏的暖色调与“现做热食”感。',
    mediaClass: 'dish-media dish-media-1',
  },
  {
    title: '慢炖番茄牛肉锅',
    tag: 'Most Loved',
    copy: '文案适合强调汤底、时间、温度与分享场景，而不是堆原料名词。',
    mediaClass: 'dish-media dish-media-2',
  },
  {
    title: '海盐焦糖热布丁',
    tag: 'Dessert Hour',
    copy: '第三张卡片可以稍轻一些，用甜点或酒水把“约会感”补完整。',
    mediaClass: 'dish-media dish-media-3',
  },
];

const highlights = [
  { title: '适合聚会', copy: '桌距舒适、动线安静，适合聊天而不是匆忙打卡。' },
  { title: '手作热食', copy: '强调现做、慢炖、炙烤等关键词，比“丰富菜品”更有记忆点。' },
  { title: '晚间氛围', copy: '从色温、材质到文案，整个页面都围绕下班后的松弛感展开。' },
  { title: '可快速替换', copy: '真实门店接入时，只需要换品牌名、文案、图片和地址即可。' },
];

let observer;

function syncNav() {
  if (!navRef.value) return;
  navRef.value.classList.toggle('is-scrolled', isScrolled(window.scrollY));
}

onMounted(() => {
  syncNav();
  const nodes = [...document.querySelectorAll('[data-reveal]')];
  revealVisible(nodes, window.innerHeight * 0.92);
  observer = createRevealObserver(nodes);
  window.addEventListener('scroll', syncNav, { passive: true });
});

onBeforeUnmount(() => {
  observer?.disconnect();
  window.removeEventListener('scroll', syncNav);
});
</script>

<template>
  <div>
    <div class="page-glow page-glow-left"></div>
    <div class="page-glow page-glow-right"></div>

    <header class="site-header">
      <nav ref="navRef" class="site-nav" aria-label="主导航">
        <a class="brand" href="#hero">
          <span class="brand-mark">MU</span>
          <span class="brand-copy">
            <strong>木舍食堂</strong>
            <small>Warm Kitchen &amp; Gatherings</small>
          </span>
        </a>
        <div class="nav-links">
          <a v-for="item in navItems" :key="item.href" :href="item.href">{{ item.label }}</a>
        </div>
        <a class="button button-small" href="#contact">立即预订</a>
      </nav>
    </header>

    <main>
      <section id="hero" class="hero section-shell" data-reveal>
        <div class="hero-copy">
          <p class="eyebrow">Warm dinners, slow evenings.</p>
          <h1>把晚餐还给灯光、木香与好好说话的时间。</h1>
          <p class="hero-text">
            木舍食堂是一张可替换内容的温馨餐馆模板页。它把品牌氛围放在第一位，用暖色灯光感、
            手作料理感和舒缓留白，让用户先想坐下来，再去看菜、看环境、看路线。
          </p>
          <div class="hero-actions">
            <a class="button" href="#contact">立即预订</a>
            <a class="button button-ghost" href="#dishes">浏览招牌菜</a>
          </div>
          <ul class="hero-notes">
            <li v-for="note in heroNotes" :key="note">{{ note }}</li>
          </ul>
        </div>

        <div class="hero-visual" aria-hidden="true">
          <div class="photo-card photo-card-main">
            <span>主视觉位 / 可替换门店大图</span>
          </div>
          <div class="photo-card photo-card-top">
            <span>料理近景</span>
          </div>
          <div class="photo-card photo-card-bottom">
            <span>木质空间</span>
          </div>
          <div class="hero-badge">
            <strong>12:00 - 22:00</strong>
            <span>营业中 · 适合晚餐与慢聚</span>
          </div>
        </div>
      </section>

      <section id="story" class="story section-shell" data-reveal>
        <div class="section-heading">
          <p class="eyebrow">Brand Story</p>
          <h2>不是把菜端上来，而是把这一顿饭的情绪布置好。</h2>
        </div>
        <div class="story-grid">
          <div class="story-copy">
            <p>
              这里的文案默认围绕“手作、陪伴、放慢”来写。你可以替换成真实餐馆故事，比如主厨背景、
              食材来源、社区感，或者一句最能代表餐馆气质的话。
            </p>
            <p>
              页面结构已经把情绪、卖点和到店动作拆开：首屏打动人，招牌菜给理由，环境区强化想象，
              最后用清晰的联系信息承接转化。
            </p>
          </div>
          <aside class="story-panel">
            <blockquote>“今晚想吃点认真做的，也想在认真布置过的灯光里坐一会儿。”</blockquote>
            <dl class="story-stats">
              <div>
                <dt>48h</dt>
                <dd>慢炖高汤</dd>
              </div>
              <div>
                <dt>4.9</dt>
                <dd>模板评分占位</dd>
              </div>
              <div>
                <dt>26</dt>
                <dd>木质暖座席</dd>
              </div>
            </dl>
          </aside>
        </div>
      </section>

      <section id="dishes" class="dishes section-shell" data-reveal>
        <div class="section-heading">
          <p class="eyebrow">Signature Dishes</p>
          <h2>招牌菜</h2>
        </div>
        <div class="dish-grid">
          <article v-for="dish in dishes" :key="dish.title" class="dish-card">
            <div :class="dish.mediaClass"></div>
            <div class="dish-copy">
              <p class="dish-tag">{{ dish.tag }}</p>
              <h3>{{ dish.title }}</h3>
              <p>{{ dish.copy }}</p>
            </div>
          </article>
        </div>
      </section>

      <section id="space" class="space section-shell" data-reveal>
        <div class="section-heading">
          <p class="eyebrow">Atmosphere</p>
          <h2>空间环境</h2>
        </div>
        <div class="space-strip" aria-label="环境展示">
          <article class="space-card space-card-wide">
            <span>靠窗长桌 / 适合两人晚餐</span>
          </article>
          <article class="space-card space-card-tall">
            <span>灯光细节 / 木色与亚麻</span>
          </article>
          <article class="space-card space-card-wide alt">
            <span>半开放厨房 / 新鲜出餐感</span>
          </article>
        </div>
      </section>

      <section id="highlights" class="highlights section-shell" data-reveal>
        <div class="section-heading">
          <p class="eyebrow">Why Here</p>
          <h2>用餐亮点</h2>
        </div>
        <div class="highlight-grid">
          <article v-for="item in highlights" :key="item.title" class="highlight-card">
            <h3>{{ item.title }}</h3>
            <p>{{ item.copy }}</p>
          </article>
        </div>
      </section>

      <section id="contact" class="contact section-shell" data-reveal>
        <div class="contact-panel">
          <div class="contact-copy">
            <p class="eyebrow">Visit Us</p>
            <h2>把这一顿饭安排在一个值得慢下来的地方。</h2>
            <dl class="contact-list">
              <div>
                <dt>地址</dt>
                <dd>静安区安和路 118 号 1F（模板占位）</dd>
              </div>
              <div>
                <dt>营业时间</dt>
                <dd>周一至周日 12:00 - 22:00</dd>
              </div>
              <div>
                <dt>电话</dt>
                <dd><a href="tel:400-800-2026">400-800-2026</a></dd>
              </div>
            </dl>
            <div class="hero-actions">
              <a class="button" href="tel:400-800-2026">电话预约</a>
              <a class="button button-ghost" href="#hero">返回顶部</a>
            </div>
          </div>
          <div class="map-card" aria-hidden="true">
            <strong>Map Placeholder</strong>
            <span>这里可替换为真实地图截图、门店外立面或手绘路线图。</span>
          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <p>木舍食堂 Restaurant Template</p>
      <p>页面为静态模板，可直接替换品牌文案与门店素材。</p>
    </footer>
  </div>
</template>
