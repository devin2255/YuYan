import { api } from "@/services/http";
import { ApiError } from "@/types";

export interface TextCheckPayload {
  access_key: string;
  ugc_source: string;
  data: Record<string, unknown>;
}

export const textCheckService = {
  async check(payload: TextCheckPayload): Promise<Record<string, unknown>> {
    const res = await api.post("/moderation/text", payload);
    const data = res.data as Record<string, unknown>;
    if (data && typeof data.code === "number" && data.code !== 0) {
      throw new ApiError(String(data.message || "检测失败"), Number(data.code));
    }
    return data;
  },
};
