// API Types for ReleaseGuard

export interface Organization {
  id: string
  name: string
  slug: string
  description?: string
  member_count?: number
  project_count?: number
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  date_joined: string
}

export interface Membership {
  id: string
  user: User
  organization: Organization
  role: 'owner' | 'admin' | 'member' | 'viewer'
  created_at: string
}

export interface Project {
  id: string
  name: string
  slug: string
  description?: string
  organization: Organization
  created_at: string
  updated_at: string
}

export interface Environment {
  id: string
  name: string
  slug: string
  project: Project
  color: string
  created_at: string
}

export interface ProjectToken {
  id: string
  name: string
  token: string
  project: Project
  expires_at?: string
  created_at: string
  last_used_at?: string
}

export interface Release {
  id: string
  version: string
  commit_sha?: string
  branch?: string
  environment: Environment
  deployed_at: string
  created_at: string
  status: 'pending' | 'deploying' | 'deployed' | 'failed' | 'rolled_back'
}

export interface TestRun {
  id: string
  release: Release
  ci_provider: string
  ci_build_id?: string
  ci_build_url?: string
  started_at: string
  finished_at?: string
  status: 'running' | 'passed' | 'failed' | 'error'
  total_tests: number
  passed_tests: number
  failed_tests: number
  skipped_tests: number
  duration_seconds: number
}

export interface TestCaseResult {
  id: string
  test_run: TestRun
  name: string
  classname: string
  status: 'passed' | 'failed' | 'skipped' | 'error'
  duration_seconds: number
  failure_message?: string
  failure_trace?: string
}

export interface ReleaseComparison {
  release_a: Release
  release_b: Release
  new_failures: TestCaseResult[]
  persistent_failures: TestCaseResult[]
  fixed_failures: TestCaseResult[]
  unchanged_passed: TestCaseResult[]
  flaky_tests: TestCaseResult[]
  policy_decision: 'GREEN' | 'YELLOW' | 'RED'
  policy_reasons: string[]
}

