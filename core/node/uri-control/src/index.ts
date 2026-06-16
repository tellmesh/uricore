export type UriControlPlaceholder = {
  uri: string;
  payload?: Record<string, unknown>;
  context?: Record<string, unknown>;
};

export function describePlaceholder(): string {
  return "uri-control Node/TypeScript SDK placeholder";
}
