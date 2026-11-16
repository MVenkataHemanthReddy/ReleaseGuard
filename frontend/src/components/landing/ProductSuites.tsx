import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { 
  Zap, 
  Activity, 
  Bot, 
  Globe, 
  ArrowRight, 
  CheckCircle2, 
  Sliders, 
  Sparkles, 
  Layers,
  Terminal,
  Cpu,
  Database
} from 'lucide-react'

interface Suite {
  id: string
  code: string
  title: string
  tagline: string
  description: string
  icon: any
  color: string
  borderColor: string
  glowColor: string
  metrics: { label: string; value: string }[]
  capabilities: string[]
  previewTitle: string
  previewBadges: string[]
  visualMock: {
    stat1Title: string
    stat1Val: string
    stat2Title: string
    stat2Val: string
    radarLabel: string
    statusText: string
  }
}

const suites: Suite[] = [
  {
    id: 'astraflow',
    code: 'SAAS-01',
    title: 'AstraFlow™',
    tagline: 'Autonomous AI Workflow Orchestrator',
    description: 'Build, trigger, and scale complex event-driven business workflows with zero maintenance. Natural language prompt-to-pipeline engine with self-healing error recovery.',
    icon: Zap,
    color: 'from-cyan-400 to-blue-500',
    borderColor: 'border-cyan-500/40',
    glowColor: 'rgba(6, 182, 212, 0.25)',
    metrics: [
      { label: 'Execution Speed', value: '18ms average' },
      { label: 'Step Reliability', value: '99.999%' },
      { label: 'Dev Time Saved', value: '82% reduction' },
    ],
    capabilities: [
      'Prompt-to-Workflow: Generate production pipelines from plain English',
      'Event-Driven Webhooks across 500+ SaaS apps (Stripe, HubSpot, Salesforce)',
      'Deterministic State Machine with automated rollback on transaction failures',
      'Conditional Branching & Multi-Model AI Reasoning in every node'
    ],
    previewTitle: 'Autonomous Pipeline Graph & State Visualizer',
    previewBadges: ['Stripe Webhook', 'OpenAI / Anthropic', 'Postgres Edge', 'Slack Realtime'],
    visualMock: {
      stat1Title: 'Active Pipelines',
      stat1Val: '1,420 flows',
      stat2Title: 'Throughput',
      stat2Val: '48,000 runs/hr',
      radarLabel: 'Pipeline Execution Efficiency',
      statusText: 'All business logic executing autonomously'
    }
  },
  {
    id: 'astradata',
    code: 'SAAS-02',
    title: 'AstraData™',
    tagline: 'Real-Time Telemetry & Predictive Analytics',
    description: 'Transform raw clickstreams and product events into instant predictive revenue insights. Cohort retention modeling, churn probability detection, and ARR forecasting in real time.',
    icon: Activity,
    color: 'from-teal-400 to-emerald-500',
    borderColor: 'border-teal-500/40',
    glowColor: 'rgba(20, 184, 166, 0.25)',
    metrics: [
      { label: 'Ingest Rate', value: '1M events/sec' },
      { label: 'Query Latency', value: '< 25ms' },
      { label: 'Forecast Accuracy', value: '98.8%' },
    ],
    capabilities: [
      'Real-Time High-Throughput Event Streaming & Aggregation',
      'Predictive Customer Lifetime Value (LTV) & Churn Scoring',
      'Self-Service Natural Language SQL Query Engine for Product Teams',
      'Instant Sync with Snowflake, BigQuery, Databricks, and ClickHouse'
    ],
    previewTitle: 'Predictive Revenue & Product Telemetry Dashboard',
    previewBadges: ['1M+ events/s', 'Zero Lag', 'ClickHouse Powered', 'SOC2 Compliant'],
    visualMock: {
      stat1Title: 'Tracked ARR',
      stat1Val: '$48.2M',
      stat2Title: 'Retention Rate',
      stat2Val: '118% NRR',
      radarLabel: 'Predictive Churn Risk Surface',
      statusText: 'Telemetry synchronized across 12,000 active users'
    }
  },
  {
    id: 'astraagent',
    code: 'SAAS-03',
    title: 'AstraAgent™',
    tagline: 'Autonomous AI Copilots & Enterprise Workforce',
    description: 'Deploy specialized AI agents that act autonomously across your CRM, customer support desk, and internal tools. Context-aware, guardrailed, and integrated with your knowledge base.',
    icon: Bot,
    color: 'from-blue-400 to-indigo-500',
    borderColor: 'border-blue-500/40',
    glowColor: 'rgba(59, 130, 246, 0.25)',
    metrics: [
      { label: 'First Response', value: '< 1.4s' },
      { label: 'Ticket Resolution', value: '72% autonomous' },
      { label: 'Hallucination Rate', value: '0.00% bounded' },
    ],
    capabilities: [
      'Multi-Agent Collaboration: Specialized researcher, coder, and resolver swarms',
      'Deep RAG Integration with Notion, Jira, Zendesk, and GitHub docs',
      'Human-in-the-Loop Approval checkpoints for mission-critical actions',
      'Custom Tone of Voice & Dynamic Multi-Language Translation'
    ],
    previewTitle: 'Agent Swarm Coordination & Customer Resolution',
    previewBadges: ['72% Auto-Resolved', 'Zendesk Sync', 'Strict Guardrails', 'Multi-Lingual'],
    visualMock: {
      stat1Title: 'Autonomous Tickets',
      stat1Val: '8,920 resolved',
      stat2Title: 'CSAT Score',
      stat2Val: '4.95 / 5.0',
      radarLabel: 'Agent Response & Precision Vector',
      statusText: 'All agents operating within safety boundaries'
    }
  },
  {
    id: 'astramesh',
    code: 'SAAS-04',
    title: 'AstraMesh™',
    tagline: 'Global Enterprise Edge & Multi-Tenant Mesh',
    description: 'The foundation for hyper-scale SaaS. Dynamic tenant isolation, global edge caching, distributed database syncing, and zero-trust IAM authentication running in 28 regions.',
    icon: Globe,
    color: 'from-cyan-300 to-teal-200',
    borderColor: 'border-cyan-400/40',
    glowColor: 'rgba(5, 238, 250, 0.3)',
    metrics: [
      { label: 'Edge Locations', value: '28 PoPs' },
      { label: 'P99 Latency', value: '< 14ms' },
      { label: 'Global Uptime', value: '99.999% SLA' },
    ],
    capabilities: [
      'Automated Multi-Tenant Database Partitioning & Row-Level Security',
      'Global Anycast Edge Gateway with DDoS Protection & Rate Limiting',
      'Enterprise SAML / Okta SSO & SCIM Directory Sync Out-of-the-Box',
      'Cryptographic End-to-End Encryption with Hardware Security Modules (HSM)'
    ],
    previewTitle: 'Global Edge Mesh & Multi-Tenant Isolation',
    previewBadges: ['28 Global PoPs', 'SAML SSO', 'mTLS v1.3', 'Row-Level Isolation'],
    visualMock: {
      stat1Title: 'Active Tenants',
      stat1Val: '4,500 orgs',
      stat2Title: 'Mean Edge Latency',
      stat2Val: '11.8ms',
      radarLabel: 'Multi-Region Traffic Distribution',
      statusText: 'Zero downtime across all global cloud zones'
    }
  }
]

