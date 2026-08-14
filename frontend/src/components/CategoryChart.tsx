import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CategoryCount } from "../api/types";

const PALETTE = ["#5b7cfa", "#8b5cf6", "#2dd4a7", "#f6c453", "#fb6f92", "#38bdf8", "#94a3b8", "#fb923c"];

export default function CategoryChart({ categories }: { categories: CategoryCount[] }) {
  if (categories.length === 0) {
    return <p className="text-sm text-slate-500 italic py-8 text-center">No categories yet.</p>;
  }

  const data = [...categories].sort((a, b) => b.count - a.count).slice(0, 8);

  return (
    <div className="h-64 -ml-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 4, bottom: 4 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="category"
            width={130}
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(255,255,255,0.03)" }}
            contentStyle={{
              background: "#0f1220",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 12,
              fontSize: 12,
              color: "#e2e8f0",
            }}
          />
          <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={16}>
            {data.map((_, idx) => (
              <Cell key={idx} fill={PALETTE[idx % PALETTE.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
