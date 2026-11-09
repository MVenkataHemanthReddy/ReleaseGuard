import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { ProjectProvider } from './context/ProjectContext'
import { Dashboard } from './pages/Dashboard'
import { Releases } from './pages/Releases'
import { ReleaseDetail } from './pages/ReleaseDetail'
import { ApiChecks } from './pages/ApiChecks'
import { Issues } from './pages/Issues'
import { Settings } from './pages/Settings'
import { Organizations } from './pages/Organizations'
import { LoadingScreen } from './components/ui/LoadingScreen'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  override render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '32px', fontFamily: 'system-ui, sans-serif', maxWidth: '800px', margin: '40px auto', background: '#ffffff', borderRadius: '12px', border: '1px solid #fee2e2', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
          <h2 style={{ color: '#dc2626', fontSize: '22px', fontWeight: 700, margin: '0 0 12px' }}>Dashboard Render Error</h2>
          <p style={{ color: '#4b5563', fontSize: '15px', lineHeight: 1.5, margin: '0 0 16px' }}>
            {this.state.error?.message || 'An error occurred while rendering the page.'}
          </p>
          {this.state.error?.stack && (
            <pre style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '16px', borderRadius: '8px', overflowX: 'auto', fontSize: '12px', color: '#334155', maxHeight: '300px' }}>
              {this.state.error.stack}
            </pre>
          )}
          <button
            onClick={() => {
              localStorage.clear()
              window.location.href = '/dashboard'
            }}
            style={{ marginTop: '20px', padding: '10px 20px', background: '#3b82f6', color: '#ffffff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '14px' }}
          >
            Reset State & Reload
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route element={<Layout />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="releases" element={<Releases />} />
        <Route path="releases/:releaseId" element={<ReleaseDetail />} />
        <Route path="api-checks" element={<ApiChecks />} />
        <Route path="issues" element={<Issues />} />
        <Route path="organizations" element={<Organizations />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export function App() {
  return (
    <ErrorBoundary>
      <ProjectProvider>
        <AppRoutes />
        <LoadingScreen />
      </ProjectProvider>
    </ErrorBoundary>
  )
}
