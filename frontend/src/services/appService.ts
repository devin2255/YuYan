import { api, maybeUnwrap, unwrap } from "@/services/http";
import type { ApiResponse, AppInfo } from "@/types";

export const appService = {
  async list(): Promise<AppInfo[]> {
    const res = await api.get<ApiResponse<AppInfo[]>>("/apps");
    return unwrap(res.data);
  },
  async get(appId: string): Promise<AppInfo> {
    const res = await api.get<ApiResponse<AppInfo>>(`/apps/${appId}`);
    return unwrap(res.data);
  },
  async create(payload: { app_id: string; name: string; username: string }): Promise<string> {
    const res = await api.post<ApiResponse>("/apps", payload);
    const data = maybeUnwrap(res.data);
    return res.data.message || (data as unknown as string) || "创建成功";
  },
  async update(appId: string, payload: { name: string; username: string }): Promise<string> {
    const res = await api.put<ApiResponse>(`/apps/${appId}`, payload);
    return res.data.message || "更新成功";
  },
  async remove(appId: string): Promise<string> {
    const res = await api.delete<ApiResponse>(`/apps/${appId}`);
    return res.data.message || "删除成功";
  },
};
