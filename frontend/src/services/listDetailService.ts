import { api } from "@/services/http";
import type { ApiResponse, ListDetail } from "@/types";

export const listDetailService = {
  async getDetail(id: number): Promise<ListDetail> {
    const res = await api.get<ListDetail>(`/list-details/${id}`);
    return res.data;
  },
  async searchByText(text: string): Promise<ListDetail[]> {
    const res = await api.get<ListDetail[]>("/list-details/search", { params: { text } });
    return res.data;
  },
  async addDetail(payload: { list_no: string; text: string; memo?: string; username: string }): Promise<string> {
    const res = await api.post<ApiResponse>("/list-details", payload);
    return res.data.message || "新增成功";
  },
  async addBatch(payload: { list_no: string; data: string[]; username: string }): Promise<string> {
    const res = await api.post<ApiResponse>("/list-details/batch", payload);
    return res.data.message || "新增成功";
  },
  async updateDetail(id: number, payload: { text: string; memo?: string; username: string }): Promise<string> {
    const res = await api.put<ApiResponse>(`/list-details/${id}`, payload);
    return res.data.message || "更新成功";
  },
  async deleteDetail(id: number, payload: { username: string }): Promise<string> {
    const res = await api.delete<ApiResponse>(`/list-details/${id}`, { data: payload });
    return res.data.message || "删除成功";
  },
  async deleteBatch(payload: { ids: number[]; username: string }): Promise<string> {
    const res = await api.delete<ApiResponse>("/list-details/batch", { data: payload });
    return res.data.message || "删除成功";
  },
  async deleteByText(payload: { list_name: string; text: string; username: string }): Promise<string> {
    const res = await api.delete<ApiResponse>("/list-details/by-text", { data: payload });
    return res.data.message || "删除成功";
  },
};
