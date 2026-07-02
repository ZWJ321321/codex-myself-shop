import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import StoryPage from './pages/StoryPage.vue';
import DishesPage from './pages/DishesPage.vue';
import SpacePage from './pages/SpacePage.vue';
import ContactPage from './pages/ContactPage.vue';
import OrderingPage from './pages/OrderingPage.vue';

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/story', name: 'story', component: StoryPage },
  { path: '/dishes', name: 'dishes', component: DishesPage },
  { path: '/space', name: 'space', component: SpacePage },
  { path: '/contact', name: 'contact', component: ContactPage },
  { path: '/ordering', name: 'ordering', component: OrderingPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' };
  },
});

export default router;
