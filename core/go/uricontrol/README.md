# uricontrol Go placeholder

This folder is reserved for a thin Go SDK/runner.

Target shape:

```go
result, err := runtime.Call(ctx, "systemd://unit/docker.service/query/status", nil)
```

Keep the Go implementation compatible with the same manifest and protobuf envelope used by Python.
