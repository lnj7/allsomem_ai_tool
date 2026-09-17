export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as {
      error?: { message?: string; code?: string };
      detail?: string;
    };
    const message = body.error?.message || body.detail || `Request failed (${response.status})`;
    return new ApiError(message, response.status, body.error?.code);
  } catch {
    return new ApiError(`Request failed (${response.status})`, response.status);
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const apiGet = <T>(path: string) => apiRequest<T>(path);
export const apiPost = <T>(path: string, body?: unknown) =>
  apiRequest<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });
export const apiPut = <T>(path: string, body?: unknown) =>
  apiRequest<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined });
