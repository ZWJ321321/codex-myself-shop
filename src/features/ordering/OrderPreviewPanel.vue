<script setup>
const props = defineProps({
  summary: { type: Object, required: true },
  submitting: { type: Boolean, default: false },
  message: { type: String, default: '' },
});

const emit = defineEmits(['submit-order']);
</script>

<template>
  <section class="ordering-panel ordering-preview-panel">
    <div class="ordering-panel-header">
      <p class="ordering-panel-kicker">Confirmed by Server</p>
      <h3>确认订单信息</h3>
    </div>
    <p class="ordering-preview-copy">以下价格以后端最新菜单复算结果为准。</p>

    <div v-for="item in props.summary.items" :key="item.dish_id" class="ordering-preview-row">
      <div>
        <strong>{{ item.dish_name }}</strong>
        <p>¥{{ item.unit_price }} x {{ item.quantity }}</p>
      </div>
      <strong>¥{{ item.line_total }}</strong>
    </div>

    <dl class="ordering-preview-meta">
      <div><dt>联系人</dt><dd>{{ props.summary.customer_name }}</dd></div>
      <div><dt>手机号</dt><dd>{{ props.summary.phone }}</dd></div>
      <div><dt>取餐时间</dt><dd>{{ props.summary.pickup_time }}</dd></div>
      <div><dt>用餐方式</dt><dd>{{ props.summary.dining_mode === 'takeaway' ? '外带自取' : '到店堂食' }}</dd></div>
    </dl>

    <p v-if="props.summary.note" class="ordering-preview-note">备注：{{ props.summary.note }}</p>
    <p class="ordering-preview-total">确认总价：¥{{ props.summary.total_amount }}</p>
    <p v-if="props.message" class="ordering-inline-message">{{ props.message }}</p>

    <button class="button" type="button" :disabled="props.submitting" @click="emit('submit-order')">
      {{ props.submitting ? '正式下单中...' : '正式下单' }}
    </button>
  </section>
</template>