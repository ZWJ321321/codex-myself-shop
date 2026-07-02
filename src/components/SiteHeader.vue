<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { isScrolled } from '../ui.js';

const route = useRoute();
const navRef = ref(null);

const navItems = [
  { label: '故事', to: '/story' },
  { label: '招牌菜', to: '/dishes' },
  { label: '空间', to: '/space' },
  { label: '到店', to: '/contact' },
];

const isHome = computed(() => route.path === '/');

function syncNav() {
  if (!navRef.value) return;
  navRef.value.classList.toggle('is-scrolled', isScrolled(window.scrollY));
}

onMounted(() => {
  syncNav();
  window.addEventListener('scroll', syncNav, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', syncNav);
});
</script>

<template>
  <header class="site-header">
    <nav ref="navRef" class="site-nav" aria-label="主导航">
      <RouterLink class="brand" to="/">
        <span class="brand-mark">MU</span>
        <span class="brand-copy">
          <strong>木舍食堂</strong>
          <small>Social Bistro Evenings</small>
        </span>
      </RouterLink>

      <div class="nav-links">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
        >
          {{ item.label }}
        </RouterLink>
      </div>

      <RouterLink class="button button-small" to="/ordering">
        {{ isHome ? '在线点餐' : '开始点餐' }}
      </RouterLink>
    </nav>
  </header>
</template>
