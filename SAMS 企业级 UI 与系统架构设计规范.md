# SAMS 企业级 UI 与系统架构设计规范

# Server Asset Management System (SAMS)

技术栈：

- Python
- Streamlit
- SQLite
- pandas
- openpyxl

部署方式：

- 单文件运行：sams.py
- SQLite 自动初始化
- 企业后台风格 UI

------

# 一、企业级 UI 原型设计

# 1. 页面整体布局

采用经典企业后台布局：

```text
┌──────────────────────────────────────────────────────────────┐
│ 顶部导航栏 Header                                           │
│ Logo | SAMS | 当前用户 | 时间 | 退出登录                    │
├──────────────┬───────────────────────────────────────────────┤
│              │                                               │
│ Sidebar      │               主内容区域                      │
│ 左侧菜单      │                                               │
│              │                                               │
│              │                                               │
│              │                                               │
│              │                                               │
├──────────────┴───────────────────────────────────────────────┤
│ Footer                                               v1.0    │
└──────────────────────────────────────────────────────────────┘
```

------

# 2. 顶部 Header 设计

Header 内容：

左侧：

- 系统 Logo
- 系统名称：
  Server Asset Management System

右侧：

- 当前登录用户
- 当前时间
- 数据库状态
- 退出登录按钮

风格：

- 深蓝背景
- 白色字体
- 高度固定 60px
- 企业风格

------

# 3. Sidebar 企业菜单设计

Sidebar 固定左侧。

菜单结构：

```text
📊 Dashboard
    ├── 资产总览
    ├── 状态统计
    ├── 系统统计

🖥 Asset Management
    ├── 资产列表
    ├── 新增资产
    ├── 批量导入
    ├── 导出资产

📈 Analytics
    ├── 业务统计
    ├── 系统类型统计
    ├── 运行方式统计

⚙ System
    ├── 模板下载
    ├── 数据库备份
    ├── 用户管理

👤 User
    ├── 当前信息
    ├── 修改密码
    ├── 退出登录
```

Sidebar 风格：

- 深色主题
- hover 高亮
- 图标化菜单
- 可折叠菜单

------

# 二、Dashboard 首页设计

# 1. 顶部统计卡片

使用 st.metric() 展示。

布局：

```text
┌────────────┬────────────┬────────────┬────────────┐
│ 总资产数    │ Running   │ Stopped   │ Maint      │
│ 128         │ 102       │ 12        │ 14         │
└────────────┴────────────┴────────────┴────────────┘
```

统计内容：

- 总资产数
- running 数量
- stopped 数量
- maintenance 数量
- decommissioned 数量

颜色：

- running → 绿色
- stopped → 黄色
- maintenance → 蓝色
- decommissioned → 红色

------

# 2. 图表区域

使用：

- st.bar_chart
- st.line_chart

图表内容：

## 系统类型统计

```text
Linux      ███████████
Windows    ████
```

## 运行方式统计

```text
docker
k8s
physical
vm
```

## 业务线统计

```text
支付系统
订单系统
监控系统
数据库服务
```

------

# 三、资产列表页面设计

# 页面结构

```text
┌────────────────────────────────────────────┐
│ 搜索栏                                      │
├────────────────────────────────────────────┤
│ 筛选区域                                    │
├────────────────────────────────────────────┤
│ 资产表格                                    │
├────────────────────────────────────────────┤
│ 分页区域                                    │
└────────────────────────────────────────────┘
```

------

# 1. 搜索栏

支持：

- hostname
- private_ip
- owner
- business

实时搜索。

------

# 2. 筛选区域

支持：

- 状态筛选
- 系统类型筛选
- 运行方式筛选
- 业务线筛选

支持多选。

------

# 3. 企业级资产表格设计

表格字段：

```text
Hostname
Private IP
OS
CPU
Memory
Business
Owner
Status
Updated Time
Operation
```

操作按钮：

- 查看
- 编辑
- 删除

状态颜色标签：

```text
running         绿色
stopped         黄色
maintenance     蓝色
decommissioned  红色
```

分页：

- 每页 20 条
- 支持页码跳转

------

# 四、资产详情 Drawer UI

点击 hostname 后右侧弹出 Drawer。

布局：

