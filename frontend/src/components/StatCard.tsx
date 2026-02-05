import React from "react";
import cx from "classnames";

import "@/styles/components.css";

interface StatCardProps {
  label: string;
  value: string | number;
  delta?: string;
  tone?: "neutral" | "success" | "warning" | "danger";
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, delta, tone = "neutral" }) => {
  return (
    <div className={cx("stat-card", `stat-card--${tone}`)}>
      <span className="stat-card__label">{label}</span>
      <strong className="stat-card__value">{value}</strong>
      {delta && <span className="stat-card__delta">{delta}</span>}
    </div>
  );
};
