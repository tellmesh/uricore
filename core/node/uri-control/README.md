# uri-control Node/TypeScript placeholder

This folder is reserved for a thin Node/TypeScript SDK.

The intended interface should mirror Python:

```ts
const registry = await CapabilityRegistry.fromManifestFiles([
  "examples/packs/browser_mock/manifest.yaml"
]);

const runtime = new UriControlRuntime({ registry, eventStore });
await runtime.call("browser://default/page/open", {
  payload: { url: "https://example.com" },
  context: { approved: true }
});
```

Keep this SDK thin. The source of truth should remain manifest + URI + protobuf envelope.
