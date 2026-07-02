<script setup>
import { RouterLink } from 'vue-router';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();
</script>

<template>
  <div class="page-stack contact-page">
    <section class="page-hero page-hero-compact section-shell" data-reveal>
      <p class="page-kicker">Visit Us</p>
      <h1 class="page-title">把今晚这顿饭，安排在一个值得慢下来的地方。</h1>
      <p class="page-summary">
        到店页只处理行动信息：地址、时间、预约和路线，不再跟品牌叙事混在同一屏里争注意力。
      </p>
    </section>

    <section class="section-shell page-section contact-layout" data-reveal>
      <article class="panel-card contact-detail-card">
        <dl class="contact-list-grid">
          <div>
            <dt>地址</dt>
            <dd>静安区安和路 118 号 1F（示例地址）</dd>
          </div>
          <div>
            <dt>营业时间</dt>
            <dd>周一至周日 12:00 - 22:00</dd>
          </div>
          <div>
            <dt>电话</dt>
            <dd><a href="tel:400-800-2026">400-800-2026</a></dd>
          </div>
          <div>
            <dt>建议到店时间</dt>
            <dd>19:00 - 20:30 更有晚餐氛围，适合双人和小聚。</dd>
          </div>
        </dl>
        <div class="page-actions">
          <a class="button" href="tel:400-800-2026">电话预约</a>
          <RouterLink class="button button-ghost" to="/ordering">也可以先点餐</RouterLink>
        </div>
      </article>

      <article class="panel-card map-card-static">
        <strong>Map Placeholder</strong>
        <span>后续优先补门店外立面或地图截屏图，首版先保留到店信息结构。</span>
      </article>
    </section>
  </div>
</template>
