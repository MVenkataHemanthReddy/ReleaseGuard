'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'motion/react'
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  RefreshCw,
  ChevronDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Bug,
  Eye,
  Edit,
  MoreVertical,
  GitBranch,
  Server,
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
import { Dropdown, DropdownItem } from '@/components/ui/Dropdown'
import { Modal } from '@/components/ui/Modal'
import { springs, motionTokens } from '@/lib/motion-tokens'
import { useSafeMotion } from '@/hooks/use-reduced-motion'
import type { IssueGroup, ErrorEvent, PaginatedResponse } from '@/lib/api'

export function Issues() {
  const { currentProject } = useProject()
  const queryClient = useQueryClient()
  const safeMotion = useSafeMotion()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [selectedIssue, setSelectedIssue] = useState<IssueGroup | null>(null)
  const [showEventsModal, setShowEventsModal] = useState(false)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['issues', currentProject?.id, { page, pageSize, search, statusFilter }],
    queryFn: () => api.issues.list(currentProject!.id, {
      page: String(page),
      page_size: String(pageSize),
      search,
      status: statusFilter,
      ordering: '-last_seen',
    }),
    enabled: !!currentProject,
    placeholderData: (previousData) => previousData,
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ issueId, status }: { issueId: string; status: IssueGroup['status'] }) => 
      api.issues.updateStatus(currentProject!.id, issueId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['issues', currentProject?.id] })
      if (selectedIssue) {
        queryClient.invalidateQueries({ queryKey: ['issue', 'events', currentProject?.id, selectedIssue.id] })
      }
    },
  })

  const statusOptions: IssueGroup['status'][] = ['open', 'in_progress', 'resolved', 'ignored']

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
              Issues
            </h1>
            <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
              Track and manage error groups
            </p>
          </div>
          <Button variant="secondary" onClick={() => refetch()} size="sm">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>

        {/* Stats Summary */}
        <IssueStatsSummary projectId={currentProject!.id} />

        {/* Toolbar */}
        <DataTableToolbar
          searchValue={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search issues..."
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

        {/* Issues Table */}
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
                <AlertTriangle className="empty-state-icon" />
                <p className="empty-state-title">No issues found</p>
                <p className="empty-state-description">
                  {search || statusFilter 
                    ? 'Try adjusting your search or filters'
                    : 'All clear - no errors detected'}
                </p>
              </div>
            ) : (
              <>
                <Table
                  columns={[
                    { 
                      key: 'title', 
                      header: 'Issue', 
                      sortable: false,
                      render: (i: IssueGroup) => (
                        <div>
                          <p className="font-medium truncate max-w-xs">{i.title}</p>
                          <p className="text-caption text-surface-500 dark:text-surface-400">
                            {(i as any).occurrence_count ?? i.occurrences ?? 0} occurrences{i.example_error?.environment?.name ? ` • ${i.example_error.environment.name}` : ''}
                          </p>
                        </div>
                      )
                    },
                    { 
                      key: 'fingerprint', 
                      header: 'Fingerprint', 
                      sortable: false,
                      render: (i: IssueGroup) => (
                        <span className="font-mono text-body-sm text-surface-500 dark:text-surface-400">
                          {i.fingerprint.slice(0, 12)}…
                        </span>
                      )
                    },
                    { 
                      key: 'status', 
                      header: 'Status', 
                      sortable: false,
                      render: (i: IssueGroup) => (
                        <Badge variant={getStatusColor(i.status) as any}>{getStatusLabel(i.status)}</Badge>
                      )
                    },
                    { 
                      key: 'first_seen', 
                      header: 'First Seen', 
                      sortable: false,
                      render: (i: IssueGroup) => (
                        <span className="text-body-sm">{formatRelativeTime((i as any).first_seen_at || i.first_seen)}</span>
                      )
                    },
                    { 
                      key: 'last_seen', 
                      header: 'Last Seen', 
                      sortable: false,
                      render: (i: IssueGroup) => (
                        <span className="text-body-sm">{formatRelativeTime((i as any).last_seen_at || i.last_seen)}</span>
                      )
                    },
                    {
                      key: 'actions',
                      header: '',
                      render: (i: IssueGroup) => (
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedIssue(i)
                              setShowEventsModal(true)
                            }}
                            aria-label="View events"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Dropdown
                            trigger={
                              <Button variant="ghost" size="sm" aria-label="More actions">
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                            }
                            items={statusOptions.map(status => ({
                              label: getStatusLabel(status),
                              onClick: () => updateStatusMutation.mutate({ issueId: i.id, status }),
                            }))}
                            align="right"
                          />
                        </div>
                      )
                    },
                  ]}
                  data={data?.results || []}
                  keyExtractor={i => i.id}
                  isLoading={isLoading}
                  striped
                  hoverable
                  onRowClick={i => {
                    setSelectedIssue(i)
                    setShowEventsModal(true)
                  }}
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

      {/* Events Modal */}
      <EventsModal
        isOpen={showEventsModal}
        onClose={() => {
          setShowEventsModal(false)
          setSelectedIssue(null)
        }}
        issue={selectedIssue}
        projectId={currentProject!.id}
      />
    </div>
  )
}

