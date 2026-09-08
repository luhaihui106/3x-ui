#!/usr/bin/env python3
from pathlib import Path

p = Path('x-ui.sh')
s = p.read_text()
manager = 'https://raw.githubusercontent.com/luhaihui106/3x-ui/feature/real-client-speed-limit-v1/install-speedlimit.sh'
branch_menu = 'https://raw.githubusercontent.com/luhaihui106/3x-ui/feature/real-client-speed-limit-v1/x-ui.sh'

replacements = [
    (
        'bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/main/install.sh)',
        f'bash <(curl -Ls {manager}) install',
    ),
    (
        'bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/main/update.sh)',
        f'bash <(curl -Ls {manager}) update',
    ),
    (
        'XUI_UPDATE_TAG="dev-latest" bash <(curl -Ls https://raw.githubusercontent.com/MHSanaei/3x-ui/main/update.sh)',
        f'bash <(curl -Ls {manager}) update',
    ),
    (
        'replace_xui_script "https://raw.githubusercontent.com/MHSanaei/3x-ui/main/x-ui.sh" "false"',
        f'replace_xui_script "{branch_menu}" "false"',
    ),
]

for old, new in replacements:
    if new in s:
        continue
    if old not in s:
        raise SystemExit(f'anchor not found: {old}')
    s = s.replace(old, new, 1)

banner = '# REAL_SPEEDLIMIT_V1_MENU_GUARD\n'
if banner not in s:
    s = s.replace('#!/bin/bash\n', '#!/bin/bash\n' + banner, 1)

p.write_text(s)
