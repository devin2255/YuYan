import React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/Button";
import { Input } from "@/components/Input";
import { useAuth } from "@/store/auth";
import type { ApiError } from "@/types";

const schema = z
  .object({
    identity: z.string().min(1, "请输入用户名 / 邮箱 / 手机号"),
    displayName: z.string().min(1, "请输入显示名称"),
    password: z.string().min(6, "密码至少 6 位"),
    confirm: z.string().min(6, "请确认密码"),
  })
  .refine((data) => data.password === data.confirm, {
    message: "两次输入的密码不一致",
    path: ["confirm"],
  });

type FormValues = z.infer<typeof schema>;

const Register: React.FC = () => {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [notice, setNotice] = React.useState("");
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    try {
      setNotice("");
      await registerUser(values.identity, values.password, values.displayName);
      navigate("/apps");
    } catch (err) {
      const message = (err as ApiError)?.message || "注册失败";
      setNotice(message);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-panel auth-panel--reverse">
        <div className="auth-card">
          <h2>注册新账号</h2>
          <p className="auth-subtitle">支持 username / email / phone</p>
          <form onSubmit={handleSubmit(onSubmit)} className="form">
            <label className="form__field">
              <span>账号</span>
              <Input placeholder="任意一种账号标识" {...register("identity")} />
              {errors.identity && <em>{errors.identity.message}</em>}
            </label>
            <label className="form__field">
              <span>显示名称</span>
              <Input placeholder="用于页面展示" {...register("displayName")} />
              {errors.displayName && <em>{errors.displayName.message}</em>}
            </label>
            <label className="form__field">
              <span>密码</span>
              <Input type="password" placeholder="至少 6 位" {...register("password")} />
              {errors.password && <em>{errors.password.message}</em>}
            </label>
            <label className="form__field">
              <span>确认密码</span>
              <Input type="password" placeholder="再次输入密码" {...register("confirm")} />
              {errors.confirm && <em>{errors.confirm.message}</em>}
            </label>
            <Button type="submit" size="lg" disabled={isSubmitting}>
              {isSubmitting ? "注册中..." : "创建账号"}
            </Button>
            {notice && <div className="form__notice form__notice--error">{notice}</div>}
          </form>
          <div className="auth-footer">
            <span>已经有账号？</span>
            <Link to="/login">去登录</Link>
          </div>
        </div>
        <div className="auth-hero">
          <span className="auth-badge">策略资产 · 统一管理</span>
          <h1>将所有名单统一收拢</h1>
          <p>全局名单、应用名单、渠道名单一套控制台完成配置。</p>
          <div className="auth-grid">
            <div className="auth-grid__item">细粒度权限控制</div>
            <div className="auth-grid__item">风险规则可追溯</div>
            <div className="auth-grid__item">多进程缓存联动</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
