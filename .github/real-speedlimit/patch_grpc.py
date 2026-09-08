#!/usr/bin/env python3
from pathlib import Path

p = Path('internal/xray/api.go')
s = p.read_text()


def rep(old, new):
    global s
    if old not in s:
        raise SystemExit('api.go anchor not found')
    s = s.replace(old, new, 1)

if 'func getOptionalUserUint32' not in s:
    rep('''func getOptionalUserString(user map[string]any, key string) (string, error) {
\tvalue, ok := user[key]
\tif !ok || value == nil {
\t\treturn "", nil
\t}

\tstrValue, ok := value.(string)
\tif !ok {
\t\treturn "", fmt.Errorf("invalid type for user field %q: %T", key, value)
\t}

\treturn strValue, nil
}
''', '''func getOptionalUserString(user map[string]any, key string) (string, error) {
\tvalue, ok := user[key]
\tif !ok || value == nil {
\t\treturn "", nil
\t}

\tstrValue, ok := value.(string)
\tif !ok {
\t\treturn "", fmt.Errorf("invalid type for user field %q: %T", key, value)
\t}

\treturn strValue, nil
}

func getOptionalUserUint32(user map[string]any, key string) (uint32, error) {
\tvalue, ok := user[key]
\tif !ok || value == nil { return 0, nil }
\tswitch v := value.(type) {
\tcase uint32:
\t\treturn v, nil
\tcase uint64:
\t\tif v <= math.MaxUint32 { return uint32(v), nil }
\tcase int:
\t\tif v >= 0 && uint64(v) <= math.MaxUint32 { return uint32(v), nil }
\tcase int64:
\t\tif v >= 0 && uint64(v) <= math.MaxUint32 { return uint32(v), nil }
\tcase float64:
\t\tif v >= 0 && v <= math.MaxUint32 && v == math.Trunc(v) { return uint32(v), nil }
\t}
\treturn 0, fmt.Errorf("invalid uint32 user field %q: %T", key, value)
}
''')

if 'SpeedLimitUpMbps:' not in s:
    rep('''\tctx, cancel := context.WithTimeout(context.Background(), handlerRPCTimeout)
\tdefer cancel()
\t_, err = client.AlterInbound(ctx, &command.AlterInboundRequest{
\t\tTag: inboundTag,
\t\tOperation: serial.ToTypedMessage(&command.AddUserOperation{
\t\t\tUser: &protocol.User{
\t\t\t\tEmail:   userEmail,
\t\t\t\tAccount: account,
\t\t\t},
\t\t}),
\t})
''', '''\tupMbps, err := getOptionalUserUint32(user, "speed_limit_up_mbps")
\tif err != nil { return err }
\tdownMbps, err := getOptionalUserUint32(user, "speed_limit_down_mbps")
\tif err != nil { return err }

\tctx, cancel := context.WithTimeout(context.Background(), handlerRPCTimeout)
\tdefer cancel()
\t_, err = client.AlterInbound(ctx, &command.AlterInboundRequest{
\t\tTag: inboundTag,
\t\tOperation: serial.ToTypedMessage(&command.AddUserOperation{
\t\t\tUser: &protocol.User{
\t\t\t\tEmail:              userEmail,
\t\t\t\tAccount:            account,
\t\t\t\tSpeedLimitUpMbps:   upMbps,
\t\t\t\tSpeedLimitDownMbps: downMbps,
\t\t\t},
\t\t}),
\t})
''')

p.write_text(s)
