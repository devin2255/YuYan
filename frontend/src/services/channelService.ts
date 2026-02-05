import { api, unwrap } from "@/services/http";
import type { ApiResponse, ChannelInfo } from "@/types";

export const channelService = {
  async list(): Promise<ChannelInfo[]> {
    const res = await api.get<ApiResponse<ChannelInfo[]>>("/channels");
    return unwrap(res.data);
  },
  async create(payload: { name: string; memo?: string; username: string }): Promise<string> {
    const res = await api.post<ApiResponse>("/channels", payload);
    return res.data.message || "创建成功";
  },
  async update(channelId: number, payload: { name: string; memo?: string }): Promise<string> {
    const res = await api.put<ApiResponse>(`/channels/${channelId}`, payload);
    return res.data.message || "更新成功";
  },
  async remove(channelId: number, payload: { username: string }): Promise<string> {
    const res = await api.delete<ApiResponse>(`/channels/${channelId}`, { data: payload });
    return res.data.message || "删除成功";
  },
};
