#!/usr/bin/env python3
from pathlib import Path

p = Path('x-ui.sh')
s = p.read_text()
manager = 'https://raw.githubusercontent.com/luhaihui106/3x-ui/feature/real-client-speed-limit-v1/install-speedlimit.sh'
branch_menu = 'https://raw.githubusercontent.com/luhaihui106/3x-ui/feature/real-client-speed-limit-v1/x-ui.sh'

# Apply the more-specific patterns first. This script is intentionally
# idempotent because the generated x-ui.sh is committed back to the branch.
replacements = [
    (
        'XUI_UPDATE_TAG="dev-latest" bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/main/update.sh)',
        f'bash <(curl -Ls {manager}) update',
    ),
    (
        'bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/main/install.sh)',
        f'bash <(curl -Ls {manager}) install',
    ),
    (
        'bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/main/update.sh)',
        f'bash <(curl -Ls {manager}) update',
    ),
    (
        'replace_xui_script "https://raw.githubusercontent.com/MHSanaei/3x-ui/main/x-ui.sh" "false"',
        f'replace_xui_script "{branch_menu}" "false"',
    ),
    (
        'replace_xui_script "https://github.com/MHSanaei/3x-ui/raw/main/x-ui.sh" "true"',
        f'replace_xui_script "{branch_menu}" "true"',
    ),
    (
        'echo -e "${green}bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)${plain}"',
        f'echo -e "${{green}}bash <(curl -Ls {manager}) install${{plain}}"',
    ),
]

for old, new in replacements:
    if old in s:
        s = s.replace(old, new)

# The legacy-version feature intentionally installs an official historic build.
# In the custom limiter channel that would remove the limiter, so disable it
# with a clear Chinese explanation instead of silently leaving an escape hatch.
legacy_start = 'legacy_version() {\n'
legacy_end = '\n}\n\n# Function to handle the deletion of the script file'
if legacy_start in s and legacy_end in s:
    before, rest = s.split(legacy_start, 1)
    body, after = rest.split(legacy_end, 1)
    if '真限速测试版已禁用“安装旧版”' not in body:
        replacement = (
            'legacy_version() {\n'
            '    echo -e "${yellow}真限速测试版已禁用“安装旧版”。${plain}"\n'
            '    echo -e "${yellow}原因：官方历史版本不包含自定义 Xray 聚合限速，切换后会失去该功能。${plain}"\n'
            '    echo -e "${green}如需更新本测试版，请使用：xui-speedlimit update${plain}"\n'
            '}\n\n# Function to handle the deletion of the script file'
        )
        s = before + replacement + after

banner = '# REAL_SPEEDLIMIT_V1_MENU_GUARD\n'
if banner not in s:
    s = s.replace('#!/bin/bash\n', '#!/bin/bash\n' + banner, 1)

# Guard invariant: no normal menu action in this experimental script may point
# back to upstream install/update/menu URLs. Documentation comments are fine,
# but executable upstream escape hatches are not.
for forbidden in (
    'raw.githubusercontent.com/MHSanaei/3x-ui/main/update.sh',
    'github.com/MHSanaei/3x-ui/raw/main/x-ui.sh',
    'raw.githubusercontent.com/mhsanaei/3x-ui/v$tag_version/install.sh',
):
    if forbidden in s:
        raise SystemExit(f'upstream escape hatch remains: {forbidden}')

p.write_text(s)
