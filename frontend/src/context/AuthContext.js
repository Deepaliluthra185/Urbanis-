import { createContext, useContext, useEffect, useState } from "react";
import api, { formatApiError } from "../lib/api";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // null = checking, false = anon, obj = user
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("urbanis_token");
    if (!token) {
      setUser(false);
      setReady(true);
      return;
    }
    api.get("/auth/me")
      .then(({ data }) => setUser(data))
      .catch(() => {
        localStorage.removeItem("urbanis_token");
        setUser(false);
      })
      .finally(() => setReady(true));
  }, []);

  const login = async (email, password) => {
    try {
      const { data } = await api.post("/auth/login", { email, password });
      localStorage.setItem("urbanis_token", data.token);
      setUser(data.user);
      return { ok: true };
    } catch (e) {
      return { ok: false, error: formatApiError(e.response?.data?.detail) || e.message };
    }
  };

  const register = async (name, email, password) => {
    try {
      const { data } = await api.post("/auth/register", { name, email, password });
      localStorage.setItem("urbanis_token", data.token);
      setUser(data.user);
      return { ok: true };
    } catch (e) {
      return { ok: false, error: formatApiError(e.response?.data?.detail) || e.message };
    }
  };

  const logout = () => {
    localStorage.removeItem("urbanis_token");
    setUser(false);
  };

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
