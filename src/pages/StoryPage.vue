<script setup>
import { RouterLink } from 'vue-router';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();

const storyPoints = [
  { title: '手作感', copy: '菜单和空间都围绕“认真做晚餐”展开，而不是快节奏填饱肚子。', key: 'story-craft' },
  { title: '社交感', copy: '约会、小聚、下班后聊天，都是这套视觉和文案的核心使用场景。', key: 'story-social' },
  { title: '晚间氛围', copy: '标题、光线和配色都优先服务夜间用餐，而不是白天快餐感。', key: 'story-evening' },
  { title: '可替换性', copy: '真实商家接入时，只需替换品牌名、门店信息与真实图片资产。', key: 'story-adapt' },
];
</script>

<template>
  <div class="page-stack story-page">
    <section class="page-hero page-hero-compact section-shell" data-reveal>
      <p class="page-kicker">Brand Story</p>
      <h1 class="page-title">把这顿饭的情绪先布置好，再把菜端上来。</h1>
      <p class="page-summary">
        故事页不再混在首页中段，而是独立承担品牌态度表达，让“为什么值得来”比“这里有什么”更先成立。
      </p>
    </section>

    <section class="section-shell page-section story-grid" data-reveal>
      <article class="panel-card story-quote">
        <p class="quote-mark">“</p>
        <blockquote>
          今晚想吃点认真做的，也想在认真布置过的灯光里坐一会儿。
        </blockquote>
        <RouterLink class="inline-link" to="/dishes">继续看招牌菜</RouterLink>
      </article>

      <article class="panel-card story-copy-card">
        <p>
          原来的单页结构把品牌、菜品、空间和联系信息全部压在一张页面里。现在故事页独立出来，负责解释这家店的语气、节奏和适合谁来。
        </p>
        <p>
          这里的文案不追求百科全书式介绍，而是用更少的话把餐厅最值得记住的感受固定下来。
        </p>
      </article>
    </section>

    <section class="section-shell page-section" data-reveal>
      <div class="stat-grid">
        <article v-for="item in storyPoints" :key="item.key" class="panel-card stat-card">
          <h3>{{ item.title }}</h3>
          <p>{{ item.copy }}</p>
        </article>
      </div>
    </section>
  </div>
</template>
