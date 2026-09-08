# 3X-UI 真限速 V1（中文测试指南）

> 基线：3X-UI v3.7.0 + Xray-core v26.7.28。当前为实验性 V1，仅建议独立测试 VPS 使用。

## 设计方向

这个分支保留 3X-UI 上游架构、数据库、API、订阅、多节点、IP/HWID 等能力，同时吸收中文用户常见面板的操作优势：

- 中文优先：关键字段直接说明用途、单位和 `0 = 不限速`。
- 一键操作：安装、更新、备份、状态、回滚统一由一个命令入口完成。
- 防误操作：更新前自动备份；检测到 X-Panel 时默认拒绝直接覆盖。
- 可识别构建：安装包内置 `REAL_SPEEDLIMIT_V1` 标记，避免官方 Xray 与自定义 Xray 混淆。
- 可回滚：保留更新前的 `/etc/x-ui`、`/usr/local/x-ui`、systemd 配置和证书目录。

中文交互和一键管理的产品思路参考了 X-Panel 公共 README 中展示的中文安装界面、一键配置、状态检测、快照/急救恢复等使用体验；本分支实现代码为独立实现，不依赖 X-Panel Pro 授权、闭源组件或私有服务。

## 限速语义

客户端新增两个字段：

- `speedLimitUpMbps`：上传限速，单位 Mbps。
- `speedLimitDownMbps`：下载限速，单位 Mbps。

规则：

- `0` = 不限速。
- 限速按客户端聚合，而不是按单条连接。
- 同一客户端同时建立多条连接时，共享同一个总速率预算。
- 上传和下载分别限制，可只限制一个方向。

例如：

- 上传 `20`、下载 `100`：该客户端所有并发连接合计上传约 20 Mbps、下载约 100 Mbps。
- 上传 `0`、下载 `100`：上传不限速，下载约 100 Mbps。

## 一键命令

### 打开中文菜单

```bash
bash <(curl -Ls https://raw.githubusercontent.com/luhaihui106/3x-ui/feature/real-client-speed-limit-v1/install-speedlimit.sh)
```

安装后也可以直接执行：

```bash
xui-speedlimit
```

### 新测试 VPS 一键安装

```bash
bash <(curl -Ls https://raw.githubusercontent.com/luhaihui106/3x-ui/feature/real-client-speed-limit-v1/install-speedlimit.sh) install
```

### 更新测试版

```bash
xui-speedlimit update
```

更新前会自动创建备份。

### 查看状态

```bash
xui-speedlimit status
```

重点确认：

- `x-ui` 服务为 active；
- `/usr/local/x-ui/bin/REAL_SPEEDLIMIT_V1` 存在；
- 自定义 Xray 二进制存在；
- 构建标记中显示对应 panel/xray commit。

### 手动备份

```bash
xui-speedlimit backup
```

默认备份目录：

```text
/root/3x-ui-speedlimit-backups/
```

### 回滚最近一次备份

```bash
xui-speedlimit rollback
```

也可以指定备份：

```bash
xui-speedlimit rollback /root/3x-ui-speedlimit-backups/speedlimit-backup-YYYYMMDD-HHMMSS.tar.gz
```

## X-Panel 用户特别注意

V1 **不会自动把 X-Panel 当成普通 3X-UI 覆盖升级**。

如果脚本检测到 X-Panel，会默认停止。原因不是路径不同，而是 X-Panel 与最新 3X-UI 已存在数据库字段、功能和行为分叉，尤其是独立限速、设备限制、中转/主从/Pro 等扩展字段。

正确顺序：

1. 独立 VPS 验证真限速构建；
2. 完成 Reality/Vision 实机验收；
3. 再做 X-Panel 数据库兼容检查；
4. 生成迁移前备份；
5. 最后才进行正式迁移。

## V1 实机验收清单

推荐至少验证：

1. VLESS + TCP + REALITY + Vision 可以正常连接。
2. 下载限制 100 Mbps 时，单连接长传输稳定接近目标值。
3. 同一客户端 8 条并发连接时，总速率仍约 100 Mbps，而不是 8 × 100 Mbps。
4. 上传 20 Mbps / 下载 100 Mbps 能分别生效。
5. 设置 0 后恢复不限速。
6. 修改客户端限速后，在线 AddUser/UpdateUser 路径生效。
7. 流量统计仍正常。
8. IP 限制、HWID 限制仍正常。
9. Reality/Vision direct-copy 场景限速不失效。
10. 重启 Xray、重启面板后限速仍保持。

只有以上关键项通过，才考虑合并到 `main`。
