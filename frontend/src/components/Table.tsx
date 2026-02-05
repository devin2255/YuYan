import React from "react";
import cx from "classnames";

import "@/styles/components.css";

interface TableProps {
  className?: string;
  children: React.ReactNode;
}

export const Table: React.FC<TableProps> = ({ className, children }) => {
  return <table className={cx("table", className)}>{children}</table>;
};
