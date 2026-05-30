# SAMS — 服务器资产管理系统

Server Asset Management System，企业级服务器资产全生命周期管理平台。

## 技术栈

- Python 3.11+/Python 3.12+
- Streamlit 1.57+
- SQLite (WAL 模式)
- pandas / openpyxl
- cryptography (Fernet 对称加密)
- Docker

---

## 快速部署

### Docker Compose（推荐）

```bash
cd /path/to/SAMS
docker compose up -d
# 浏览器打开 http://<服务器IP>:8501
# 默认账号: admin / admin123
```

常用命令：

```bash
docker compose up -d              # 后台启动
docker compose down               # 停止
docker compose restart            # 重启
docker compose logs -f            # 查看日志
docker compose up -d --build      # 重新构建并启动
```

### Docker 直接运行

```bash
docker build -t sams:latest .
docker run -d \
  --name sams \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  sams:latest
```

### 镜像导出/分发

```bash
# 构建后导出（约 200MB）
docker save sams:latest | gzip > sams_latest.tar.gz

# 目标服务器导入
docker load < sams_latest.tar.gz
docker run -d --name sams -p 8501:8501 -v $(pwd)/data:/app/data sams:latest
```

### 手动部署

```bash
pip install -r requirements.txt
streamlit run sams.py --server.port 8501 --server.address 0.0.0.0
```

后台运行：

```bash
nohup streamlit run sams.py --server.port 8501 --server.address 0.0.0.0 > sams.log 2>&1 &
```

---

## 系统功能

| 模块 | 功能 |
|------|------|
| **仪表盘** | 资产数量统计卡片、状态分布图、系统/运行方式/业务线图表、**保修到期提醒** |
| **资产列表** | 分页表格(20条/页)、搜索、4维度筛选、勾选查看详情、批量删除 |
| **新增/编辑** | 26字段双列表单、IP校验、系统用户/密码/密钥/应用密码、密钥文件导入 |
| **批量导入** | xlsx/csv 上传、中英文列名自动识别、按内网IP UPSERT |
| **导出资产** | 按业务线/状态筛选导出 xlsx（不导出系统密码和密钥） |
| **模板下载** | 空白模板 + 含12条示例数据的测试模板 |
| **统计分析** | 业务线/系统类型/运行方式图表 |
| **用户管理** | 管理员可添加用户（SHA256 密码哈希） |
| **数据备份/恢复** | 一键备份 + 上传恢复，恢复前自动备份当前数据 |

---

## 安全设计

| 特性 | 说明 |
|------|------|
| 敏感字段加密 | `系统密码`、`系统密钥`、`应用密码` 使用 Fernet 对称加密存储在数据库中 |
| 加密密钥 | 首次启动时自动生成，保存在 `data/.encryption_key` |
| 明文迁移 | 已有明文数据在首次启动时自动迁移加密，兼容升级 |
| 密码哈希 | 用户密码 SHA256 哈希存储 |
| SQL 注入防护 | 全参数化查询 |
| 详情掩码 | 系统密码/密钥/应用密码在详情页显示 `********` |
| 导出脱敏 | 系统密码和系统密钥不包含在导出文件中 |
| 删除确认 | 单条/批量删除均有二次确认弹窗 |
| 会话管理 | URL token 持久化认证，刷新不掉线 |

---

## 模板字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| 主机名 | 是 | 服务器 hostname |
| 内网IP | 是 | 唯一标识，用作 UPSERT 键 |
| 公网IP | 否 | |
| **系统用户** | 否 | 服务器登录用户名，如 root |
| 系统密码 | 否 | root/Administrator 密码，加密存储 |
| **系统密钥** | 否 | SSH 私钥/证书，多行文本，加密存储；支持文件导入/导出 |
| 应用密码 | 否 | 格式 `应用名:用户名/密码`，每行一条 |
| 操作系统 | 否 | Linux/UNIX/Windows/macOS/Other |
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
| 保修截止 | 否 | YYYY-MM-DD，仪表盘有到期提醒 |
| 业务服务 | 否 | |
| 应用框架 | 否 | |
| 数据库 | 否 | |
| 运行方式 | 否 | physical/vm/docker/k8s/other |
| 运行详情 | 否 | |
| 端口信息 | 否 | |
| 备注 | 否 | |

---

## 数据备份

```bash
# Docker 环境 — 导出数据库
docker cp sams:/app/data/sams.db ./sams_backup_$(date +%Y%m%d).db

# Docker 环境 — 导入数据库
docker cp ./sams_backup.db sams:/app/data/sams.db
docker restart sams

# 非 Docker 环境 — 直接复制
cp sams.db sams_backup_$(date +%Y%m%d).db
```

---

## 项目结构

```
SAMS/
├── sams.py                    # 入口文件
├── sams/                      # 核心包
│   ├── main.py                # 页面路由、会话初始化
│   ├── config.py              # 常量、列名映射
│   ├── database.py            # 数据库连接、初始化、索引
│   ├── auth.py                # 用户认证、token 会话持久化
│   ├── crud.py                # 服务器 CRUD、加解密集成
│   ├── stats.py               # 仪表盘统计、保修到期计算
│   ├── crypto_utils.py        # Fernet 加密/解密/密钥管理
│   ├── excel_utils.py         # Excel 导入/导出/模板
│   └── ui/                    # 界面模块
│       ├── common.py          # CSS 主题、状态徽章
│       ├── sidebar.py         # 侧边栏/顶栏
│       ├── login.py           # 登录页
│       ├── dashboard.py       # 仪表盘
│       ├── server_list.py     # 资产列表、详情抽屉
│       ├── server_form.py     # 新增/编辑表单
│       ├── import_export.py   # 导入/导出/模板
│       ├── analytics.py       # 统计分析
│       ├── backup.py          # 备份恢复
│       ├── user_mgmt.py       # 用户管理
│       └── profile.py         # 个人信息/改密
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .streamlit/
│   └── config.toml            # Streamlit 暗黑主题
├── data/                      # 运行时数据（Docker volume）
│   ├── sams.db
│   └── .encryption_key
└── README.md
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SAMS_DATA_DIR` | 数据库和密钥文件存放目录 | 项目根目录 |

---

## 默认账号

- 用户名: `admin`
- 密码: `admin123`
- 首次登录后请立即修改密码
