import React from 'react'
import { motion } from 'motion/react'
import { ChevronRight, Play, ArrowRight, ShieldCheck, Zap, Activity, Users, Bot, Sparkles } from 'lucide-react'

interface AppleHeroProps {
  onOpenTrial: () => void
}

export function AppleHero({ onOpenTrial }: AppleHeroProps) {
  return (
    <section id="overview" className="relative pt-16 pb-24 overflow-hidden bg-[#fbfbfd]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Apple Sub-Header Eyebrow */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 text-xs sm:text-sm font-semibold tracking-wide text-[#b64400] mb-3"
        >
          <span>INTRODUCING ASTRA OS</span>
        </motion.div>

        {/* Master Apple Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl sm:text-7xl lg:text-8xl font-semibold tracking-tight text-[#1d1d1f] max-w-5xl mx-auto leading-[1.05]"
        >
          Intelligence meets simplicity.
        </motion.h1>

        {/* Subheadline with Apple Clarity */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 text-lg sm:text-2xl text-[#86868b] max-w-3xl mx-auto font-normal leading-relaxed tracking-tight"
        >
          The autonomous AI operating system designed from the ground up for modern software companies. Effortlessly scale from your first customer to hundreds of thousands.
        </motion.p>

        {/* Apple-Style Action Links */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-5"
        >
          <button
            onClick={onOpenTrial}
            className="rounded-full bg-[#0071e3] hover:bg-[#0077ed] text-white px-7 py-3 text-sm font-medium tracking-tight shadow-sm hover:shadow-md transition-all active:scale-95 cursor-pointer"
          >
            Start free trial
          </button>

          <a
            href="#demo"
            className="inline-flex items-center gap-1.5 text-sm font-normal text-[#0071e3] hover:underline"
          >
            <span>Watch the interactive demo</span>
            <ChevronRight className="h-4 w-4" />
          </a>
        </motion.div>

        <div className="mt-3 text-xs text-[#86868b]">
          14-day full access. No credit card required.
        </div>

        {/* Apple-Style Studio Product Canvas Showcase */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-16 relative max-w-6xl mx-auto"
        >
          {/* Subtle Ambient Backing Glow */}
          <div className="absolute inset-0 bg-gradient-to-t from-blue-100/40 via-sky-50/20 to-transparent blur-3xl rounded-[3rem] -z-10" />

          {/* Canvas Window Container */}
          <div className="rounded-[2rem] sm:rounded-[2.5rem] border border-black/[0.08] bg-white p-3 sm:p-5 shadow-[0_30px_90px_-20px_rgba(0,0,0,0.12)]">
            {/* macOS Chrome Header */}
            <div className="flex items-center justify-between px-3 py-2 border-b border-black/[0.05] mb-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-[#ff5f57] inline-block" />
                <span className="h-3 w-3 rounded-full bg-[#febc2e] inline-block" />
                <span className="h-3 w-3 rounded-full bg-[#28c840] inline-block" />
              </div>

              <div className="px-4 py-1 rounded-full bg-[#f5f5f7] text-[11px] font-medium text-[#1d1d1f] flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                <span>app.astraos.cloud/console</span>
              </div>

              <div className="text-[11px] font-medium text-[#86868b]">
                Multi-Region Active
              </div>
            </div>

            {/* In-Canvas SaaS Studio UI Preview */}
            <div className="rounded-2xl bg-[#fafafa] border border-black/[0.04] p-5 sm:p-8 text-left">
              <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-black/[0.06]">
                <div>
                  <span className="text-xs font-semibold text-[#86868b] uppercase tracking-wider">
                    EXECUTIVE SAAS CONTROL PLANE
                  </span>
                  <h3 className="text-2xl font-bold text-[#1d1d1f] tracking-tight">
                    Global ARR & Customer Operations
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium border border-emerald-200">
                    SLA: 99.999% Optimal
                  </span>
                  <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-medium border border-blue-200">
                    28 PoPs Synced
                  </span>
                </div>
              </div>

              {/* 3 High-Impact Apple Studio Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
                <div className="rounded-2xl bg-white p-5 border border-black/[0.05] shadow-sm">
                  <div className="text-xs font-medium text-[#86868b]">Annual Recurring Revenue</div>
                  <div className="text-3xl font-semibold text-[#1d1d1f] mt-1 tracking-tight">
                    $14,840,000
                  </div>
                  <div className="text-xs font-medium text-emerald-600 mt-2 flex items-center gap-1">
                    <span>↑ +24.8% YoY</span>
                    <span className="text-[#86868b] font-normal">• Automated retention</span>
                  </div>
                </div>

                <div className="rounded-2xl bg-white p-5 border border-black/[0.05] shadow-sm">
                  <div className="text-xs font-medium text-[#86868b]">Autonomous Resolution</div>
                  <div className="text-3xl font-semibold text-[#1d1d1f] mt-1 tracking-tight">
                    78.4%
                  </div>
                  <div className="text-xs font-medium text-blue-600 mt-2 flex items-center gap-1">
                    <span>Zero Human Touch</span>
                    <span className="text-[#86868b] font-normal">• 1.4s avg response</span>
                  </div>
                </div>

                <div className="rounded-2xl bg-white p-5 border border-black/[0.05] shadow-sm">
                  <div className="text-xs font-medium text-[#86868b]">Edge P99 Latency</div>
                  <div className="text-3xl font-semibold text-[#1d1d1f] mt-1 tracking-tight">
                    12.2 ms
                  </div>
                  <div className="text-xs font-medium text-purple-600 mt-2 flex items-center gap-1">
                    <span>Global Anycast</span>
                    <span className="text-[#86868b] font-normal">• 28 regions</span>
                  </div>
                </div>
              </div>

              {/* Real-Time Workflow Stream Strip */}
              <div className="rounded-2xl bg-white p-4 sm:p-5 border border-black/[0.05] shadow-sm">
                <div className="flex items-center justify-between text-xs font-semibold text-[#1d1d1f] mb-3">
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-[#0071e3]" />
                    Live Autonomous Event Stream
                  </span>
                  <span className="text-[#86868b] font-normal">Real-Time WebSocket Tick</span>
                </div>

                <div className="space-y-2 text-xs font-mono">
                  <div className="p-2.5 rounded-xl bg-[#f5f5f7] flex items-center justify-between text-[#1d1d1f]">
                    <span className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-emerald-500" />
                      <span>[18:04:12] Tenant #8402 provisioned schema on EU-Central edge in 280ms</span>
                    </span>
                    <span className="text-[#86868b] font-sans text-[11px]">Completed</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[#f5f5f7] flex items-center justify-between text-[#1d1d1f]">
                    <span className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-blue-500" />
                      <span>[18:04:15] Churn risk score 0.04 - Account health validated optimal</span>
                    </span>
                    <span className="text-[#86868b] font-sans text-[11px]">Verified</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
