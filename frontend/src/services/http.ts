import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

import { ApiError, ApiResponse } from "@/types";

let accessToken = "";
let refreshHandler: (() => Promise<string | null>) | null = null;
let logoutHandler: (() => void) | null = null;
let refreshing: Promise<string | null> | null = null;

const joinUrl = (base: string, prefix: string) => {
  if (!base && !prefix) return "";
  if (!base) return prefix;
  if (!prefix) return base;
  return `${base.replace(/\/$/, "")}\/\/${prefix.replace(/^\//, "")}`;
};

const baseURL = joinUrl(
  import.meta.env.VITE_API_BASE_URL || "",
  import.meta.env.VITE_API_PREFIX || ""
);

export const api: AxiosInstance = axios.create({
  baseURL,
  timeout: 20_000,
  withCredentials: true,
});

export const setAccessToken = (token: string | null) => {
  accessToken = token || "";
};

export const setAuthHandlers = (handlers: {
  refreshToken: () => Promise<string | null>;
  onLogout: () => void;
}) => {
  refreshHandler = handlers.refreshToken;
  logoutHandler = handlers.onLogout;
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiResponse>) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (!original) throw error;

    if (error.response?.status === 401 && refreshHandler && !original._retry) {
      original._retry = true;
      if (!refreshing) {
        refreshing = refreshHandler().finally(() => {
          refreshing = null;
        });
      }
      const token = await refreshing;
      if (token) {
        setAccessToken(token);
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
      if (logoutHandler) logoutHandler();
    }
    throw error;
  }
);

export const unwrap = <T>(payload: ApiResponse<T>): T => {
  if (payload && typeof payload.code === "number") {
    if (payload.code !== 0) {
      const message = payload.message || "请求失败";
      throw new ApiError(message, payload.code);
    }
    return (payload.data as T) ?? (null as T);
  }
  return payload as unknown as T;
};

export const maybeUnwrap = <T>(payload: ApiResponse<T> | T): T => {
  if (payload && typeof (payload as ApiResponse<T>).code === "number") {
    return unwrap(payload as ApiResponse<T>);
  }
  return payload as T;
};
