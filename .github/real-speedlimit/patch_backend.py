#!/usr/bin/env python3
from pathlib import Path


def rep(path, old, new, first=False):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'anchor not found: {path}')
    p.write_text(s.replace(old, new, 1))

# model.Client
rep('internal/database/model/model.go', '\tLimitIP             int              `json:"limitIp"`                      // IP limit for this client\n\tTotalGB             int64            `json:"totalGB" form:"totalGB"`       // Total traffic limit in GB\n', '\tLimitIP             int              `json:"limitIp"`                      // IP limit for this client\n\tSpeedLimitUpMbps    uint32           `json:"speedLimitUpMbps" form:"speedLimitUpMbps"`\n\tSpeedLimitDownMbps  uint32           `json:"speedLimitDownMbps" form:"speedLimitDownMbps"`\n\tTotalGB             int64            `json:"totalGB" form:"totalGB"`       // Total traffic limit in GB\n')
rep('internal/database/model/model.go', '\tLimitIP         int    `json:"limitIp" gorm:"column:limit_ip"`\n\tLimitHwid       int    `json:"limitHwid" gorm:"column:limit_hwid;default:0"`\n\tTotalGB         int64  `json:"totalGB" gorm:"column:total_gb"`\n', '\tLimitIP            int    `json:"limitIp" gorm:"column:limit_ip"`\n\tLimitHwid          int    `json:"limitHwid" gorm:"column:limit_hwid;default:0"`\n\tSpeedLimitUpMbps   uint32 `json:"speedLimitUpMbps" gorm:"column:speed_limit_up_mbps;default:0"`\n\tSpeedLimitDownMbps uint32 `json:"speedLimitDownMbps" gorm:"column:speed_limit_down_mbps;default:0"`\n\tTotalGB            int64  `json:"totalGB" gorm:"column:total_gb"`\n')
rep('internal/database/model/model.go', '\t\tLimitIP:         c.LimitIP,\n\t\tTotalGB:         c.TotalGB,\n', '\t\tLimitIP:            c.LimitIP,\n\t\tSpeedLimitUpMbps:   c.SpeedLimitUpMbps,\n\t\tSpeedLimitDownMbps: c.SpeedLimitDownMbps,\n\t\tTotalGB:            c.TotalGB,\n')
rep('internal/database/model/model.go', '\t\tLimitIP:         r.LimitIP,\n\t\tTotalGB:         r.TotalGB,\n', '\t\tLimitIP:            r.LimitIP,\n\t\tSpeedLimitUpMbps:   r.SpeedLimitUpMbps,\n\t\tSpeedLimitDownMbps: r.SpeedLimitDownMbps,\n\t\tTotalGB:            r.TotalGB,\n')

# merge/persist global client record
rep('internal/web/service/client_link.go', '\trow.LimitIP = incoming.LimitIP\n\trow.TotalGB = incoming.TotalGB\n', '\trow.LimitIP = incoming.LimitIP\n\trow.SpeedLimitUpMbps = incoming.SpeedLimitUpMbps\n\trow.SpeedLimitDownMbps = incoming.SpeedLimitDownMbps\n\trow.TotalGB = incoming.TotalGB\n')

rep('internal/web/service/client_crud.go', '\t\t\t\t"limit_ip":          merged.LimitIP,\n\t\t\t\t"total_gb":          merged.TotalGB,\n', '\t\t\t\t"limit_ip":              merged.LimitIP,\n\t\t\t\t"speed_limit_up_mbps":   merged.SpeedLimitUpMbps,\n\t\t\t\t"speed_limit_down_mbps": merged.SpeedLimitDownMbps,\n\t\t\t\t"total_gb":              merged.TotalGB,\n')

# paged clients response
rep('internal/web/service/client_paging.go', '\tLimitIP    int                 `json:"limitIp"`\n\tLimitHwid  int                 `json:"limitHwid"`\n\tReset      int                 `json:"reset"`\n', '\tLimitIP            int                 `json:"limitIp"`\n\tLimitHwid          int                 `json:"limitHwid"`\n\tSpeedLimitUpMbps   uint32              `json:"speedLimitUpMbps"`\n\tSpeedLimitDownMbps uint32              `json:"speedLimitDownMbps"`\n\tReset              int                 `json:"reset"`\n')

# full Xray config
rep('internal/web/service/xray.go', '\t\t\tentry := map[string]any{"email": c.Email}\n\t\t\tswitch inbound.Protocol {\n', '\t\t\tentry := map[string]any{"email": c.Email}\n\t\t\tif c.SpeedLimitUpMbps > 0 { entry["speed_limit_up_mbps"] = c.SpeedLimitUpMbps }\n\t\t\tif c.SpeedLimitDownMbps > 0 { entry["speed_limit_down_mbps"] = c.SpeedLimitDownMbps }\n\t\t\tswitch inbound.Protocol {\n')

# live local runtime user add/update
rep('internal/web/runtime/local.go', '\t\t"keepAlive":    wgKeepAlive(client.KeepAlive),\n\t}\n', '\t\t"keepAlive":             wgKeepAlive(client.KeepAlive),\n\t\t"speed_limit_up_mbps":   client.SpeedLimitUpMbps,\n\t\t"speed_limit_down_mbps": client.SpeedLimitDownMbps,\n\t}\n')
rep('internal/web/runtime/local.go', '\t\t"keepAlive":    wgKeepAlive(payload.KeepAlive),\n\t}\n', '\t\t"keepAlive":             wgKeepAlive(payload.KeepAlive),\n\t\t"speed_limit_up_mbps":   payload.SpeedLimitUpMbps,\n\t\t"speed_limit_down_mbps": payload.SpeedLimitDownMbps,\n\t}\n')
rep('internal/web/service/client_inbound_apply.go', '\t\t\t\t\t"keepAlive":    keepAliveStr(client.KeepAlive),\n\t\t\t\t})\n', '\t\t\t\t\t"keepAlive":             keepAliveStr(client.KeepAlive),\n\t\t\t\t\t"speed_limit_up_mbps":   client.SpeedLimitUpMbps,\n\t\t\t\t\t"speed_limit_down_mbps": client.SpeedLimitDownMbps,\n\t\t\t\t})\n')

# prevent official Xray binary replacement from silently dropping limiter
rep('internal/web/service/server.go', 'func (s *ServerService) UpdateXray(version string) error {\n', 'func (s *ServerService) UpdateXray(version string) error {\n\treturn errors.New("Xray version switching is disabled in the real-speedlimit build")\n}\n\nfunc (s *ServerService) updateXrayUpstreamDisabled(version string) error {\n')
