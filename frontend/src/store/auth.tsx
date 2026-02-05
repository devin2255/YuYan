import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { authService } from "@/services/auth";
import { setAccessToken, setAuthHandlers } from "@/services/http";
import type { AuthUser } from "@/types";

interface AuthContextValue {
  user: AuthUser | null;
  accessToken: string | null;
  loading: boolean;
  login: (identity: string, password: string) => Promise<void>;
  register: (identity: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const res = await authService.refresh();
      setUser(res.user);
      setAccessTokenState(res.access_token);
      setAccessToken(res.access_token);
      return res.access_token;
    } catch {
      setUser(null);
      setAccessTokenState(null);
      setAccessToken(null);
      return null;
    }
  }, []);

  const login = useCallback(async (identity: string, password: string) => {
    const res = await authService.login({ identity, password });
    setUser(res.user);
    setAccessTokenState(res.access_token);
    setAccessToken(res.access_token);
  }, []);

  const register = useCallback(async (identity: string, password: string, displayName: string) => {
    const res = await authService.register({ identity, password, display_name: displayName });
    setUser(res.user);
    setAccessTokenState(res.access_token);
    setAccessToken(res.access_token);
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setAccessTokenState(null);
      setAccessToken(null);
    }
  }, []);

  useEffect(() => {
    setAuthHandlers({
      refreshToken: refresh,
      onLogout: () => {
        setUser(null);
        setAccessTokenState(null);
        setAccessToken(null);
      },
    });
  }, [refresh]);

  useEffect(() => {
    const boot = async () => {
      await refresh();
      setLoading(false);
    };
    boot();
  }, [refresh]);

  const value = useMemo(
    () => ({ user, accessToken, loading, login, register, logout, refresh }),
    [user, accessToken, loading, login, register, logout, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("AuthContext missing");
  return ctx;
};
