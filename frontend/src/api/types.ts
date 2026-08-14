export type Verdict = "VERIFIED" | "FALSE" | "MISLEADING" | "UNVERIFIED";
export type EvidenceStrength = "LOW" | "MEDIUM" | "HIGH";
export type InputType = "text" | "image" | "url" | "voice";
export type ReliabilityTier = "HIGH" | "MEDIUM" | "LOW";

export interface EvidenceItemOut {
  source_name: string;
  source_url: string;
  snippet: string;
  reliability: ReliabilityTier;
}

export interface ClaimResult {
  id: number;
  original_text: string;
  normalized_claim: string;
  verdict: Verdict;
  evidence_strength: EvidenceStrength;
  explanation: string;
  category: string;
  input_type: InputType;
  source_url: string | null;
  sources: EvidenceItemOut[];
  previously_verified: boolean;
  check_count: number;
  created_at: string;
}

export interface LedgerListItem {
  id: number;
  normalized_claim: string;
  verdict: Verdict;
  evidence_strength: EvidenceStrength;
  category: string;
  input_type: InputType;
  check_count: number;
  created_at: string;
}

export interface LedgerListResponse {
  total: number;
  page: number;
  page_size: number;
  items: LedgerListItem[];
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface DashboardStats {
  total_claims: number;
  verified_count: number;
  false_count: number;
  misleading_count: number;
  unverified_count: number;
  total_checks: number;
  categories: CategoryCount[];
  most_checked: LedgerListItem[];
  recent: LedgerListItem[];
}

export interface ApiError {
  detail: string;
}
