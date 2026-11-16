import React from 'react'
import { motion } from 'motion/react'
import { 
  Sparkles, 
  ArrowRight, 
  Play, 
  Cpu, 
  Activity, 
  Zap, 
  Radio, 
  Layers, 
  ShieldCheck, 
  TrendingUp,
  Globe
} from 'lucide-react'

interface HeroSectionProps {
  onOpenDemo: () => void
}

export function HeroSection({ onOpenDemo }: HeroSectionProps) {
  const stats = [
    { label: 'Autonomous Velocity', value: '10x Faster', sub: 'From Idea to Deployed Workflow' },
    { label: 'Global Infrastructure', value: '99.99%', sub: 'Multi-Region Enterprise Uptime' },
    { label: 'Telemetry Throughput', value: '500M+ /day', sub: 'Real-Time Edge Events' },
    { label: 'Operational Efficiency', value: '64% Cut', sub: 'In Manual Engineering Overhead' },
  ]

  return (
    <section className="relative min-h-screen pt-32 pb-20 overflow-hidden bg-[#030712] flex flex-col justify-center">
      {/* Cybernetic Grid & Radial Neon Lighting */}
      <div className="absolute inset-0 cyber-grid-bg opacity-35 pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-gradient-to-tr from-cyan-600/15 via-teal-500/10 to-indigo-600/15 blur-[140px] rounded-full pointer-events-none" />
      
      {/* NeoAstra-Inspired Rotating Geometric HUD / Cybernetic Rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] pointer-events-none opacity-25">
        {/* Outer Ring */}
        <div className="absolute inset-0 rounded-full border border-dashed border-cyan-400/40 animate-spin-slow" />
        {/* Middle Ring with tick accents */}
        <div className="absolute inset-20 rounded-full border border-teal-500/30 animate-spin-reverse-slow" />
        {/* Core Ring */}
        <div className="absolute inset-44 rounded-full border border-dashed border-cyan-300/20 animate-spin-slow" />
        {/* Diagonal Crosshairs */}
        <div className="absolute top-1/2 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
        <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Top Cyber Badge */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2.5 rounded-full border border-cyan-500/40 bg-cyan-950/40 px-4 py-1.5 backdrop-blur-md mb-8 group cursor-default"
          >
            <div className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400" />
            </div>
            <span className="text-xs font-mono font-medium tracking-wide text-cyan-200">
              ASTRA SAAS ENGINE 5.0 LIVE
            </span>
            <span className="text-zinc-500">|</span>
            <span className="text-xs font-mono text-teal-300 flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Autonomous Intelligence
            </span>
          </motion.div>

          {/* Master Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-[1.08]"
          >
            The Autonomous AI Operating System for{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-200 to-cyan-400">
              Modern SaaS
            </span>
          </motion.h1>

          {/* Subtext */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mt-6 text-base sm:text-lg lg:text-xl text-zinc-300 max-w-3xl mx-auto leading-relaxed font-light"
          >
            Orchestrate autonomous workflows, deploy AI copilots, and analyze real-time business telemetry in a single hyper-scalable cloud platform. Scale from day 1 to IPO without infrastructure bottlenecks.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-4"
          >
            {/* Primary CTA */}
            <button
              onClick={onOpenDemo}
              className="group relative inline-flex items-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-cyan-400 via-teal-400 to-cyan-500 px-7 py-3.5 text-sm font-bold text-black shadow-[0_0_35px_rgba(5,238,250,0.4)] hover:shadow-[0_0_50px_rgba(5,238,250,0.6)] hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 cursor-pointer"
            >
              <Zap className="h-4 w-4" />
              <span>Start 14-Day Free Trial</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>

            {/* Live Interactive Demo CTA */}
            <a
              href="#demo"
              className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-[#0a1226]/80 px-6 py-3.5 text-sm font-semibold text-zinc-200 hover:text-white hover:border-cyan-400 hover:bg-[#0f1b38] backdrop-blur-md transition-all duration-200 shadow-lg shadow-black/40"
            >
              <Play className="h-4 w-4 text-cyan-400 fill-cyan-400/20" />
              <span>Interactive Platform Demo</span>
            </a>

            {/* Product Tour link */}
            <a
              href="#products"
              className="inline-flex items-center gap-1.5 rounded-xl border border-zinc-800 bg-zinc-900/60 px-5 py-3.5 text-sm font-semibold text-zinc-400 hover:text-cyan-300 hover:border-zinc-700 transition-colors"
            >
              <span>Explore Ecosystem</span>
              <span className="text-xs font-mono text-zinc-500">↓</span>
            </a>
          </motion.div>

          {/* Social Proof Badges */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-zinc-400 font-mono"
          >
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-teal-400" />
              <span>SOC2 Type II & ISO 27001 Certified</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Zap className="h-3.5 w-3.5 text-cyan-400" />
              <span>Instant 60-Second Setup</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe className="h-3.5 w-3.5 text-teal-300" />
              <span>Global Low-Latency Edge (28 Regions)</span>
            </div>
          </motion.div>
        </div>

        {/* Real-time SaaS Metrics Counter Strip */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="relative overflow-hidden rounded-2xl border border-cyan-500/20 bg-[#090f1f]/80 p-5 backdrop-blur-md hover:border-cyan-400/50 hover:shadow-[0_0_30px_rgba(5,238,250,0.15)] transition-all duration-300 group"
            >
              {/* Corner accent glow */}
              <div className="absolute top-0 right-0 w-16 h-16 bg-cyan-500/10 rounded-full blur-xl group-hover:bg-cyan-500/20 transition-all" />
              <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight flex items-baseline gap-1">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-100 to-teal-300">
                  {stat.value}
                </span>
              </div>
              <div className="mt-1 text-xs font-semibold text-zinc-200 uppercase tracking-wider">
                {stat.label}
              </div>
              <div className="mt-1 text-[11px] text-zinc-400">
                {stat.sub}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
