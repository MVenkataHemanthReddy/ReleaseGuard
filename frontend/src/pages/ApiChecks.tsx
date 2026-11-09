'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'motion/react'
import { 
  MonitorCheck, 
  Search, 
  Filter, 
  Plus, 
  RefreshCw,
  Play,
  Pause,
  Edit,
  Trash2,
  ExternalLink,
  ChevronDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Zap
} from '@/components/ui/Icons'
import { api } from '@/lib/api'
import { useProject } from '@/context/ProjectContext'
import { 
  formatRelativeTime, 
  formatDuration, 
  getStatusColor, 
  getStatusLabel,
  cn 
} from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Table, DataTableToolbar, Pagination } from '@/components/ui/Table'
import { Input } from '@/components/ui/Input'
import { Dropdown, DropdownItem } from '@/components/ui/Dropdown'
import { Modal } from '@/components/ui/Modal'
import { springs, motionTokens } from '@/lib/motion-tokens'
import { useSafeMotion } from '@/hooks/use-reduced-motion'
import type { ApiCheck, ApiCheckResult, PaginatedResponse } from '@/lib/api'

export function ApiChecks() {
  const { currentProject } = useProject()
  const queryClient = useQueryClient()
  const safeMotion = useSafeMotion()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingCheck, setEditingCheck] = useState<ApiCheck | null>(null)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['apiChecks', currentProject?.id, { page, pageSize, search, statusFilter }],
    queryFn: () => api.apiChecks.list(currentProject!.id, {
      page: String(page),
      page_size: String(pageSize),
      search,
      status: statusFilter,
    }),
    enabled: !!currentProject,
    placeholderData: (previousData) => previousData,
  })

  const runCheckMutation = useMutation({
    mutationFn: (checkId: string) => api.apiChecks.results.run(currentProject!.id, checkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiChecks', currentProject?.id] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (checkId: string) => api.apiChecks.delete(currentProject!.id, checkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiChecks', currentProject?.id] })
      setEditingCheck(null)
    },
  })

  const statusOptions = ['healthy', 'unhealthy', 'timeout', 'error']

  if (!currentProject) return null

  return (
    <div className="container-page">
      <motion.div
        initial={safeMotion.initial}
        animate={safeMotion.animate}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-display-sm font-bold text-surface-900 dark:text-surface-100 text-balance">
              API Checks
            </h1>
            <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
              Monitor your API endpoints health
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => refetch()} size="sm">
              <RefreshCw className="w-4 h-4" />
              Refresh
            </Button>
            <Button onClick={() => setShowCreateModal(true)} size="sm">
              <Plus className="w-4 h-4" />
              New Check
            </Button>
          </div>
        </div>

        {/* Toolbar */}
        <DataTableToolbar
          searchValue={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search API checks..."
          filters={
            <Dropdown
              trigger={
                <Button variant="ghost" size="sm" className="gap-1">
                  <Filter className="w-4 h-4" />
                  {statusFilter ? 'Status' : 'Filter'}
                  <ChevronDown className="w-4 h-4" />
                </Button>
              }
              items={[
                { label: 'All Statuses', onClick: () => setStatusFilter('') },
                { divider: true },
                ...statusOptions.map(status => ({
                  label: getStatusLabel(status),
                  onClick: () => setStatusFilter(status),
                })),
              ]}
              align="right"
            />
          }
        />

        {/* API Checks Table */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-8">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="skeleton h-12 w-full mb-2 mx-6" />
                ))}
              </div>
            ) : data?.results.length === 0 ? (
              <div className="empty-state py-16">
                <MonitorCheck className="empty-state-icon" />
                <p className="empty-state-title">No API checks configured</p>
                <p className="empty-state-description">
                  Create your first API health check to start monitoring
                </p>
                <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                  <Plus className="w-4 h-4" />
                  Create Check
                </Button>
              </div>
            ) : (
              <>
                <Table
                  columns={[
                    { 
                      key: 'name', 
                      header: 'Name', 
                      sortable: false,
                      render: (c: ApiCheck) => (
                        <div>
                          <p className="font-medium">{c.name}</p>
                          <p className="text-caption text-surface-500 dark:text-surface-400 truncate max-w-xs">
                            {c.method} {c.url}
                          </p>
                        </div>
                      )
                    },
                    { 
                      key: 'environment', 
                      header: 'Environment', 
                      sortable: false,
                      render: (c: ApiCheck) => (
                        <Badge variant="brand">{c.environment?.name || 'Production'}</Badge>
                      )
                    },
                    { 
                      key: 'interval', 
                      header: 'Interval', 
                      sortable: false,
                      render: (c: ApiCheck) => (
                        <span className="text-body-sm">{formatInterval((c as any).interval_seconds ?? c.check_interval_seconds)}</span>
                      )
                    },
                    { 
                      key: 'timeout', 
                      header: 'Timeout', 
                      sortable: false,
                      render: (c: ApiCheck) => (
                        <span className="text-body-sm">{c.timeout_seconds}s</span>
                      )
                    },
                    { 
                      key: 'status', 
                      header: 'Status', 
                      sortable: false,
                      render: (c: ApiCheck) => (
                        <Badge variant={c.is_active ? 'success' : 'neutral'}>
                          {c.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      )
                    },
                    { 
                      key: 'last_run', 
                      header: 'Last Run', 
                      sortable: false,
                      render: (c: ApiCheck) => {
                        // Would need last result from API
                        return <span className="text-body-sm text-surface-500 dark:text-surface-400">—</span>
                      }
                    },
                    {
                      key: 'actions',
                      header: '',
                      render: (c: ApiCheck) => (
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => runCheckMutation.mutate(c.id)}
                            disabled={runCheckMutation.isPending}
                            aria-label="Run check now"
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingCheck(c)}
                            aria-label="Edit check"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteMutation.mutate(c.id)}
                            disabled={deleteMutation.isPending}
                            className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                            aria-label="Delete check"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      )
                    },
                  ]}
                  data={data?.results || []}
                  keyExtractor={c => c.id}
                  isLoading={isLoading}
                  striped
                  hoverable
                />
                <Pagination
                  currentPage={page}
                  totalPages={data ? Math.ceil(data.count / pageSize) : 1}
                  onPageChange={setPage}
                  showPageSize
                  pageSize={pageSize}
                  onPageSizeChange={setPageSize}
                  totalItems={data?.count}
                />
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Create/Edit Modal */}
      <ApiCheckModal
        isOpen={showCreateModal || !!editingCheck}
        onClose={() => {
          setShowCreateModal(false)
          setEditingCheck(null)
        }}
        projectId={currentProject!.id}
        initialData={editingCheck}
        onSuccess={() => {
          setShowCreateModal(false)
          setEditingCheck(null)
          refetch()
        }}
      />
    </div>
  )
}

