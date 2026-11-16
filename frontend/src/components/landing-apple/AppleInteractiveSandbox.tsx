import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { CheckCircle2, Play, RotateCcw, ChevronRight, Zap, ShieldCheck, Activity, Users, Bot, Sparkles } from 'lucide-react'

interface Scenario {
  id: string
  title: string
  tag: string
  subtitle: string
  metric1: { label: string; value: string }
  metric2: { label: string; value: string }
  metric3: { label: string; value: string }
  steps: { title: string; desc: string; time: string }[]
  outcome: string
}

const scenarios: Scenario[] = [
  {
    id: 'onboard',
    title: 'Customer Onboarding',
    tag: 'AUTONOMOUS ZERO-TOUCH',
    subtitle: 'From signup click to fully provisioned workspace in under half a second.',
    metric1: { label: 'Provisioning Time', value: '340ms' },
    metric2: { label: 'Completion Rate', value: '99.8%' },
    metric3: { label: 'Human Intervention', value: '0 minutes' },
    steps: [
      { title: 'User Account Created', desc: 'Enterprise signup webhook received from app gateway', time: '0ms' },
      { title: 'AML & Fraud Screening', desc: 'Global database query verifies domain authenticity', time: '+18ms' },
      { title: 'Multi-Tenant Database Isolated', desc: 'Dedicated schema provisioned with AES-256 keys', time: '+140ms' },
      { title: 'Personalized AI Copilot Ready', desc: 'Workspace context loaded into autonomous agent', time: '+340ms' },
    ],
    outcome: 'Tenant live and operational across 28 global edge nodes.'
  },
  {
    id: 'churn',
    title: 'Churn Prevention',
    tag: 'REVENUE PROTECTION',
    subtitle: 'Detect usage anomalies weeks early and automatically trigger retention playbooks.',
    metric1: { label: 'ARR Protected', value: '$184,000' },
    metric2: { label: 'Intervention Speed', value: '< 2.1s' },
    metric3: { label: 'Customer Retention', value: '94.2%' },
    steps: [
      { title: 'Usage Velocity Analyzed', desc: 'Telemetry identifies a 35% drop in weekly active sessions', time: '0ms' },
      { title: 'Predictive Model Evaluation', desc: 'Churn risk computed at 87.4% probability within 14 days', time: '+45ms' },
      { title: 'Personalized Retention Incentive', desc: 'Bonus copilot seats auto-allocated to target account', time: '+120ms' },
      { title: 'Executive CSM Brief Dispatched', desc: 'Tailored ROI summary delivered directly to Slack', time: '+2.1s' },
    ],
    outcome: 'Account health score restored to 96/100 without manual churn firefighting.'
  },
  {
    id: 'scale',
    title: 'Global Edge Scale',
    tag: 'HIGH VELOCITY TRAFFIC',
    subtitle: 'Seamlessly absorb traffic spikes with serverless Anycast edge elasticity.',
    metric1: { label: 'Throughput', value: '142,000 req/s' },
    metric2: { label: 'Global P99 Latency', value: '12.4ms' },
    metric3: { label: 'Availability', value: '100.00%' },
    steps: [
      { title: 'Incoming Traffic Wave', desc: 'Anycast DNS resolves requests to closest geographical PoP', time: '0ms' },
      { title: 'Zero-Trust Token Validation', desc: 'Ed25519 cryptographic tokens verified at edge border', time: '+1.1ms' },
      { title: 'Elastic Worker Auto-Scaling', desc: 'Serverless instances expand by +44 micro-nodes instantly', time: '+24ms' },
      { title: 'Response Stream Dispatched', desc: 'Sub-15ms round-trip latency maintained across all continents', time: '+12.4ms' },
    ],
    outcome: '0 dropped packets, 100% SLA uptime, zero origin database overload.'
  }
]

