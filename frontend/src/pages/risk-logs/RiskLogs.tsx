import React, { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import * as echarts from "echarts";

import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { Select } from "@/components/Select";
import { Table } from "@/components/Table";
import { Pagination } from "@/components/Pagination";
import { EmptyState } from "@/components/EmptyState";
import { riskLogService } from "@/services/riskLogService";
import { formatDateTime } from "@/utils/format";
import type { RiskLogItem } from "@/types";

const pageSize = 8;

const RiskLogs: React.FC = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ app_id: "", risk_type: "" });
  const chartRef = useRef<HTMLDivElement | null>(null);

  const { data = [], isLoading } = useQuery({
    queryKey: ["risk-logs", filters],
    queryFn: () => riskLogService.list(filters),
  });

  const filtered = useMemo(() => {
    return data.filter((item) => {
      if (filters.app_id && item.app_id !== filters.app_id) return false;
      if (filters.risk_type && String(item.risk_type) !== filters.risk_type) return false;
      return true;
    });
  }, [data, filters]);

  const paged = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, page]);

  useEffect(() => {
    if (!chartRef.current) return;
    const instance = echarts.init(chartRef.current);
    const timeSeries = filtered
      .slice()
      .reverse()
      .map((item) => ({ time: item.created_at, value: 1 }));
    instance.setOption({
      tooltip: { trigger: "axis" },
      grid: { left: 20, right: 10, top: 20, bottom: 30, containLabel: true },
      xAxis: {
        type: "category",
        data: timeSeries.map((item) => formatDateTime(item.time)),
        axisLabel: { color: "#334" },
      },
      yAxis: { type: "value", minInterval: 1 },
      series: [
        {
          type: "line",
          data: timeSeries.map((item) => item.value),
          smooth: true,
          lineStyle: { color: "#e4572e", width: 3 },
          areaStyle: { color: "rgba(228,87,46,0.18)" },
        },
      ],
    });
    const resize = () => instance.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      instance.dispose();
    };
  }, [filtered]);

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h2>风控日志</h2>
          <p>按应用、风险类型过滤命中记录，并查看趋势。</p>
        </div>
      </div>

      <div className="grid">
        <Card title="实时命中趋势" subtitle="最近命中时间分布" className="grid__span-5">
          <div ref={chartRef} className="chart" />
        </Card>
        <Card title="筛选条件" subtitle="支持前端筛选" className="grid__span-7">
          <div className="filter-grid">
            <label className="form__field">
              <span>应用 ID</span>
              <Input
                placeholder="例如 4001"
                value={filters.app_id}
                onChange={(e) => setFilters((prev) => ({ ...prev, app_id: e.target.value }))}
              />
            </label>
            <label className="form__field">
              <span>风险类型</span>
              <Select
                value={filters.risk_type}
                onChange={(e) => setFilters((prev) => ({ ...prev, risk_type: e.target.value }))}
              >
                <option value="">全部</option>
                <option value="100">涉政</option>
                <option value="200">色情</option>
                <option value="300">广告</option>
                <option value="400">灌水</option>
                <option value="600">违禁</option>
              </Select>
            </label>
          </div>
        </Card>
      </div>

      <Card title="命中列表" subtitle={`共计 ${filtered.length} 条`}>
        {isLoading ? (
          <div className="loading">加载中...</div>
        ) : filtered.length === 0 ? (
          <EmptyState title="暂无命中" subtitle="调整筛选条件或稍后刷新" />
        ) : (
          <>
            <Table>
              <thead>
                <tr>
                  <th>时间</th>
                  <th>应用</th>
                  <th>渠道</th>
                  <th>风险类型</th>
                  <th>命中文本</th>
                  <th>建议</th>
                </tr>
              </thead>
              <tbody>
                {paged.map((item: RiskLogItem) => (
                  <tr key={item.id}>
                    <td>{formatDateTime(item.created_at)}</td>
                    <td>{item.app_id}</td>
                    <td>{item.channel_id || "-"}</td>
                    <td>{item.risk_type}</td>
                    <td>{item.hit_text || item.content_preview || "-"}</td>
                    <td>{item.suggestion || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
            <Pagination page={page} pageSize={pageSize} total={filtered.length} onChange={setPage} />
          </>
        )}
      </Card>
    </div>
  );
};

export default RiskLogs;
