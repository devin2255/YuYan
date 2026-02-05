import React, { useMemo, useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { Select } from "@/components/Select";
import { textCheckService } from "@/services/textCheckService";
import type { ApiError } from "@/types";

const defaultPayload = {
  access_key: "",
  ugc_source: "text",
  app_id: "",
  channel: "",
  text: "",
  nickname: "test_user",
  account_id: "10001",
  role_id: "r001",
  server_id: "s001",
  vip_level: 0,
  level: 1,
  ip: "127.0.0.1",
};

const TextCheck: React.FC = () => {
  const [form, setForm] = useState(defaultPayload);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);

  const payload = useMemo(() => {
    return {
      access_key: form.access_key.trim(),
      ugc_source: form.ugc_source,
      data: {
        timestamp: Date.now(),
        token_id: null,
        nickname: form.nickname,
        text: form.text,
        server_id: form.server_id,
        account_id: form.account_id,
        app_id: form.app_id,
        role_id: form.role_id,
        vip_level: Number(form.vip_level) || 0,
        level: Number(form.level) || 0,
        ip: form.ip,
        channel: form.channel,
      },
    };
  }, [form]);

  const onSubmit = async () => {
    setLoading(true);
    setNotice("");
    try {
      const data = await textCheckService.check(payload);
      setResult(data);
    } catch (err) {
      const message = (err as ApiError)?.message || "检测失败";
      setNotice(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>文本风控测试</h2>
          <p>用于测试名单命中与拦截效果，直接调用 /moderation/text。</p>
        </div>
      </div>

      <div className="grid">
        <Card title="请求参数" subtitle="必填字段已内置，按需修改" className="grid__span-5">
          <div className="form">
            <label className="form__field">
              <span>Access Key</span>
              <Input
                placeholder="应用的 access_key"
                value={form.access_key}
                onChange={(e) => setForm((prev) => ({ ...prev, access_key: e.target.value }))}
              />
            </label>
            <label className="form__field">
              <span>UGC Source</span>
              <Select
                value={form.ugc_source}
                onChange={(e) => setForm((prev) => ({ ...prev, ugc_source: e.target.value }))}
              >
                <option value="text">text</option>
                <option value="nickname">nickname</option>
                <option value="comment">comment</option>
              </Select>
            </label>
            <label className="form__field">
              <span>App ID</span>
              <Input value={form.app_id} onChange={(e) => setForm((prev) => ({ ...prev, app_id: e.target.value }))} />
            </label>
            <label className="form__field">
              <span>Channel</span>
              <Input value={form.channel} onChange={(e) => setForm((prev) => ({ ...prev, channel: e.target.value }))} />
            </label>
            <label className="form__field">
              <span>文本内容</span>
              <Input value={form.text} onChange={(e) => setForm((prev) => ({ ...prev, text: e.target.value }))} />
            </label>
            <div className="form__row">
              <label className="form__field">
                <span>昵称</span>
                <Input
                  value={form.nickname}
                  onChange={(e) => setForm((prev) => ({ ...prev, nickname: e.target.value }))}
                />
              </label>
              <label className="form__field">
                <span>账号 ID</span>
                <Input
                  value={form.account_id}
                  onChange={(e) => setForm((prev) => ({ ...prev, account_id: e.target.value }))}
                />
              </label>
            </div>
            <div className="form__row">
              <label className="form__field">
                <span>角色 ID</span>
                <Input
                  value={form.role_id}
                  onChange={(e) => setForm((prev) => ({ ...prev, role_id: e.target.value }))}
                />
              </label>
              <label className="form__field">
                <span>服务器 ID</span>
                <Input
                  value={form.server_id}
                  onChange={(e) => setForm((prev) => ({ ...prev, server_id: e.target.value }))}
                />
              </label>
            </div>
            <div className="form__row">
              <label className="form__field">
                <span>VIP 等级</span>
                <Input
                  type="number"
                  value={form.vip_level}
                  onChange={(e) => setForm((prev) => ({ ...prev, vip_level: e.target.value }))}
                />
              </label>
              <label className="form__field">
                <span>等级</span>
                <Input
                  type="number"
                  value={form.level}
                  onChange={(e) => setForm((prev) => ({ ...prev, level: e.target.value }))}
                />
              </label>
            </div>
            <label className="form__field">
              <span>IP</span>
              <Input value={form.ip} onChange={(e) => setForm((prev) => ({ ...prev, ip: e.target.value }))} />
            </label>
            <Button disabled={loading} onClick={onSubmit}>
              {loading ? "检测中..." : "开始检测"}
            </Button>
            {notice && <div className="form__notice form__notice--error">{notice}</div>}
          </div>
        </Card>

        <Card title="检测结果" subtitle="原始响应" className="grid__span-7">
          {result ? (
            <pre className="code-block">{JSON.stringify(result, null, 2)}</pre>
          ) : (
            <div className="empty">尚未检测，填写参数后点击开始检测。</div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default TextCheck;
