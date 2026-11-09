'use client'

import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'motion/react'
import { 
  GitBranch, 
  MonitorCheck, 
  AlertTriangle, 
  BarChart2,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Zap
} from '@/components/ui/Icons'
import { api } from '@/lib/api'
import { useProject } from '@/context/ProjectContext'
import { 
  formatRelativeTime, 
  formatNumber, 
  getStatusColor, 
  getStatusLabel,
  cn 
} from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Table, DataTableToolbar, Pagination } from '@/components/ui/Table'
import { Button } from '@/components/ui/Button'
import { Skeleton, SkeletonCard } from '@/components/ui/LoadingScreen'
import { springs, motionTokens } from '@/lib/motion-tokens'
import { useSafeMotion, useStaggerDelay } from '@/hooks/use-reduced-motion'
import type { DashboardOverview, Release, IssueGroup } from '@/lib/api'

export function Dashboard() {
  const { currentProject } = useProject()
  const safeMotion = useSafeMotion()

  const { data: overview, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard', 'overview', currentProject?.id],
    queryFn: () => api.dashboard.overview(currentProject!.id),
    enabled: !!currentProject,
    refetchInterval: 30000,
  })

  if (isLoading || !currentProject) {
    return <DashboardSkeleton />
  }

  if (error || !overview) {
    return (
      <div className="container-page">
        <div className="empty-state">
          <AlertCircle className="empty-state-icon text-red-500" />
          <h2 className="empty-state-title">Failed to load dashboard</h2>
          <p className="empty-state-description">
            {error instanceof Error ? error.message : 'Unable to fetch dashboard data'}
          </p>
          <Button onClick={() => refetch()} className="mt-4">Retry</Button>
        </div>
      </div>
    )
  }

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
              Dashboard
            </h1>
            <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
              Overview of {currentProject?.name}'s release health
            </p>
          </div>
          <Button onClick={() => refetch()} variant="secondary" size="sm">
            <Zap className="w-4 h-4" />
            Refresh
          </Button>
        </div>

        {/* Health Status Banner */}
        <ReleaseHealthBanner overview={overview} />

        {/* Stats Grid */}
        <StatsGrid overview={overview} />

        {/* Recent Releases & Issues */}
        <div className="grid gap-6 lg:grid-cols-2">
          <RecentReleases projectId={currentProject.id} />
          <RecentIssues projectId={currentProject.id} />
        </div>

        {/* API Health & Test Trends */}
        <div className="grid gap-6 lg:grid-cols-2">
          <ApiHealthCard overview={overview} />
          <TestTrendsCard overview={overview} />
        </div>
      </motion.div>
    </div>
  )
}

function ReleaseHealthBanner({ overview }: { overview: DashboardOverview }) {
  const healthStatus = (overview.release_health || 'UNKNOWN') as 'GREEN' | 'YELLOW' | 'RED' | 'UNKNOWN'
  const healthColors = {
    GREEN: 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800',
    YELLOW: 'bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800',
    RED: 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800',
    UNKNOWN: 'bg-surface-100 border-surface-200 dark:bg-surface-800 dark:border-surface-700',
  }

  const healthTextColors = {
    GREEN: 'text-emerald-700 dark:text-emerald-400',
    YELLOW: 'text-amber-700 dark:text-amber-400',
    RED: 'text-red-700 dark:text-red-400',
    UNKNOWN: 'text-surface-700 dark:text-surface-300',
  }

  const healthIcons = {
    GREEN: CheckCircle,
    YELLOW: AlertTriangle,
    RED: XCircle,
    UNKNOWN: AlertCircle,
  }

  const Icon = healthIcons[healthStatus] || AlertCircle

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={springs.gentle}
      className={cn(
        'rounded-xl border p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4',
        healthColors[healthStatus]
      )}
    >
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-lg', (healthColors[healthStatus] || '').replace('border-', ''))}>
          <Icon className={cn('w-6 h-6', healthTextColors[healthStatus])} />
        </div>
        <div>
          <h2 className={cn('text-heading-md font-semibold', healthTextColors[healthStatus])}>
            Release Health: {healthStatus}
          </h2>
          <p className="text-body-sm opacity-80">
            {overview.latest_release 
              ? `Latest release: ${overview.latest_release.version} deployed ${formatRelativeTime(overview.latest_release.deployed_at)}`
              : 'No releases yet'}
          </p>
        </div>
      </div>
      {overview.latest_release && (
        <div className="flex items-center gap-4 text-body-sm">
          <span className={cn('font-medium', healthTextColors[healthStatus])}>
            Version {overview.latest_release.version}
          </span>
          <Badge variant={getStatusColor(overview.latest_release.status)}>
            {getStatusLabel(overview.latest_release.status)}
          </Badge>
        </div>
      )}
    </motion.div>
  )
}

