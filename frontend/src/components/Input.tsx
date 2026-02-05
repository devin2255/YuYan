import React from "react";
import cx from "classnames";

import "@/styles/components.css";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  tone?: "default" | "soft";
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ tone = "default", className, ...props }, ref) => {
    return <input ref={ref} className={cx("input", `input--${tone}`, className)} {...props} />;
  }
);

Input.displayName = "Input";
