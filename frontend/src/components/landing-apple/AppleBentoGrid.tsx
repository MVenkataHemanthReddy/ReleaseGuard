import React, { useState } from 'react'
import { motion } from 'motion/react'
import { Bot, Zap, Lock, Globe, Layers, ArrowRight, ShieldCheck, Sparkles, Sliders } from 'lucide-react'

export function AppleBentoGrid() {
  const [sliderVal, setSliderVal] = useState(85)

  const integrations = [
    'Stripe',
    'PostgreSQL',
    'Salesforce',
    'Slack',
    'Snowflake',
    'OpenAI',
    'HubSpot',
    'Zendesk',
    'Supabase',
    'AWS'
  ]

  return (
    <section id="capabilities" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Apple Keynote Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
            BUILT DIFFERENTLY
          </span>
          <h2 className="text-4xl sm:text-6xl font-semibold text-[#1d1d1f] tracking-tight mt-2">
            Remarkably capable.<br />Effortlessly simple.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#86868b] font-normal leading-relaxed">
            Every layer of AstraOS is meticulously engineered to provide maximum power with zero cognitive load.
          </p>
        </div>

        {/* Bento Grid Container */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Bento 1: Large 2-Cols - Multi-Agent Swarm */}
          <div className="md:col-span-2 rounded-[2rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white text-xs font-medium text-[#1d1d1f] shadow-sm mb-4">
                <Bot className="h-3.5 w-3.5 text-[#0071e3]" />
                <span>Autonomous Multi-Agent Swarms</span>
              </div>
              <h3 className="text-2xl sm:text-4xl font-semibold text-[#1d1d1f] tracking-tight">
                Intelligence that acts.<br />Not just chats.
              </h3>
              <p className="mt-3 text-sm sm:text-base text-[#86868b] max-w-xl font-normal leading-relaxed">
                Deploy specialized autonomous agents that coordinate across your support desk, billing system, and database to resolve customer requests in milliseconds without hallucination.
              </p>
            </div>

            {/* Apple-style Interactive Control inside Bento */}
            <div className="mt-8 rounded-2xl bg-white p-6 border border-black/[0.05] shadow-sm">
              <div className="flex items-center justify-between text-xs font-medium text-[#1d1d1f] mb-3">
                <span className="flex items-center gap-1.5">
                  <Sliders className="h-4 w-4 text-[#0071e3]" />
                  Autonomous Resolution Threshold:
                </span>
                <span className="font-semibold text-[#0071e3]">{sliderVal}% Auto-Resolved</span>
              </div>
              <input
                type="range"
                min="40"
                max="95"
                value={sliderVal}
                onChange={(e) => setSliderVal(Number(e.target.value))}
                className="w-full accent-[#0071e3] cursor-pointer h-2 bg-[#f5f5f7] rounded-lg"
              />
              <div className="mt-3 flex items-center justify-between text-[11px] text-[#86868b]">
                <span>Supervised (Human Approval Required)</span>
                <span className="text-emerald-600 font-medium">
                  {sliderVal > 75 ? 'Full Autonomous Zero-Touch' : 'Copilot Suggestion'}
                </span>
              </div>
            </div>
          </div>

          {/* Bento 2: 1-Col - Speed & Latency */}
          <div className="rounded-[2rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white text-xs font-medium text-[#1d1d1f] shadow-sm mb-4">
                <Zap className="h-3.5 w-3.5 text-amber-500" />
                <span>Anycast Edge Ingress</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-semibold text-[#1d1d1f] tracking-tight">
                12 milliseconds.<br />Speed you can feel.
              </h3>
              <p className="mt-3 text-xs sm:text-sm text-[#86868b] font-normal leading-relaxed">
                Queries and webhooks resolve at the closest point of presence across 28 global regions with zero round-trip lag.
              </p>
            </div>

            <div className="mt-8 rounded-2xl bg-white p-5 border border-black/[0.05] shadow-sm text-center">
              <div className="text-4xl font-semibold text-[#1d1d1f] tracking-tight">
                99.999%
              </div>
              <div className="text-xs font-medium text-emerald-600 mt-1">
                Guaranteed Enterprise SLA Uptime
              </div>
            </div>
          </div>

          {/* Bento 3: 1-Col - Apple Signature Privacy Card */}
          <div className="rounded-[2rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white text-xs font-medium text-[#1d1d1f] shadow-sm mb-4">
                <Lock className="h-3.5 w-3.5 text-emerald-600" />
                <span>Data Isolation</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-semibold text-[#1d1d1f] tracking-tight">
                Privacy. That's Astra.
              </h3>
              <p className="mt-3 text-xs sm:text-sm text-[#86868b] font-normal leading-relaxed">
                Your proprietary customer data and prompts never train public foundation models. Strictly encrypted at rest and in transit.
              </p>
            </div>

            <div className="mt-8 space-y-2">
              <div className="flex items-center gap-2 text-xs font-medium text-[#1d1d1f]">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                <span>SOC 2 Type II Certified</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-[#1d1d1f]">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                <span>Row-Level Tenant Isolation</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium text-[#1d1d1f]">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                <span>GDPR & HIPAA BAA Ready</span>
              </div>
            </div>
          </div>

          {/* Bento 4: Large 2-Cols - 500+ Native Ecosystem */}
          <div className="md:col-span-2 rounded-[2rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white text-xs font-medium text-[#1d1d1f] shadow-sm mb-4">
                <Globe className="h-3.5 w-3.5 text-blue-500" />
                <span>Universal App Mesh</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-semibold text-[#1d1d1f] tracking-tight">
                Plays beautifully with everything you already use.
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-[#86868b] font-normal leading-relaxed max-w-xl">
                One-click native webhooks and pre-authenticated connectors for billing, communication, and databases.
              </p>
            </div>

            <div className="mt-6 flex flex-wrap gap-2.5">
              {integrations.map((app, idx) => (
                <span
                  key={idx}
                  className="rounded-full bg-white border border-black/[0.06] px-4 py-1.5 text-xs font-medium text-[#1d1d1f] shadow-sm hover:border-[#0071e3] transition-colors"
                >
                  {app}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