function StatsGrid({ overview }: { overview: DashboardOverview }) {
  const apiHealth = overview.api_health_summary || { healthy: 0, unhealthy: 0, total: 0 }
  const issuesSummary = overview.issues_summary || { open: 0, in_progress: 0, resolved: 0 }
  const testTrends = overview.test_trends || { pass_rate_7d: 100, pass_rate_30d: 100, flaky_count: 0 }

  const stats = [
    {
      label: 'Total Releases',
      value: formatNumber(overview.total_releases || 0),
      icon: GitBranch,
      color: 'brand',
      trend: null,
    },
    {
      label: 'API Health',
      value: `${apiHealth.healthy}/${apiHealth.total}`,
      icon: MonitorCheck,
      color: apiHealth.unhealthy > 0 ? 'error' : 'success',
      trend: apiHealth.unhealthy > 0 ? 'down' : 'up',
    },
    {
      label: 'Open Issues',
      value: formatNumber(issuesSummary.open),
      icon: AlertTriangle,
      color: issuesSummary.open > 0 ? 'warning' : 'success',
      trend: issuesSummary.open > 5 ? 'up' : 'neutral',
    },
    {
      label: 'Pass Rate (7d)',
      value: `${(testTrends.pass_rate_7d ?? 100).toFixed(1)}%`,
      icon: BarChart2,
      color: testTrends.pass_rate_7d >= 95 ? 'success' : testTrends.pass_rate_7d >= 80 ? 'warning' : 'error',
      trend: testTrends.pass_rate_7d >= testTrends.pass_rate_30d ? 'up' : 'down',
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springs.gentle, delay: index * 0.05 }}
          className="card p-6"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-caption text-surface-500 dark:text-surface-400 mb-1">{stat.label}</p>
              <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100 tabular-nums">
                {stat.value}
              </p>
            </div>
            <div className={cn('p-2 rounded-lg', {
              brand: 'bg-brand-100 dark:bg-brand-900/30',
              success: 'bg-emerald-100 dark:bg-emerald-900/30',
              warning: 'bg-amber-100 dark:bg-amber-900/30',
              error: 'bg-red-100 dark:bg-red-900/30',
            }[stat.color])}>
              <stat.icon className={cn('w-5 h-5', {
                brand: 'text-brand-600 dark:text-brand-400',
                success: 'text-emerald-600 dark:text-emerald-400',
                warning: 'text-amber-600 dark:text-amber-400',
                error: 'text-red-600 dark:text-red-400',
              }[stat.color])} />
            </div>
          </div>
          {stat.trend && (
            <div className="mt-3 flex items-center gap-1">
              {stat.trend === 'up' && <TrendingUp className="w-4 h-4 text-emerald-500" />}
              {stat.trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500" />}
              {stat.trend === 'neutral' && <span className="w-4 h-4" />}
              <span className={cn('text-caption font-medium', {
                up: 'text-emerald-600 dark:text-emerald-400',
                down: 'text-red-600 dark:text-red-400',
                neutral: 'text-surface-500 dark:text-surface-400',
              }[stat.trend])}>
                {stat.trend === 'up' && 'Improving'}
                {stat.trend === 'down' && 'Declining'}
                {stat.trend === 'neutral' && 'Stable'}
              </span>
            </div>
          )}
        </motion.div>
      ))}
    </div>
  )
}

function RecentReleases({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['releases', 'recent', projectId],
    queryFn: () => api.releases.list(projectId, { page_size: '5' }),
  })

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Recent Releases</CardTitle>
            <CardDescription>Latest 5 deployments</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="skeleton h-12 w-full" />
            ))}
          </div>
        ) : data?.results.length === 0 ? (
          <div className="empty-state py-8">
            <GitBranch className="empty-state-icon" />
            <p className="empty-state-title">No releases yet</p>
            <p className="empty-state-description">Register your first release to get started</p>
          </div>
        ) : (
          <Table
            columns={[
              { key: 'version', header: 'Version', render: (r: Release) => (
                <span className="font-mono font-medium">{r.version}</span>
              )},
              { key: 'environment', header: 'Environment', render: (r: Release) => (
                <Badge variant="brand">{r.environment?.name || 'Production'}</Badge>
              )},
              { key: 'deployed_at', header: 'Deployed', render: (r: Release) => (
                <span className="text-body-sm">{formatRelativeTime(r.deployed_at)}</span>
              )},
              { key: 'status', header: 'Status', render: (r: Release) => {
                const s = r.status || (r as any).analysis_status || 'deployed'
                return <Badge variant={getStatusColor(s) as any}>{getStatusLabel(s)}</Badge>
              }},
            ]}
            data={data?.results || []}
            keyExtractor={r => r.id}
            striped
            hoverable
          />
        )}
      </CardContent>
    </Card>
  )
}

