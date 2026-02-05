import React from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "@/store/auth";

export const RouteGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="page-loading">
        <div className="page-loading__ring" />
        <span>正在校验身份...</span>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
