# ===================================================================
# SAMS - Config / Constants
# ===================================================================

import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(os.environ.get("SAMS_DATA_DIR", _PROJECT_ROOT), "sams.db")
PAGE_SIZE = 20

STATUS_COLORS = {
    "running": "#10b981",
    "stopped": "#f59e0b",
    "maintenance": "#3b82f6",
    "decommissioned": "#ef4444",
}

STATUS_LABELS = {
    "running": "运行中",
    "stopped": "已停止",
    "maintenance": "维护中",
    "decommissioned": "已下线",
}

STATUS_OPTIONS = ["running", "stopped", "maintenance", "decommissioned"]
OS_OPTIONS = ["Linux","UNIX", "Windows", "macOS", "Other"]
RUNTIME_OPTIONS = ["physical", "vm", "docker", "k8s", "other"]

TEMPLATE_COLUMNS = [
    "hostname", "private_ip", "public_ip",
    "system_user", "credentials", "system_key", "credential_ref",
    "os_type", "os_version", "kernel_version",
    "cpu_cores", "memory_gb", "disk_info",
    "location", "business", "owner", "status",
    "purchase_date", "warranty_expire", "business_service",
    "app_framework", "db_info", "runtime_type", "runtime_detail",
    "port_info", "remarks",
]

COLUMN_LABELS_CN = {
    "hostname": "主机名",
    "private_ip": "内网IP",
    "public_ip": "公网IP",
    "system_user": "系统用户",
    "credentials": "系统密码",
    "system_key": "系统密钥",
    "credential_ref": "应用密码",
    "os_type": "操作系统",
    "os_version": "系统版本",
    "kernel_version": "内核版本",
    "cpu_cores": "CPU(核)",
    "memory_gb": "内存(GB)",
    "disk_info": "磁盘信息",
    "location": "位置",
    "business": "业务线",
    "owner": "负责人",
    "status": "状态",
    "purchase_date": "采购日期",
    "warranty_expire": "保修截止",
    "business_service": "业务服务",
    "app_framework": "应用框架",
    "db_info": "数据库",
    "runtime_type": "运行方式",
    "runtime_detail": "运行详情",
    "port_info": "端口信息",
    "remarks": "备注",
}

COLUMN_LABELS_EN = {v: k for k, v in COLUMN_LABELS_CN.items()}

# Fields that must be encrypted at rest
ENCRYPTED_FIELDS = {"credentials", "system_key", "credential_ref"}

# Fields excluded from export
EXPORT_EXCLUDED_FIELDS = {"credentials", "system_key"}