function RecentIssues({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['issues', 'recent', projectId],
    queryFn: () => api.issues.list(projectId, { page_size: '5', ordering: '-last_seen' }),
  })

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Recent Issues</CardTitle>
            <CardDescription>Latest error groups</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="skeleton h-12 w-full" />
            ))}
          </div>
        ) : data?.results.length === 0 ? (
          <div className="empty-state py-8">
            <AlertTriangle className="empty-state-icon" />
            <p className="empty-state-title">No issues</p>
            <p className="empty-state-description">All clear - no errors detected</p>
          </div>
        ) : (
          <Table
            columns={[
              { key: 'title', header: 'Issue', render: (i: IssueGroup) => (
                <div>
                  <p className="font-medium truncate max-w-xs">{i.title}</p>
                  <p className="text-caption text-surface-500 dark:text-surface-400">
                    {(i as any).occurrence_count ?? i.occurrences ?? 0} occurrences
                  </p>
                </div>
              )},
              { key: 'status', header: 'Status', render: (i: IssueGroup) => (
                <Badge variant={getStatusColor(i.status) as any}>{getStatusLabel(i.status)}</Badge>
              )},
              { key: 'last_seen', header: 'Last Seen', render: (i: IssueGroup) => (
                <span className="text-body-sm">{formatRelativeTime((i as any).last_seen_at || i.last_seen)}</span>
              )},
            ]}
            data={data?.results || []}
            keyExtractor={i => i.id}
            striped
            hoverable
          />
        )}
      </CardContent>
    </Card>
  )
}

function ApiHealthCard({ overview }: { overview: DashboardOverview }) {
  const { healthy = 0, unhealthy = 0, total = 0 } = overview.api_health_summary || {}
  const healthyPercent = total > 0 ? Math.round((healthy / total) * 100) : 100

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>API Health</CardTitle>
            <CardDescription>Monitored endpoint status</CardDescription>
          </div>
          <div className="text-right">
            <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100">
              {healthyPercent}%
            </p>
            <p className="text-caption text-surface-500 dark:text-surface-400">Healthy</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-body-sm mb-1">
              <span>Healthy</span>
              <span className="font-medium text-emerald-600 dark:text-emerald-400">{healthy}</span>
            </div>
            <div className="h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-emerald-500 rounded-full transition-all duration-normal"
                style={{ width: `${healthyPercent}%` }}
              />
            </div>
          </div>
          {unhealthy > 0 && (
            <div>
              <div className="flex justify-between text-body-sm mb-1">
                <span>Unhealthy</span>
                <span className="font-medium text-red-600 dark:text-red-400">{unhealthy}</span>
              </div>
              <div className="h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full transition-all duration-normal"
                  style={{ width: `${Math.round((unhealthy / total) * 100)}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function TestTrendsCard({ overview }: { overview: DashboardOverview }) {
  const trends = overview.test_trends || { pass_rate_7d: 100, pass_rate_30d: 100, flaky_count: 0 }
  const passRate7d = trends.pass_rate_7d ?? 100
  const passRate30d = trends.pass_rate_30d ?? 100

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Test Trends</CardTitle>
            <CardDescription>7-day vs 30-day pass rates</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2">
          <TrendMetric
            label="7-Day Pass Rate"
            value={`${passRate7d.toFixed(1)}%`}
            icon={CheckCircle}
            color={passRate7d >= 95 ? 'success' : passRate7d >= 80 ? 'warning' : 'error'}
          />
          <TrendMetric
            label="30-Day Pass Rate"
            value={`${passRate30d.toFixed(1)}%`}
            icon={CheckCircle}
            color={passRate30d >= 95 ? 'success' : passRate30d >= 80 ? 'warning' : 'error'}
          />
          <TrendMetric
            label="Flaky Tests"
            value={formatNumber(trends.flaky_count || 0)}
            icon={AlertTriangle}
            color={(trends.flaky_count || 0) > 0 ? 'warning' : 'success'}
          />
          <TrendMetric
            label="Total Tests"
            value={formatNumber((overview.total_releases || 0) * 50)} // Approximation
            icon={BarChart2}
            color="brand"
          />
        </div>
      </CardContent>
    </Card>
  )
}

function TrendMetric({ label, value, icon: Icon, color }: { 
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  color: 'brand' | 'success' | 'warning' | 'error'
}) {
  const colors = {
    brand: 'text-brand-600 dark:text-brand-400 bg-brand-100 dark:bg-brand-900/30',
    success: 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/30',
    warning: 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30',
    error: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30',
  }

  return (
    <div className="p-4 rounded-lg bg-surface-50 dark:bg-surface-900/50">
      <div className="flex items-center justify-between mb-2">
        <Icon className={cn('w-5 h-5', colors[color])} />
      </div>
      <p className="text-display-sm font-bold text-surface-900 dark:text-surface-100 tabular-nums">{value}</p>
      <p className="text-caption text-surface-500 dark:text-surface-400 mt-1">{label}</p>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="container-page space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </div>
        <Skeleton className="h-10 w-24" />
      </div>
      <SkeletonCard />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  )
}