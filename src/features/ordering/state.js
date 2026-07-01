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

export function validateOrderDraft(form, cartItems) {
  const errors = {};
  if (!form.customerName.trim()) errors.customerName = '请输入姓名';
  if (!form.phone.trim()) errors.phone = '请输入手机号';
  if (!cartItems.length) errors.items = '请至少选择一道菜';
  return errors;
}

export function buildOrderPayload(form, cartItems) {
  return {
    customer_name: form.customerName.trim(),
    phone: form.phone.trim(),
    note: form.note.trim(),
    items: cartItems.map((item) => ({ dish_id: item.dishId, quantity: item.quantity })),
  };
}
