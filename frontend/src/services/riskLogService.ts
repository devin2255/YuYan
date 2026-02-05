import { api, maybeUnwrap } from "@/services/http";
import type { ApiResponse, RiskLogItem } from "@/types";

const useMock = String(import.meta.env.VITE_MOCK_RISK_LOGS || "").toLowerCase() === "1";

const mockLogs = (): RiskLogItem[] => {
  const now = Date.now();
  return Array.from({ length: 24 }).map((_, idx) => ({
    id: `log-${idx}`,
    app_id: idx % 2 === 0 ? "4001" : "5001",
    channel_id: idx % 3 === 0 ? "1" : "2",
    risk_type: idx % 3 === 0 ? 300 : 200,
    match_rule: idx % 2 === 0 ? 1 : 2,
    hit_text: idx % 3 === 0 ? "敏感词" : "广告",
    suggestion: idx % 2 === 0 ? "block" : "review",
    created_at: new Date(now - idx * 60_000 * 5).toISOString(),
    content_preview: "这是一次示例的命中内容片段，用于演示列表显示。",
  }));
};

export const riskLogService = {
  async list(params?: Record<string, unknown>): Promise<RiskLogItem[]> {
    if (useMock) return mockLogs();
    const res = await api.get<ApiResponse<RiskLogItem[]>>("/risk-logs", { params });
    return maybeUnwrap(res.data);
  },
};