export function AppleInteractiveSandbox() {
  const [activeId, setActiveId] = useState('onboard')
  const [isRunning, setIsRunning] = useState(false)

  const current = scenarios.find((s) => s.id === activeId) || scenarios[0]

  const handleSimulate = (id: string) => {
    setIsRunning(true)
    setActiveId(id)
    setTimeout(() => {
      setIsRunning(false)
    }, 400)
  }

  return (
    <section id="demo" className="py-24 bg-[#fbfbfd] border-t border-black/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
            INTERACTIVE DEMO
          </span>
          <h2 className="text-4xl sm:text-6xl font-semibold text-[#1d1d1f] tracking-tight mt-2">
            See simplicity in action.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#86868b] font-normal leading-relaxed">
            Select a live workflow to test how AstraOS autonomously manages customer lifecycle events in real time.
          </p>
        </div>

        {/* Apple-style Pill Segmented Control */}
        <div className="flex justify-center mb-10">
          <div className="inline-flex rounded-full bg-[#e8e8ed] p-1.5 shadow-inner">
            {scenarios.map((sc) => {
              const isActive = sc.id === activeId
              return (
                <button
                  key={sc.id}
                  onClick={() => handleSimulate(sc.id)}
                  className={`rounded-full px-5 py-2 text-xs sm:text-sm font-medium transition-all duration-200 cursor-pointer ${
                    isActive
                      ? 'bg-white text-[#1d1d1f] shadow-sm'
                      : 'text-[#86868b] hover:text-[#1d1d1f]'
                  }`}
                >
                  {sc.title}
                </button>
              )
            })}
          </div>
        </div>

        {/* Apple Studio Sandbox Card */}
        <div className="rounded-[2.5rem] bg-white border border-black/[0.06] p-6 sm:p-12 shadow-[0_20px_70px_-15px_rgba(0,0,0,0.07)] max-w-5xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-baseline justify-between gap-4 pb-8 border-b border-black/[0.06]">
            <div>
              <span className="text-xs font-semibold text-[#0071e3] tracking-wide uppercase">
                {current.tag}
              </span>
              <h3 className="text-2xl sm:text-3xl font-semibold text-[#1d1d1f] tracking-tight mt-1">
                {current.title}
              </h3>
              <p className="text-sm text-[#86868b] mt-1 font-normal">
                {current.subtitle}
              </p>
            </div>

            <button
              onClick={() => handleSimulate(activeId)}
              className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-[#f5f5f7] hover:bg-[#e8e8ed] px-4 py-2 text-xs font-medium text-[#1d1d1f] transition-all cursor-pointer self-start md:self-auto"
            >
              <RotateCcw className="h-3.5 w-3.5 text-[#0071e3]" />
              <span>Re-run workflow</span>
            </button>
          </div>

          {/* 3 Apple Highlight Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-8">
            <div className="rounded-2xl bg-[#f5f5f7] p-5">
              <div className="text-xs font-medium text-[#86868b]">{current.metric1.label}</div>
              <div className="text-3xl font-semibold text-[#1d1d1f] mt-1 tracking-tight">
                {current.metric1.value}
              </div>
            </div>

            <div className="rounded-2xl bg-[#f5f5f7] p-5">
              <div className="text-xs font-medium text-[#86868b]">{current.metric2.label}</div>
              <div className="text-3xl font-semibold text-[#1d1d1f] mt-1 tracking-tight">
                {current.metric2.value}
              </div>
            </div>

            <div className="rounded-2xl bg-[#f5f5f7] p-5">
              <div className="text-xs font-medium text-[#86868b]">{current.metric3.label}</div>
              <div className="text-3xl font-semibold text-[#1d1d1f] mt-1 tracking-tight">
                {current.metric3.value}
              </div>
            </div>
          </div>

          {/* Clean Stepper Execution Diagram */}
          <div className="space-y-3.5 my-8">
            {current.steps.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between p-4 rounded-2xl bg-[#fbfbfd] border border-black/[0.04] hover:border-black/[0.1] transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 mt-0.5">
                    <CheckCircle2 className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-[#1d1d1f]">{step.title}</div>
                    <div className="text-xs text-[#86868b] mt-0.5">{step.desc}</div>
                  </div>
                </div>
                <span className="text-xs font-mono font-medium text-[#0071e3] bg-blue-50 px-2.5 py-1 rounded-full shrink-0">
                  {step.time}
                </span>
              </div>
            ))}
          </div>

          {/* Outcome Footer */}
          <div className="pt-6 border-t border-black/[0.06] flex items-center justify-between text-xs text-[#86868b]">
            <span className="flex items-center gap-1.5 font-medium text-[#1d1d1f]">
              <Sparkles className="h-4 w-4 text-[#0071e3]" />
              {current.outcome}
            </span>
            <span className="font-mono">Astra Core Engine v2.4</span>
          </div>
        </div>
      </div>
    </section>
  )
}
