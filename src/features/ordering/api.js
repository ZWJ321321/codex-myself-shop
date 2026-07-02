function buildApiError(body, fallbackMessage) {
  const error = new Error(body?.message || fallbackMessage);
  error.code = body?.code || 'request_failed';
  error.errors = body?.errors || {};
  error.data = body?.data || null;
  return error;
}

export async function requestJson(url, options = {}, fallbackMessage = '请求失败') {
  let response;

  try {
    response = await fetch(url, options);
  } catch {
    throw buildApiError(null, fallbackMessage);
  }

  let body = null;
  try {
    const raw = await response.text();
    body = raw.trim() ? JSON.parse(raw) : null;
  } catch {
    body = null;
  }

  if (!response.ok) {
    throw buildApiError(body, fallbackMessage);
  }
  if (!body || typeof body !== 'object') {
    throw buildApiError(null, fallbackMessage);
  }
  return body;
}

export function fetchCategories() {
  return requestJson('/api/categories/', {}, '加载分类失败');
}

export function fetchDishes() {
  return requestJson('/api/dishes/', {}, '加载菜品失败');
}

export function previewOrder(payload) {
  return requestJson(
    '/api/order-previews',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    '确认订单信息失败'
  );
}

export function createOrder(payload) {
  return requestJson(
    '/api/orders',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    '正式下单失败'
  );
}

export function submitOrder(payload) {
  return requestJson(
    '/api/orders',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    '提交订单失败'
  );
}