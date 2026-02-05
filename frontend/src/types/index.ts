export interface ApiResponse<T = unknown> {
  code?: number;
  message?: string;
  data?: T;
  requestId?: string;
}

export class ApiError extends Error {
  code?: number;
  constructor(message: string, code?: number) {
    super(message);
    this.code = code;
  }
}

export interface AuthUser {
  id?: string;
  displayName: string;
  identity: string;
  roles?: string[];
}

export interface AppInfo {
  id?: number;
  app_id: string;
  name: string;
  access_key?: string;
}

export interface ChannelInfo {
  id?: number;
  name: string;
  memo?: string;
}

export interface NameList {
  id?: number;
  no: string;
  name: string;
  type: number;
  match_rule: number;
  match_type: number;
  suggest: number;
  risk_type: number;
  status: number;
  scope: "GLOBAL" | "APP" | "APP_CHANNEL" | string;
  language_scope: "ALL" | "SPECIFIC" | string;
  language?: string;
  language_codes?: string[];
  app_ids?: string[];
  channel_ids?: number[];
}

export interface ListDetail {
  id?: number;
  list_id?: number;
  list_no: string;
  text: string;
  memo?: string;
}

export interface RiskLogItem {
  id: string;
  app_id: string;
  channel_id?: string | number;
  risk_type: number | string;
  match_rule?: number | string;
  hit_text?: string;
  suggestion?: string;
  created_at: string;
  content_preview?: string;
}
