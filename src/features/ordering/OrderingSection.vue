<script setup>
import { computed, onMounted, reactive, ref } from 'vue';

import OrderPreviewPanel from './OrderPreviewPanel.vue';
import OrderReceiptCard from './OrderReceiptCard.vue';
import { createOrder, fetchCategories, fetchDishes, previewOrder } from './api.js';
import {
  addCartItem,
  buildCreateOrderPayload,
  buildDraftSignature,
  buildPreviewPayload,
  estimateTotalAmount,
  updateCartItemQuantity,
  validateOrderDraft,
} from './state.js';

const ERROR_KEY_MAP = {
  customer_name: 'customerName',
  pickup_time: 'pickupTime',
  dining_mode: 'diningMode',
  expected_total_amount: 'expectedTotalAmount',
};

const stage = ref('editing');
const categories = ref([]);
const dishes = ref([]);
const cartItems = ref([]);
const loading = ref(true);
const loadError = ref('');
const submitMessage = ref('');
const fieldErrors = ref({});
const previewSummary = ref(null);
const previewSignature = ref('');
const receipt = ref(null);

const form = reactive({
  customerName: '',
  phone: '',
  pickupTime: '',
  diningMode: 'takeaway',
  note: '',
});

const estimatedTotal = computed(() => estimateTotalAmount(cartItems.value));
const formLocked = computed(() => stage.value === 'previewing' || stage.value === 'submitting');

function normalizeFieldErrors(errors = {}) {
  const normalized = {};
  for (const [key, value] of Object.entries(errors)) {
    const mappedKey = ERROR_KEY_MAP[key] || key;
    normalized[mappedKey] = Array.isArray(value) ? value[0] : value;
  }
  return normalized;
}

function resetPreviewState() {
  previewSummary.value = null;
  previewSignature.value = '';
}

function moveBackToEditing(message = '订单信息已变更，请重新确认价格。') {
  stage.value = 'editing';
  submitMessage.value = message;
  resetPreviewState();
}

onMounted(async () => {
  try {
    const [categoryResponse, dishResponse] = await Promise.all([fetchCategories(), fetchDishes()]);
    categories.value = categoryResponse.data;
    dishes.value = dishResponse.data;
  } catch (error) {
    loadError.value = error.message || '加载点餐信息失败';
  } finally {
    loading.value = false;
  }
});

function invalidatePreview(message = '订单信息已变更，请重新确认价格。') {
  if (stage.value === 'preview_ready' || stage.value === 'previewing' || stage.value === 'submitting') {
    moveBackToEditing(message);
    return;
  }

  if (stage.value === 'success') {
    stage.value = 'editing';
    submitMessage.value = '';
    receipt.value = null;
    resetPreviewState();
  }
}

function handleAddDish(dish) {
  if (formLocked.value) {
    return;
  }
  cartItems.value = addCartItem(cartItems.value, dish);
  invalidatePreview();
}

function updateQuantity(dishId, quantity) {
  if (formLocked.value) {
    return;
  }
  cartItems.value = updateCartItemQuantity(cartItems.value, dishId, quantity);
  invalidatePreview();
}

function updateField(field, value) {
  if (formLocked.value) {
    return;
  }
  form[field] = value;
  invalidatePreview();
}

async function handlePreview() {
  submitMessage.value = '';
  fieldErrors.value = validateOrderDraft(form, cartItems.value);
  if (Object.keys(fieldErrors.value).length) {
    return;
  }

  const payload = buildPreviewPayload(form, cartItems.value);
  const requestSignature = buildDraftSignature(form, cartItems.value);

  stage.value = 'previewing';
  receipt.value = null;

  try {
    const result = await previewOrder(payload);
    if (buildDraftSignature(form, cartItems.value) !== requestSignature) {
      moveBackToEditing();
      return;
    }

    previewSummary.value = result.data;
    previewSignature.value = requestSignature;
    fieldErrors.value = {};
    stage.value = 'preview_ready';
  } catch (error) {
    stage.value = 'editing';
    fieldErrors.value = normalizeFieldErrors(error.errors);
    submitMessage.value = error.message || '确认订单信息失败';
  }
}

async function handleSubmit() {
  const currentSignature = buildDraftSignature(form, cartItems.value);
  if (currentSignature !== previewSignature.value) {
    moveBackToEditing();
    return;
  }

  const payload = buildCreateOrderPayload(form, cartItems.value, previewSummary.value);
  const submitSignature = currentSignature;

  stage.value = 'submitting';
  try {
    const result = await createOrder(payload);
    if (buildDraftSignature(form, cartItems.value) !== submitSignature) {
      moveBackToEditing();
      return;
    }

    receipt.value = result.data;
    previewSummary.value = result.data;
    previewSignature.value = '';
    fieldErrors.value = {};
    submitMessage.value = '';
    stage.value = 'success';
    cartItems.value = [];
  } catch (error) {
    if (error.code === 'price_changed' && error.data) {
      if (buildDraftSignature(form, cartItems.value) !== submitSignature) {
        moveBackToEditing();
        return;
      }

      previewSummary.value = error.data;
      previewSignature.value = submitSignature;
      fieldErrors.value = {};
      submitMessage.value = error.message || '订单金额已变化，请重新确认';
      stage.value = 'preview_ready';
      return;
    }

    stage.value = 'preview_ready';
    fieldErrors.value = normalizeFieldErrors(error.errors);
    submitMessage.value = error.message || '正式下单失败';
  }
}
</script>

