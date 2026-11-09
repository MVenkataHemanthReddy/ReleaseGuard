'use client'

import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'motion/react'
import { 
  GitBranch, 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Clock,
  Zap,
  Bug,
  Download,
  ChevronRight,
  FileText,
  Search
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
import { Tabs, TabPanel, Tab } from '@/components/ui/Tabs'
import { Modal } from '@/components/ui/Modal'
import { Skeleton, SkeletonCard } from '@/components/ui/LoadingScreen'
import { springs, motionTokens } from '@/lib/motion-tokens'
import { useSafeMotion, useStaggerDelay } from '@/hooks/use-reduced-motion'
import type { Release, TestRun, TestCaseResult, ReleaseComparison } from '@/lib/api'

export function ReleaseDetail() {
  const { releaseId } = useParams<{ releaseId: string }>()
  const { currentProject } = useProject()
  const safeMotion = useSafeMotion()
  const [activeTab, setActiveTab] = useState<'overview' | 'tests' | 'comparison'>('overview')
  const [comparisonBaseline, setComparisonBaseline] = useState<string>('')
  const [showComparisonModal, setShowComparisonModal] = useState(false)
  const [testStatusFilter, setTestStatusFilter] = useState<string>('')
  const [testSearch, setTestSearch] = useState('')
  const [testPage, setTestPage] = useState(1)

  const { data: release, isLoading: releaseLoading, error: releaseError } = useQuery({
    queryKey: ['release', currentProject?.id, releaseId],
    queryFn: () => api.releases.get(currentProject!.id, releaseId!),
    enabled: !!currentProject && !!releaseId,
  })

  const { data: testRuns, isLoading: testRunsLoading } = useQuery({
    queryKey: ['testRuns', currentProject?.id, releaseId],
    queryFn: () => api.releases.testRuns.list(currentProject!.id, releaseId!),
    enabled: !!currentProject && !!releaseId,
  })

  const { data: comparison, isLoading: comparisonLoading } = useQuery({
    queryKey: ['comparison', currentProject?.id, releaseId, comparisonBaseline],
    queryFn: () => api.releases.compare(currentProject!.id, releaseId!, comparisonBaseline),
    enabled: !!currentProject && !!releaseId && !!comparisonBaseline,
  })

  if (releaseLoading || !currentProject) {
    return <ReleaseDetailSkeleton />
  }

  if (releaseError || !release) {
    return (
      <div className="container-page">
        <div className="empty-state">
          <XCircle className="empty-state-icon text-red-500" />
          <h2 className="empty-state-title">Release not found</h2>
          <p className="empty-state-description">
            {releaseError instanceof Error ? releaseError.message : 'Unable to load release details'}
          </p>
          <Button onClick={() => window.history.back()} variant="secondary" className="mt-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Releases
          </Button>
        </div>
      </div>
    )
  }

  const latestTestRun = testRuns?.results[0]

  return (
    <div className="container-page">
      <motion.div
        initial={safeMotion.initial}
        animate={safeMotion.animate}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => window.history.back()}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-display-sm font-bold text-surface-900 dark:text-surface-100 text-balance">
                  Release {release.version}
                </h1>
                <Badge variant={getStatusColor(release.status) as any}>
                  {getStatusLabel(release.status)}
                </Badge>
              </div>
              <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
                Deployed to {release.environment?.name || 'Production'} • {formatRelativeTime(release.deployed_at)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant="secondary" 
              onClick={() => setShowComparisonModal(true)}
              size="sm"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" />
              </svg>
              Compare
            </Button>
          </div>
        </div>

        {/* Release Meta */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetaCard 
            label="Environment" 
            value={release.environment?.name || 'Production'}
            icon={<GitBranch className="w-5 h-5 text-brand-600 dark:text-brand-400" />}
            color="brand"
          />
          <MetaCard 
            label="Branch" 
            value={release.branch || '—'}
            icon={<GitBranch className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />}
            color="success"
            monospace
          />
          <MetaCard 
            label="Commit" 
            value={release.commit_sha ? release.commit_sha.slice(0, 12) : '—'}
            icon={<FileText className="w-5 h-5 text-amber-600 dark:text-amber-400" />}
            color="warning"
            monospace
          />
          <MetaCard 
            label="Deployed" 
            value={formatRelativeTime(release.deployed_at)}
            icon={<Clock className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
            color="info"
          />
        </div>

        {/* Tabs */}
        <Tabs
          tabs={[
            { value: 'overview', label: 'Overview', icon: <Zap className="w-4 h-4" /> },
            { value: 'tests', label: 'Test Results', icon: <FileText className="w-4 h-4" /> },
            { value: 'comparison', label: 'Comparison', icon: <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" /></svg> },
          ]}
          value={activeTab}
          onChange={(val) => setActiveTab(val as typeof activeTab)}
          variant="line"
        />

        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <OverviewTab release={release} latestTestRun={latestTestRun} key="overview" />
          )}
          {activeTab === 'tests' && (
            <TestsTab 
              releaseId={releaseId!} 
              projectId={currentProject!.id}
              latestTestRun={latestTestRun}
              key="tests"
            />
          )}
          {activeTab === 'comparison' && (
            <ComparisonTab 
              comparison={comparison}
              isLoading={comparisonLoading}
              key="comparison"
            />
          )}
        </AnimatePresence>
      </motion.div>

      {/* Compare Modal */}
      <Modal
        isOpen={showComparisonModal}
        onClose={() => setShowComparisonModal(false)}
        title="Compare Releases"
        description="Select a baseline release to compare against"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-body-sm font-medium text-surface-900 dark:text-surface-100 mb-1.5">
              Baseline Release
            </label>
            <select
              value={comparisonBaseline}
              onChange={e => setComparisonBaseline(e.target.value)}
              className="input"
            >
              <option value="">Select a release to compare...</option>
              {/* Would populate with previous releases */}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => setShowComparisonModal(false)}>
              Cancel
            </Button>
            <Button onClick={() => setShowComparisonModal(false)} disabled={!comparisonBaseline}>
              Compare
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

function MetaCard({ label, value, icon, color, monospace = false }: { 
  label: string
  value: string
  icon: React.ReactNode
  color: 'brand' | 'success' | 'warning' | 'error' | 'info'
  monospace?: boolean
}) {
  const colors = {
    brand: 'bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400',
    success: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400',
    warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
    error: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
    info: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
  }

  return (
    <Card className="p-4">
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-lg', colors[color])}>
          {icon}
        </div>
        <div>
          <p className="text-caption text-surface-500 dark:text-surface-400">{label}</p>
          <p className={cn('font-medium text-surface-900 dark:text-surface-100', monospace && 'font-mono text-body-sm')}>
            {value}
          </p>
        </div>
      </div>
    </Card>
  )
}

function OverviewTab({ release, latestTestRun }: { release: Release; latestTestRun?: TestRun }) {
  return (
    <div className="space-y-6 mt-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-caption text-surface-500 dark:text-surface-400">Test Runs</p>
              <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100">
                {latestTestRun ? '1' : '0'}
              </p>
            </div>
            <Zap className="w-10 h-10 text-brand-500/20" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-caption text-surface-500 dark:text-surface-400">Total Tests</p>
              <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100">
                {latestTestRun?.total_tests || 0}
              </p>
            </div>
            <FileText className="w-10 h-10 text-emerald-500/20" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-caption text-surface-500 dark:text-surface-400">Pass Rate</p>
              <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100">
                {latestTestRun && latestTestRun.total_tests > 0 
                  ? `${((latestTestRun.passed_tests / latestTestRun.total_tests) * 100).toFixed(1)}%`
                  : '—'}
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-emerald-500/20" />
          </div>
        </Card>
      </div>

      {latestTestRun && (
        <Card>
          <CardHeader>
            <CardTitle>Latest Test Run</CardTitle>
            <CardDescription>CI Provider: {latestTestRun.ci_provider}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-4">
              <StatItem 
                label="Passed" 
                value={latestTestRun.passed_tests}
                color="success"
                icon={<CheckCircle className="w-5 h-5" />}
              />
              <StatItem 
                label="Failed" 
                value={latestTestRun.failed_tests}
                color="error"
                icon={<XCircle className="w-5 h-5" />}
              />
              <StatItem 
                label="Skipped" 
                value={latestTestRun.skipped_tests}
                color="neutral"
                icon={<AlertTriangle className="w-5 h-5" />}
              />
              <StatItem 
                label="Duration" 
                value={formatDuration(latestTestRun.duration_seconds * 1000)}
                color="info"
                icon={<Clock className="w-5 h-5" />}
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function StatItem({ label, value, color, icon }: { 
  label: string
  value: number | string
  color: 'success' | 'error' | 'warning' | 'neutral' | 'info'
  icon: React.ReactNode
}) {
  const colors = {
    success: 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30',
    error: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30',
    warning: 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30',
    neutral: 'text-surface-600 dark:text-surface-400 bg-surface-100 dark:bg-surface-800',
    info: 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30',
  }

  return (
    <div className="p-4 rounded-lg bg-surface-50 dark:bg-surface-900/50">
      <div className="flex items-center justify-between mb-2">
        <span className="text-caption text-surface-500 dark:text-surface-400">{label}</span>
        <div className={cn('p-1.5 rounded', colors[color])}>{icon}</div>
      </div>
      <p className="text-heading-lg font-bold text-surface-900 dark:text-surface-100 tabular-nums">{value}</p>
    </div>
  )
}

function TestsTab({ releaseId, projectId, latestTestRun }: { 
  releaseId: string
  projectId: string
  latestTestRun?: TestRun
}) {
  const [testPage, setTestPage] = useState(1)
  const [testSearch, setTestSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: testCases, isLoading } = useQuery({
    queryKey: ['testCases', projectId, releaseId, { page: testPage, pageSize: 20, search: testSearch, status: statusFilter }],
    queryFn: () => {
      // This would need a proper API endpoint - using test run results for now
      return Promise.resolve({ results: [], count: 0 })
    },
    enabled: false, // Disabled until proper endpoint exists
  })

  return (
    <div className="mt-6 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Test Cases</CardTitle>
          <CardDescription>Individual test results from the latest run</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="empty-state py-12">
            <FileText className="empty-state-icon" />
            <p className="empty-state-title">Test case details not available</p>
            <p className="empty-state-description">
              Upload JUnit XML to see detailed test results
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ComparisonTab({ comparison, isLoading }: { 
  comparison?: ReleaseComparison
  isLoading: boolean
}) {
  if (isLoading) {
    return <ComparisonSkeleton />
  }

  if (!comparison) {
    return (
      <div className="mt-6 empty-state py-12">
        <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M16 18l6-6-6-6" /><path d="M8 6l-6 6 6 6" />
        </svg>
        <p className="empty-state-title">No comparison selected</p>
        <p className="empty-state-description">Select a baseline release to compare against</p>
      </div>
    )
  }

  const { new_failures, persistent_failures, fixed_failures, policy_decision, policy_reasons } = comparison

  return (
    <div className="mt-6 space-y-6">
      {/* Policy Decision */}
      <Card className={cn(
        'border-l-4',
        policy_decision === 'GREEN' && 'border-emerald-500',
        policy_decision === 'YELLOW' && 'border-amber-500',
        policy_decision === 'RED' && 'border-red-500',
      )}>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className={cn('p-3 rounded-xl', {
              GREEN: 'bg-emerald-100 dark:bg-emerald-900/30',
              YELLOW: 'bg-amber-100 dark:bg-amber-900/30',
              RED: 'bg-red-100 dark:bg-red-900/30',
            }[policy_decision])}>
              <span className={cn('text-2xl font-bold', {
                GREEN: 'text-emerald-600 dark:text-emerald-400',
                YELLOW: 'text-amber-600 dark:text-amber-400',
                RED: 'text-red-600 dark:text-red-400',
              }[policy_decision])}>
                {policy_decision}
              </span>
            </div>
            <div>
              <h3 className="text-heading-md font-semibold text-surface-900 dark:text-surface-100">
                Release Policy Decision
              </h3>
              <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
                {policy_reasons.length > 0 
                  ? policy_reasons.join('; ')
                  : 'No specific policy reasons'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <ComparisonStat 
          label="New Failures" 
          value={new_failures.length}
          color="error"
          icon={<AlertTriangle className="w-5 h-5" />}
        />
        <ComparisonStat 
          label="Persistent Failures" 
          value={persistent_failures.length}
          color="warning"
          icon={<Bug className="w-5 h-5" />}
        />
        <ComparisonStat 
          label="Fixed Failures" 
          value={fixed_failures.length}
          color="success"
          icon={<CheckCircle className="w-5 h-5" />}
        />
      </div>

      {/* Failure Details */}
      {new_failures.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>New Failures</CardTitle>
            <CardDescription>Tests that failed in this release but passed in baseline</CardDescription>
          </CardHeader>
          <CardContent>
            <FailureTable failures={new_failures} />
          </CardContent>
        </Card>
      )}

      {persistent_failures.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Persistent Failures</CardTitle>
            <CardDescription>Tests that failed in both releases</CardDescription>
          </CardHeader>
          <CardContent>
            <FailureTable failures={persistent_failures} />
          </CardContent>
        </Card>
      )}

      {fixed_failures.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Fixed Failures</CardTitle>
            <CardDescription>Tests that failed in baseline but passed in this release</CardDescription>
          </CardHeader>
          <CardContent>
            <FailureTable failures={fixed_failures} />
          </CardContent>
        </Card>
      )}

      {new_failures.length === 0 && persistent_failures.length === 0 && fixed_failures.length === 0 && (
        <div className="empty-state py-12">
          <CheckCircle className="empty-state-icon text-emerald-500" />
          <p className="empty-state-title">No test differences</p>
          <p className="empty-state-description">All tests have the same status in both releases</p>
        </div>
      )}
    </div>
  )
}

function ComparisonStat({ label, value, color, icon }: { 
  label: string
  value: number
  color: 'success' | 'error' | 'warning' | 'info'
  icon: React.ReactNode
}) {
  const colors = {
    success: 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30',
    error: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30',
    warning: 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30',
    info: 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30',
  }

  return (
    <Card className="p-4 text-center">
      <div className={cn('inline-flex items-center justify-center w-12 h-12 rounded-xl mx-auto mb-3', colors[color])}>
        {icon}
      </div>
      <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100 tabular-nums">{value}</p>
      <p className="text-caption text-surface-500 dark:text-surface-400 mt-1">{label}</p>
    </Card>
  )
}

function FailureTable({ failures }: { failures: TestCaseResult[] }) {
  return (
    <Table
      columns={[
        { key: 'name', header: 'Test Name', render: (f: TestCaseResult) => (
          <span className="font-mono text-body-sm">{f.classname}.{f.name}</span>
        )},
        { key: 'status', header: 'Status', render: (f: TestCaseResult) => (
          <Badge variant={getStatusColor(f.status) as any}>{getStatusLabel(f.status)}</Badge>
        )},
        { key: 'duration', header: 'Duration', render: (f: TestCaseResult) => (
          <span className="text-body-sm tabular-nums">{formatDuration(f.duration_seconds * 1000)}</span>
        )},
        { key: 'message', header: 'Failure Message', render: (f: TestCaseResult) => (
          <span className="text-body-sm text-surface-600 dark:text-surface-400 max-w-md truncate block">
            {f.failure_message || '—'}
          </span>
        )},
      ]}
      data={failures}
      keyExtractor={f => f.id}
      striped
      hoverable
    />
  )
}

function ReleaseDetailSkeleton() {
  return (
    <div className="container-page space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-8 w-48" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <Skeleton className="h-10 w-32" />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </div>
  )
}

function ComparisonSkeleton() {
  return (
    <div className="mt-6 space-y-6">
      <SkeletonCard />
      <div className="grid gap-4 sm:grid-cols-3">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <SkeletonCard />
    </div>
  )
}