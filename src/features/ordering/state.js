const DINING_MODES = new Set(['takeaway', 'dine_in']);
const PHONE_RE = /^1\d{10}$/;

function trimText(value) {
  if (value == null) {
    return '';
  }
  return String(value).trim();
}

function hasOwn(form, field) {
  return Object.prototype.hasOwnProperty.call(form, field);
}

function toPickupDate(value) {
  if (!value) {
    return null;
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function buildItemsPayload(cartItems) {
  return cartItems.map((item) => ({ dish_id: item.dishId, quantity: item.quantity }));
}

export function addCartItem(cartItems, dish) {
  const existing = cartItems.find((item) => item.dishId === dish.id);
  if (!existing) {
    return [...cartItems, { dishId: dish.id, name: dish.name, price: dish.price, quantity: 1 }];
  }
  return cartItems.map((item) =>
    item.dishId === dish.id ? { ...item, quantity: item.quantity + 1 } : item
  );
}

export function updateCartItemQuantity(cartItems, dishId, quantity) {
  if (quantity <= 0) {
    return cartItems.filter((item) => item.dishId !== dishId);
  }
  return cartItems.map((item) => (item.dishId === dishId ? { ...item, quantity } : item));
}

export function estimateTotalAmount(cartItems) {
  return cartItems
    .reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
    .toFixed(2);
}

export function validateOrderDraft(form, cartItems, now = new Date()) {
  const errors = {};
  const customerName = trimText(form.customerName);
  const phone = trimText(form.phone);

  if (!customerName) {
    errors.customerName = '请输入姓名';
  }
  if (!PHONE_RE.test(phone)) {
    errors.phone = '请输入 11 位手机号';
  }
  if (!cartItems.length) {
    errors.items = '请至少选择一道菜';
  }

  if (hasOwn(form, 'pickupTime')) {
    const pickupTime = trimText(form.pickupTime);
    if (!pickupTime) {
      errors.pickupTime = '请选择取餐时间';
    } else {
      const pickupDate = toPickupDate(pickupTime);
      if (!pickupDate) {
        errors.pickupTime = '请选择有效的取餐时间';
      } else if (pickupDate <= now) {
        errors.pickupTime = '取餐时间必须晚于当前时间';
      }
    }
  }

  if (hasOwn(form, 'diningMode')) {
    const diningMode = trimText(form.diningMode);
    if (!DINING_MODES.has(diningMode)) {
      errors.diningMode = '请选择用餐方式';
    }
  }

  return errors;
}

export function buildPreviewPayload(form, cartItems) {
  return {
    customer_name: trimText(form.customerName),
    phone: trimText(form.phone),
    pickup_time: trimText(form.pickupTime),
    dining_mode: trimText(form.diningMode),
    note: trimText(form.note),
    items: buildItemsPayload(cartItems),
  };
}

export function buildCreateOrderPayload(form, cartItems, summary) {
  return {
    ...buildPreviewPayload(form, cartItems),
    expected_total_amount: summary?.total_amount || '',
  };
}

export function buildDraftSignature(form, cartItems) {
  return JSON.stringify(buildPreviewPayload(form, cartItems));
}

export function buildOrderPayload(form, cartItems) {
  return {
    customer_name: trimText(form.customerName),
    phone: trimText(form.phone),
    note: trimText(form.note),
    items: buildItemsPayload(cartItems),
  };
}