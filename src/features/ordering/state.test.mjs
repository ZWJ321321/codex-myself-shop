import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildCreateOrderPayload,
  buildDraftSignature,
  buildPreviewPayload,
  estimateTotalAmount,
  validateOrderDraft,
} from './state.js';
import { createOrder, previewOrder } from './api.js';

test('ordering state builds preview and create payloads from the same draft', () => {
  const form = {
    customerName: '张三',
    phone: '13800138000',
    pickupTime: '2026-07-01T18:30',
    diningMode: 'takeaway',
    note: '少辣',
  };
  const cartItems = [{ dishId: 3, name: '招牌烤鸡', price: '68.00', quantity: 2 }];

  assert.equal(estimateTotalAmount(cartItems), '136.00');
  assert.deepEqual(buildPreviewPayload(form, cartItems), {
    customer_name: '张三',
    phone: '13800138000',
    pickup_time: '2026-07-01T18:30',
    dining_mode: 'takeaway',
    note: '少辣',
    items: [{ dish_id: 3, quantity: 2 }],
  });
  assert.equal(
    buildDraftSignature(form, cartItems),
    JSON.stringify(buildPreviewPayload(form, cartItems))
  );
  assert.deepEqual(buildCreateOrderPayload(form, cartItems, { total_amount: '136.00' }), {
    customer_name: '张三',
    phone: '13800138000',
    pickup_time: '2026-07-01T18:30',
    dining_mode: 'takeaway',
    note: '少辣',
    expected_total_amount: '136.00',
    items: [{ dish_id: 3, quantity: 2 }],
  });
});

test('ordering state rejects empty carts, invalid phones, and past pickup times', () => {
  const errors = validateOrderDraft(
    {
      customerName: '',
      phone: '123',
      pickupTime: '2026-06-30T10:00',
      diningMode: '',
      note: '',
    },
    [],
    new Date('2026-07-01T12:00:00')
  );

  assert.deepEqual(errors, {
    customerName: '请输入姓名',
    phone: '请输入 11 位手机号',
    pickupTime: '取餐时间必须晚于当前时间',
    diningMode: '请选择用餐方式',
    items: '请至少选择一道菜',
  });
});

test('ordering api helpers use the new endpoints and surface structured failures', async () => {
  const originalFetch = globalThis.fetch;

  try {
    globalThis.fetch = async () => ({
      ok: false,
      status: 409,
      text: async () => JSON.stringify({
        code: 'price_changed',
        message: '订单金额已变化，请重新确认',
        data: { total_amount: '138.00', items: [] },
      }),
    });

    await assert.rejects(
      createOrder({ expected_total_amount: '136.00' }),
      (error) => error.code === 'price_changed' && error.data.total_amount === '138.00'
    );

    globalThis.fetch = async (url, options) => ({
      ok: true,
      status: 200,
      text: async () =>
        JSON.stringify({
          code: 'ok',
          message: 'success',
          data: { echo: { url, method: options.method } },
        }),
    });

    const preview = await previewOrder({ customer_name: '张三', items: [] });
    assert.equal(preview.data.echo.url, '/api/order-previews');
    assert.equal(preview.data.echo.method, 'POST');

    globalThis.fetch = async () => {
      throw new Error('network down');
    };

    await assert.rejects(
      previewOrder({ customer_name: '张三', items: [] }),
      (error) =>
        error.message === '确认订单信息失败' &&
        error.code === 'request_failed' &&
        deepEqual(error.errors, {}) &&
        error.data === null
    );

    globalThis.fetch = async () => ({
      ok: true,
      status: 200,
      text: async () => '',
    });

    await assert.rejects(
      createOrder({ expected_total_amount: '136.00' }),
      (error) =>
        error.message === '正式下单失败' &&
        error.code === 'request_failed' &&
        deepEqual(error.errors, {}) &&
        error.data === null
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

function deepEqual(actual, expected) {
  try {
    assert.deepEqual(actual, expected);
    return true;
  } catch {
    return false;
  }
}