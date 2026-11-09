'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { 
  User, 
  Settings as SettingsIcon, 
  Server,
  Key, 
  Trash2, 
  Plus, 
  Eye, 
  Copy, 
  Github, 
  Gitlab, 
  Bitbucket, 
  Edit 
} from '@/components/ui/Icons'
import { useProject } from '@/context/ProjectContext'
import { cn, formatRelativeTime } from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Tabs } from '@/components/ui/Tabs'
import { Table } from '@/components/ui/Table'
import { useSafeMotion } from '@/hooks/use-reduced-motion'
import type { Project, ProjectToken, Environment } from '@/lib/api'
import { api } from '@/lib/api'

export function Settings() {
  const { currentProject } = useProject()
  const safeMotion = useSafeMotion()
  const [activeTab, setActiveTab] = useState<'general' | 'environments' | 'tokens' | 'integrations' | 'members' | 'danger'>('general')
  const [showCreateEnvModal, setShowCreateEnvModal] = useState(false)
  const [showCreateTokenModal, setShowCreateTokenModal] = useState(false)
  const [editingEnv, setEditingEnv] = useState<Environment | null>(null)
  const [newToken, setNewToken] = useState<string | null>(null)

  if (!currentProject) {
    return (
      <div className="container-page">
        <div className="empty-state">
          <SettingsIcon className="empty-state-icon" />
          <h2 className="empty-state-title">No project selected</h2>
          <p className="empty-state-description">Select a project from the sidebar to manage settings</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { value: 'general', label: 'General', icon: <SettingsIcon className="w-4 h-4" /> },
    { value: 'environments', label: 'Environments', icon: <Server className="w-4 h-4" /> },
    { value: 'tokens', label: 'API Tokens', icon: <Key className="w-4 h-4" /> },
    { value: 'integrations', label: 'Integrations', icon: <Github className="w-4 h-4" /> },
    { value: 'members', label: 'Members', icon: <User className="w-4 h-4" /> },
    { value: 'danger', label: 'Danger Zone', icon: <Trash2 className="w-4 h-4" /> },
  ]

  return (
    <div className="container-page max-w-4xl">
      <motion.div
        initial={safeMotion.initial}
        animate={safeMotion.animate}
        className="space-y-6"
      >
        {/* Header */}
        <div>
          <h1 className="text-display-sm font-bold text-surface-900 dark:text-surface-100 text-balance">
            Settings
          </h1>
          <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
            Manage your project configuration
          </p>
        </div>

        {/* Tabs */}
        <Tabs
          tabs={tabs}
          value={activeTab}
          onChange={(val) => setActiveTab(val as typeof activeTab)}
          variant="line"
        />

        <AnimatePresence mode="wait">
          {activeTab === 'general' && <GeneralSettingsTab project={currentProject} key="general" />}
          {activeTab === 'environments' && (
            <EnvironmentsTab 
              project={currentProject} 
              key="environments" 
              onNewEnv={() => setShowCreateEnvModal(true)}
              onEditEnv={(e) => setEditingEnv(e)}
            />
          )}
          {activeTab === 'tokens' && (
            <TokensTab 
              project={currentProject} 
              key="tokens" 
              onNewToken={() => setShowCreateTokenModal(true)}
            />
          )}
          {activeTab === 'integrations' && <IntegrationsTab key="integrations" />}
          {activeTab === 'members' && <MembersTab key="members" />}
          {activeTab === 'danger' && <DangerZoneTab project={currentProject} key="danger" />}
        </AnimatePresence>
      </motion.div>

      {/* Modals */}
      <EnvironmentModal
        isOpen={showCreateEnvModal || !!editingEnv}
        onClose={() => {
          setShowCreateEnvModal(false)
          setEditingEnv(null)
        }}
        projectId={currentProject.id}
        initialData={editingEnv}
      />
      <TokenModal
        isOpen={showCreateTokenModal}
        onClose={() => {
          setShowCreateTokenModal(false)
          setNewToken(null)
        }}
        projectId={currentProject.id}
        newToken={newToken}
        setNewToken={setNewToken}
      />
    </div>
  )
}

function GeneralSettingsTab({ project }: { project: Project }) {
  const [formData, setFormData] = useState({
    name: project.name,
    description: project.description || '',
  })
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setMessage(null)

    try {
      await api.projects.update(project.id, formData)
      setMessage({ type: 'success', text: 'Settings saved successfully' })
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to save settings' })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6 mt-6">
      <Card>
        <CardHeader>
          <CardTitle>Project Information</CardTitle>
          <CardDescription>Basic project details</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {message && (
              <div className={cn(
                'p-3 rounded-lg border text-body-sm',
                message.type === 'success' 
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-900/30 dark:border-emerald-800 dark:text-emerald-400'
                  : 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/30 dark:border-red-800 dark:text-red-400'
              )}>
                {message.text}
              </div>
            )}
            <Input
              label="Project Name"
              value={formData.name}
              onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
              required
            />
            <Input
              label="Description"
              value={formData.description}
              onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Optional description"
            />
            <div className="flex justify-end pt-4">
              <Button type="submit" isLoading={isSaving}>
                Save Changes
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Project ID</CardTitle>
          <CardDescription>Unique identifier for API access</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <code className="flex-1 font-mono text-body-sm bg-surface-100 dark:bg-surface-800 px-3 py-2 rounded-lg text-surface-900 dark:text-surface-100">
              {project.id}
            </code>
            <Button variant="ghost" size="sm" onClick={() => navigator.clipboard.writeText(project.id)}>
              <Copy className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function EnvironmentsTab({ 
  project, 
  onNewEnv, 
  onEditEnv 
}: { 
  project: Project
  onNewEnv: () => void
  onEditEnv: (env: Environment) => void
}) {
  const [environments, setEnvironments] = useState<Environment[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchEnvironments()
  }, [])

  const fetchEnvironments = async () => {
    setIsLoading(true)
    try {
      const response = await api.environments.list(project.id)
      setEnvironments(response.results)
    } catch (err) {
      console.error('Failed to fetch environments:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mt-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-heading-md font-semibold text-surface-900 dark:text-surface-100">Environments</h2>
          <p className="text-body-sm text-surface-500 dark:text-surface-400">Manage deployment environments</p>
        </div>
        <Button onClick={onNewEnv}>
          <Plus className="w-4 h-4" />
          New Environment
        </Button>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="py-8">
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton h-16 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      ) : environments.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="empty-state">
              <Server className="empty-state-icon" />
              <p className="empty-state-title">No environments</p>
              <p className="empty-state-description">Create your first environment to get started</p>
              <Button onClick={onNewEnv} className="mt-4">
                <Plus className="w-4 h-4" />
                Create Environment
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table
              columns={[
                { 
                  key: 'name', 
                  header: 'Name', 
                  render: (e: Environment) => (
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: e.color }} />
                      <span className="font-medium">{e.name}</span>
                    </div>
                  )
                },
                { 
                  key: 'slug', 
                  header: 'Slug', 
                  render: (e: Environment) => (
                    <span className="font-mono text-body-sm text-surface-500 dark:text-surface-400">{e.slug}</span>
                  )
                },
                { 
                  key: 'color', 
                  header: 'Color', 
                  render: (e: Environment) => (
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded border border-surface-300 dark:border-surface-600" style={{ backgroundColor: e.color }} />
                      <span className="font-mono text-body-sm">{e.color}</span>
                    </div>
                  )
                },
                {
                  key: 'actions',
                  header: '',
                  render: (e: Environment) => (
                    <Button variant="ghost" size="sm" onClick={() => onEditEnv(e)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                  )
                },
              ]}
              data={environments}
              keyExtractor={e => e.id}
              striped
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function TokensTab({ 
  project, 
  onNewToken 
}: { 
  project: Project
  onNewToken: () => void 
}) {
  const [tokens, setTokens] = useState<ProjectToken[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchTokens()
  }, [])

  const fetchTokens = async () => {
    setIsLoading(true)
    try {
      const response = await api.tokens.list(project.id)
      setTokens(response.results)
    } catch (err) {
      console.error('Failed to fetch tokens:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRevoke = async (tokenId: string) => {
    if (!confirm('Are you sure you want to revoke this token? This action cannot be undone.')) return
    try {
      await api.tokens.revoke(project.id, tokenId)
      fetchTokens()
    } catch (err) {
      console.error('Failed to revoke token:', err)
    }
  }

  const handleCopy = (token: string) => {
    navigator.clipboard.writeText(token)
  }

  return (
    <div className="mt-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-heading-md font-semibold text-surface-900 dark:text-surface-100">API Tokens</h2>
          <p className="text-body-sm text-surface-500 dark:text-surface-400">Manage API access tokens</p>
        </div>
        <Button onClick={onNewToken}>
          <Plus className="w-4 h-4" />
          Generate Token
        </Button>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="py-8">
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton h-16 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      ) : tokens.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="empty-state">
              <Key className="empty-state-icon" />
              <p className="empty-state-title">No API tokens</p>
              <p className="empty-state-description">Generate a token to authenticate API requests</p>
              <Button onClick={onNewToken} className="mt-4">
                <Plus className="w-4 h-4" />
                Generate Token
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table
              columns={[
                { 
                  key: 'name', 
                  header: 'Name', 
                  render: (t: ProjectToken) => (
                    <span className="font-medium">{t.name}</span>
                  )
                },
                { 
                  key: 'token', 
                  header: 'Token', 
                  render: (t: ProjectToken) => (
                    <div className="flex items-center gap-2">
                      <code className="font-mono text-body-sm bg-surface-100 dark:bg-surface-800 px-2 py-1 rounded">
                        {t.token.slice(0, 12)}…
                      </code>
                      <Button variant="ghost" size="sm" onClick={() => handleCopy(t.token)} aria-label="Copy token">
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleCopy(t.token)} aria-label="Show token">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  )
                },
                { 
                  key: 'last_used', 
                  header: 'Last Used', 
                  render: (t: ProjectToken) => (
                    <span className="text-body-sm text-surface-500 dark:text-surface-400">
                      {t.last_used_at ? formatRelativeTime(t.last_used_at) : 'Never'}
                    </span>
                  )
                },
                { 
                  key: 'expires', 
                  header: 'Expires', 
                  render: (t: ProjectToken) => (
                    <span className="text-body-sm text-surface-500 dark:text-surface-400">
                      {t.expires_at ? formatRelativeTime(t.expires_at) : 'Never'}
                    </span>
                  )
                },
                {
                  key: 'actions',
                  header: '',
                  render: (t: ProjectToken) => (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => handleRevoke(t.id)}
                      className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )
                },
              ]}
              data={tokens}
              keyExtractor={t => t.id}
              striped
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function IntegrationsTab() {
  const integrations = [
    { name: 'GitHub', icon: Github, description: 'Connect GitHub for release tracking', configured: false },
    { name: 'GitLab', icon: Gitlab, description: 'Connect GitLab for release tracking', configured: false },
    { name: 'Bitbucket', icon: Bitbucket, description: 'Connect Bitbucket for release tracking', configured: false },
  ]

  return (
    <div className="mt-6 space-y-4">
      <h2 className="text-heading-md font-semibold text-surface-900 dark:text-surface-100">Integrations</h2>
      <p className="text-body-sm text-surface-500 dark:text-surface-400">Connect external services</p>
      
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {integrations.map(integration => (
          <Card key={integration.name} className="p-6" variant="hover">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-xl bg-brand-100 dark:bg-brand-900/30">
                <integration.icon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-surface-900 dark:text-surface-100">{integration.name}</h3>
                <p className="text-body-sm text-surface-500 dark:text-surface-400 mt-1">{integration.description}</p>
                <div className="mt-3 flex items-center gap-2">
                  <Badge variant={integration.configured ? 'success' : 'neutral'}>
                    {integration.configured ? 'Connected' : 'Not connected'}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    {integration.configured ? 'Manage' : 'Connect'}
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

function MembersTab() {
  return (
    <div className="mt-6 space-y-4">
      <h2 className="text-heading-md font-semibold text-surface-900 dark:text-surface-100">Team Members</h2>
      <p className="text-body-sm text-surface-500 dark:text-surface-400">Manage project access</p>
      
      <Card>
        <CardContent className="py-12">
          <div className="empty-state">
            <User className="empty-state-icon" />
            <p className="empty-state-title">Member management coming soon</p>
            <p className="empty-state-description">Team member management will be available in a future release</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function DangerZoneTab({ project }: { project: Project }) {
  return (
    <div className="mt-6 space-y-6">
      <div className="p-6 rounded-xl border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-red-100 dark:bg-red-900/30">
            <Trash2 className="w-6 h-6 text-red-600 dark:text-red-400" />
          </div>
          <div>
            <h3 className="text-heading-md font-semibold text-red-700 dark:text-red-400">Danger Zone</h3>
            <p className="text-body text-red-600 dark:text-red-400 mt-1">
              Irreversible actions that permanently delete data
            </p>
          </div>
        </div>
      </div>

      <Card className="border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="text-red-700 dark:text-red-400">Delete Project</CardTitle>
          <CardDescription>Permanently delete this project and all its data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-body text-surface-600 dark:text-surface-400">
              This action cannot be undone. All releases, test runs, API checks, issues, and settings will be permanently deleted.
            </p>
            <div className="flex items-center gap-3">
              <Input
                label="Type project name to confirm"
                placeholder={project.name}
              />
            </div>
            <Button variant="danger" className="w-full sm:w-auto">
              <Trash2 className="w-4 h-4" />
              Delete Project
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function EnvironmentModal({ 
  isOpen, 
  onClose, 
  projectId, 
  initialData 
}: { 
  isOpen: boolean
  onClose: () => void
  projectId: string
  initialData: Environment | null
}) {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    color: '#2a6eff',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setFormData({
          name: initialData.name,
          slug: initialData.slug,
          color: initialData.color,
        })
      } else {
        setFormData({
          name: '',
          slug: '',
          color: '#2a6eff',
        })
      }
    }
  }, [isOpen, initialData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (initialData) {
        await api.environments.create(projectId, formData) // Would need update endpoint
      } else {
        await api.environments.create(projectId, formData)
      }
      onClose()
      window.location.reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save environment')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialData ? 'Edit Environment' : 'Create Environment'}
      description="Configure deployment environment details"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-body-sm">
            {error}
          </div>
        )}
        <Input
          label="Environment Name"
          value={formData.name}
          onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., Production"
          required
        />
        <Input
          label="Slug"
          value={formData.slug}
          onChange={e => setFormData(prev => ({ ...prev, slug: e.target.value }))}
          placeholder="e.g., prod"
          required
        />
        <div>
          <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
            Badge Color
          </label>
          <div className="flex items-center gap-3">
            <input
              type="color"
              value={formData.color}
              onChange={e => setFormData(prev => ({ ...prev, color: e.target.value }))}
              className="w-10 h-10 rounded border border-surface-300 dark:border-surface-600 cursor-pointer"
            />
            <Input
              value={formData.color}
              onChange={e => setFormData(prev => ({ ...prev, color: e.target.value }))}
              placeholder="#2a6eff"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Save Changes' : 'Create Environment'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function TokenModal({ 
  isOpen, 
  onClose, 
  projectId, 
  newToken,
  setNewToken
}: { 
  isOpen: boolean
  onClose: () => void
  projectId: string
  newToken: string | null
  setNewToken: (token: string | null) => void
}) {
  const [formData, setFormData] = useState({
    name: '',
    expires_at: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await api.tokens.create(projectId, formData)
      setNewToken(response.token)
      // Save token for API auth
      if (response.token) {
        localStorage.setItem('releaseguard:apiToken', response.token)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create token')
    } finally {
      setIsLoading(false)
    }
  }

  if (newToken) {
    return (
      <Modal
        isOpen={isOpen}
        onClose={() => {
          setNewToken(null)
          onClose()
        }}
        title="Token Created"
        description="Copy this token now - you won't be able to see it again"
        size="md"
      >
        <div className="space-y-4">
          <div className="p-4 bg-surface-100 dark:bg-surface-800 rounded-lg">
            <code className="font-mono text-body text-surface-900 dark:text-surface-100 break-all">
              {newToken}
            </code>
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => navigator.clipboard.writeText(newToken)}>
              <Copy className="w-4 h-4 mr-2" />
              Copy Token
            </Button>
            <Button onClick={() => {
              setNewToken(null)
              onClose()
            }}>
              Done
            </Button>
          </div>
          <p className="text-caption text-surface-500 dark:text-surface-400">
            Store this token securely. It will not be shown again.
          </p>
        </div>
      </Modal>
    )
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Generate API Token"
      description="Create a new API token for authentication"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-body-sm">
            {error}
          </div>
        )}
        <Input
          label="Token Name"
          value={formData.name}
          onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., CI/CD Token"
          required
        />
        <Input
          label="Expires At (optional)"
          type="datetime-local"
          value={formData.expires_at}
          onChange={e => setFormData(prev => ({ ...prev, expires_at: e.target.value }))}
        />
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            Generate Token
          </Button>
        </div>
      </form>
    </Modal>
  )
}
