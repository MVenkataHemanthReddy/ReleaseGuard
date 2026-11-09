import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date?: string | Date | null, options?: Intl.DateTimeFormatOptions): string {
  if (!date) return 'N/A'
  const d = typeof date === 'string' ? new Date(date) : date
  if (!d || isNaN(d.getTime())) return 'N/A'
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  })
}

export function formatDateTime(date?: string | Date | null): string {
  if (!date) return 'N/A'
  const d = typeof date === 'string' ? new Date(date) : date
  if (!d || isNaN(d.getTime())) return 'N/A'
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelativeTime(date?: string | Date | null): string {
  if (!date) return 'N/A'
  const d = typeof date === 'string' ? new Date(date) : date
  if (!d || isNaN(d.getTime())) return 'N/A'
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSecs < 60) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return formatDate(d)
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  const secs = (ms / 1000).toFixed(1)
  if (ms < 60000) return `${secs}s`
  const mins = Math.floor(ms / 60000)
  const remainingSecs = Math.floor((ms % 60000) / 1000)
  return `${mins}m ${remainingSecs}s`
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

export type StatusColor = 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'brand'

export function getStatusColor(status?: string | null): StatusColor {
  if (!status || typeof status !== 'string') return 'neutral'
  const colors: Record<string, StatusColor> = {
    passed: 'success',
    failed: 'error',
    skipped: 'neutral',
    error: 'error',
    running: 'info',
    healthy: 'success',
    unhealthy: 'error',
    timeout: 'warning',
    open: 'error',
    in_progress: 'warning',
    resolved: 'success',
    ignored: 'neutral',
    deployed: 'success',
    deploying: 'info',
    pending: 'neutral',
    rolled_back: 'warning',
    green: 'success',
    yellow: 'warning',
    red: 'error',
    unknown: 'neutral',
  }
  return colors[status.toLowerCase()] ?? 'neutral'
}

export function getStatusLabel(status?: string | null): string {
  if (!status || typeof status !== 'string') return 'Unknown'
  return status
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ')
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length - 1) + '…'
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

export function generateId(): string {
  return Math.random().toString(36).slice(2, 11)
}