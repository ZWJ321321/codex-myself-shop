# Ubuntu 部署说明

本项目由两部分组成：

- 前端：`Vue 3 + Vite`，生产产物在 `dist/`
- 后端：`Django + MySQL`，接口路径为 `/api/`

推荐部署结构：

- `Nginx` 提供前端静态资源
- `Gunicorn` 运行 Django，监听 `127.0.0.1:8000`
- `Nginx` 反向代理 `/api/` 到 Django
- `MySQL` 存储菜品和订单数据

## 1. 准备服务器

以下命令基于 Ubuntu 24.04 或相近版本：

```bash
sudo apt update
sudo apt install -y nginx mysql-server python3-venv python3-pip
```

安装 Node.js LTS。推荐使用 NodeSource 或 `nvm`，确保服务器上的 `node` 和 `npm` 可用。

## 2. 上传项目

建议部署目录：

```bash
sudo mkdir -p /srv/restaurant-intro
sudo chown -R $USER:$USER /srv/restaurant-intro
```

然后将仓库代码上传到：

```text
/srv/restaurant-intro
```

## 3. 构建前端

在项目根目录执行：

```bash
cd /srv/restaurant-intro
npm ci
npm run build
```

构建后页面文件位于：

```text
/srv/restaurant-intro/dist
```

## 4. 创建 MySQL 数据库

进入 MySQL：

```bash
sudo mysql
```

执行：

```sql
CREATE DATABASE restaurant_ordering CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'restaurant_app'@'127.0.0.1' IDENTIFIED BY 'replace-with-a-strong-password';
GRANT ALL PRIVILEGES ON restaurant_ordering.* TO 'restaurant_app'@'127.0.0.1';
FLUSH PRIVILEGES;
```

## 5. 配置 Django 环境变量

服务器上创建环境文件：

```bash
sudo cp /srv/restaurant-intro/backend/.env.example /etc/restaurant-intro.env
sudo nano /etc/restaurant-intro.env
```

至少要改这些值：

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `MYSQL_PASSWORD`

说明：

- `DJANGO_ALLOWED_HOSTS` 填你的域名和服务器 IP，例如 `example.com,www.example.com,203.0.113.10`
- `DJANGO_CSRF_TRUSTED_ORIGINS` 要带协议，例如 `https://example.com,https://www.example.com`
- 如果暂时只用 IP 访问，可以填 `http://203.0.113.10`

## 6. 安装并初始化 Django

```bash
cd /srv/restaurant-intro/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
set -a
source /etc/restaurant-intro.env
set +a
python manage.py migrate
python manage.py ensure_catalog_demo
python manage.py collectstatic --noinput
```

如果需要创建后台管理员：

```bash
python manage.py createsuperuser
```

## 7. 配置 systemd 启动 Django

复制模板：

```bash
sudo cp /srv/restaurant-intro/deploy/ubuntu/restaurant-backend.service /etc/systemd/system/restaurant-backend.service
```

确认模板里的 `WorkingDirectory` 和 `ExecStart` 与实际部署目录一致，然后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now restaurant-backend
sudo systemctl status restaurant-backend
```

查看日志：

```bash
sudo journalctl -u restaurant-backend -f
```

## 8. 配置 Nginx

复制模板：

```bash
sudo cp /srv/restaurant-intro/deploy/ubuntu/restaurant-intro.nginx.conf /etc/nginx/sites-available/restaurant-intro
```

编辑 `server_name` 为你的域名，然后启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/restaurant-intro /etc/nginx/sites-enabled/restaurant-intro
sudo nginx -t
sudo systemctl reload nginx
```

说明：

- 该配置已经包含 `try_files ... /index.html;`，这是给 Vue Router `createWebHistory()` 用的
- 该配置会把 `/api/` 转发到 `127.0.0.1:8000`
- Django admin 的静态资源由 `/static/` 指向 `backend/staticfiles/`

## 9. 配置 HTTPS

如果使用域名，建议立即配置 HTTPS：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

## 10. 上线后检查

建议依次检查：

```bash
curl -I http://127.0.0.1:8000/admin/
curl -I http://your-domain/
curl http://your-domain/api/categories/
```

浏览器里再检查：

- 首页是否正常加载
- 路由 `/story`、`/dishes`、`/ordering` 刷新后是否仍能打开
- 点餐页是否能正常加载分类和菜品
- 提交订单后接口是否返回成功
- Django 后台 `/admin/` 样式是否正常

## 11. 更新发布

后续代码更新常用流程：

```bash
cd /srv/restaurant-intro
git pull
npm ci
npm run build
cd backend
source .venv/bin/activate
pip install -r requirements.txt
set -a
source /etc/restaurant-intro.env
set +a
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart restaurant-backend
sudo systemctl reload nginx
```

## 当前仓库内相关文件

- 环境变量示例：`backend/.env.example`
- systemd 模板：`deploy/ubuntu/restaurant-backend.service`
- Nginx 模板：`deploy/ubuntu/restaurant-intro.nginx.conf`
