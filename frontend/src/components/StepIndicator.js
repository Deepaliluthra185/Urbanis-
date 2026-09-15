import { useNavigate } from "react-router-dom";
import { Check } from "lucide-react";

const STEPS = [
  { key: "site", n: 1, label: "Site Validation" },
  { key: "design", n: 2, label: "Design & Costing" },
  { key: "formulation", n: 3, label: "AI Formulation" },
  { key: "summary", n: 4, label: "Summary / Export" },
];

export default function StepIndicator({ projectId, activeStep }) {
  const navigate = useNavigate();
  const activeIdx = STEPS.findIndex((s) => s.key === activeStep);

  return (
    <nav className="flex items-center gap-1 overflow-x-auto no-scrollbar" data-testid="step-indicator">
      {STEPS.map((s, i) => {
        const done = i < activeIdx;
        const active = i === activeIdx;
        return (
          <div key={s.key} className="flex items-center">
            <button
              onClick={() => navigate(`/project/${projectId}/${s.key}`)}
              data-testid={`nav-step-${s.n}`}
              className={`flex items-center gap-2 px-2 lg:px-3 py-1.5 transition-colors group ${
                active ? "" : "opacity-70 hover:opacity-100"
              }`}
            >
              <span
                className={`w-6 h-6 shrink-0 flex items-center justify-center text-[11px] font-mono font-semibold border ${
                  active
                    ? "bg-zinc-100 text-black border-zinc-100"
                    : done
                    ? "bg-green-500/15 text-green-400 border-green-500/40"
                    : "bg-transparent text-zinc-500 border-zinc-700"
                }`}
              >
                {done ? <Check className="w-3.5 h-3.5" /> : s.n}
              </span>
              <span
                className={`hidden lg:block text-xs font-medium whitespace-nowrap ${
                  active ? "text-zinc-100" : "text-zinc-500 group-hover:text-zinc-300"
                }`}
              >
                {s.label}
              </span>
            </button>
            {i < STEPS.length - 1 && <div className="w-4 lg:w-6 h-px bg-zinc-800" />}
          </div>
        );
      })}
    </nav>
  );
}
