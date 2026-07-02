<script setup>
import spaceImage from '../assets/generated/space-window-seating.png';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();

const spaces = [
  {
    title: '窗边座位',
    copy: '适合双人晚餐、轻约会和下班后慢一点的聊天。',
  },
  {
    title: '多人小聚区',
    copy: '更强调桌距和轻社交氛围，适合三到四人的晚间聚餐。',
  },
  {
    title: '开放感餐区',
    copy: '让料理热度和空间节奏在视线上联通，增强现场感。',
  },
];
</script>

<template>
  <div class="page-stack space-page">
    <section class="page-hero section-shell" data-reveal>
      <div class="page-hero-grid page-hero-grid-reverse">
        <div class="hero-visual-card">
          <img class="hero-image" :src="spaceImage" alt="木舍食堂空间环境图" />
        </div>
        <div>
          <p class="page-kicker">Atmosphere</p>
          <h1 class="page-title">让人想坐下来，而不是匆匆吃完离开。</h1>
          <p class="page-summary">
            空间页从原来的横向滚动图片区，改成独立的场景介绍页，用一张主图和三块分区说明强调“适合来这里待一会儿”。
          </p>
        </div>
      </div>
    </section>

    <section class="section-shell page-section" data-reveal>
      <div class="space-feature-grid">
        <article class="panel-card space-feature-lead">
          <h2 class="section-title">木质、暖光、留白和桌距，决定了这里更像一场晚餐，而不是一笔订单。</h2>
          <p>
            多页面结构下，空间不再只是品牌说明的附属图，而是独立承担“让人愿意到店”的任务。
          </p>
        </article>
        <div class="space-list">
          <article v-for="item in spaces" :key="item.title" class="panel-card stat-card">
            <h3>{{ item.title }}</h3>
            <p>{{ item.copy }}</p>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>
