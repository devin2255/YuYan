import React from "react";
import cx from "classnames";

import "@/styles/components.css";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  tone?: "primary" | "ghost" | "outline" | "danger" | "soft";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  tone = "primary",
  size = "md",
  className,
  ...props
}) => {
  return (
    <button
      className={cx("btn", `btn--${tone}`, `btn--${size}`, className)}
      {...props}
    />
  );
};
