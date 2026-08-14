import axios, { AxiosError } from "axios";
import type { ClaimResult, DashboardStats, LedgerListResponse } from "./types";

// In dev, Vite proxies /api -> the FastAPI backend (see vite.config.ts).
// In production, set VITE_API_BASE_URL to the deployed backend origin.
const baseURL = import.meta.env.VITE_API_BASE_URL || "";

const client = axios.create({ baseURL, timeout: 30000 });

export class ApiRequestError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
  }
}

function unwrap(error: unknown): never {
  const axiosErr = error as AxiosError<{ detail?: string }>;
  const detail = axiosErr.response?.data?.detail;
  const message = detail || axiosErr.message || "Something went wrong. Please try again.";
  throw new ApiRequestError(message, axiosErr.response?.status);
}

export async function verifyText(text: string): Promise<ClaimResult> {
  try {
    const { data } = await client.post<ClaimResult>("/api/verify/text", { text });
    return data;
  } catch (e) {
    unwrap(e);
  }
}

export async function verifyVoice(text: string, language: "en" | "hi" = "en"): Promise<ClaimResult> {
  try {
    const { data } = await client.post<ClaimResult>("/api/verify/voice", { text, language });
    return data;
  } catch (e) {
    unwrap(e);
  }
}

export async function verifyUrl(url: string): Promise<ClaimResult> {
  try {
    const { data } = await client.post<ClaimResult>("/api/verify/url", { url });
    return data;
  } catch (e) {
    unwrap(e);
  }
}

export async function verifyImage(file: File): Promise<ClaimResult> {
  const form = new FormData();
  form.append("file", file);
  try {
    const { data } = await client.post<ClaimResult>("/api/verify/image", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  } catch (e) {
    unwrap(e);
  }
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const { data } = await client.get<DashboardStats>("/api/dashboard/stats");
    return data;
  } catch (e) {
    unwrap(e);
  }
}

export interface LedgerQuery {
  search?: string;
  verdict?: string;
  category?: string;
  page?: number;
  page_size?: number;
}

export async function fetchLedger(query: LedgerQuery): Promise<LedgerListResponse> {
  try {
    const { data } = await client.get<LedgerListResponse>("/api/ledger", { params: query });
    return data;
  } catch (e) {
    unwrap(e);
  }
}

export async function fetchLedgerDetail(id: number): Promise<ClaimResult> {
  try {
    const { data } = await client.get<ClaimResult>(`/api/ledger/${id}`);
    return data;
  } catch (e) {
    unwrap(e);
  }
}
