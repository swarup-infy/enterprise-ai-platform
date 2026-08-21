import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

/* ==========================================================================
   Configuration
   ========================================================================== */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() ||
  "http://127.0.0.1:8000/api";

const DEFAULT_TIMEOUT = 30_000;
const CHAT_TIMEOUT = 120_000;
const UPLOAD_TIMEOUT = 120_000;

const ACCESS_TOKEN_KEY = "access_token";

/* ==========================================================================
   Types
   ========================================================================== */

export interface User {
  id: string | number;
  email: string;
  username: string;
  full_name?: string;
  role?: string;
  is_active?: boolean;
  is_verified?: boolean;
  is_superuser?: boolean;
  created_at?: string;
  updated_at?: string;
  last_login?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Document {
  id: string | number;
  filename?: string;
  file_name?: string;
  original_filename?: string;
  file_path?: string;
  mime_type?: string;
  content_type?: string;
  file_size?: number;
  size?: number;
  title?: string | null;
  summary?: string | null;
  embedding_model?: string | null;
  vector_collection?: string | null;
  is_processed?: boolean;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface UpdateUserRequest {
  email?: string;
  username?: string;
  password?: string;
  is_active?: boolean;
  role?: string;
}

export interface UpdateDocumentRequest {
  filename?: string;
  status?: string;
}

export interface ChatRequest {
  message: string;
  collection_name?: string;
  top_k?: number;
  document_id?: string | number | null;
}

export interface ChatResponse {
  answer?: string;
  response?: string;
  message?: string;
  conversation_id?: string;
  [key: string]: unknown;
}

export interface ChatHistoryItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatHistoryMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatConversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatHistoryMessage[];
}

export interface HealthResponse {
  status: string;
  service?: string;
}

/* ==========================================================================
   API Error
   ========================================================================== */

export interface ApiErrorDetail {
  message: string;
  status?: number;
  code?: string;
}

export function getApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again.",
): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      const firstError = data.detail[0];

      if (
        typeof firstError === "object" &&
        firstError !== null &&
        "msg" in firstError &&
        typeof firstError.msg === "string"
      ) {
        return firstError.msg;
      }

      return "The server rejected the request.";
    }

    if (
      typeof data?.message === "string"
    ) {
      return data.message;
    }

    if (error.code === "ECONNABORTED") {
      return "The request took too long. Please try again.";
    }

    if (!error.response) {
      return "Unable to connect to the server.";
    }
  }

  if (
    error instanceof Error &&
    error.message
  ) {
    return error.message;
  }

  return fallback;
}

/* ==========================================================================
   Token Storage
   ========================================================================== */

export const tokenStorage = {
  get(): string | null {
    try {
      const token =
        localStorage.getItem(
          ACCESS_TOKEN_KEY,
        );

      if (!token?.trim()) {
        return null;
      }

      return token;
    } catch {
      return null;
    }
  },

  set(token: string): void {
    if (!token.trim()) {
      return;
    }

    try {
      localStorage.setItem(
        ACCESS_TOKEN_KEY,
        token,
      );
    } catch {
      /*
       * Storage can fail in privacy-restricted
       * browser environments.
       */
    }
  },

  clear(): void {
    try {
      localStorage.removeItem(
        ACCESS_TOKEN_KEY,
      );
    } catch {
      /*
       * Ignore storage cleanup failures.
       */
    }
  },
};

/* ==========================================================================
   Axios Instance
   ========================================================================== */

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    Accept: "application/json",
  },
});

/* ==========================================================================
   Request Interceptor
   ========================================================================== */

api.interceptors.request.use(
  (
    config: InternalAxiosRequestConfig,
  ) => {
    const token =
      tokenStorage.get();

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },
  (error) =>
    Promise.reject(error),
);

/* ==========================================================================
   Response Interceptor
   ========================================================================== */

api.interceptors.response.use(
  (response) =>
    response,

  (error: AxiosError) => {
    const status =
      error.response?.status;

    if (status === 401) {
      tokenStorage.clear();

      const requestUrl =
        error.config?.url ?? "";

      const currentPath =
        window.location.pathname;

      const isAuthenticationRequest =
        requestUrl.includes(
          "/auth/login",
        ) ||
        requestUrl.includes(
          "/auth/register",
        );

      const isAuthenticationPage =
        currentPath === "/login" ||
        currentPath === "/register";

      /*
       * Do not redirect authentication requests.
       *
       * Otherwise a failed login could redirect
       * back into the login page and create an
       * unpleasant navigation loop.
       */
      if (
        !isAuthenticationRequest &&
        !isAuthenticationPage
      ) {
        window.location.assign(
          `/login?redirect=${encodeURIComponent(
            currentPath,
          )}`,
        );
      }
    }

    return Promise.reject(error);
  },
);

