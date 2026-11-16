import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { 
  Terminal, 
  RotateCcw, 
  Activity, 
  Cpu, 
  Radio, 
  CheckCircle2, 
  Sliders, 
  Database,
  Play,
  Zap,
  TrendingUp,
  Users,
  ShieldCheck,
  Bot
} from 'lucide-react'

interface SaaSFlow {
  id: string
  title: string
  module: string
  status: 'ACTIVE' | 'SCALING' | 'OPTIMIZED'
  metric1Label: string
  metric1Val: string
  metric2Label: string
  metric2Val: string
  metric3Label: string
  metric3Val: string
  verdict: string
  workflowSteps: string[]
  liveLogs: string[]
}

const flows: SaaSFlow[] = [
  {
    id: 'onboarding',
    title: 'Autonomous User Onboarding & KYC',
    module: 'astra-agent-identity',
    status: 'OPTIMIZED',
    metric1Label: 'Pipeline Duration',
    metric1Val: '340ms',
    metric2Label: 'Completion Rate',
    metric2Val: '99.8%',
    metric3Label: 'Fraud Detection',
    metric3Val: '0.00% False Positives',
    verdict: 'TENANT PROVISIONED • COPILOT ACTIVATED IN 340ms',
    workflowSteps: [
      'Webhook received: New enterprise account creation trigger',
      'AI Fraud & Sanction screening completed in 18ms via global database',
      'Dedicated multi-tenant schema dynamically provisioned on Postgres Edge',
      'Personalized in-app AI onboarding agent assigned & workspace ready'
    ],
    liveLogs: [
      '[18:00:12.104] [INGEST] POST /v1/auth/signup - Company: "HyperScale Tech"',
      '[18:00:12.112] [AML_GUARD] Zero fraud risk vectors detected (Score: 0.01)',
      '[18:00:12.124] [DATABASE] Multi-tenant schema #tenant_8492 isolated on AWS eu-central',
      '[18:00:12.138] [AI_AGENT] AstraCopilot initialized with custom company context',
      '[18:00:12.145] [DISPATCH] Slack welcome webhook dispatched to client success team'
    ]
  },
  {
    id: 'churn',
    title: 'Predictive Churn & Revenue Guard',
    module: 'astra-pulse-intelligence',
    status: 'ACTIVE',
    metric1Label: 'ARR Protected',
    metric1Val: '$184,000',
    metric2Label: 'Intervention Time',
    metric2Val: '< 2.1s',
    metric3Label: 'Retention Success',
    metric3Val: '94.2%',
    verdict: 'AUTOMATED RETENTION PLAYBOOK EXECUTED',
    workflowSteps: [
      'Event telemetry detects 35% decline in daily active seats for Account #A-901',
      'Predictive ML model flags churn probability: 87.4% within 14 days',
      'Triggered automated custom VIP incentive & allocated senior solutions engineer',
      'Executive stakeholder notified with tailored expansion ROI brief'
    ],
    liveLogs: [
      '[18:01:05.420] [TELEMETRY] Ingesting 120,000 product activity events / sec',
      '[18:01:05.429] [CHURN_SIGNAL] Account "Global FinCore" usage pattern anomaly flagged',
      '[18:01:05.437] [NEURAL_SCORE] Projected retention risk: 87.4% (Threshold: 60%)',
      '[18:01:05.445] [ACTION_TRIGGER] Auto-provisioned 15 bonus AI seats & scheduled CSM check-in',
      '[18:01:05.452] [RESOLVED] Account health score recovered to 96/100'
    ]
  },
  {
    id: 'edge',
    title: 'Global High-Throughput API Gateway',
    module: 'astra-mesh-gateway',
    status: 'SCALING',
    metric1Label: 'Throughput',
    metric1Val: '142,000 req/s',
    metric2Label: 'Global P99 Latency',
    metric2Val: '12.4ms',
    metric3Label: 'Edge Availability',
    metric3Val: '100.00%',
    verdict: 'GLOBAL TRAFFIC ROUTED ACROSS 28 REGIONS',
    workflowSteps: [
      'Anycast DNS routes client queries to closest geographic Point of Presence',
      'Smart caching layer resolves 89.4% of reads without database origin hits',
      'Zero-trust token verification verified at edge boundary in <1.2ms',
      'Dynamic auto-scaler adjusted replica pool from 24 -> 68 micro-nodes'
    ],
    liveLogs: [
      '[18:02:44.019] [DNS_ROUTING] Incoming burst from APAC-South, redirecting to Singapore PoP',
      '[18:02:44.025] [AUTH_CACHE] JWT Ed25519 cryptographic token validated locally (1.1ms)',
      '[18:02:44.032] [AUTOSCALE] Scaling edge micro-instances +44 nodes to handle traffic wave',
      '[18:02:44.041] [LATENCY] P99 stabilized at 12.4ms across all 28 edge locations',
      '[18:02:44.049] [STATUS] 0 dropped packets • 100.00% continuous uptime maintained'
    ]
  }
]