export function ProductSuites() {
  const [activeSuiteId, setActiveSuiteId] = useState('astraflow')
  const activeSuite = suites.find((s) => s.id === activeSuiteId) || suites[0]

  return (
    <section id="products" className="relative py-28 bg-[#030712] border-t border-cyan-500/10 overflow-hidden">
      {/* Decorative Cybernetic Background Rings */}
      <div className="absolute top-1/3 -right-48 w-96 h-96 rounded-full border border-cyan-500/15 animate-spin-slow pointer-events-none" />
      <div className="absolute bottom-10 -left-48 w-96 h-96 rounded-full border border-teal-500/10 animate-spin-reverse-slow pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <Layers className="h-3.5 w-3.5 text-cyan-400" />
            <span>UNIFIED SAAS PLATFORM ECOSYSTEM</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Four Pillars. Endless SaaS Possibilities.
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Every module in AstraOS works seamlessly together or as a standalone API to power your product's growth, intelligence, and scale.
          </p>
        </div>

        {/* 4 Interactive Suite Tabs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-10">
          {suites.map((s) => {
            const Icon = s.icon
            const isActive = s.id === activeSuiteId
            return (
              <button
                key={s.id}
                onClick={() => setActiveSuiteId(s.id)}
                className={`relative text-left p-5 rounded-2xl border transition-all duration-300 cursor-pointer ${
                  isActive
                    ? 'border-cyan-400 bg-cyan-950/40 shadow-[0_0_30px_rgba(5,238,250,0.25)]'
                    : 'border-zinc-800/80 bg-[#070d1d]/80 hover:border-zinc-700 hover:bg-[#0c1630]'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div
                    className={`p-2 rounded-xl border ${
                      isActive
                        ? 'border-cyan-400/60 bg-cyan-400/20 text-cyan-300'
                        : 'border-zinc-700 bg-zinc-800 text-zinc-400'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">
                    {s.code}
                  </span>
                </div>
                <div className="text-base font-bold text-white tracking-tight">{s.title}</div>
                <div className="text-xs text-zinc-400 mt-1 line-clamp-1">{s.tagline}</div>
                {isActive && (
                  <div className="absolute -bottom-[1px] left-6 right-6 h-[2px] bg-gradient-to-r from-cyan-400 to-teal-400" />
                )}
              </button>
            )
          })}
        </div>

        {/* Active Suite Deep-Dive Showcase */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeSuite.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.35 }}
            className="grid grid-cols-1 lg:grid-cols-12 gap-8 rounded-3xl border border-cyan-500/25 bg-[#070e20]/90 backdrop-blur-2xl p-6 sm:p-10 shadow-2xl shadow-cyan-950/30"
          >
            {/* Left Content (6 Cols) */}
            <div className="lg:col-span-6 flex flex-col justify-between space-y-6">
              <div>
                <div className="inline-flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">
                  <Sparkles className="h-3 w-3" />
                  <span>{activeSuite.code} ARCHITECTURE & CAPABILITIES</span>
                </div>
                <h3 className="text-3xl font-extrabold text-white tracking-tight">
                  {activeSuite.title}
                </h3>
                <p className="text-sm font-medium text-cyan-300 mt-1">
                  {activeSuite.tagline}
                </p>
                <p className="mt-4 text-sm text-zinc-300 leading-relaxed font-light">
                  {activeSuite.description}
                </p>
              </div>

              {/* Enterprise Capabilities Checklist */}
              <div>
                <div className="text-xs font-mono uppercase tracking-wider text-zinc-400 mb-3 font-semibold">
                  Core SaaS Features
                </div>
                <div className="space-y-2.5">
                  {activeSuite.capabilities.map((cap, idx) => (
                    <div key={idx} className="flex items-start gap-3 text-xs sm:text-sm text-zinc-200">
                      <div className="p-0.5 rounded-full bg-cyan-500/20 text-cyan-400 mt-0.5">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                      </div>
                      <span>{cap}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Three Metric Badges */}
              <div className="grid grid-cols-3 gap-3 pt-4 border-t border-zinc-800">
                {activeSuite.metrics.map((m, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-[#030611] border border-zinc-800/80">
                    <div className="text-base sm:text-lg font-bold font-mono text-white text-transparent bg-clip-text bg-gradient-to-r from-white to-cyan-300">
                      {m.value}
                    </div>
                    <div className="text-[10px] uppercase font-mono text-zinc-400 mt-0.5">
                      {m.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Visual Interactive Terminal HUD (6 Cols) */}
            <div className="lg:col-span-6 rounded-2xl border border-cyan-500/30 bg-[#02050f] p-6 flex flex-col justify-between shadow-inner">
              {/* Header of HUD */}
              <div className="border-b border-zinc-800 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
                    <span className="text-xs font-mono text-white font-medium">
                      {activeSuite.previewTitle}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
                    ENTERPRISE READY
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5 mt-3">
                  {activeSuite.previewBadges.map((badge, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] font-mono px-2 py-0.5 rounded-md border border-cyan-500/20 bg-cyan-950/30 text-cyan-300"
                    >
                      {badge}
                    </span>
                  ))}
                </div>
              </div>

              {/* Visual Simulated Mock Screen */}
              <div className="my-6 space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 rounded-xl bg-[#081024] border border-cyan-500/20">
                    <span className="text-[11px] font-mono text-zinc-400">
                      {activeSuite.visualMock.stat1Title}
                    </span>
                    <div className="text-xl font-bold font-mono text-cyan-300 mt-1">
                      {activeSuite.visualMock.stat1Val}
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-[#081024] border border-teal-500/20">
                    <span className="text-[11px] font-mono text-zinc-400">
                      {activeSuite.visualMock.stat2Title}
                    </span>
                    <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                      {activeSuite.visualMock.stat2Val}
                    </div>
                  </div>
                </div>

                {/* Simulated Radar Bar / HUD Scanner */}
                <div className="p-4 rounded-xl bg-[#050b1a] border border-zinc-800">
                  <div className="flex justify-between text-xs font-mono text-zinc-400 mb-2">
                    <span>{activeSuite.visualMock.radarLabel}</span>
                    <span className="text-cyan-400">99.98% HEALTH</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-zinc-800 overflow-hidden relative">
                    <div className="h-full w-4/5 rounded-full bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 relative">
                      <div className="absolute inset-0 bg-white/20 animate-pulse" />
                    </div>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono text-zinc-500 mt-1.5">
                    <span>Low Load</span>
                    <span>Auto-Balancing</span>
                    <span>Peak Throughput</span>
                  </div>
                </div>
              </div>

              {/* Footer of HUD */}
              <div className="border-t border-zinc-800/80 pt-4 flex items-center justify-between text-xs font-mono">
                <span className="text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  {activeSuite.visualMock.statusText}
                </span>
                <span className="text-zinc-500">v5.0</span>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  )
}