function formatInterval(seconds?: number): string {
  if (!seconds || isNaN(seconds)) return '60s'
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`
  return `${Math.floor(seconds / 86400)}d`
}

function ApiCheckModal({ 
  isOpen, 
  onClose, 
  projectId, 
  initialData,
  onSuccess 
}: { 
  isOpen: boolean
  onClose: () => void
  projectId: string
  initialData: ApiCheck | null
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    name: '',
    environment_id: '',
    method: 'GET',
    url: '',
    expected_status: 200,
    headers: '',
    body: '',
    check_interval_seconds: 60,
    timeout_seconds: 10,
    is_active: true,
  })
  const [environments, setEnvironments] = useState<{ id: string; name: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      fetchEnvironments()
      if (initialData) {
        setFormData({
          name: initialData.name,
          environment_id: initialData.environment?.id || '',
          method: initialData.method,
          url: initialData.url,
          expected_status: initialData.expected_status,
          headers: JSON.stringify(initialData.headers || {}, null, 2),
          body: initialData.body || '',
          check_interval_seconds: initialData.check_interval_seconds,
          timeout_seconds: initialData.timeout_seconds,
          is_active: initialData.is_active,
        })
      } else {
        setFormData({
          name: '',
          environment_id: '',
          method: 'GET',
          url: '',
          expected_status: 200,
          headers: '',
          body: '',
          check_interval_seconds: 60,
          timeout_seconds: 10,
          is_active: true,
        })
      }
    }
  }, [isOpen, initialData])

  const fetchEnvironments = async () => {
    try {
      const response = await api.environments.list(projectId)
      setEnvironments(response.results.map(e => ({ id: e.id, name: e.name })))
    } catch (err) {
      console.error('Failed to fetch environments:', err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      let parsedHeaders: Record<string, string> = {}
      try {
        parsedHeaders = formData.headers ? JSON.parse(formData.headers) : {}
      } catch {
        setError('Invalid JSON in headers')
        setIsLoading(false)
        return
      }

      const payload = {
        ...formData,
        method: formData.method as ApiCheck['method'],
        headers: parsedHeaders,
        body: formData.body || undefined,
      }

      if (initialData) {
        await api.apiChecks.update(projectId, initialData.id, payload)
      } else {
        await api.apiChecks.create(projectId, payload)
      }
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save check')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialData ? 'Edit API Check' : 'Create API Check'}
      description={initialData ? 'Update the API health check configuration' : 'Configure a new API health check'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-body-sm">
            {error}
          </div>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Name"
            value={formData.name}
            onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="e.g., Health Check"
            required
          />
          <div className="w-full">
            <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
              Environment
            </label>
            <select
              value={formData.environment_id}
              onChange={e => setFormData(prev => ({ ...prev, environment_id: e.target.value }))}
              className="input"
              required
            >
              <option value="">Select environment</option>
              {environments.map(env => (
                <option key={env.id} value={env.id}>{env.name}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="w-full">
            <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
              Method
            </label>
            <select
              value={formData.method}
              onChange={e => setFormData(prev => ({ ...prev, method: e.target.value }))}
              className="input"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
              <option value="HEAD">HEAD</option>
            </select>
          </div>
          <Input
            label="Expected Status"
            type="number"
            value={formData.expected_status}
            onChange={e => setFormData(prev => ({ ...prev, expected_status: parseInt(e.target.value) }))}
            placeholder="200"
          />
          <Input
            label="Timeout (seconds)"
            type="number"
            value={formData.timeout_seconds}
            onChange={e => setFormData(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) }))}
            placeholder="10"
          />
        </div>
        <Input
          label="URL"
          value={formData.url}
          onChange={e => setFormData(prev => ({ ...prev, url: e.target.value }))}
          placeholder="https://api.example.com/health"
          required
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Check Interval (seconds)"
            type="number"
            value={formData.check_interval_seconds}
            onChange={e => setFormData(prev => ({ ...prev, check_interval_seconds: parseInt(e.target.value) }))}
            placeholder="60"
          />
          <div className="w-full">
            <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
              Active
            </label>
            <label className="inline-flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={e => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                className="w-4 h-4 rounded border-surface-300 text-brand-500 focus:ring-brand-500"
              />
              <span className="text-body-sm text-surface-700 dark:text-surface-300">Enabled</span>
            </label>
          </div>
        </div>
        <div>
          <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
            Headers (JSON)
          </label>
          <textarea
            value={formData.headers}
            onChange={e => setFormData(prev => ({ ...prev, headers: e.target.value }))}
            placeholder='{"Authorization": "Bearer token"}'
            className="input font-mono text-sm min-h-[80px]"
            rows={3}
          />
        </div>
        <div>
          <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
            Request Body
          </label>
          <textarea
            value={formData.body}
            onChange={e => setFormData(prev => ({ ...prev, body: e.target.value }))}
            placeholder='{"key": "value"}'
            className="input font-mono text-sm min-h-[80px]"
            rows={3}
          />
        </div>
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Save Changes' : 'Create Check'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}