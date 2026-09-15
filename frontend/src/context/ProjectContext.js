import { createContext, useContext, useState, useCallback } from "react";
import api from "../lib/api";

const ProjectContext = createContext(null);
export const useProject = () => useContext(ProjectContext);

export function ProjectProvider({ children }) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadProject = useCallback(async (id) => {
    setLoading(true);
    try {
      const { data } = await api.get(`/projects/${id}`);
      setProject(data);
      localStorage.setItem("urbanis_project", id);
      return data;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProject = useCallback(async (id, patch) => {
    const { data } = await api.put(`/projects/${id}`, patch);
    setProject(data);
    return data;
  }, []);

  const runAgent = useCallback(async (id, agentId) => {
    const { data } = await api.post(`/projects/${id}/agents/${agentId}`);
    setProject((prev) => (prev ? { ...prev, agents: { ...prev.agents, [agentId]: data } } : prev));
    return data;
  }, []);

  return (
    <ProjectContext.Provider value={{ project, setProject, loading, loadProject, updateProject, runAgent }}>
      {children}
    </ProjectContext.Provider>
  );
}
