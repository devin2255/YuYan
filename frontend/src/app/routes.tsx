import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { RouteGuard } from "@/app/RouteGuard";
import { AppShell } from "@/app/AppShell";
import Login from "@/pages/auth/Login";
import Register from "@/pages/auth/Register";
import Apps from "@/pages/apps/Apps";
import Channels from "@/pages/apps/Channels";
import NameLists from "@/pages/name-lists/NameLists";
import NameListDetails from "@/pages/name-lists/NameListDetails";
import RiskLogs from "@/pages/risk-logs/RiskLogs";
import Settings from "@/pages/settings/Settings";
import TextCheck from "@/pages/text-check/TextCheck";

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <RouteGuard>
            <AppShell />
          </RouteGuard>
        }
      >
        <Route index element={<Navigate to="/apps" replace />} />
        <Route path="apps" element={<Apps />} />
        <Route path="channels" element={<Channels />} />
        <Route path="name-lists" element={<NameLists />} />
        <Route path="name-lists/:listNo" element={<NameListDetails />} />
        <Route path="text-check" element={<TextCheck />} />
        <Route path="risk-logs" element={<RiskLogs />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/apps" replace />} />
    </Routes>
  );
};
