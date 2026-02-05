import React, { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { Select } from "@/components/Select";
import { Table } from "@/components/Table";
import { Pagination } from "@/components/Pagination";
import { Badge } from "@/components/Badge";
import { EmptyState } from "@/components/EmptyState";
import { appService } from "@/services/appService";
import { channelService } from "@/services/channelService";
import { nameListService, NameListPayload } from "@/services/nameListService";
import { queryClient } from "@/store/query";
import { useAuth } from "@/store/auth";
import type { AppInfo, ChannelInfo, NameList } from "@/types";

const pageSize = 6;

const defaultForm: Omit<NameListPayload, "username"> = {
  name: "",
  type: 1,
  match_rule: 1,
  match_type: 1,
  suggest: 2,
  risk_type: 300,
  status: 1,
  scope: "APP_CHANNEL",
  app_ids: [],
  channel_ids: [],
  language_scope: "ALL",
  language_codes: [],
};

const NameLists: React.FC = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState<NameList | null>(null);
  const [form, setForm] = useState(defaultForm);
  const [filters, setFilters] = useState({ scope: "", status: "" });

  const { data: apps = [] } = useQuery({ queryKey: ["apps"], queryFn: () => appService.list() });
  const { data: channels = [] } = useQuery({
    queryKey: ["channels"],
    queryFn: () => channelService.list(),
  });
  const { data: lists = [], isLoading } = useQuery({
    queryKey: ["name-lists"],
    queryFn: () => nameListService.list(),
  });

  const mutation = useMutation({
    mutationFn: (payload: NameListPayload) =>
      editing?.id ? nameListService.update(String(editing.id), payload) : nameListService.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["name-lists"] });
      setEditing(null);
      setForm(defaultForm);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (lid: string) => nameListService.remove(lid),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["name-lists"] }),
  });

  const filtered = useMemo(() => {
    return lists.filter((item) => {
      if (filters.scope && item.scope !== filters.scope) return false;
      if (filters.status && String(item.status) !== filters.status) return false;
      return true;
    });
  }, [lists, filters]);

  const paged = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, page]);

  const toggleApp = (appId: string) => {
    setForm((prev) => {
      const exists = prev.app_ids.includes(appId);
      if (!exists && prev.app_ids.length >= 5) return prev;
      return {
        ...prev,
        app_ids: exists ? prev.app_ids.filter((id) => id !== appId) : [...prev.app_ids, appId],
      };
    });
  };

  const toggleChannel = (channelId: number) => {
    setForm((prev) => {
      const exists = prev.channel_ids.includes(channelId);
      if (!exists && prev.channel_ids.length >= 5) return prev;
      return {
        ...prev,
        channel_ids: exists
          ? prev.channel_ids.filter((id) => id !== channelId)
          : [...prev.channel_ids, channelId],
      };
    });
  };

  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name) return;
    mutation.mutate({
      ...form,
      username: user?.identity || "",
    });
  };

  const onEdit = (item: NameList) => {
    setEditing(item);
    setForm({
      name: item.name,
      type: item.type,
      match_rule: item.match_rule,
      match_type: item.match_type,
      suggest: item.suggest,
      risk_type: item.risk_type,
      status: item.status,
      scope: item.scope,
      app_ids: item.app_ids || [],
      channel_ids: item.channel_ids || [],
      language_scope: item.language_scope || "ALL",
      language_codes: item.language_codes || [],
    });
  };

  const resetForm = () => {
    setEditing(null);
    setForm(defaultForm);
  };

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>名单维护</h2>
          <p>覆盖全局、应用、渠道三种作用域，并支持多语种策略。</p>
        </div>
      </div>

      <div className="grid">
        <Card
          title={editing ? "编辑名单" : "创建名单"}
          subtitle="scope + app_ids + channel_ids 规则已对齐后端"
          className="grid__span-4"
          actions={
            editing ? (
              <Button tone="ghost" size="sm" onClick={resetForm}>
                取消编辑
              </Button>
            ) : null
          }
        >
          <form className="form" onSubmit={onSubmit}>
            <label className="form__field">
              <span>名单名称</span>
              <Input value={form.name} onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))} />
            </label>
            <div className="form__row">
              <label className="form__field">
                <span>名单类型</span>
                <Select value={form.type} onChange={(e) => setForm((prev) => ({ ...prev, type: Number(e.target.value) }))}>
                  <option value={0}>白名单</option>
                  <option value={1}>敏感词</option>
                  <option value={2}>忽略词</option>
                </Select>
              </label>
              <label className="form__field">
                <span>匹配方式</span>
                <Select
                  value={form.match_type}
                  onChange={(e) => setForm((prev) => ({ ...prev, match_type: Number(e.target.value) }))}
                >
                  <option value={1}>原文匹配</option>
                  <option value={2}>语义匹配</option>
                </Select>
              </label>
            </div>
            <div className="form__row">
              <label className="form__field">
                <span>匹配规则</span>
                <Select
                  value={form.match_rule}
                  onChange={(e) => setForm((prev) => ({ ...prev, match_rule: Number(e.target.value) }))}
                >
                  <option value={0}>文本+昵称</option>
                  <option value={1}>文本</option>
                  <option value={2}>昵称</option>
                  <option value={3}>IP</option>
                  <option value={6}>账号</option>
                </Select>
              </label>
              <label className="form__field">
                <span>处置建议</span>
                <Select
                  value={form.suggest}
                  onChange={(e) => setForm((prev) => ({ ...prev, suggest: Number(e.target.value) }))}
                >
                  <option value={0}>拒绝</option>
                  <option value={1}>通过</option>
                  <option value={2}>审核</option>
                </Select>
              </label>
            </div>
            <div className="form__row">
              <label className="form__field">
                <span>风险类型</span>
                <Select
                  value={form.risk_type}
                  onChange={(e) => setForm((prev) => ({ ...prev, risk_type: Number(e.target.value) }))}
                >
                  <option value={100}>涉政</option>
                  <option value={200}>色情</option>
                  <option value={300}>广告</option>
                  <option value={400}>灌水</option>
                  <option value={600}>违禁</option>
                  <option value={700}>其他</option>
                </Select>
              </label>
              <label className="form__field">
                <span>状态</span>
                <Select
                  value={form.status}
                  onChange={(e) => setForm((prev) => ({ ...prev, status: Number(e.target.value) }))}
                >
                  <option value={1}>启用</option>
                  <option value={0}>停用</option>
                </Select>
              </label>
            </div>
            <label className="form__field">
              <span>作用域</span>
              <Select
                value={form.scope}
                onChange={(e) =>
                  setForm((prev) => {
                    const scope = e.target.value;
                    if (scope === "GLOBAL") {
                      return { ...prev, scope, app_ids: [], channel_ids: [] };
                    }
                    if (scope === "APP") {
                      return { ...prev, scope, channel_ids: [] };
                    }
                    return { ...prev, scope };
                  })
                }
              >
                <option value="GLOBAL">全局</option>
                <option value="APP">应用</option>
                <option value="APP_CHANNEL">应用+渠道</option>
              </Select>
            </label>
            {form.scope !== "GLOBAL" && (
              <div className="form__field">
                <span>应用范围</span>
                <div className="chip-list">
                  {apps.map((app: AppInfo) => (
                    <label key={app.app_id} className="chip">
                      <input
                        type="checkbox"
                        checked={form.app_ids.includes(app.app_id)}
                        onChange={() => toggleApp(app.app_id)}
                      />
                      <span>{app.name} ({app.app_id})</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
            {form.scope === "APP_CHANNEL" && (
              <div className="form__field">
                <span>渠道范围</span>
                <div className="chip-list">
                  {channels.map((channel: ChannelInfo) => (
                    <label key={channel.id} className="chip">
                      <input
                        type="checkbox"
                        checked={form.channel_ids.includes(channel.id || 0)}
                        onChange={() => channel.id && toggleChannel(channel.id)}
                      />
                      <span>{channel.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
            <label className="form__field">
              <span>语种范围</span>
              <Select
                value={form.language_scope}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    language_scope: e.target.value,
                    language_codes: e.target.value === "ALL" ? [] : prev.language_codes,
                  }))
                }
              >
                <option value="ALL">全部语种</option>
                <option value="SPECIFIC">指定语种</option>
              </Select>
            </label>
            {form.language_scope === "SPECIFIC" && (
              <label className="form__field">
                <span>语种代码</span>
                <Input
                  placeholder="例如 zh,en,ja"
                  value={form.language_codes.join(",")}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      language_codes: e.target.value
                        .split(",")
                        .map((item) => item.trim().toLowerCase())
                        .filter(Boolean),
                    }))
                  }
                />
              </label>
            )}
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "提交中..." : editing ? "保存更新" : "创建名单"}
            </Button>
          </form>
        </Card>

        <Card
          title="名单列表"
          subtitle={`共计 ${filtered.length} 个名单`}
          className="grid__span-8"
          actions={
            <div className="filters">
              <Select
                value={filters.scope}
                onChange={(e) => setFilters((prev) => ({ ...prev, scope: e.target.value }))}
              >
                <option value="">全部作用域</option>
                <option value="GLOBAL">全局</option>
                <option value="APP">应用</option>
                <option value="APP_CHANNEL">应用+渠道</option>
              </Select>
              <Select
                value={filters.status}
                onChange={(e) => setFilters((prev) => ({ ...prev, status: e.target.value }))}
              >
                <option value="">全部状态</option>
                <option value="1">启用</option>
                <option value="0">停用</option>
              </Select>
            </div>
          }
        >
          {isLoading ? (
            <div className="loading">加载中...</div>
          ) : filtered.length === 0 ? (
            <EmptyState title="暂无名单" subtitle="创建一个名单并配置作用域" />
          ) : (
            <>
              <Table>
                <thead>
                  <tr>
                    <th>编号</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>作用域</th>
                    <th>语种</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {paged.map((item: NameList) => (
                    <tr key={item.no}>
                      <td className="mono">{item.no}</td>
                      <td>{item.name}</td>
                      <td>{item.type === 0 ? "白名单" : item.type === 2 ? "忽略词" : "敏感词"}</td>
                      <td>{item.scope}</td>
                      <td>
                        {item.language_scope === "ALL" ? (
                          <Badge tone="info">ALL</Badge>
                        ) : (
                          <span className="mini-list">{(item.language_codes || []).join(", ")}</span>
                        )}
                      </td>
                      <td>
                        {item.status === 1 ? <Badge tone="success">启用</Badge> : <Badge tone="danger">停用</Badge>}
                      </td>
                      <td className="actions">
                        <Button tone="soft" size="sm" onClick={() => onEdit(item)}>
                          编辑
                        </Button>
                        <Link to={`/name-lists/${item.no}?name=${encodeURIComponent(item.name)}`} className="link">
                          维护词条
                        </Link>
                        <Button
                          tone="danger"
                          size="sm"
                          onClick={() => item.id && deleteMutation.mutate(String(item.id))}
                        >
                          删除
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              <Pagination page={page} pageSize={pageSize} total={filtered.length} onChange={setPage} />
            </>
          )}
        </Card>
      </div>
    </div>
  );
};

export default NameLists;
