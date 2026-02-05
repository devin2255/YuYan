import React from "react";
import cx from "classnames";

import "@/styles/components.css";

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  tone?: "default" | "soft";
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ tone = "default", className, ...props }, ref) => {
    return <select ref={ref} className={cx("select", `select--${tone}`, className)} {...props} />;
  }
);

Select.displayName = "Select";