export function LiveSimulationTerminal() {
  const [activeFlowId, setActiveFlowId] = useState('onboarding')
  const [isRefreshing, setIsRefreshing] = useState(false)

  const current = flows.find((f) => f.id === activeFlowId) || flows[0]

  const handleSwitch = (id: string) => {
    setIsRefreshing(true)
    setActiveFlowId(id)
    setTimeout(() => {
      setIsRefreshing(false)
    }, 350)
  }

  return (
    <section id="demo" className="relative py-24 bg-[#040815] border-t border-cyan-500/15 overflow-hidden">
      {/* Background Radial Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[850px] h-[400px] bg-cyan-600/10 blur-[140px] pointer-events-none rounded-full" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <Activity className="h-3.5 w-3.5 text-cyan-400" />
            <span>INTERACTIVE SAAS CONTROL PLANE DEMO</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Experience the Autonomous Engine Live
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Toggle between live SaaS production workflows and watch how AstraOS orchestrates user onboarding, revenue protection, and edge scalability in real time.
          </p>
        </div>

        {/* Interactive Workflow Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
          {flows.map((flow) => {
            const isActive = flow.id === activeFlowId
            return (
              <button
                key={flow.id}
                onClick={() => handleSwitch(flow.id)}
                className={`relative flex items-center gap-3 px-5 py-3 rounded-xl font-medium text-xs sm:text-sm transition-all duration-300 border cursor-pointer ${
                  isActive
                    ? 'border-cyan-400 bg-cyan-950/60 text-white shadow-[0_0_25px_rgba(5,238,250,0.3)]'
                    : 'border-zinc-800 bg-[#090f1f]/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
                }`}
              >
                <div
                  className={`h-2.5 w-2.5 rounded-full ${
                    flow.status === 'OPTIMIZED'
                      ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                      : flow.status === 'ACTIVE'
                      ? 'bg-cyan-400 shadow-[0_0_8px_#38bdf8]'
                      : 'bg-teal-400 shadow-[0_0_8px_#2dd4bf]'
                  }`}
                />
                <span className="font-mono">{flow.title}</span>
                {isActive && (
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
                    Live Telemetry
                  </span>
                )}
              </button>
            )
          })}
        </div>

        {/* Interactive Console Terminal HUD */}
        <div className="relative rounded-2xl border border-cyan-500/30 bg-[#070d1d]/90 backdrop-blur-2xl overflow-hidden shadow-2xl shadow-cyan-950/50">
          {/* Top Bar / Mac-Style HUD Header */}
          <div className="flex flex-wrap items-center justify-between border-b border-zinc-800/80 px-6 py-4 bg-[#0a1228]/80">
            <div className="flex items-center gap-3">
              <div className="flex gap-1.5">
                <span className="h-3 w-3 rounded-full bg-rose-500/80 inline-block" />
                <span className="h-3 w-3 rounded-full bg-amber-500/80 inline-block" />
                <span className="h-3 w-3 rounded-full bg-emerald-500/80 inline-block" />
              </div>
              <div className="h-4 w-[1px] bg-zinc-800 mx-1" />
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-300">
                <Radio className="h-3.5 w-3.5 text-cyan-400 animate-pulse" />
                <span>active_worker: <strong className="text-white">{current.module}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono text-zinc-400 mt-2 sm:mt-0">
              <span className="hidden md:inline">Protocol: Async Event Bus</span>
              <span className="text-zinc-600">|</span>
              <span className="flex items-center gap-1.5 text-cyan-300">
                <Bot className="h-3.5 w-3.5" /> Engine: Astra-Autonomous-Core
              </span>
            </div>
          </div>

          {/* Main Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 sm:p-8">
            {/* Left Column: Diagnostics & Workflow Orchestration (7 Cols) */}
            <div className="lg:col-span-7 space-y-6">
              {/* Verdict Banner */}
              <div className="p-5 rounded-xl border border-emerald-500/40 bg-emerald-950/20 text-emerald-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="p-2.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40">
                    <ShieldCheck className="h-6 w-6 text-emerald-400" />
                  </div>
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-zinc-400">
                      Autonomous Pipeline Status
                    </div>
                    <div className="text-base sm:text-lg font-bold font-mono tracking-tight text-white">
                      {current.verdict}
                    </div>
                  </div>
                </div>

                <div className="text-right sm:border-l sm:border-zinc-800/80 sm:pl-4">
                  <div className="text-[11px] font-mono text-zinc-400">Execution Health</div>
                  <div className="text-2xl font-black font-mono text-emerald-400">
                    100.0%
                  </div>
                </div>
              </div>

              {/* Real-time Metric Dials */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-4 rounded-xl bg-[#0b1428] border border-zinc-800">
                  <div className="text-xs font-mono text-zinc-400">{current.metric1Label}</div>
                  <div className="mt-1 text-xl font-bold font-mono text-white">{current.metric1Val}</div>
                  <div className="mt-1 text-[11px] font-mono text-cyan-400">Sub-Second SLA</div>
                </div>

                <div className="p-4 rounded-xl bg-[#0b1428] border border-zinc-800">
                  <div className="text-xs font-mono text-zinc-400">{current.metric2Label}</div>
                  <div className="mt-1 text-xl font-bold font-mono text-white">{current.metric2Val}</div>
                  <div className="mt-1 text-[11px] font-mono text-emerald-400">Automated Scale</div>
                </div>

                <div className="p-4 rounded-xl bg-[#0b1428] border border-zinc-800">
                  <div className="text-xs font-mono text-zinc-400">{current.metric3Label}</div>
                  <div className="mt-1 text-xl font-bold font-mono text-white">{current.metric3Val}</div>
                  <div className="mt-1 text-[11px] font-mono text-teal-400">Enterprise Verified</div>
                </div>
              </div>

              {/* Workflow Step Breakdown */}
              <div className="p-5 rounded-xl bg-[#081024] border border-cyan-500/20">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono uppercase tracking-wider text-cyan-300 font-semibold flex items-center gap-2">
                    <Sliders className="h-3.5 w-3.5 text-cyan-400" />
                    Autonomous Orchestration Pipeline
                  </span>
                  <span className="text-[10px] font-mono text-zinc-500">Zero Manual Coding</span>
                </div>
                <div className="space-y-2.5">
                  {current.workflowSteps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-zinc-300">
                      <span className="text-cyan-400 font-mono mt-0.5">❯</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Live Event Stream Terminal (5 Cols) */}
            <div className="lg:col-span-5 flex flex-col justify-between rounded-xl bg-[#02050e] border border-zinc-800/80 p-5 font-mono text-xs">
              <div>
                <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-3">
                  <span className="text-zinc-400 flex items-center gap-2">
                    <Terminal className="h-3.5 w-3.5 text-cyan-400" />
                    LIVE TELEMETRY STREAM
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                    REALTIME
                  </span>
                </div>

                <div className="space-y-2.5 text-zinc-300 overflow-y-auto max-h-[260px] pr-2">
                  {current.liveLogs.map((log, idx) => (
                    <div key={idx} className="leading-relaxed hover:text-white transition-colors">
                      {log.includes('RESOLVED') || log.includes('PROVISIONED') || log.includes('dispatched') ? (
                        <span className="text-emerald-400 font-semibold">{log}</span>
                      ) : log.includes('FLAGGED') || log.includes('RISK') ? (
                        <span className="text-cyan-300 font-medium">{log}</span>
                      ) : (
                        <span className="text-zinc-400">{log}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Bottom Interactive Trigger */}
              <div className="mt-6 pt-4 border-t border-zinc-900 flex items-center justify-between">
                <span className="text-[11px] text-zinc-500">Autonomous Worker: astra-core-v5</span>
                <button
                  onClick={() => handleSwitch(activeFlowId)}
                  className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium transition cursor-pointer"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span>Re-trigger Pipeline</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
