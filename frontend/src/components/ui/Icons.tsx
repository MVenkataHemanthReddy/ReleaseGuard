import React from 'react'
import { 
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  BarChart2,
  Bell,
  Bug,
  Building2,
  Check,
  CheckCircle,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Clock,
  Copy,
  Database,
  Download,
  Edit,
  ExternalLink,
  Eye,
  EyeOff,
  FileText,
  Filter,
  GitBranch,
  Github,
  Gitlab,
  Info,
  Key,
  LayoutDashboard,
  LogOut,
  MonitorCheck,
  Moon,
  MoreVertical,
  Palette,
  Pause,
  Play,
  Plus,
  RefreshCw,
  Search,
  Server,
  Settings,
  Shield,
  Sun,
  Trash2,
  TrendingDown,
  TrendingUp,
  User,
  Users,
  X,
  XCircle,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function Bitbucket(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M2.65 3C2.3 3 2 3.3 2 3.65c0 .08.02.16.05.23l2.87 16.27c.07.41.42.72.84.72h12.48c.42 0 .77-.31.84-.72L21.95 3.88c.03-.07.05-.15.05-.23 0-.35-.3-.65-.65-.65H2.65zm3.76 14.88L4.62 5.09h14.76l-1.79 12.79H6.41z" />
    </svg>
  )
}

export {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  BarChart2,
  Bell,
  Bug,
  Building2,
  Check,
  CheckCircle,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Clock,
  Copy,
  Database,
  Download,
  Edit,
  ExternalLink,
  Eye,
  EyeOff,
  FileText,
  Filter,
  GitBranch,
  Github,
  Gitlab,
  Info,
  Key,
  LayoutDashboard,
  LogOut,
  MonitorCheck,
  Moon,
  MoreVertical,
  Palette,
  Pause,
  Play,
  Plus,
  RefreshCw,
  Search,
  Server,
  Settings,
  Shield,
  Sun,
  Trash2,
  TrendingDown,
  TrendingUp,
  User,
  Users,
  X,
  XCircle,
  Zap,
}

// Logo icon
export function LogoIcon({ className, ...props }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      {...props}
    >
      <rect width="32" height="32" rx="8" fill="currentColor" />
      <path
        d="M8 12h16M8 16h12M8 20h8"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

// Status indicators
export function StatusDot({ status, size = 8 }: { status: string; size?: number }) {
  const colors: Record<string, string> = {
    passed: 'text-emerald-500',
    failed: 'text-red-500',
    skipped: 'text-surface-400',
    error: 'text-red-500',
    running: 'text-blue-500',
    healthy: 'text-emerald-500',
    unhealthy: 'text-red-500',
    timeout: 'text-amber-500',
    open: 'text-red-500',
    in_progress: 'text-amber-500',
    resolved: 'text-emerald-500',
    ignored: 'text-surface-400',
    deployed: 'text-emerald-500',
    deploying: 'text-blue-500',
    pending: 'text-surface-400',
    rolled_back: 'text-amber-500',
    GREEN: 'text-emerald-500',
    YELLOW: 'text-amber-500',
    RED: 'text-red-500',
    UNKNOWN: 'text-surface-400',
  }
  
  return (
    <span
      className={cn('inline-block rounded-full', colors[status] || 'text-surface-400')}
      style={{ width: size, height: size }}
      aria-label={status}
    />
  )
}
