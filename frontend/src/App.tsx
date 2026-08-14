import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import DashboardPage from "./pages/DashboardPage";
import HomePage from "./pages/HomePage";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
      <footer className="border-t border-white/[0.06] py-6 text-center text-xs text-slate-600">
        Parakh — an independent Truth Agent core, ready to plug into WhatsApp, web, or any future channel.
      </footer>
    </div>
  );
}
