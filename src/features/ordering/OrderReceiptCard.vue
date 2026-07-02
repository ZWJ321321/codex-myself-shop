<script setup>
const props = defineProps({
  receipt: { type: Object, required: true },
});
</script>

<template>
  <section class="ordering-panel ordering-receipt-card">
    <div class="ordering-panel-header">
      <p class="ordering-panel-kicker">Order Created</p>
      <h3>订单回执</h3>
    </div>

    <dl class="ordering-preview-meta">
      <div><dt>订单号</dt><dd>{{ props.receipt.order_no }}</dd></div>
      <div><dt>联系人</dt><dd>{{ props.receipt.customer_name }}</dd></div>
      <div><dt>手机号</dt><dd>{{ props.receipt.phone }}</dd></div>
      <div><dt>取餐时间</dt><dd>{{ props.receipt.pickup_time }}</dd></div>
      <div><dt>用餐方式</dt><dd>{{ props.receipt.dining_mode === 'takeaway' ? '外带自取' : '到店堂食' }}</dd></div>
    </dl>

    <div v-for="item in props.receipt.items" :key="item.dish_id" class="ordering-preview-row">
      <div>
        <strong>{{ item.dish_name }}</strong>
        <p>¥{{ item.unit_price }} x {{ item.quantity }}</p>
      </div>
      <strong>¥{{ item.line_total }}</strong>
    </div>

    <p class="ordering-preview-total">最终总价：¥{{ props.receipt.total_amount }}</p>
    <p v-if="props.receipt.note" class="ordering-preview-note">备注：{{ props.receipt.note }}</p>
  </section>
</template>