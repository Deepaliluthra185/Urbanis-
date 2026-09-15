import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Boxes, Loader2, ArrowRight } from "lucide-react";
import { toast } from "sonner";

export default function LoginPage() {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("admin@urbanis.ai");
  const [password, setPassword] = useState("urbanis2025");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (user) navigate("/");
  }, [user, navigate]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    const res = mode === "login" ? await login(email, password) : await register(name, email, password);
    setBusy(false);
    if (res.ok) {
      toast.success(mode === "login" ? "Signed in" : "Account created");
      navigate("/");
    } else {
      toast.error(res.error);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-[#09090b]">
      {/* Left — brand / visual */}
      <div className="relative hidden lg:flex flex-col justify-between p-12 border-r border-zinc-800 grid-bg overflow-hidden">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 border border-zinc-100 flex items-center justify-center">
            <Boxes className="w-5 h-5 text-zinc-100" />
          </div>
          <span className="font-display font-bold text-xl tracking-tight text-zinc-100">
            URBANIS<span className="text-zinc-500">AI</span>
          </span>
        </div>
        <div className="relative z-10 max-w-lg">
          <p className="eyebrow mb-4">Planning · Validation · Costing</p>
          <h1 className="font-display font-black text-5xl xl:text-6xl leading-[0.95] tracking-tight text-zinc-100 uppercase">
            From raw site<br />to submission-<br />ready plan.
          </h1>
          <p className="mt-6 text-zinc-400 text-base leading-relaxed">
            An AI-driven workspace for modular, sustainable housing. Validate parcels against flood and
            ecological vetoes, cost every module by carbon and capital, and compile a municipal dossier.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-px bg-zinc-800 border border-zinc-800">
          {[["6", "AI Agents"], ["4", "Step Workflow"], ["100%", "Grounded Data"]].map(([v, l]) => (
            <div key={l} className="bg-[#09090b] p-4">
              <div className="font-display font-bold text-2xl text-zinc-100">{v}</div>
              <div className="eyebrow mt-1">{l}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Right — form */}
      <div className="flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-10">
            <div className="w-9 h-9 border border-zinc-100 flex items-center justify-center">
              <Boxes className="w-5 h-5 text-zinc-100" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight text-zinc-100">URBANIS<span className="text-zinc-500">AI</span></span>
          </div>

          <p className="eyebrow mb-2">{mode === "login" ? "Welcome back" : "Create account"}</p>
          <h2 className="font-display font-bold text-3xl tracking-tight text-zinc-100 mb-8">
            {mode === "login" ? "Sign in" : "Register"}
          </h2>

          <form onSubmit={submit} className="space-y-4" data-testid="auth-form">
            {mode === "register" && (
              <Field label="Full name">
                <input
                  data-testid="input-name" required value={name} onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#121215] border border-zinc-800 focus:border-zinc-500 outline-none px-3 py-2.5 text-sm text-zinc-100 transition-colors"
                  placeholder="Jane Planner"
                />
              </Field>
            )}
            <Field label="Email">
              <input
                data-testid="input-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#121215] border border-zinc-800 focus:border-zinc-500 outline-none px-3 py-2.5 text-sm text-zinc-100 transition-colors"
                placeholder="you@studio.com"
              />
            </Field>
            <Field label="Password">
              <input
                data-testid="input-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#121215] border border-zinc-800 focus:border-zinc-500 outline-none px-3 py-2.5 text-sm text-zinc-100 transition-colors"
                placeholder="••••••••"
              />
            </Field>

            <button
              type="submit" disabled={busy} data-testid="auth-submit-btn"
              className="w-full bg-zinc-100 text-black font-semibold text-sm py-3 flex items-center justify-center gap-2 hover:bg-white disabled:opacity-60 transition-colors group"
            >
              {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                <>{mode === "login" ? "Enter workspace" : "Create account"}<ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" /></>
              )}
            </button>
          </form>

          <p className="mt-6 text-sm text-zinc-500">
            {mode === "login" ? "No account yet?" : "Already registered?"}{" "}
            <button
              onClick={() => setMode(mode === "login" ? "register" : "login")}
              className="text-zinc-100 underline underline-offset-4 hover:text-white"
              data-testid="auth-toggle-btn"
            >
              {mode === "login" ? "Create one" : "Sign in"}
            </button>
          </p>
          <p className="mt-8 eyebrow text-zinc-600">Demo · admin@urbanis.ai / urbanis2025</p>
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="eyebrow block mb-1.5">{label}</span>
      {children}
    </label>
  );
}
