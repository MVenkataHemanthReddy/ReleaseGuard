import React, { useState } from 'react'
import { motion } from 'motion/react'
import { Calculator, DollarSign, Clock, TrendingUp, Sparkles, ArrowRight, Users } from 'lucide-react'

interface RoiCalculatorProps {
  onOpenDemo: () => void
}

export function RoiCalculator({ onOpenDemo }: RoiCalculatorProps) {
  const [activeCustomers, setActiveCustomers] = useState(1200)
  const [avgAcv, setAvgAcv] = useState(2400) // $2400/yr ACV
  const [teamSize, setTeamSize] = useState(30)

  // SaaS ROI Calculations:
  // 1. Churn reduction: AstraOS reduces churn by ~2.8% on average
  const totalARR = activeCustomers * avgAcv
  const preservedARR = Math.round(totalARR * 0.028)

  // 2. Automated AI support & workflow hours saved: ~8 hours per team member per month
  const totalHoursSavedYearly = Math.round(teamSize * 8 * 12)
  const opsCostSavings = Math.round(totalHoursSavedYearly * 75) // $75/hr avg ops/dev cost

  // 3. Total Annual Value Created
  const totalAnnualValue = preservedARR + opsCostSavings

  return (
    <section id="roi" className="relative py-28 bg-[#040817] border-t border-cyan-500/10 overflow-hidden">
      {/* Background radial highlight */}
      <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-96 h-96 bg-cyan-600/10 blur-[140px] pointer-events-none rounded-full" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <Calculator className="h-3.5 w-3.5 text-cyan-400" />
            <span>SAAS VALUE & ARR EXPANSION MODEL</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Calculate Your SaaS Growth & Efficiency ROI
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Measure the exact revenue protected from churn and operational labor hours reclaimed by automating your SaaS stack with AstraOS.
          </p>
        </div>

        {/* Interactive Calculator Bento Box */}
        <div className="rounded-3xl border border-cyan-500/25 bg-[#060c1d]/90 backdrop-blur-2xl p-6 sm:p-10 shadow-2xl">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Controls (6 Cols) */}
            <div className="lg:col-span-6 space-y-7">
              {/* Slider 1: Customers */}
              <div>
                <div className="flex justify-between items-center text-sm font-mono mb-2">
                  <span className="text-zinc-300 font-medium">Active Customer Accounts</span>
                  <span className="text-cyan-400 font-bold text-base">{activeCustomers.toLocaleString()} Customers</span>
                </div>
                <input
                  type="range"
                  min="100"
                  max="10000"
                  step="100"
                  value={activeCustomers}
                  onChange={(e) => setActiveCustomers(Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer h-2 bg-zinc-800 rounded-lg"
                />
                <div className="flex justify-between text-[11px] font-mono text-zinc-500 mt-1">
                  <span>100 accounts</span>
                  <span>5,000 accounts</span>
                  <span>10,000+ scale</span>
                </div>
              </div>

              {/* Slider 2: ACV */}
              <div>
                <div className="flex justify-between items-center text-sm font-mono mb-2">
                  <span className="text-zinc-300 font-medium">Average ACV (Annual Contract Value)</span>
                  <span className="text-cyan-400 font-bold text-base">${avgAcv.toLocaleString()} / year</span>
                </div>
                <input
                  type="range"
                  min="500"
                  max="15000"
                  step="500"
                  value={avgAcv}
                  onChange={(e) => setAvgAcv(Number(e.target.value))}
                  className="w-full accent-teal-400 cursor-pointer h-2 bg-zinc-800 rounded-lg"
                />
                <div className="flex justify-between text-[11px] font-mono text-zinc-500 mt-1">
                  <span>$500 / yr</span>
                  <span>$7,500 / yr</span>
                  <span>$15,000+ enterprise</span>
                </div>
              </div>

              {/* Slider 3: Team Size */}
              <div>
                <div className="flex justify-between items-center text-sm font-mono mb-2">
                  <span className="text-zinc-300 font-medium">Team Size (Product, Eng, & Ops)</span>
                  <span className="text-cyan-400 font-bold text-base">{teamSize} Members</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="200"
                  step="5"
                  value={teamSize}
                  onChange={(e) => setTeamSize(Number(e.target.value))}
                  className="w-full accent-blue-400 cursor-pointer h-2 bg-zinc-800 rounded-lg"
                />
                <div className="flex justify-between text-[11px] font-mono text-zinc-500 mt-1">
                  <span>5 team</span>
                  <span>50 team</span>
                  <span>200+ enterprise</span>
                </div>
              </div>
            </div>

            {/* Right Output HUD (6 Cols) */}
            <div className="lg:col-span-6 rounded-2xl border border-cyan-500/30 bg-[#02050f] p-7 flex flex-col justify-between shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

              <div>
                <div className="flex items-center justify-between text-xs font-mono text-zinc-400 border-b border-zinc-800 pb-3 mb-5">
                  <span>ANNUAL PROJECTED VALUE UNLOCKED</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <Sparkles className="h-3 w-3" /> 16.4x ROI Multiple
                  </span>
                </div>

                <div className="text-3xl sm:text-4xl lg:text-5xl font-black font-mono text-white tracking-tight flex items-baseline gap-1">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-cyan-400">
                    ${totalAnnualValue.toLocaleString()}
                  </span>
                  <span className="text-xs font-mono text-zinc-400 font-normal">/ year</span>
                </div>
                <div className="text-xs text-zinc-400 font-mono mt-1">
                  Net Combined ARR Expansion & Operational Cost Savings
                </div>

                {/* Sub Metrics Grid */}
                <div className="grid grid-cols-2 gap-3 mt-6">
                  <div className="p-3.5 rounded-xl bg-[#070e20] border border-zinc-800">
                    <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
                      <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
                      <span>Net ARR Protected</span>
                    </div>
                    <div className="text-lg font-bold font-mono text-emerald-400 mt-1">
                      ${preservedARR.toLocaleString()}
                    </div>
                    <div className="text-[10px] text-zinc-500 mt-0.5">
                      From automated churn defense
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-[#070e20] border border-zinc-800">
                    <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
                      <Clock className="h-3.5 w-3.5 text-cyan-400" />
                      <span>Work Hours Saved</span>
                    </div>
                    <div className="text-lg font-bold font-mono text-white mt-1">
                      {totalHoursSavedYearly.toLocaleString()} hrs
                    </div>
                    <div className="text-[10px] text-zinc-500 mt-0.5">
                      Via autonomous AI workflows
                    </div>
                  </div>
                </div>
              </div>

              {/* Call to action inside ROI box */}
              <div className="mt-8 pt-5 border-t border-zinc-800/80 flex flex-col sm:flex-row items-center justify-between gap-3">
                <span className="text-xs text-zinc-400 font-mono">
                  Scale your SaaS pipeline today
                </span>
                <button
                  onClick={onOpenDemo}
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-teal-400 px-5 py-2.5 text-xs font-bold text-black hover:opacity-90 transition cursor-pointer shadow-lg shadow-cyan-500/20"
                >
                  <span>Start 14-Day Free Trial</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
