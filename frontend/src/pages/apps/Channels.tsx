import React, { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { Table } from "@/components/Table";
import { Pagination } from "@/components/Pagination";
import { EmptyState } from "@/components/EmptyState";
import { channelService } from "@/services/channelService";
import { queryClient } from "@/store/query";
import { useAuth } from "@/store/auth";
import type { ChannelInfo } from "@/types";

const pageSize = 8;

const Channels: React.FC = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [form, setForm] = useState({ name: "", memo: "" });

  const { data = [], isLoading } = useQuery({
    queryKey: ["channels"],
    queryFn: () => channelService.list(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: { name: string; memo?: string; username: string }) => channelService.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["channels"] });
      setForm({ name: "", memo: "" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (channelId: number) => channelService.remove(channelId, { username: user?.identity || "" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["channels"] }),
  });

  const paged = useMemo(() => {
    const start = (page - 1) * pageSize;
    return data.slice(start, start + pageSize);
  }, [data, page]);

  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name) return;
    createMutation.mutate({
      name: form.name,
      memo: form.memo,
      username: user?.identity || "",
    });
  };

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>渠道管理</h2>
          <p>维护渠道入口，用于名单绑定与审计。</p>
        </div>
      </div>

      <div className="grid">
        <Card title="新增渠道" subtitle="支持自定义备注" className="grid__span-4">
          <form className="form" onSubmit={onSubmit}>
            <label className="form__field">
              <span>渠道名称</span>
              <Input
                placeholder="例如 AppStore"
                value={form.name}
                onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              />
            </label>
            <label className="form__field">
              <span>备注</span>
              <Input
                placeholder="可选"
                value={form.memo}
                onChange={(e) => setForm((prev) => ({ ...prev, memo: e.target.value }))}
              />
            </label>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "创建中..." : "创建渠道"}
            </Button>
          </form>
        </Card>

        <Card title="渠道列表" subtitle={`共计 ${data.length} 个渠道`} className="grid__span-8">
          {isLoading ? (
            <div className="loading">加载中...</div>
          ) : data.length === 0 ? (
            <EmptyState title="暂无渠道" subtitle="先新增一个渠道" />
          ) : (
            <>
              <Table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>备注</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {paged.map((channel: ChannelInfo) => (
                    <tr key={channel.id}>
                      <td>{channel.id}</td>
                      <td>{channel.name}</td>
                      <td>{channel.memo || "-"}</td>
                      <td>
                        <Button
                          tone="danger"
                          size="sm"
                          onClick={() => channel.id && deleteMutation.mutate(channel.id)}
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

export default Channels;
