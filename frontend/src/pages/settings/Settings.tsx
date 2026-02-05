import React from "react";

import { Card } from "@/components/Card";
import { useAuth } from "@/store/auth";

const Settings: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>账户设置</h2>
          <p>查看账号信息与角色权限。</p>
        </div>
      </div>

      <Card title="当前账户">
        <div className="info-grid">
          <div>
            <span className="info-label">显示名称</span>
            <strong>{user?.displayName || "-"}</strong>
          </div>
          <div>
            <span className="info-label">账号标识</span>
            <strong>{user?.identity || "-"}</strong>
          </div>
          <div>
            <span className="info-label">角色</span>
            <strong>{user?.roles?.join(", ") || "admin"}</strong>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
