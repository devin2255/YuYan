import React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/Button";
import { Input } from "@/components/Input";
import { useAuth } from "@/store/auth";
import type { ApiError } from "@/types";

const schema = z.object({
  identity: z.string().min(1, "请输入用户名 / 邮箱 / 手机号"),
  password: z.string().min(6, "密码至少 6 位"),
});

type FormValues = z.infer<typeof schema>;

const Login: React.FC = () => {
  const { login } = useAuth();
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
      await login(values.identity, values.password);
      navigate("/apps");
    } catch (err) {
      const message = (err as ApiError)?.message || "登录失败";
      setNotice(message);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <div className="auth-hero">
          <span className="auth-badge">语燕风控 · 控制台</span>
          <h1>欢迎回来</h1>
          <p>一个账号即可管理应用接入、名单策略与风控日志。</p>
          <div className="auth-grid">
            <div className="auth-grid__item">多语种名单同步</div>
            <div className="auth-grid__item">AC Tree 实时更新</div>
            <div className="auth-grid__item">命中追溯与复核</div>
          </div>
        </div>
        <div className="auth-card">
          <h2>登录控制台</h2>
          <p className="auth-subtitle">账号支持 username / email / phone 任意一种</p>
          <form onSubmit={handleSubmit(onSubmit)} className="form">
            <label className="form__field">
              <span>账号</span>
              <Input placeholder="输入用户名 / 邮箱 / 手机号" {...register("identity")} />
              {errors.identity && <em>{errors.identity.message}</em>}
            </label>
            <label className="form__field">
              <span>密码</span>
              <Input type="password" placeholder="至少 6 位" {...register("password")} />
              {errors.password && <em>{errors.password.message}</em>}
            </label>
            <Button type="submit" size="lg" disabled={isSubmitting}>
              {isSubmitting ? "登录中..." : "进入控制台"}
            </Button>
            {notice && <div className="form__notice form__notice--error">{notice}</div>}
          </form>
          <div className="auth-footer">
            <span>没有账号？</span>
            <Link to="/register">去注册</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
