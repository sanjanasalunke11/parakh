import { LayoutDashboard, ShieldCheck } from "lucide-react";
import { NavLink } from "react-router-dom";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-base-950/80 backdrop-blur-xl">
      <div className="mx-auto max-w-6xl px-4 md:px-6 h-16 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-glow flex items-center justify-center shadow-glow">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-extrabold tracking-tight text-white">
            Para<span className="text-brand-400">kh</span>
          </span>
        </NavLink>

        <nav className="flex items-center gap-1">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `px-3.5 py-2 rounded-lg text-sm font-medium transition ${
                isActive ? "bg-white/[0.06] text-white" : "text-slate-400 hover:text-slate-200"
              }`
            }
          >
            Verify
          </NavLink>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `px-3.5 py-2 rounded-lg text-sm font-medium transition flex items-center gap-1.5 ${
                isActive ? "bg-white/[0.06] text-white" : "text-slate-400 hover:text-slate-200"
              }`
            }
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
