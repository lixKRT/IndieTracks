# IndieTracks 部署指南

## 服务器要求

| 组件 | 最低版本 |
|------|---------|
| OS | Ubuntu 22.04+ / CentOS 8+ |
| JDK | 21+ |
| Node.js | 20+ |
| PostgreSQL | 15+ |
| Nginx | 1.22+ |
| MinIO | 最新版 |

## 一键部署（推荐）

### 1. 本地构建

```bash
cd /path/to/IndieTracks
bash scripts/linux/build.sh
```

### 2. 上传到服务器

```bash
# 前端产物
scp -r frontend/dist/* user@server:/opt/indietracks/frontend/dist/

# 后端产物
scp backend/target/backend-0.0.1-SNAPSHOT.jar user@server:/opt/indietracks/backend/

# 配置文件
scp scripts/linux/application-prod.properties user@server:/opt/indietracks/backend/
scp scripts/linux/nginx.conf user@server:/tmp/
scp scripts/linux/indietracks.service user@server:/tmp/
```

### 3. 服务器上执行

```bash
# 安装 Nginx（如果没有）
sudo apt install -y nginx

# 配置 Nginx
sudo cp /tmp/nginx.conf /etc/nginx/sites-available/indietracks.conf
sudo ln -sf /etc/nginx/sites-available/indietracks.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 创建系统用户
sudo useradd -r -s /bin/false indietracks
sudo chown -R indietracks:indietracks /opt/indietracks

# 配置 systemd 服务
sudo cp /tmp/indietracks.service /etc/systemd/system/
# 编辑 /etc/systemd/system/indietracks.service，填写密码等环境变量
sudo systemctl daemon-reload
sudo systemctl enable indietracks
sudo systemctl start indietracks

# 开放防火墙
sudo ufw allow 80/tcp
```

## 环境变量说明

在 `indietracks.service` 中配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `5432` |
| `DB_NAME` | 数据库名 | `indietracks` |
| `DB_USER` | 数据库用户 | `indietracks` |
| `DB_PASS` | 数据库密码 | `your_password` |
| `JWT_SECRET` | JWT 密钥（≥32字符） | `random-string-here...` |
| `MINIO_ENDPOINT` | MinIO 地址 | `http://localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO 用户名 | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO 密码 | `minioadmin` |
| `MINIO_BUCKET` | MinIO 桶名 | `indietracks` |

## 常用命令

```bash
# 查看后端状态
sudo systemctl status indietracks

# 查看实时日志
sudo journalctl -u indietracks -f

# 重启后端
sudo systemctl restart indietracks

# 检查端口
sudo ss -tlnp | grep -E '80|8080'
```

## 访问

部署完成后，浏览器访问 `http://你的服务器IP` 即可。

如果需要 HTTPS，可以用 Let's Encrypt：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```