export interface ApiCheck {
  id: string
  name: string
  project: Project
  environment: Environment
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD'
  url: string
  expected_status: number
  headers?: Record<string, string>
  body?: string
  check_interval_seconds: number
  timeout_seconds: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ApiCheckResult {
  id: string
  api_check: ApiCheck
  checked_at: string
  status: 'healthy' | 'unhealthy' | 'timeout' | 'error'
  response_status?: number
  response_time_ms?: number
  response_body?: string
  error_message?: string
}

export interface IssueGroup {
  id: string
  project: Project
  fingerprint: string
  title: string
  first_seen: string
  last_seen: string
  occurrences: number
  status: 'open' | 'in_progress' | 'resolved' | 'ignored'
  resolved_at?: string
  example_error: ErrorEvent
}

export interface ErrorEvent {
  id: string
  issue_group: IssueGroup
  release?: Release
  environment: Environment
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  message: string
  stack_trace?: string
  context?: Record<string, unknown>
}

export interface DashboardOverview {
  project: Project
  latest_release: Release | null
  release_health: 'GREEN' | 'YELLOW' | 'RED' | 'UNKNOWN'
  total_releases: number
  recent_comparison?: ReleaseComparison
  api_health_summary: {
    total: number
    healthy: number
    unhealthy: number
  }
  issues_summary: {
    open: number
    in_progress: number
    resolved_today: number
  }
  test_trends: {
    pass_rate_7d: number
    pass_rate_30d: number
    flaky_count: number
  }
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// API Client
const API_BASE = '/api/v1'

function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('releaseguard:apiToken')
  }
  return null
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Token ${token}`
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    credentials: 'include',
    headers,
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    const message = error.error?.message || error.detail || error.message || `API error: ${response.status}`
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export const api = {
  // Organizations
  organizations: {
    list: () => request<PaginatedResponse<Organization>>('/organizations/'),
    get: (id: string) => request<Organization>(`/organizations/${id}/`),
    create: (data: Partial<Organization>) => request<Organization>('/organizations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: Partial<Organization>) => request<Organization>(`/organizations/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  },

  // Projects
  projects: {
    list: (orgId?: string) => {
      const params = orgId ? `?organization=${orgId}` : ''
      return request<PaginatedResponse<Project>>(`/projects/${params}`)
    },
    get: (id: string) => request<Project>(`/projects/${id}/`),
    create: (data: Partial<Project>) => request<Project>('/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: Partial<Project>) => request<Project>(`/projects/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<void>(`/projects/${id}/`, { method: 'DELETE' }),
  },

  // Environments
  environments: {
    list: (projectId: string) => request<PaginatedResponse<Environment>>(`/projects/${projectId}/environments/`),
    get: (projectId: string, id: string) => request<Environment>(`/projects/${projectId}/environments/${id}/`),
    create: (projectId: string, data: Partial<Environment>) => request<Environment>(`/projects/${projectId}/environments/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },

  // Project Tokens
  tokens: {
    list: (projectId: string) => request<PaginatedResponse<ProjectToken>>(`/projects/${projectId}/tokens/`),
    get: (projectId: string, id: string) => request<ProjectToken>(`/projects/${projectId}/tokens/${id}/`),
    create: (projectId: string, data: Partial<ProjectToken>) => request<ProjectToken>(`/projects/${projectId}/tokens/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    revoke: (projectId: string, id: string) => request<void>(`/projects/${projectId}/tokens/${id}/`, { method: 'DELETE' }),
  },

  // Releases
  releases: {
    list: (projectId: string, params?: Record<string, string>) => {
      const searchParams = new URLSearchParams(params)
      return request<PaginatedResponse<Release>>(`/projects/${projectId}/releases/?${searchParams}`)
    },
    get: (projectId: string, id: string) => request<Release>(`/projects/${projectId}/releases/${id}/`),
    create: (projectId: string, data: Partial<Release>) => request<Release>(`/projects/${projectId}/releases/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    compare: (projectId: string, releaseId: string, baselineId?: string) =>
      request<ReleaseComparison>(`/projects/${projectId}/releases/${releaseId}/compare/${baselineId ? `?baseline=${baselineId}` : ''}`),
    testRuns: {
      list: (projectId: string, releaseId: string) => request<PaginatedResponse<TestRun>>(`/projects/${projectId}/releases/${releaseId}/test-runs/`),
      create: (projectId: string, releaseId: string, formData: FormData) =>
        fetch(`${API_BASE}/projects/${projectId}/releases/${releaseId}/test-runs/`, {
          method: 'POST',
          body: formData,
        }).then(r => r.json()),
    },
  },

  // API Checks
  apiChecks: {
    list: (projectId: string, params?: Record<string, string>) => {
      const searchParams = new URLSearchParams(params)
      return request<PaginatedResponse<ApiCheck>>(`/projects/${projectId}/api-checks/?${searchParams}`)
    },
    get: (projectId: string, id: string) => request<ApiCheck>(`/projects/${projectId}/api-checks/${id}/`),
    create: (projectId: string, data: Partial<ApiCheck>) => request<ApiCheck>(`/projects/${projectId}/api-checks/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (projectId: string, id: string, data: Partial<ApiCheck>) => request<ApiCheck>(`/projects/${projectId}/api-checks/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (projectId: string, id: string) => request<void>(`/projects/${projectId}/api-checks/${id}/`, { method: 'DELETE' }),
    results: {
      list: (projectId: string, checkId: string, params?: Record<string, string>) => {
        const searchParams = new URLSearchParams(params)
        return request<PaginatedResponse<ApiCheckResult>>(`/projects/${projectId}/api-checks/${checkId}/results/?${searchParams}`)
      },
      run: (projectId: string, checkId: string) => request<ApiCheckResult>(`/projects/${projectId}/api-checks/${checkId}/run/`, {
        method: 'POST',
      }),
    },
  },

  // Issues
  issues: {
    list: (projectId: string, params?: Record<string, string>) => {
      const searchParams = new URLSearchParams(params)
      return request<PaginatedResponse<IssueGroup>>(`/projects/${projectId}/issues/?${searchParams}`)
    },
    get: (projectId: string, id: string) => request<IssueGroup>(`/projects/${projectId}/issues/${id}/`),
    events: (projectId: string, issueId: string, params?: Record<string, string>) => {
      const searchParams = new URLSearchParams(params)
      return request<PaginatedResponse<ErrorEvent>>(`/projects/${projectId}/issues/${issueId}/events/?${searchParams}`)
    },
    updateStatus: (projectId: string, id: string, status: IssueGroup['status']) => request<IssueGroup>(`/projects/${projectId}/issues/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  },

  // Dashboard
  dashboard: {
    overview: (projectId: string) => request<DashboardOverview>(`/projects/${projectId}/dashboard/overview/`),
  },

  // Health
  health: () => request<{ status: string }>('/health/'),
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  return 'An unexpected error occurred'
}