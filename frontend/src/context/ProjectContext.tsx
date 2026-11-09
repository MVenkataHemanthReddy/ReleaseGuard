import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { Project } from '@/lib/api'
import { api } from '@/lib/api'

// Demo token - auto-save on first load
const DEMO_TOKEN = 'SpiFECk63Y3cwxUgA2f9eRvhz4lqTXVsKAF2YcN1JII'

interface ProjectContextType {
  currentProject: Project | null
  setCurrentProject: (project: Project | null) => void
  projects: Project[]
  setProjects: (projects: Project[]) => void
  createProject: (data: { name: string; slug: string; description?: string; organisation: string }) => Promise<Project>
  isLoading: boolean
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined)

export function ProjectProvider({ children }: { children: ReactNode }) {
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Load projects on mount: restore from localStorage, then refresh from API
  useEffect(() => {
    // Auto-save demo token if not present
    if (typeof window !== 'undefined' && !localStorage.getItem('releaseguard:apiToken')) {
      localStorage.setItem('releaseguard:apiToken', DEMO_TOKEN)
    }

    const savedProjectId = localStorage.getItem('releaseguard:currentProjectId')
    const savedProjects = localStorage.getItem('releaseguard:projects')

    // 1. Restore cached projects immediately so the UI isn't blank
    let cached: Project[] = []
    if (savedProjects) {
      try {
        const parsed = JSON.parse(savedProjects)
        if (Array.isArray(parsed)) {
          cached = parsed
          setProjects(cached)
        }
      } catch {
        cached = []
      }
    }

    // 2. Restore the last selected project from the cached list
    if (savedProjectId && Array.isArray(cached) && cached.length > 0) {
      const project = cached.find(p => p && p.id === savedProjectId)
      if (project) setCurrentProject(project)
    }

    // 3. Fetch fresh projects from the API (now with auth token)
    api.projects.list()
      .then(response => {
        const fresh = Array.isArray(response?.results) ? response.results : []
        setProjects(fresh)
        try {
          localStorage.setItem('releaseguard:projects', JSON.stringify(fresh))
        } catch {}

        // Auto-select: re-select saved project from fresh list, or pick first
        const toSelect = savedProjectId
          ? fresh.find(p => p && p.id === savedProjectId)
          : fresh[0]
        if (toSelect) setCurrentProject(toSelect)
      })
      .catch(() => {
        // Network error — keep whatever was in localStorage
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, []) // Run once on mount

  const updateCurrentProject = (project: Project | null) => {
    setCurrentProject(project)
    if (project) {
      localStorage.setItem('releaseguard:currentProjectId', project.id)
    } else {
      localStorage.removeItem('releaseguard:currentProjectId')
    }
  }

  const updateProjects = (newProjects: Project[]) => {
    setProjects(newProjects)
    localStorage.setItem('releaseguard:projects', JSON.stringify(newProjects))
  }

  const createProject = async (data: { name: string; slug: string; description?: string; organisation: string }): Promise<Project> => {
    const newProject = await api.projects.create(data)
    setProjects(prev => [newProject, ...prev])
    return newProject
  }

  return (
    <ProjectContext.Provider value={{
      currentProject,
      setCurrentProject: updateCurrentProject,
      projects,
      setProjects: updateProjects,
      createProject,
      isLoading,
    }}>
      {children}
    </ProjectContext.Provider>
  )
}

export function useProject() {
  const context = useContext(ProjectContext)
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider')
  }
  return context
}