/* ==========================================================================
   Authentication
   ========================================================================== */

export async function register(
  data: RegisterRequest,
): Promise<User> {
  const response =
    await api.post<User>(
      "/auth/register",
      data,
    );

  return response.data;
}

export async function login(
  data: LoginRequest,
): Promise<TokenResponse> {
  const response =
    await api.post<TokenResponse>(
      "/auth/login",
      data,
    );

  if (!response.data.access_token) {
    throw new Error(
      "Authentication succeeded but no access token was returned.",
    );
  }

  tokenStorage.set(
    response.data.access_token,
  );

  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response =
    await api.get<User>(
      "/auth/me",
    );

  return response.data;
}

export async function logout(): Promise<void> {
  try {
    await api.post(
      "/auth/logout",
    );
  } finally {
    tokenStorage.clear();
  }
}

/* ==========================================================================
   Users
   ========================================================================== */

export async function getUsers(): Promise<User[]> {
  const response =
    await api.get<User[]>(
      "/users/",
    );

  return response.data;
}

export async function getUser(
  userId: string | number,
): Promise<User> {
  const response =
    await api.get<User>(
      `/users/${encodeURIComponent(
        String(userId),
      )}`,
    );

  return response.data;
}

export async function updateUser(
  userId: string | number,
  data: UpdateUserRequest,
): Promise<User> {
  const response =
    await api.put<User>(
      `/users/${encodeURIComponent(
        String(userId),
      )}`,
      data,
    );

  return response.data;
}

export async function deleteUser(
  userId: string | number,
): Promise<void> {
  await api.delete(
    `/users/${encodeURIComponent(
      String(userId),
    )}`,
  );
}

/* ==========================================================================
   Documents
   ========================================================================== */

export async function uploadDocument(
  file: File,
): Promise<Document> {
  const formData =
    new FormData();

  formData.append(
    "file",
    file,
  );

  /*
   * Do not manually set Content-Type here.
   *
   * Axios/browser will automatically add the
   * correct multipart boundary.
   */
  const response =
    await api.post<Document>(
      "/documents/upload",
      formData,
      {
        timeout: UPLOAD_TIMEOUT,
      },
    );

  return response.data;
}

export async function getDocuments(): Promise<Document[]> {
  const response =
    await api.get<Document[]>(
      "/documents/",
    );

  return response.data;
}

export async function getDocument(
  documentId: string | number,
): Promise<Document> {
  const response =
    await api.get<Document>(
      `/documents/${encodeURIComponent(
        String(documentId),
      )}`,
    );

  return response.data;
}

export async function updateDocument(
  documentId: string | number,
  data: UpdateDocumentRequest,
): Promise<Document> {
  const response =
    await api.put<Document>(
      `/documents/${encodeURIComponent(
        String(documentId),
      )}`,
      data,
    );

  return response.data;
}

export async function deleteDocument(
  documentId: string | number,
): Promise<void> {
  await api.delete(
    `/documents/${encodeURIComponent(
      String(documentId),
    )}`,
  );
}

/* ==========================================================================
   Chat
   ========================================================================== */

export async function sendChatMessage(
  data: ChatRequest,
  config?: AxiosRequestConfig,
): Promise<ChatResponse> {
  const response =
    await api.post<ChatResponse>(
      "/chat",
      data,
      {
        timeout: CHAT_TIMEOUT,
        ...config,
      },
    );

  return response.data;
}

/* ==========================================================================
   Chat History
   ========================================================================== */

export async function getChatHistory(
  config?: AxiosRequestConfig,
): Promise<ChatHistoryItem[]> {
  const response =
    await api.get<ChatHistoryItem[]>(
      "/chat/history",
      config,
    );

  return response.data;
}

export async function getChatConversation(
  conversationId: string,
  config?: AxiosRequestConfig,
): Promise<ChatConversation> {
  const response =
    await api.get<ChatConversation>(
      `/chat/history/${encodeURIComponent(
        conversationId,
      )}`,
      config,
    );

  return response.data;
}

export async function deleteChatConversation(
  conversationId: string,
): Promise<void> {
  await api.delete(
    `/chat/history/${encodeURIComponent(
      conversationId,
    )}`,
  );
}

/* ==========================================================================
   Health
   ========================================================================== */

export async function checkHealth(): Promise<HealthResponse> {
  const response =
    await api.get<HealthResponse>(
      "/health",
    );

  return response.data;
}

/* ==========================================================================
   Exports
   ========================================================================== */

export { api };

export default api;