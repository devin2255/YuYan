import React from "react";

import "@/styles/components.css";

export const EmptyState: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  return (
    <div className="empty">
      <div className="empty__icon">◦</div>
      <div>
        <h4 className="empty__title">{title}</h4>
        {subtitle && <p className="empty__subtitle">{subtitle}</p>}
      </div>
    </div>
  );
};