<template>
  <section id="ordering" class="ordering section-shell" data-reveal>
    <div class="section-heading">
      <p class="eyebrow">Online Ordering</p>
      <h2>在线点餐</h2>
    </div>

    <p v-if="loadError" class="ordering-error">{{ loadError }}</p>

    <div v-else class="ordering-grid ordering-grid-rebuilt">
      <div class="ordering-menu-panel">
        <div v-if="categories.length" class="ordering-category-row">
          <span v-for="category in categories" :key="category.id" class="ordering-chip">{{ category.name }}</span>
        </div>

        <p v-if="loading" class="ordering-muted">正在加载菜单...</p>

        <div v-else class="ordering-dish-grid">
          <article v-for="dish in dishes" :key="dish.id" class="ordering-dish-card">
            <div class="ordering-dish-copy">
              <p class="dish-tag">{{ dish.category.name }}</p>
              <h3>{{ dish.name }}</h3>
              <p>{{ dish.description || '当日现做，适合当前页面的即时下单流程。' }}</p>
            </div>
            <div class="ordering-dish-meta">
              <strong>¥{{ dish.price }}</strong>
              <button class="button button-small" type="button" :disabled="formLocked" @click="handleAddDish(dish)">加入订单</button>
            </div>
          </article>
        </div>
      </div>

      <aside class="ordering-sidebar-panel">
        <section class="ordering-panel ordering-draft-panel">
          <div class="ordering-panel-header">
            <p class="ordering-panel-kicker">Draft Order</p>
            <h3>填写订单信息</h3>
          </div>

          <p v-if="fieldErrors.items" class="ordering-error">{{ fieldErrors.items }}</p>

          <div v-for="item in cartItems" :key="item.dishId" class="ordering-cart-row">
            <div>
              <strong>{{ item.name }}</strong>
              <p>¥{{ item.price }}</p>
            </div>
            <div class="ordering-cart-actions">
              <button type="button" :disabled="formLocked" @click="updateQuantity(item.dishId, item.quantity - 1)">-</button>
              <span>{{ item.quantity }}</span>
              <button type="button" :disabled="formLocked" @click="updateQuantity(item.dishId, item.quantity + 1)">+</button>
            </div>
          </div>

          <p v-if="!cartItems.length" class="ordering-muted">还没选菜，先加入一道招牌菜。</p>
          <p class="ordering-total">预计总价：¥{{ estimatedTotal }}</p>

          <div class="ordering-form-grid">
            <label class="ordering-field">
              <span>姓名</span>
              <input :value="form.customerName" class="ordering-input" type="text" :disabled="formLocked" @input="updateField('customerName', $event.target.value)" />
              <small v-if="fieldErrors.customerName" class="ordering-error">{{ fieldErrors.customerName }}</small>
            </label>

            <label class="ordering-field">
              <span>手机号</span>
              <input :value="form.phone" class="ordering-input" type="text" :disabled="formLocked" @input="updateField('phone', $event.target.value)" />
              <small v-if="fieldErrors.phone" class="ordering-error">{{ fieldErrors.phone }}</small>
            </label>

            <label class="ordering-field">
              <span>取餐时间</span>
              <input :value="form.pickupTime" class="ordering-input" type="datetime-local" :disabled="formLocked" @input="updateField('pickupTime', $event.target.value)" />
              <small v-if="fieldErrors.pickupTime" class="ordering-error">{{ fieldErrors.pickupTime }}</small>
            </label>

            <label class="ordering-field">
              <span>用餐方式</span>
              <select :value="form.diningMode" class="ordering-input" :disabled="formLocked" @change="updateField('diningMode', $event.target.value)">
                <option value="takeaway">外带自取</option>
                <option value="dine_in">到店堂食</option>
              </select>
              <small v-if="fieldErrors.diningMode" class="ordering-error">{{ fieldErrors.diningMode }}</small>
            </label>

            <label class="ordering-field ordering-field-full">
              <span>备注</span>
              <textarea :value="form.note" class="ordering-input ordering-textarea" rows="3" :disabled="formLocked" @input="updateField('note', $event.target.value)"></textarea>
            </label>
          </div>

          <p v-if="submitMessage && stage === 'editing'" class="ordering-inline-message">{{ submitMessage }}</p>

          <button class="button" type="button" :disabled="formLocked" @click="handlePreview">
            {{ stage === 'previewing' ? '确认中...' : '确认订单信息' }}
          </button>
        </section>

        <OrderPreviewPanel
          v-if="previewSummary && stage !== 'success'"
          :summary="previewSummary"
          :submitting="stage === 'submitting'"
          :message="submitMessage"
          @submit-order="handleSubmit"
        />

        <OrderReceiptCard v-if="receipt && stage === 'success'" :receipt="receipt" />
      </aside>
    </div>
  </section>
</template>