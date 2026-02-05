import { api, unwrap } from "@/services/http";
import type { ApiResponse, AuthUser } from "@/types";

const useMock = String(import.meta.env.VITE_MOCK_AUTH || "").toLowerCase() === "1";

export interface LoginPayload {
  identity: string;
  password: string;
}

export interface RegisterPayload {
  identity: string;
  password: string;
  display_name: string;
}

export interface AuthResult {
  access_token: string;
  user: AuthUser;
}

const mockLogin = async (payload: LoginPayload): Promise<AuthResult> => {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return {
    access_token: "mock-access-token",
    user: {
      id: "u-demo",
      displayName: payload.identity,
      identity: payload.identity,
      roles: ["admin"],
    },
  };
};

const mockRegister = async (payload: RegisterPayload): Promise<AuthResult> => {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return {
    access_token: "mock-access-token",
    user: {
      id: "u-new",
      displayName: payload.display_name,
      identity: payload.identity,
      roles: ["admin"],
    },
  };
};

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResult> {
    if (useMock) return mockLogin(payload);
    const res = await api.post<ApiResponse<AuthResult>>("/auth/login", payload);
    return unwrap(res.data);
  },
  async register(payload: RegisterPayload): Promise<AuthResult> {
    if (useMock) return mockRegister(payload);
    const res = await api.post<ApiResponse<AuthResult>>("/auth/register", payload);
    return unwrap(res.data);
  },
  async refresh(): Promise<AuthResult> {
    const res = await api.post<ApiResponse<AuthResult>>("/auth/refresh", {});
    return unwrap(res.data);
  },
  async me(): Promise<AuthUser> {
    const res = await api.get<ApiResponse<AuthUser>>("/auth/me");
    return unwrap(res.data);
  },
  async logout(): Promise<void> {
    await api.post("/auth/logout", {});
  },
};