```text
┌──────────────────────────────┐
│         Asset Detail          │
├──────────────────────────────┤
│ Hostname                      │
│ Private IP                    │
│ Public IP                     │
│ OS Type                       │
│ OS Version                    │
│ CPU                           │
│ Memory                        │
│ Disk                          │
│ Location                      │
│ Business                      │
│ Owner                         │
│ Runtime                       │
│ Database                      │
│ Port Info                     │
│ Credential Ref                │
│ Created Time                  │
│ Updated Time                  │
│ Remarks                       │
├──────────────────────────────┤
│ [编辑]        [关闭]          │
└──────────────────────────────┘
```

要求：

- credentials 不显示
- credential_ref 可显示
- Drawer 宽度约 500px
- 支持滚动

------

# 五、新增/编辑资产页面

布局：

双列表单。

```text
Hostname           Private IP
Public IP          OS Type
OS Version         CPU
Memory             Disk
Location           Business
Owner              Status
Runtime Type       Runtime Detail
Database           Port Info
Credential Ref     Purchase Date
Warranty Date      Remarks
```

按钮：

- 保存
- 重置
- 返回

------

# 六、Excel 导入页面

# 功能

支持：

- xlsx
- csv

上传后：

- 自动校验字段
- 自动校验日期
- 自动校验 IP
- 自动 UPSERT

导入结果：

```text
成功：120
更新：18
失败：2
```

失败记录显示：

```text
第12行：IP格式错误
第25行：hostname为空
```

------

# 七、Excel 导出功能

导出内容：

- 当前筛选结果
- 全部资产

文件名：

```text
servers_20260528_120000.xlsx
```

导出时：

- 不导出 credentials
- 自动格式化表头

------

# 八、SQLite 企业级索引优化

# 1. 主索引

```sql
CREATE UNIQUE INDEX idx_private_ip
ON servers(private_ip);
```

------

# 2. 搜索索引

```sql
CREATE INDEX idx_hostname
ON servers(hostname);

CREATE INDEX idx_owner
ON servers(owner);

CREATE INDEX idx_business
ON servers(business);

CREATE INDEX idx_status
ON servers(status);

CREATE INDEX idx_os_type
ON servers(os_type);
```

------

# 3. 时间索引

```sql
CREATE INDEX idx_updated_at
ON servers(updated_at);
```

------

# 九、Excel 标准导入模板

# 模板字段顺序

```text
hostname
private_ip
public_ip
os_type
os_version
cpu_cores
memory_gb
disk_info
location
business
owner
status
purchase_date
warranty_expire
business_service
app_framework
db_info
runtime_type
runtime_detail
port_info
credentials
credential_ref
remarks
```

------

# 十、完整 sams.py 架构设计

# 文件结构（单文件模块化）

```python
# =========================
# Imports
# =========================

# =========================
# Config
# =========================

# =========================
# Database Module
# =========================

def get_connection():
    pass

def init_db():
    pass

def create_indexes():
    pass

# =========================
# Security Module
# =========================

def hash_password():
    pass

def verify_password():
    pass

# =========================
# Auth Module
# =========================

def login():
    pass

def logout():
    pass

# =========================
# CRUD Module
# =========================

def add_server():
    pass

def update_server():
    pass

def delete_server():
    pass

def get_servers():
    pass

# =========================
# Excel Module
# =========================

def import_excel():
    pass

def export_excel():
    pass

def generate_template():
    pass

# =========================
# Statistics Module
# =========================

def get_dashboard_stats():
    pass

# =========================
# UI Module
# =========================

def render_sidebar():
    pass

def render_dashboard():
    pass

def render_server_table():
    pass

def render_server_detail():
    pass

# =========================
# Main
# =========================

def main():
    pass
```

------

# 十一、Streamlit 页面设计规范

# 页面宽度

```python
st.set_page_config(
    page_title="SAMS",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

------

# 企业主题

风格：

- 深蓝色
- 灰白背景
- 卡片化
- 圆角按钮
- 企业后台风格

------

# 十二、企业级交互要求

所有危险操作：

- 必须确认
- 必须提示

删除：

```text
确认删除该资产？
此操作不可恢复。
```

------

# 十三、性能优化要求

必须实现：

- SQLite WAL
- 分页查询
- 缓存统计
- DataFrame 缓存
- 延迟加载详情 Drawer

------

# 十四、安全要求

禁止：

- SQL 拼接
- 明文密码
- 明文凭证显示

必须：

- SHA256
- 参数化查询
- Session 管理
- 凭证隐藏
- 删除确认