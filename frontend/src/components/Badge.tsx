import React from "react";
import cx from "classnames";

import "@/styles/components.css";

interface BadgeProps {
  tone?: "neutral" | "success" | "warning" | "danger" | "info";
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ tone = "neutral", children }) => {
  return <span className={cx("badge", `badge--${tone}`)}>{children}</span>;
};
