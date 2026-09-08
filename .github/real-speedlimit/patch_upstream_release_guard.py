#!/usr/bin/env python3
from pathlib import Path
import re

p = Path('.github/workflows/release.yml')
s = p.read_text()
guard = "github.ref != 'refs/heads/feature/real-client-speed-limit-v1' && github.head_ref != 'feature/real-client-speed-limit-v1'"

# The upstream release workflow downloads the official Xray binary. It remains
# useful on main/upstream-compatible branches, but must never manufacture
# misleading artifacts for our custom limiter development branch or its PR.
head, sep, tail = s.partition('jobs:\n')
if not sep:
    raise SystemExit('jobs block not found')

lines = tail.splitlines(True)
out = []
i = 0
while i < len(lines):
    line = lines[i]
    out.append(line)
    if re.match(r'^  [A-Za-z0-9_-]+:\s*$', line.rstrip('\n')):
        next_line = lines[i + 1] if i + 1 < len(lines) else ''
        if f'if: {guard}' not in next_line:
            out.append(f'    if: {guard}\n')
    i += 1

new = head + sep + ''.join(out)
if new == s:
    print('upstream release workflow guard already applied')
else:
    p.write_text(new)
