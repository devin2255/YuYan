import React from "react";
import { NavLink, Outlet } from "react-router-dom";

import { Button } from "@/components/Button";
import { useAuth } from "@/store/auth";

export const AppShell: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand__mark">语燕</div>
          <div className="brand__meta">
            <span className="brand__title">风控控制台</span>
            <span className="brand__subtitle">Risk Control Studio</span>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/apps" className={({ isActive }) => `nav__item ${isActive ? "active" : ""}`}>
            应用接入
          </NavLink>
          <NavLink to="/channels" className={({ isActive }) => `nav__item ${isActive ? "active" : ""}`}>
            渠道管理
          </NavLink>
          <NavLink to="/name-lists" className={({ isActive }) => `nav__item ${isActive ? "active" : ""}`}>
            名单维护
          </NavLink>
          <NavLink to="/text-check" className={({ isActive }) => `nav__item ${isActive ? "active" : ""}`}>
            文本风控测试
          </NavLink>
          <NavLink to="/risk-logs" className={({ isActive }) => `nav__item ${isActive ? "active" : ""}`}>
            风控日志
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav__item ${isActive ? "active" : ""}`}>
            账户设置
          </NavLink>
        </nav>
        <div className="sidebar__footer">
          <div className="sidebar__user">
            <span className="sidebar__label">当前用户</span>
            <strong>{user?.displayName || user?.identity}</strong>
          </div>
          <Button tone="ghost" size="sm" onClick={logout}>
            退出登录
          </Button>
        </div>
      </aside>
      <main className="content">
        <header className="topbar">
          <div className="topbar__left">
            <span className="topbar__badge">实时风控 · 多名单联动</span>
          </div>
          <div className="topbar__right">
            <span className="topbar__user">{user?.identity}</span>
          </div>
        </header>
        <section className="content__inner">
          <Outlet />
        </section>
      </main>
    </div>
  );
};
