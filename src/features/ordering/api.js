export async function fetchCategories() {
  const response = await fetch('/api/categories/');
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.message || '加载分类失败');
  }
  return body;
}

export async function fetchDishes() {
  const response = await fetch('/api/dishes/');
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.message || '加载菜品失败');
  }
  return body;
}

export async function submitOrder(payload) {
  const response = await fetch('/api/orders/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const body = await response.json();
  if (!response.ok) {
    throw body;
  }
  return body;
}
