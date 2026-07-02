<script setup>
import roastedChicken from '../assets/generated/dish-roasted-chicken.png';
import braisedBeef from '../assets/generated/dish-braised-beef.png';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();

const dishes = [
  {
    title: '炙烤南瓜奶油鸡腿排',
    tag: 'Chef Pick',
    copy: '适合第一次来时下单，质地、颜色和份量都很容易成为这家店的第一记忆点。',
    image: roastedChicken,
  },
  {
    title: '慢炖番茄牛肉锅',
    tag: 'Most Shared',
    copy: '更适合两人或小聚场景，强调热度、汤感和慢慢吃的节奏。',
    image: braisedBeef,
  },
  {
    title: '甜点与饮品组合位',
    tag: 'Next Asset',
    copy: '首版先保留第三张卡位，后续优先补一张甜点或饮品图，丰富页面完成度。',
    image: '',
  },
];
</script>

<template>
  <div class="page-stack dishes-page">
    <section class="page-hero page-hero-compact section-shell" data-reveal>
      <p class="page-kicker">Signature Dishes</p>
      <h1 class="page-title">菜单页负责让人产生“这道我今晚想点”的冲动。</h1>
      <p class="page-summary">
        菜品页用更大的图和更短的推荐理由承接转化，不再只是首页里的三张均匀占位卡。
      </p>
    </section>

    <section class="section-shell page-section" data-reveal>
      <div class="dish-grid-page">
        <article v-for="dish in dishes" :key="dish.title" class="dish-page-card">
          <div class="dish-page-media" :class="{ 'dish-page-placeholder': !dish.image }">
            <img v-if="dish.image" :src="dish.image" :alt="dish.title" />
            <div v-else class="placeholder-copy">
              <span>第三张图待补</span>
            </div>
          </div>
          <div class="dish-page-copy">
            <p class="dish-tag">{{ dish.tag }}</p>
            <h3>{{ dish.title }}</h3>
            <p>{{ dish.copy }}</p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
