import { CheckCircle2, Flame, HelpCircle, Search, ShieldAlert, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchDashboardStats, fetchLedger, fetchLedgerDetail } from "../api/client";
import type { ClaimResult, DashboardStats, LedgerListItem, Verdict } from "../api/types";
import CategoryChart from "../components/CategoryChart";
import LedgerRow from "../components/LedgerRow";
import LoadingSpinner from "../components/LoadingSpinner";
import Modal from "../components/Modal";
import ResultCard from "../components/ResultCard";
import StatTile from "../components/StatTile";

const VERDICT_FILTERS: { label: string; value: Verdict | "" }[] = [
  { label: "All verdicts", value: "" },
  { label: "Verified", value: "VERIFIED" },
  { label: "False", value: "FALSE" },
  { label: "Misleading", value: "MISLEADING" },
  { label: "Unverified", value: "UNVERIFIED" },
];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [search, setSearch] = useState("");
  const [verdictFilter, setVerdictFilter] = useState<Verdict | "">("");
  const [items, setItems] = useState<LedgerListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loadingLedger, setLoadingLedger] = useState(false);
  const [selected, setSelected] = useState<ClaimResult | null>(null);
  const pageSize = 8;

  useEffect(() => {
    fetchDashboardStats().then(setStats).catch(() => setStats(null));
  }, []);

  useEffect(() => {
    setLoadingLedger(true);
    const timeout = setTimeout(() => {
      fetchLedger({ search: search || undefined, verdict: verdictFilter || undefined, page, page_size: pageSize })
        .then((res) => {
          setItems(res.items);
          setTotal(res.total);
        })
        .catch(() => {
          setItems([]);
          setTotal(0);
        })
        .finally(() => setLoadingLedger(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [search, verdictFilter, page]);

  const openDetail = (id: number) => {
    fetchLedgerDetail(id).then(setSelected).catch(() => {});
  };

  if (!stats) {
    return <LoadingSpinner label="Loading dashboard…" />;
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="mx-auto max-w-6xl px-4 md:px-6 py-10 md:py-14 space-y-10">
      <div className="animate-fade-in">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Public Verification Ledger</h1>
        <p className="text-slate-500 mt-1">Every claim Parakh has checked, and how it was resolved.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 animate-rise">
        <StatTile label="Total Checked" value={stats.total_claims} icon={Flame} accent="bg-brand-500/15 text-brand-300" />
        <StatTile label="Verified" value={stats.verified_count} icon={CheckCircle2} accent="bg-emerald-500/15 text-emerald-300" />
        <StatTile label="False" value={stats.false_count} icon={XCircle} accent="bg-rose-500/15 text-rose-300" />
        <StatTile label="Misleading" value={stats.misleading_count} icon={ShieldAlert} accent="bg-amber-500/15 text-amber-300" />
        <StatTile label="Unverified" value={stats.unverified_count} icon={HelpCircle} accent="bg-slate-500/15 text-slate-300" />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <h2 className="text-sm font-bold text-slate-200 mb-4">Claims by Category</h2>
          <CategoryChart categories={stats.categories} />
        </div>
        <div className="glass-panel p-6">
          <h2 className="text-sm font-bold text-slate-200 mb-4">Most Checked Claims</h2>
          <div className="space-y-2">
            {stats.most_checked.length === 0 && (
              <p className="text-sm text-slate-500 italic py-8 text-center">Nothing checked yet.</p>
            )}
            {stats.most_checked.map((item) => (
              <LedgerRow key={item.id} item={item} onClick={() => openDetail(item.id)} />
            ))}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <h2 className="text-sm font-bold text-slate-200">Searchable Verification History</h2>
          <div className="flex gap-2 flex-wrap">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                placeholder="Search claims…"
                className="input-field pl-9 py-2 text-sm w-56"
              />
            </div>
            <select
              value={verdictFilter}
              onChange={(e) => {
                setVerdictFilter(e.target.value as Verdict | "");
                setPage(1);
              }}
              className="input-field py-2 text-sm w-40"
            >
              {VERDICT_FILTERS.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-2 min-h-[200px]">
          {loadingLedger && <LoadingSpinner label="Searching ledger…" />}
          {!loadingLedger && items.length === 0 && (
            <p className="text-sm text-slate-500 italic py-12 text-center">No matching claims found.</p>
          )}
          {!loadingLedger &&
            items.map((item) => <LedgerRow key={item.id} item={item} onClick={() => openDetail(item.id)} />)}
        </div>

        {!loadingLedger && total > pageSize && (
          <div className="flex items-center justify-between mt-5 pt-4 border-t border-white/[0.06]">
            <p className="text-xs text-slate-500">
              Page {page} of {totalPages} · {total} claims
            </p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="btn-ghost !px-3 !py-1.5 text-sm"
              >
                Prev
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="btn-ghost !px-3 !py-1.5 text-sm"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {selected && (
        <Modal onClose={() => setSelected(null)}>
          <ResultCard result={selected} />
        </Modal>
      )}
    </div>
  );
}
