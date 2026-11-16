import React, { useState } from 'react'
import { motion } from 'motion/react'
import { 
  Bot, 
  Zap, 
  Lock, 
  BellRing, 
  Database, 
  Sparkles, 
  Globe, 
  ArrowUpRight,
  Sliders,
  CheckCircle2
} from 'lucide-react'

export function BentoFeatures() {
  const [autonomyLevel, setAutonomyLevel] = useState(80)
  const [realtimeSync, setRealtimeSync] = useState(true)

  const integrations = [
    'Stripe',
    'Salesforce',
    'HubSpot',
    'Slack',
    'PostgreSQL',
    'OpenAI',
    'Snowflake',
    'Zendesk'
  ]

  return (
    <section id="features" className="relative py-28 bg-[#030712] border-t border-cyan-500/10 overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
            <span>ENTERPRISE SAAS BENTO MATRIX</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Engineered for Modern SaaS Scale
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Every feature is designed to automate manual labor, unlock predictive revenue growth, and eliminate infrastructure bottlenecks.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Bento Item 1: Large 2-Cols - Autonomous AI Copilot */}
          <div className="md:col-span-2 rounded-3xl border border-cyan-500/25 bg-[#070e20] p-7 sm:p-8 relative overflow-hidden flex flex-col justify-between group hover:border-cyan-400/50 transition-all duration-300 shadow-xl">
            <div className="absolute top-0 right-0 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                  <Bot className="h-6 w-6" />
                </div>
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                  AGENT SWARM v5.2
                </span>
              </div>
              <h3 className="text-2xl font-bold text-white tracking-tight">
                Autonomous AI Agent Swarm & Copilot
              </h3>
              <p className="mt-2 text-sm text-zinc-300 max-w-xl font-light">
                Empower your SaaS customers with specialized AI agents capable of resolving support tickets, executing multi-step CRM actions, and generating complex database queries.
              </p>
            </div>

            {/* Interactive Autonomy Slider inside Bento */}
            <div className="mt-6 p-5 rounded-2xl bg-[#030611] border border-zinc-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-zinc-400 flex items-center gap-1.5">
                  <Sliders className="h-3.5 w-3.5 text-cyan-400" />
                  Agent Autonomy Level:
                </span>
                <span className="text-cyan-300 font-bold">{autonomyLevel}% Autonomous</span>
              </div>
              <input
                type="range"
                min="30"
                max="100"
                value={autonomyLevel}
                onChange={(e) => setAutonomyLevel(Number(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer h-2 bg-zinc-800 rounded-lg"
              />
              <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                <span>Guided (Human Approval Required)</span>
                <span className="text-emerald-400">
                  {autonomyLevel > 75 ? 'Full Autonomous Resolution (Zero Touch)' : 'Co-pilot Assist'}
                </span>
              </div>
            </div>
          </div>

          {/* Bento Item 2: 1-Col - Real-time Sync */}
          <div className="rounded-3xl border border-teal-500/25 bg-[#070e20] p-7 relative overflow-hidden flex flex-col justify-between group hover:border-teal-400/50 transition-all duration-300 shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-400">
                  <Zap className="h-6 w-6" />
                </div>
                <span className="text-xs font-mono text-zinc-500">&lt;14ms LATENCY</span>
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Instant Real-Time Sync
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-zinc-300 font-light">
                Sub-millisecond event streaming and state synchronization across browser tabs and edge workers.
              </p>
            </div>

            <div className="mt-6 p-4 rounded-xl bg-[#030611] border border-zinc-800">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-zinc-300">Live WebSockets:</span>
                <button
                  onClick={() => setRealtimeSync(!realtimeSync)}
                  className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition cursor-pointer ${
                    realtimeSync
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                  }`}
                >
                  {realtimeSync ? 'ACTIVE STREAM' : 'PAUSED'}
                </button>
              </div>
              <div className="mt-2 text-[10px] font-mono text-zinc-500">
                142,000 active concurrent channels
              </div>
            </div>
          </div>

          {/* Bento Item 3: 1-Col - 500+ Integrations */}
          <div className="rounded-3xl border border-zinc-800 bg-[#070e20] p-7 relative overflow-hidden flex flex-col justify-between group hover:border-cyan-400/40 transition-all duration-300 shadow-xl">
            <div>
              <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 w-fit mb-4">
                <Globe className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                500+ SaaS App Mesh
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-zinc-300 font-light">
                One-click native connectors for payment gateways, CRMs, data warehouses, and messaging apps.
              </p>
            </div>

            <div className="mt-6 flex flex-wrap gap-2">
              {integrations.map((tool, idx) => (
                <span
                  key={idx}
                  className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-[#02050e] border border-zinc-800 text-zinc-300 hover:border-cyan-500/40 hover:text-cyan-300 transition"
                >
                  {tool}
                </span>
              ))}
            </div>
          </div>

          {/* Bento Item 4: 1-Col - Enterprise Security Vault */}
          <div className="rounded-3xl border border-zinc-800 bg-[#070e20] p-7 relative overflow-hidden flex flex-col justify-between group hover:border-teal-400/40 transition-all duration-300 shadow-xl">
            <div>
              <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 w-fit mb-4">
                <Lock className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Institutional Security
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-zinc-300 font-light">
                Enterprise compliance with row-level tenant encryption and continuous audit logging.
              </p>
            </div>

            <div className="mt-6 space-y-2">
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-300">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>SOC2 Type II & ISO 27001</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-300">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>AES-256 HSM KMS Keys</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-300">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>GDPR & HIPAA BAA Ready</span>
              </div>
            </div>
          </div>

          {/* Bento Item 5: 1-Col - Automated Ops Bot */}
          <div className="rounded-3xl border border-zinc-800 bg-[#070e20] p-7 relative overflow-hidden flex flex-col justify-between group hover:border-cyan-400/40 transition-all duration-300 shadow-xl">
            <div>
              <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 w-fit mb-4">
                <BellRing className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Slack & Teams Copilot
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-zinc-300 font-light">
                Trigger workflows, approve tenant upgrades, and query metrics directly inside your team's chat.
              </p>
            </div>

            <div className="mt-6 p-3.5 rounded-xl bg-[#030611] border border-zinc-800/80 text-xs font-mono text-zinc-300 flex items-center justify-between">
              <span className="text-cyan-400">/astra query mrr</span>
              <span className="text-zinc-500">$2.4M ARR (+18%)</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
