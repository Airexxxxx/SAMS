# SAMS - 服务器资产管理系统

Server Asset Management System — 企业级服务器资产全生命周期管理平台。

## 技术栈

- Python 3.12+
- Streamlit 1.57+
- SQLite (WAL 模式)
- pandas / openpyxl
- Docker

---

## 部署方式

### 方式一：Docker Compose（推荐）

任意安装 Docker 的服务器即可运行，无需安装 Python 环境。

```bash
# 1. 拷贝项目到服务器
cd /path/to/SAMS

# 2. 构建并启动
docker compose up -d

# 3. 浏览器打开 http://<服务器IP>:8501
# 4. 默认账号: admin / admin123
```

**常用命令：**

```bash
docker compose up -d          # 后台启动
docker compose down           # 停止
docker compose restart        # 重启
docker compose logs -f        # 查看日志
docker compose up -d --build  # 重新构建并启动
```

---

### 方式二：Docker 直接运行

构建完成后可直接 `docker run`，适合单容器场景。

```bash
# 构建镜像
docker build -t sams:latest .

# 运行（数据存当前目录）
docker run -d \
  --name sams \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  sams:latest

# 浏览器打开 http://<服务器IP>:8501
```

---

### 方式三：镜像导出/导入

构建一次，导出为文件分发到其他服务器，无需每台重新构建。

```bash
# 导出镜像为文件（约 180MB）
docker save sams:latest | gzip > sams_latest.tar.gz

# 拷贝到目标服务器后导入
docker load < sams_latest.tar.gz

# 然后正常运行
docker run -d --name sams -p 8501:8501 -v $(pwd)/data:/app/data sams:latest
```

---

### 方式四：手动部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动（默认端口 8501）
streamlit run sams.py --server.port 8501 --server.address 0.0.0.0

# 3. 浏览器打开 http://<服务器IP>:8501
# 4. 默认账号: admin / admin123
```

**后台运行：**

```bash
nohup streamlit run sams.py --server.port 8501 --server.address 0.0.0.0 > sams.log 2>&1 &
```

---

### 方式三：开发模式

```bash
pip install streamlit pandas openpyxl
cd /path/to/SAMS
streamlit run sams.py
```

---

## 数据备份与恢复

Docker 环境下的数据库备份：

```bash
# 导出数据库
docker cp sams:/app/data/sams.db ./sams_backup_$(date +%Y%m%d).db

# 导入数据库（覆盖当前数据）
docker cp ./sams_backup.db sams:/app/data/sams.db
docker restart sams
```

非 Docker 环境下直接复制 `sams.db` 文件即可。

---

## 系统功能

| 模块 | 功能 |
|------|------|
| **仪表盘** | 资产数量统计卡片、状态分布图、系统/运行方式/业务线图表 |
| **资产列表** | 分页表格(20条/页)、搜索、4维度筛选、多选批量删除、点击查看详情 |
| **新增/编辑** | 23字段双列表单、IP校验、编辑时自动预填 |
| **批量导入** | xlsx/csv 上传、中英文列名自动识别、按内网IP UPSERT |
| **导出资产** | 按业务线/状态筛选导出 xlsx（不导出系统密码） |
| **模板下载** | 空白模板 + 含12条示例数据的测试模板 |
| **统计分析** | 业务线/系统类型/运行方式图表 |
| **用户管理** | 管理员可添加用户 |
| **数据备份/恢复** | 一键备份 + 上传恢复，恢复前自动备份当前数据 |

---

## 模板字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| 主机名 | 是 | 服务器 hostname |
| 内网IP | 是 | 唯一标识，用作 UPSERT 键 |
| 公网IP | 否 | |
| 系统密码 | 否 | root/Administrator 密码，详情页 `********` 隐藏，导出不包含 |
| 应用密码 | 否 | 格式 `应用名:用户名:密码`，每行一条。如 `MySQL:root:pass123` |
| 操作系统 | 否 | Linux/Windows/macOS/Other |
| 系统版本 | 否 | 如 Ubuntu 22.04 |
| 内核版本 | 否 | 如 5.15.0-91-generic |
| CPU(核) | 否 | 整数 |
| 内存(GB) | 否 | 整数 |
| 磁盘信息 | 否 | |
| 位置 | 否 | 机房/机柜位置 |
| 业务线 | 否 | |
| 负责人 | 否 | |
| 状态 | 否 | running/stopped/maintenance/decommissioned |
| 采购日期 | 否 | YYYY-MM-DD |
| 保修截止 | 否 | YYYY-MM-DD |
| 业务服务 | 否 | |
| 应用框架 | 否 | |
| 数据库 | 否 | |
| 运行方式 | 否 | physical/vm/docker/k8s/other |
| 运行详情 | 否 | |
| 端口信息 | 否 | |
| 备注 | 否 | |

---

## 项目结构

```
SAMS/
  sams.py                    # 主程序（单文件）
  Dockerfile                 # Docker 镜像
  docker-compose.yml         # Docker Compose 编排
  requirements.txt           # Python 依赖
  .dockerignore              # Docker 忽略文件
  .streamlit/
    config.toml               # Streamlit 暗黑主题配置
  sams.db                    # SQLite 数据库（自动创建）
  README.md
```

---

## 安全设计

- 密码 SHA256 哈希存储
- 参数化查询防 SQL 注入
- 系统密码/应用密码详情中以 `********` 掩码显示
- 系统密码导出排除
- Session 状态管理
- 删除操作二次确认
- SQLite WAL 模式

## 性能优化

- SQLite WAL 模式
- 分页查询 (20条/页)
- `@st.cache_data` 缓存统计结果 (60s TTL)
- `@st.cache_resource` 复用数据库连接
- 详情延迟加载（点击后才查询）
