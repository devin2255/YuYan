import { api, unwrap } from "@/services/http";
import type { ApiResponse, NameList } from "@/types";

export interface NameListPayload {
  name: string;
  type: number;
  match_rule: number;
  match_type: number;
  suggest: number;
  risk_type: number;
  status: number;
  scope: "GLOBAL" | "APP" | "APP_CHANNEL" | string;
  app_ids: string[];
  channel_ids: number[];
  language_scope: "ALL" | "SPECIFIC" | string;
  language_codes: string[];
  username: string;
}

export const nameListService = {
  async list(): Promise<NameList[]> {
    const res = await api.get<NameList[]>("/name-lists");
    return res.data;
  },
  async get(lid: string): Promise<NameList> {
    const res = await api.get<NameList>(`/name-lists/${lid}`);
    return res.data;
  },
  async create(payload: NameListPayload): Promise<string> {
    const res = await api.post<ApiResponse>("/name-lists", payload);
    return res.data.message || "创建成功";
  },
  async update(lid: string, payload: NameListPayload): Promise<string> {
    const res = await api.put<ApiResponse>(`/name-lists/${lid}`, payload);
    return res.data.message || "更新成功";
  },
  async remove(lid: string): Promise<string> {
    const res = await api.delete<ApiResponse>(`/name-lists/${lid}`);
    return res.data.message || "删除成功";
  },
  async switchStatus(lid: string, status: number, username: string): Promise<string> {
    const res = await api.patch<ApiResponse>(`/name-lists/${lid}/status`, { status, username });
    return res.data.message || "更新成功";
  },
};
