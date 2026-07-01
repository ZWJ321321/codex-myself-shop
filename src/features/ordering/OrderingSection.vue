<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { fetchCategories, fetchDishes, submitOrder } from './api.js';
import { addCartItem, buildOrderPayload, updateCartItemQuantity, validateOrderDraft } from './state.js';

const categories = ref([]);
const dishes = ref([]);
const cartItems = ref([]);
const loading = ref(true);
const loadError = ref('');
const submitError = ref('');
const fieldErrors = ref({});
const submitState = reactive({
  loading: false,
  orderNo: '',
});
const form = reactive({
  customerName: '',
  phone: '',
  note: '',
});

const totalAmount = computed(() =>
  cartItems.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0).toFixed(2)
);

onMounted(async () => {
  try {
    const [categoryResponse, dishResponse] = await Promise.all([fetchCategories(), fetchDishes()]);
    categories.value = categoryResponse.data;
    dishes.value = dishResponse.data;
  } catch (error) {
    loadError.value = error.message || '加载点菜信息失败';
  } finally {
    loading.value = false;
  }
});

function handleAddDish(dish) {
  cartItems.value = addCartItem(cartItems.value, dish);
}

function changeQuantity(dishId, quantity) {
  cartItems.value = updateCartItemQuantity(cartItems.value, dishId, quantity);
}

async function handleSubmit() {
  submitError.value = '';
  fieldErrors.value = validateOrderDraft(form, cartItems.value);
  if (Object.keys(fieldErrors.value).length) return;

  submitState.loading = true;
  try {
    const result = await submitOrder(buildOrderPayload(form, cartItems.value));
    submitState.orderNo = result.data.order_no;
    cartItems.value = [];
    form.customerName = '';
    form.phone = '';
    form.note = '';
  } catch (error) {
    fieldErrors.value = error.errors || {};
    submitError.value = error.message || '提交订单失败';
  } finally {
    submitState.loading = false;
  }
}
</script>

<template>
  <section id="ordering" class="ordering section-shell" data-reveal>
    <div class="section-heading">
      <p class="eyebrow">Online Ordering</p>
      <h2>在线点菜</h2>
    </div>

    <p v-if="loadError" class="ordering-error">{{ loadError }}</p>

    <div v-else class="ordering-grid">
      <div class="ordering-menu-panel">
        <div class="ordering-category-row" v-if="categories.length">
          <span v-for="category in categories" :key="category.id" class="ordering-chip">
            {{ category.name }}
          </span>
        </div>

        <p v-if="loading" class="ordering-muted">正在加载菜单...</p>

        <div v-else class="ordering-dish-grid">
          <article v-for="dish in dishes" :key="dish.id" class="ordering-dish-card">
            <div class="ordering-dish-copy">
              <p class="dish-tag">{{ dish.category.name }}</p>
              <h3>{{ dish.name }}</h3>
              <p>{{ dish.description || '当日现做，适合当前页面的轻量点单演示。' }}</p>
            </div>
            <div class="ordering-dish-meta">
              <strong>￥{{ dish.price }}</strong>
              <button class="button button-small" type="button" @click="handleAddDish(dish)">
                加入购物车
              </button>
            </div>
          </article>
        </div>
      </div>

      <aside class="ordering-cart-panel">
        <div class="ordering-cart-header">
          <h3>购物车</h3>
          <p>同页提交订单，不跳转新页面。</p>
        </div>

        <p v-if="fieldErrors.items" class="ordering-error">{{ fieldErrors.items }}</p>
        <p v-else-if="!cartItems.length" class="ordering-muted">还没选菜，先从左侧加一道招牌菜。</p>

        <div v-for="item in cartItems" :key="item.dishId" class="ordering-cart-row">
          <div>
            <strong>{{ item.name }}</strong>
            <p>￥{{ item.price }}</p>
          </div>
          <div class="ordering-cart-actions">
            <button type="button" @click="changeQuantity(item.dishId, item.quantity - 1)">-</button>
            <span>{{ item.quantity }}</span>
            <button type="button" @click="changeQuantity(item.dishId, item.quantity + 1)">+</button>
          </div>
        </div>

        <p class="ordering-total">合计：￥{{ totalAmount }}</p>

        <div class="ordering-form">
          <label class="ordering-field">
            <span>姓名</span>
            <input v-model="form.customerName" class="ordering-input" type="text" placeholder="请输入姓名" />
            <small v-if="fieldErrors.customerName" class="ordering-error">{{ fieldErrors.customerName }}</small>
          </label>

          <label class="ordering-field">
            <span>手机号</span>
            <input v-model="form.phone" class="ordering-input" type="text" placeholder="请输入手机号" />
            <small v-if="fieldErrors.phone" class="ordering-error">{{ fieldErrors.phone }}</small>
          </label>

          <label class="ordering-field">
            <span>备注</span>
            <textarea v-model="form.note" class="ordering-input ordering-textarea" rows="3" placeholder="口味、忌口、其他说明"></textarea>
          </label>

          <p v-if="submitError" class="ordering-error">{{ submitError }}</p>

          <button class="button" type="button" :disabled="submitState.loading" @click="handleSubmit">
            {{ submitState.loading ? '提交中...' : '提交订单' }}
          </button>

          <p v-if="submitState.orderNo" class="order-success">
            订单已提交，订单号 {{ submitState.orderNo }}
          </p>
        </div>
      </aside>
    </div>
  </section>
</template>
