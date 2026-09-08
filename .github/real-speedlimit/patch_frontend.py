#!/usr/bin/env python3
from pathlib import Path


def rep(path, old, new):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'anchor not found: {path}')
    p.write_text(s.replace(old, new, 1))

# Schema
rep('frontend/src/schemas/client.ts', '    limitIp: z.number().optional(),\n    limitHwid: z.number().optional(),\n    tgId: z.union([z.number(), z.string()]).optional(),\n', '    limitIp: z.number().optional(),\n    limitHwid: z.number().optional(),\n    speedLimitUpMbps: z.number().optional(),\n    speedLimitDownMbps: z.number().optional(),\n    tgId: z.union([z.number(), z.string()]).optional(),\n')
rep('frontend/src/schemas/client.ts', '  limitIp: z.number().int().min(0),\n  limitHwid: z.number().int().min(0),\n  tgId: z.number().int().min(0),\n', '  limitIp: z.number().int().min(0),\n  limitHwid: z.number().int().min(0),\n  speedLimitUpMbps: z.number().int().min(0).max(100000),\n  speedLimitDownMbps: z.number().int().min(0).max(100000),\n  tgId: z.number().int().min(0),\n')
rep('frontend/src/schemas/client.ts', '  limitIp: z.number().int().min(0),\n  limitHwid: z.number().int().min(0),\n  totalGB: z.number().min(0),\n', '  limitIp: z.number().int().min(0),\n  limitHwid: z.number().int().min(0),\n  speedLimitUpMbps: z.number().int().min(0).max(100000),\n  speedLimitDownMbps: z.number().int().min(0).max(100000),\n  totalGB: z.number().min(0),\n')

# Single-client form
p = 'frontend/src/pages/clients/ClientFormModal.tsx'
rep(p, '  limitIp: 0,\n  limitHwid: 0,\n  tgId: 0,\n', '  limitIp: 0,\n  limitHwid: 0,\n  speedLimitUpMbps: 0,\n  speedLimitDownMbps: 0,\n  tgId: 0,\n')
rep(p, '      limitIp: values.limitIp,\n      limitHwid: values.limitHwid,\n      tgId: values.tgId,\n', '      limitIp: values.limitIp,\n      limitHwid: values.limitHwid,\n      speedLimitUpMbps: values.speedLimitUpMbps,\n      speedLimitDownMbps: values.speedLimitDownMbps,\n      tgId: values.tgId,\n')
rep(p, '      limitIp: Number(values.limitIp) || 0,\n      limitHwid: Number(values.limitHwid) || 0,\n      tgId: Number(values.tgId) || 0,\n', '      limitIp: Number(values.limitIp) || 0,\n      limitHwid: Number(values.limitHwid) || 0,\n      speedLimitUpMbps: Number(values.speedLimitUpMbps) || 0,\n      speedLimitDownMbps: Number(values.speedLimitDownMbps) || 0,\n      tgId: Number(values.tgId) || 0,\n')
rep(p, '                      </Row>\n\n                      <Row gutter={16}>\n                        <Col xs={24} md={12}>\n                          {delayedStart ? (\n', '                      </Row>\n\n                      <Row gutter={16}>\n                        <Col xs={24} md={12}>\n                          <FormField name="speedLimitUpMbps" label={t(\'pages.clients.speedLimitUpMbps\')} tooltip={t(\'pages.clients.speedLimitUpMbpsDesc\')} transform={{ output: (v) => Number(v) || 0 }}>\n                            <InputNumber min={0} max={100000} step={1} addonAfter="Mbps" style={{ width: \'100%\' }} />\n                          </FormField>\n                        </Col>\n                        <Col xs={24} md={12}>\n                          <FormField name="speedLimitDownMbps" label={t(\'pages.clients.speedLimitDownMbps\')} tooltip={t(\'pages.clients.speedLimitDownMbpsDesc\')} transform={{ output: (v) => Number(v) || 0 }}>\n                            <InputNumber min={0} max={100000} step={1} addonAfter="Mbps" style={{ width: \'100%\' }} />\n                          </FormField>\n                        </Col>\n                      </Row>\n\n                      <Row gutter={16}>\n                        <Col xs={24} md={12}>\n                          {delayedStart ? (\n')

# Add edit hydration fields if anchor exists
text = Path(p).read_text()
anchor = '        limitIp: client.limitIp || 0,\n        limitHwid: client.limitHwid || 0,\n        tgId: Number(client.tgId) || 0,\n'
if anchor in text:
    Path(p).write_text(text.replace(anchor, '        limitIp: client.limitIp || 0,\n        limitHwid: client.limitHwid || 0,\n        speedLimitUpMbps: Number(client.speedLimitUpMbps) || 0,\n        speedLimitDownMbps: Number(client.speedLimitDownMbps) || 0,\n        tgId: Number(client.tgId) || 0,\n', 1))

# Bulk create defaults/payload/UI
p = 'frontend/src/pages/clients/ClientBulkAddModal.tsx'
rep(p, '  limitIp: 0,\n  limitHwid: 0,\n  totalGB: 0,\n', '  limitIp: 0,\n  limitHwid: 0,\n  speedLimitUpMbps: 0,\n  speedLimitDownMbps: 0,\n  totalGB: 0,\n')
rep(p, '          limitIp: Number(current.limitIp) || 0,\n          limitHwid: Number(current.limitHwid) || 0,\n          group: current.group,\n', '          limitIp: Number(current.limitIp) || 0,\n          limitHwid: Number(current.limitHwid) || 0,\n          speedLimitUpMbps: Number(current.speedLimitUpMbps) || 0,\n          speedLimitDownMbps: Number(current.speedLimitDownMbps) || 0,\n          group: current.group,\n')

# i18n minimal locales
for name, vals in {
    'zh-CN.json': ('上传限速（Mbps）','该客户端所有并发连接合计的最大上传速率。0 = 不限制。','下载限速（Mbps）','该客户端所有并发连接合计的最大下载速率。0 = 不限制。'),
    'en-US.json': ('Upload limit (Mbps)','Aggregate upload rate for this client. 0 = unlimited.','Download limit (Mbps)','Aggregate download rate for this client. 0 = unlimited.'),
}.items():
    p = Path('internal/web/translation') / name
    s = p.read_text()
    if '"speedLimitUpMbps"' in s:
        continue
    anchor = '      "limitHwidDesc": '
    idx = s.find(anchor)
    if idx < 0:
        raise SystemExit(f'i18n anchor not found: {name}')
    end = s.find('\n', idx) + 1
    ins = f'      "speedLimitUpMbps": "{vals[0]}",\n      "speedLimitUpMbpsDesc": "{vals[1]}",\n      "speedLimitDownMbps": "{vals[2]}",\n      "speedLimitDownMbpsDesc": "{vals[3]}",\n'
    p.write_text(s[:end] + ins + s[end:])
