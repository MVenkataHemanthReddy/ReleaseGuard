'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { 
  LayoutDashboard, 
  GitBranch, 
  MonitorCheck, 
  AlertTriangle, 
  Settings,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  LogoIcon,
  Plus,
  Building2
} from '@/components/ui/Icons'
import { useProject } from '@/context/ProjectContext'
import { useSafeMotion } from '@/hooks/use-reduced-motion'
import { springs } from '@/lib/motion-tokens'
import type { Project } from '@/lib/api'
import { Modal } from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Releases', href: '/releases', icon: GitBranch },
  { name: 'API Checks', href: '/api-checks', icon: MonitorCheck },
  { name: 'Issues', href: '/issues', icon: AlertTriangle },
  { name: 'Organizations', href: '/organizations', icon: Building2 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const { currentProject, projects, setCurrentProject, createProject } = useProject()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isProjectMenuOpen, setIsProjectMenuOpen] = useState(false)
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false)
  const safeMotion = useSafeMotion()

  if (!currentProject) {
    return (
      <motion.aside
        initial={safeMotion.initial}
        animate={safeMotion.animate}
        className="fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-surface-900 border-r border-surface-200 dark:border-surface-800 flex flex-col"
      >
        <div className="flex h-16 items-center justify-center border-b border-surface-200 dark:border-surface-800">
          <LogoIcon className="w-8 h-8 text-brand-500" />
        </div>
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <p className="text-surface-500 dark:text-surface-400 mb-4">Select a project to continue</p>
          <ProjectSelector 
            projects={projects} 
            currentProject={null}
            onSelect={(p) => setCurrentProject(p)} 
            isOpen={isProjectMenuOpen}
            setIsOpen={setIsProjectMenuOpen}
            setShowCreateProjectModal={setShowCreateProjectModal}
          />
        </div>
      </motion.aside>
    )
  }

  return (
    <motion.aside
      initial={safeMotion.initial}
      animate={safeMotion.animate}
      className={cn(
        'fixed inset-y-0 left-0 z-40 bg-white dark:bg-surface-900 border-r border-surface-200 dark:border-surface-800 flex flex-col transition-all duration-normal',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b border-surface-200 dark:border-surface-800">
        <LogoIcon className="w-8 h-8 text-brand-500 flex-shrink-0" />
        {!isCollapsed && (
          <span className="text-heading-sm font-medium text-surface-900 dark:text-surface-100 truncate">
            {currentProject.name}
          </span>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="btn-ghost p-1.5 rounded-lg"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Main navigation">
        {navigation.map((item, index) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) => cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-body-sm font-medium transition-all duration-fast',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-surface-950',
                isActive
                  ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400'
                  : 'text-surface-600 hover:bg-surface-100 hover:text-surface-900 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-100'
              )}
              style={{ transitionDelay: `${index * 30}ms` }}
              title={isCollapsed ? item.name : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
              {!isCollapsed && <span className="truncate">{item.name}</span>}
            </NavLink>
          )
        })}
      </nav>

      <div className="p-3 border-t border-surface-200 dark:border-surface-800">
        <ProjectSelector 
          projects={projects} 
          currentProject={currentProject}
          onSelect={setCurrentProject}
          isCollapsed={isCollapsed}
          isOpen={isProjectMenuOpen}
          setIsOpen={setIsProjectMenuOpen}
          setShowCreateProjectModal={setShowCreateProjectModal}
        />
      </div>
      <CreateProjectModal
        isOpen={showCreateProjectModal}
        onClose={() => setShowCreateProjectModal(false)}
        onSuccess={() => {}}
        createProject={createProject}
        setShowCreateProjectModal={setShowCreateProjectModal}
      />
    </motion.aside>
  )
}

function CreateProjectModal({ 
  isOpen, 
  onClose, 
  onSuccess,
  createProject,
  setShowCreateProjectModal
}: { 
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  createProject: (data: { name: string; slug: string; description?: string; organisation: string }) => Promise<any>
  setShowCreateProjectModal: (open: boolean) => void
}) {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    organisation: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      await createProject(formData)
      onSuccess()
      onClose()
      setFormData({ name: '', slug: '', description: '', organisation: '' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Project"
      description="Add a new project to your organization"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-body-sm">
            {error}
          </div>
        )}
        <Input
          label="Project Name"
          value={formData.name}
          onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., My Awesome App"
          required
        />
        <Input
          label="Slug (URL-friendly)"
          value={formData.slug}
          onChange={e => setFormData(prev => ({ ...prev, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') }))}
          placeholder="e.g., my-awesome-app"
          required
        />
        <Input
          label="Description (optional)"
          value={formData.description}
          onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Brief description"
        />
        <Input
          label="Organisation (required)"
          value={formData.organisation}
          onChange={e => setFormData(prev => ({ ...prev, organisation: e.target.value }))}
          placeholder="e.g., f26f2c3c-f054-4341-8ccb-a8e2a926a2e6"
          required
        />
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            Create Project
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function ProjectSelector({ 
  projects, 
  currentProject, 
  onSelect, 
  isCollapsed,
  isOpen,
  setIsOpen,
  setShowCreateProjectModal
}: { 
  projects: Project[]
  currentProject: Project | null
  onSelect: (project: Project) => void
  isCollapsed?: boolean
  isOpen: boolean
  setIsOpen: (open: boolean) => void
  setShowCreateProjectModal: (open: boolean) => void
}) {
  return (
    <div className="relative">
      <button
        className={cn(
          'w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left',
          'bg-surface-50 dark:bg-surface-800/50 border border-surface-200 dark:border-surface-700',
          'hover:bg-surface-100 dark:hover:bg-surface-800',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500'
        )}
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0" />
        {!isCollapsed && (
          <span className="truncate text-body-sm font-medium text-surface-900 dark:text-surface-100">
            {currentProject?.name || 'Select Project'}
          </span>
        )}
        {!isCollapsed && <ChevronDown className="w-4 h-4 text-surface-400 ml-auto flex-shrink-0" />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={springs.snappy}
            className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg shadow-lg py-2 z-50 max-h-60 overflow-y-auto"
            role="listbox"
          >
            {projects.map(project => (
              <button
                key={project.id}
                onClick={() => {
                  onSelect(project)
                  setIsOpen(false)
                }}
                className={cn(
                  'w-full px-3 py-2 text-left text-body-sm transition-colors duration-fast',
                  project.id === currentProject?.id
                    ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400'
                    : 'text-surface-600 hover:bg-surface-100 hover:text-surface-900 dark:text-surface-400 dark:hover:bg-surface-800'
                )}
                role="option"
                aria-selected={project.id === currentProject?.id}
              >
                {project.name}
              </button>
            ))}
            {projects.length === 0 && (
              <div className="px-3 py-2 text-body-sm text-surface-500 dark:text-surface-400">
                No projects available
              </div>
            )}
            <hr className="my-2 border-surface-200 dark:border-surface-700" />
            <button
              onClick={() => {
                setIsOpen(false)
                setShowCreateProjectModal(true)
              }}
              className="w-full px-3 py-2 text-left text-body-sm font-medium text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-colors duration-fast flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Project
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}