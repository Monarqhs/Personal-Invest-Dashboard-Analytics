const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface RequestOptions extends RequestInit {
  authToken?: string;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { authToken, ...fetchOptions } = options;

  const headers = new Headers(fetchOptions.headers);
  headers.set("Content-Type", "application/json");

  // Auth header slot — injected when token is available (Phase 4+)
  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }

  const correlationId = crypto.randomUUID();
  headers.set("X-Correlation-Id", correlationId);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text(), correlationId);
  }

  return response.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: string,
    public readonly correlationId: string
  ) {
    super(`API error ${status}: ${body}`);
    this.name = "ApiError";
  }
}