function IssueStatsSummary({ projectId }: { projectId: string }) {
  const { data } = useQuery({
    queryKey: ['issues', 'summary', projectId],
    queryFn: async () => {
      const response = await api.issues.list(projectId, { page_size: '1' })
      // This is a simplified version - would need proper summary endpoint
      return {
        open: response.results.filter(i => i.status === 'open').length,
        in_progress: response.results.filter(i => i.status === 'in_progress').length,
        resolved: response.results.filter(i => i.status === 'resolved').length,
      }
    },
  })

  if (!data) return null

  const stats = [
    { label: 'Open', value: data.open, color: 'error', icon: <AlertCircle className="w-5 h-5" /> },
    { label: 'In Progress', value: data.in_progress, color: 'warning', icon: <Clock className="w-5 h-5" /> },
    { label: 'Resolved', value: data.resolved, color: 'success', icon: <CheckCircle className="w-5 h-5" /> },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springs.gentle, delay: index * 0.05 }}
          className="card p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-caption text-surface-500 dark:text-surface-400">{stat.label}</p>
              <p className="text-heading-lg font-bold text-surface-900 dark:text-surface-100 tabular-nums">
                {stat.value}
              </p>
            </div>
            <div className={cn('p-2 rounded-lg', {
              error: 'bg-red-100 dark:bg-red-900/30',
              warning: 'bg-amber-100 dark:bg-amber-900/30',
              success: 'bg-emerald-100 dark:bg-emerald-900/30',
            }[stat.color])}>
              {stat.icon}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

function EventsModal({ 
  isOpen, 
  onClose, 
  issue, 
  projectId 
}: { 
  isOpen: boolean
  onClose: () => void
  issue: IssueGroup | null
  projectId: string
}) {
  const [eventsPage, setEventsPage] = useState(1)

  const { data: events, isLoading } = useQuery({
    queryKey: ['issue', 'events', projectId, issue?.id, eventsPage],
    queryFn: () => api.issues.events(projectId, issue!.id, { 
      page: String(eventsPage), 
      page_size: '20' 
    }),
    enabled: !!issue && isOpen,
  })

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Error Events"
      description={`Events for: ${issue?.title}`}
      size="xl"
    >
      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton h-16 w-full" />
            ))}
          </div>
        ) : events?.results.length === 0 ? (
          <div className="empty-state py-8">
            <Bug className="empty-state-icon" />
            <p className="empty-state-title">No events</p>
            <p className="empty-state-description">No error events recorded for this issue</p>
          </div>
        ) : (
          <>
            <Table
              columns={[
                { 
                  key: 'timestamp', 
                  header: 'Time', 
                  sortable: false,
                  render: (e: ErrorEvent) => (
                    <span className="text-body-sm">{formatRelativeTime(e.timestamp)}</span>
                  )
                },
                { 
                  key: 'level', 
                  header: 'Level', 
                  sortable: false,
                  render: (e: ErrorEvent) => (
                    <Badge variant={getStatusColor(e.level) as any}>{getStatusLabel(e.level)}</Badge>
                  )
                },
                { 
                  key: 'release', 
                  header: 'Release', 
                  sortable: false,
                  render: (e: ErrorEvent) => (
                    <span className="text-body-sm">{e.release?.version || '—'}</span>
                  )
                },
                { 
                  key: 'environment', 
                  header: 'Environment', 
                  sortable: false,
                  render: (e: ErrorEvent) => (
                    <Badge variant="brand">{(e as any).environment_name || e.environment?.name || 'Default'}</Badge>
                  )
                },
                { 
                  key: 'message', 
                  header: 'Message', 
                  sortable: false,
                  render: (e: ErrorEvent) => (
                    <span className="text-body-sm text-surface-600 dark:text-surface-400 max-w-md truncate block font-mono">
                      {e.message}
                    </span>
                  )
                },
              ]}
              data={events?.results || []}
              keyExtractor={e => e.id}
              striped
              hoverable
            />
            <Pagination
              currentPage={eventsPage}
              totalPages={events ? Math.ceil(events.count / 20) : 1}
              onPageChange={setEventsPage}
              totalItems={events?.count}
            />
          </>
        )}
      </div>
    </Modal>
  )
}