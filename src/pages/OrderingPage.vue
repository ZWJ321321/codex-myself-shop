<script setup>
import OrderingSection from '../features/ordering/OrderingSection.vue';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();
</script>

<template>
  <div class="page-stack ordering-page-shell">
    <section class="page-hero page-hero-compact section-shell" data-reveal>
      <p class="page-kicker">Online Ordering</p>
      <h1 class="page-title">先确认价格，再正式下单。</h1>
      <p class="page-summary">
        这个页面把实时选菜、联系人填写、后端确认金额和订单回执合成一个完整流程，不再沿用旧版直接提交表单。
      </p>
    </section>

    <OrderingSection />
  </div>
</template>