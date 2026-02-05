import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useParams, useSearchParams } from "react-router-dom";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { Table } from "@/components/Table";
import { EmptyState } from "@/components/EmptyState";
import { listDetailService } from "@/services/listDetailService";
import { useAuth } from "@/store/auth";
import type { ListDetail } from "@/types";

const NameListDetails: React.FC = () => {
  const { listNo } = useParams();
  const [searchParams] = useSearchParams();
  const listName = searchParams.get("name") || "";
  const { user } = useAuth();

  const [text, setText] = useState("");
  const [memo, setMemo] = useState("");
  const [searchText, setSearchText] = useState("");
  const [results, setResults] = useState<ListDetail[]>([]);

  const addMutation = useMutation({
    mutationFn: () =>
      listDetailService.addDetail({
        list_no: listNo || "",
        text,
        memo,
        username: user?.identity || "",
      }),
    onSuccess: () => {
      setText("");
      setMemo("");
    },
  });

  const searchMutation = useMutation({
    mutationFn: (keyword: string) => listDetailService.searchByText(keyword),
    onSuccess: (data) => setResults(data),
    onError: () => setResults([]),
  });

  const deleteMutation = useMutation({
    mutationFn: (detail: ListDetail) =>
      listDetailService.deleteByText({
        list_name: listName,
        text: detail.text,
        username: user?.identity || "",
      }),
    onSuccess: () => {
      if (searchText) {
        searchMutation.mutate(searchText);
      }
    },
  });

  if (!listNo) {
    return <EmptyState title="未找到名单" subtitle="请从名单列表进入" />;
  }

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>词条维护</h2>
          <p>名单编号：{listNo}</p>
          {listName && <p>名单名称：{listName}</p>}
        </div>
      </div>

      <div className="grid">
        <Card title="新增词条" subtitle="即时触发缓存更新" className="grid__span-4">
          <div className="form">
            <label className="form__field">
              <span>文本</span>
              <Input value={text} onChange={(e) => setText(e.target.value)} placeholder="输入词条内容" />
            </label>
            <label className="form__field">
              <span>备注</span>
              <Input value={memo} onChange={(e) => setMemo(e.target.value)} placeholder="可选" />
            </label>
            <Button disabled={!text || addMutation.isPending} onClick={() => addMutation.mutate()}>
              {addMutation.isPending ? "提交中..." : "新增词条"}
            </Button>
          </div>
        </Card>

        <Card title="查询词条" subtitle="当前后端仅支持按文本检索" className="grid__span-8">
          <div className="search-bar">
            <Input
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="输入关键词查询"
            />
            <Button
              tone="outline"
              disabled={!searchText || searchMutation.isPending}
              onClick={() => searchMutation.mutate(searchText)}
            >
              {searchMutation.isPending ? "查询中..." : "查询"}
            </Button>
          </div>

          {results.length === 0 ? (
            <EmptyState title="暂无结果" subtitle="输入关键词开始查询" />
          ) : (
            <Table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>名单编号</th>
                  <th>文本</th>
                  <th>备注</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {results.map((detail) => (
                  <tr key={detail.id || detail.text}>
                    <td>{detail.id}</td>
                    <td className="mono">{detail.list_no}</td>
                    <td>{detail.text}</td>
                    <td>{detail.memo || "-"}</td>
                    <td>
                      <Button
                        tone="danger"
                        size="sm"
                        disabled={!listName}
                        onClick={() => deleteMutation.mutate(detail)}
                      >
                        删除
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
          {!listName && (
            <p className="tip">
              删除需要 list_name，建议从名单列表点击“维护词条”进入以携带名单名称。
            </p>
          )}
        </Card>
      </div>
    </div>
  );
};

export default NameListDetails;
