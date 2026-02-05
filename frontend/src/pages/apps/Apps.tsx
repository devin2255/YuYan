import React, { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { Table } from "@/components/Table";
import { Pagination } from "@/components/Pagination";
import { EmptyState } from "@/components/EmptyState";
import { appService } from "@/services/appService";
import { queryClient } from "@/store/query";
import { useAuth } from "@/store/auth";
import type { AppInfo, ApiError } from "@/types";

const pageSize = 8;

const Apps: React.FC = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [form, setForm] = useState({ app_id: "", name: "" });
  const [notice, setNotice] = useState("");

  const { data = [], isLoading } = useQuery({
    queryKey: ["apps"],
    queryFn: () => appService.list(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: { app_id: string; name: string; username: string }) => appService.create(payload),
    onSuccess: (message) => {
      queryClient.invalidateQueries({ queryKey: ["apps"] });
      setForm({ app_id: "", name: "" });
      setNotice(message || "创建成功");
    },
    onError: (err) => {
      const message = (err as ApiError)?.message || "创建失败";
      setNotice(message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (appId: string) => appService.remove(appId),
    onSuccess: (message) => {
      queryClient.invalidateQueries({ queryKey: ["apps"] });
      setNotice(message || "删除成功");
    },
    onError: (err) => {
      const message = (err as ApiError)?.message || "删除失败";
      setNotice(message);
    },
  });

  const paged = useMemo(() => {
    const start = (page - 1) * pageSize;
    return data.slice(start, start + pageSize);
  }, [data, page]);

  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.app_id || !form.name) return;
    createMutation.mutate({
      app_id: form.app_id,
      name: form.name,
      username: user?.identity || "",
    });
  };

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>应用接入</h2>
          <p>维护应用 ID 与密钥，统一接入风控能力。</p>
        </div>
      </div>

      <div className="grid">
        <Card title="新建应用" subtitle="创建后生成 access_key（后端返回）" className="grid__span-4">
          <form className="form" onSubmit={onSubmit}>
            <label className="form__field">
              <span>应用 ID</span>
              <Input
                placeholder="例如 5001"
                value={form.app_id}
                onChange={(e) => setForm((prev) => ({ ...prev, app_id: e.target.value }))}
              />
            </label>
            <label className="form__field">
              <span>应用名称</span>
              <Input
                placeholder="例如 社区业务"
                value={form.name}
                onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              />
            </label>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "创建中..." : "创建应用"}
            </Button>
            {notice && <p className="tip">{notice}</p>}
          </form>
        </Card>

        <Card title="应用列表" subtitle={`共计 ${data.length} 个应用`} className="grid__span-8">
          {isLoading ? (
            <div className="loading">加载中...</div>
          ) : data.length === 0 ? (
            <EmptyState title="暂无应用" subtitle="先创建一个应用用于接入" />
          ) : (
            <>
              <Table>
                <thead>
                  <tr>
                    <th>App ID</th>
                    <th>名称</th>
                    <th>Access Key</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {paged.map((app: AppInfo) => (
                    <tr key={app.app_id}>
                      <td>{app.app_id}</td>
                      <td>{app.name}</td>
                      <td>{app.access_key || "-"}</td>
                      <td>
                        <Button
                          tone="danger"
                          size="sm"
                          onClick={() => deleteMutation.mutate(app.app_id)}
                        >
                          删除
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              <Pagination page={page} pageSize={pageSize} total={data.length} onChange={setPage} />
            </>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Apps;
