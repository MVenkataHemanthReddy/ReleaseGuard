'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'motion/react'
import { 
  GitBranch, 
  Search, 
  Filter, 
  Plus, 
  Download,
  ChevronDown,
  ChevronUp
} from '@/components/ui/Icons'
import { api } from '@/lib/api'
import { useProject } from '@/context/ProjectContext'
import { 
  formatRelativeTime, 
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
import type { Release, PaginatedResponse } from '@/lib/api'

export function Releases() {
  const { currentProject } = useProject()
  const safeMotion = useSafeMotion()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [sortBy, setSortBy] = useState('deployed_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['releases', currentProject?.id, { page, pageSize, search, statusFilter, sortBy, sortOrder }],
    queryFn: () => api.releases.list(currentProject!.id, {
      page: String(page),
      page_size: String(pageSize),
      search,
      status: statusFilter,
      ordering: `${sortOrder === 'desc' ? '-' : ''}${sortBy}`,
    }),
    enabled: !!currentProject,
    placeholderData: (previousData) => previousData,
  })

  const handleSort = (key: string) => {
    if (sortBy === key) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(key)
      setSortOrder('desc')
    }
  }

  const statusOptions = ['deployed', 'deploying', 'pending', 'failed', 'rolled_back']

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
              Releases
            </h1>
            <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
              Manage and track your deployments
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => refetch()} size="sm">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 4v6h-6" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M1 20v-6h6" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Refresh
            </Button>
            <Button onClick={() => setShowCreateModal(true)} size="sm">
              <Plus className="w-4 h-4" />
              New Release
            </Button>
          </div>
        </div>

        {/* Toolbar */}
        <DataTableToolbar
          searchValue={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search releases..."
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

        {/* Releases Table */}
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
                <GitBranch className="empty-state-icon" />
                <p className="empty-state-title">No releases found</p>
                <p className="empty-state-description">
                  {search || statusFilter 
                    ? 'Try adjusting your search or filters'
                    : 'Register your first release to get started'}
                </p>
                {!search && !statusFilter && (
                  <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                    <Plus className="w-4 h-4" />
                    Create Release
                  </Button>
                )}
              </div>
            ) : (
              <>
                <Table
                  columns={[
                    { 
                      key: 'version', 
                      header: 'Version', 
                      sortable: true,
                      render: (r: Release) => (
                        <span className="font-mono font-medium">{r.version}</span>
                      )
                    },
                    { 
                      key: 'environment', 
                      header: 'Environment', 
                      sortable: true,
                      render: (r: Release) => (
                        <Badge variant="brand">{r.environment?.name || 'Production'}</Badge>
                      )
                    },
                    { 
                      key: 'branch', 
                      header: 'Branch', 
                      sortable: true,
                      render: (r: Release) => r.branch ? (
                        <span className="font-mono text-body-sm">{r.branch}</span>
                      ) : (
                        <span className="text-surface-400 dark:text-surface-600">—</span>
                      )
                    },
                    { 
                      key: 'commit_sha', 
                      header: 'Commit', 
                      sortable: true,
                      render: (r: Release) => r.commit_sha ? (
                        <span className="font-mono text-body-sm">{r.commit_sha.slice(0, 8)}</span>
                      ) : (
                        <span className="text-surface-400 dark:text-surface-600">—</span>
                      )
                    },
                    { 
                      key: 'deployed_at', 
                      header: 'Deployed', 
                      sortable: true,
                      render: (r: Release) => (
                        <span className="text-body-sm">{formatRelativeTime(r.deployed_at)}</span>
                      )
                    },
                    { 
                      key: 'status', 
                      header: 'Status', 
                      sortable: true,
                      render: (r: Release) => {
                        const s = r.status || (r as any).analysis_status || 'deployed'
                        return <Badge variant={getStatusColor(s) as any}>{getStatusLabel(s)}</Badge>
                      }
                    },
                    {
                      key: 'actions',
                      header: '',
                      render: (r: Release) => (
                        <Dropdown
                          trigger={
                            <button className="btn-ghost p-1.5 rounded-lg" aria-label="More actions">
                              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="1" />
                                <circle cx="19" cy="12" r="1" />
                                <circle cx="5" cy="12" r="1" />
                              </svg>
                            </button>
                          }
                          items={[
                            { 
                              label: 'View Details', 
                              onClick: () => window.location.href = `/releases/${r.id}`,
                              icon: <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                            },
                            { 
                              label: 'Compare', 
                              onClick: () => console.log('Compare', r.id),
                              icon: <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" /></svg>
                            },
                            { divider: true },
                            { 
                              label: 'Delete', 
                              onClick: () => console.log('Delete', r.id),
                              danger: true,
                              icon: <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" /></svg>
                            },
                          ]}
                          align="right"
                        />
                      )
                    },
                  ]}
                  data={data?.results || []}
                  keyExtractor={r => r.id}
                  isLoading={isLoading}
                  sortBy={sortBy}
                  sortOrder={sortOrder}
                  onSort={handleSort}
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

      {/* Create Release Modal */}
      <CreateReleaseModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        projectId={currentProject!.id}
        onSuccess={() => {
          setShowCreateModal(false)
          refetch()
        }}
      />
    </div>
  )
}

function CreateReleaseModal({ 
  isOpen, 
  onClose, 
  projectId, 
  onSuccess 
}: { 
  isOpen: boolean
  onClose: () => void
  projectId: string
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    version: '',
    commit_sha: '',
    branch: '',
    environment_id: '',
  })
  const [environments, setEnvironments] = useState<{ id: string; name: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      fetchEnvironments()
    }
  }, [isOpen])

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
      await api.releases.create(projectId, formData)
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create release')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Release"
      description="Register a new deployment"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-body-sm">
            {error}
          </div>
        )}
        <Input
          label="Version"
          value={formData.version}
          onChange={e => setFormData(prev => ({ ...prev, version: e.target.value }))}
          placeholder="e.g., v1.2.3"
          required
          error={error && !formData.version ? 'Version is required' : undefined}
        />
        <Input
          label="Commit SHA (optional)"
          value={formData.commit_sha}
          onChange={e => setFormData(prev => ({ ...prev, commit_sha: e.target.value }))}
          placeholder="e.g., abc123def"
        />
        <Input
          label="Branch (optional)"
          value={formData.branch}
          onChange={e => setFormData(prev => ({ ...prev, branch: e.target.value }))}
          placeholder="e.g., main"
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
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            Create Release
          </Button>
        </div>
      </form>
    </Modal>
  )
}