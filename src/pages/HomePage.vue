<script setup>
import { RouterLink } from 'vue-router';
import heroImage from '../assets/generated/hero-social-bistro.png';
import dishImage from '../assets/generated/dish-roasted-chicken.png';
import spaceImage from '../assets/generated/space-window-seating.png';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();

const highlights = [
  {
    title: '先看氛围，再决定今晚去哪',
    copy: '首页只负责把人带进状态，用一张主视觉和三张入口卡片完成分流。',
    to: '/story',
    image: heroImage,
  },
  {
    title: '招牌菜是最强转化内容',
    copy: '把适合分享、适合约会、适合下班后放松的菜品理由讲清楚。',
    to: '/dishes',
    image: dishImage,
  },
  {
    title: '空间要让人想拍，也想坐下来',
    copy: '空间页不再只是占位图区，而是品牌气质的一部分。',
    to: '/space',
    image: spaceImage,
  },
];
</script>

<template>
  <div class="page-stack home-page">
    <section class="page-hero section-shell" data-reveal>
      <div class="page-hero-grid">
        <div>
          <p class="page-kicker">Young Social Bistro</p>
          <h1 class="page-title">今晚想吃得认真一点，也想坐得久一点。</h1>
          <p class="page-summary">
            木舍食堂把单页模板重组为真正的品牌站：首页只负责制造晚餐冲动，其余页面分别承接故事、菜品、空间和到店决策。
          </p>
          <div class="page-actions">
            <RouterLink class="button" to="/ordering">在线点餐</RouterLink>
            <RouterLink class="button button-ghost" to="/dishes">先看招牌菜</RouterLink>
          </div>
          <ul class="note-pills">
            <li>适合两人晚餐</li>
            <li>适合下班后小聚</li>
            <li>适合边吃边聊天</li>
          </ul>
        </div>

        <div class="hero-visual-card">
          <img class="hero-image" :src="heroImage" alt="木舍食堂首页主视觉" />
          <div class="floating-badge">
            <strong>12:00 - 22:00</strong>
            <span>从晚餐前热身到夜间小聚都合适</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-shell page-section" data-reveal>
      <div class="section-heading-row">
        <div>
          <p class="page-kicker">Quick Routes</p>
          <h2 class="section-title">别再整页往下翻，直接去你真正关心的那一页。</h2>
        </div>
        <RouterLink class="inline-link" to="/contact">先看怎么到店</RouterLink>
      </div>

      <div class="feature-grid">
        <RouterLink
          v-for="item in highlights"
          :key="item.to"
          :to="item.to"
          class="feature-card"
        >
          <div class="feature-art">
            <img :src="item.image" :alt="item.title" />
          </div>
          <div class="feature-content">
            <h3>{{ item.title }}</h3>
            <p>{{ item.copy }}</p>
            <span>进入页面</span>
          </div>
        </RouterLink>
      </div>
    </section>

    <section class="section-shell spotlight-grid" data-reveal>
      <article class="panel-card spotlight-copy">
        <p class="page-kicker">Brand Positioning</p>
        <h2 class="section-title">不是“菜很多”的模板页，而是“今晚想去”的品牌入口。</h2>
        <p>
          页面把导航拆成独立根页面后，信息密度不再挤在同一张长页面里。首页负责冲动，内页负责解释，点餐页负责成交。
        </p>
      </article>
      <article class="panel-card action-tile">
        <p class="page-kicker">Next Move</p>
        <h3>准备直接下单？</h3>
        <p>点餐页保留原有业务逻辑，但从品牌内容中独立出来，减少浏览和交易互相干扰。</p>
        <RouterLink class="button button-small" to="/ordering">去点餐页</RouterLink>
      </article>
    </section>
  </div>
</template>
