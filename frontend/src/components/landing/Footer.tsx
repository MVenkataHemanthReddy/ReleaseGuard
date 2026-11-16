import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Sparkles, Terminal, ArrowRight, Zap, Check } from 'lucide-react'

interface FooterProps {
  onOpenDemo: () => void
}

export function Footer({ onOpenDemo }: FooterProps) {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return
    setSubscribed(true)
    setTimeout(() => {
      setEmail('')
    }, 2000)
  }

  return (
    <footer className="relative bg-[#02050e] border-t border-cyan-500/15 overflow-hidden text-zinc-400">
      {/* Pre-Footer Call to Action Banner */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="relative rounded-3xl border border-cyan-500/30 bg-gradient-to-b from-[#09132c] to-[#040815] p-8 sm:p-14 overflow-hidden text-center shadow-2xl">
          {/* Cybernetic glowing background rings */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-cyan-500/15 blur-[120px] rounded-full pointer-events-none" />
          <div className="absolute -top-32 -right-32 w-64 h-64 border border-dashed border-cyan-500/20 rounded-full animate-spin-slow pointer-events-none" />

          <div className="relative z-10 max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-cyan-950/60 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-6">
              <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
              <span>SUPERCHARGE YOUR SAAS VELOCITY TODAY</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
              Ready to Build the Future of SaaS?
            </h2>
            <p className="mt-4 text-sm sm:text-base text-zinc-300 font-light max-w-xl mx-auto">
              Join thousands of modern software companies orchestrating autonomous workflows, copilots, and real-time revenue telemetry with AstraOS.
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              <button
                onClick={onOpenDemo}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 via-teal-400 to-cyan-500 px-7 py-3.5 text-sm font-bold text-black shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-[1.02] active:scale-[0.98] transition cursor-pointer"
              >
                <span>Start Free 14-Day Trial</span>
                <ArrowRight className="h-4 w-4" />
              </button>

              <button
                onClick={onOpenDemo}
                className="inline-flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-900/90 px-6 py-3.5 text-sm font-semibold text-white hover:border-cyan-400 hover:text-cyan-300 transition cursor-pointer"
              >
                <span>Schedule Architecture Walkthrough</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-zinc-900">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          {/* Brand Col */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Zap className="h-5 w-5" />
              </div>
              <span className="text-xl font-black text-white tracking-tight font-sans">
                ASTRA<span className="text-cyan-400">OS</span>
              </span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed font-light max-w-sm">
              The Autonomous AI Operating System for Modern SaaS. Orchestrating event-driven workflows, intelligent multi-agent swarms, and predictive product telemetry across 28 global edge regions.
            </p>

            {/* Newsletter */}
            <form onSubmit={handleSubscribe} className="pt-2">
              <div className="text-xs font-mono text-zinc-300 mb-2">Subscribe to The Modern SaaS Frontier</div>
              <div className="flex gap-2 max-w-sm">
                <input
                  type="email"
                  required
                  placeholder="founder@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl border border-zinc-800 bg-[#070e20] px-3.5 py-2 text-xs text-white placeholder-zinc-500 focus:border-cyan-400 focus:outline-none"
                />
                <button
                  type="submit"
                  className="rounded-xl bg-cyan-500 px-4 py-2 text-xs font-bold text-black hover:bg-cyan-400 transition shrink-0 cursor-pointer"
                >
                  {subscribed ? <Check className="h-4 w-4" /> : 'Join'}
                </button>
              </div>
              {subscribed && (
                <div className="mt-1 text-[11px] text-emerald-400 font-mono">
                  ✓ Welcome to our weekly engineering & growth dispatch!
                </div>
              )}
            </form>
          </div>

          {/* Links 1 */}
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-white font-semibold mb-4">
              Products & Modules
            </div>
            <ul className="space-y-2.5 text-xs">
              <li><a href="#products" className="hover:text-cyan-400 transition">AstraFlow™ (Workflows)</a></li>
              <li><a href="#products" className="hover:text-cyan-400 transition">AstraData™ (Telemetry)</a></li>
              <li><a href="#products" className="hover:text-cyan-400 transition">AstraAgent™ (Copilots)</a></li>
              <li><a href="#products" className="hover:text-cyan-400 transition">AstraMesh™ (Edge Mesh)</a></li>
              <li><a href="#demo" className="hover:text-cyan-400 transition">Interactive Live Demo</a></li>
            </ul>
          </div>

          {/* Links 2 */}
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-white font-semibold mb-4">
              Architecture
            </div>
            <ul className="space-y-2.5 text-xs">
              <li><a href="#architecture" className="hover:text-cyan-400 transition">Multi-Tenant Global Cloud</a></li>
              <li><a href="#architecture" className="hover:text-cyan-400 transition">Dedicated Single-Tenant VPC</a></li>
              <li><a href="#architecture" className="hover:text-cyan-400 transition">Sovereign Air-Gapped Cloud</a></li>
              <li><a href="#features" className="hover:text-cyan-400 transition">500+ App Mesh & API</a></li>
              <li><a href="#roi" className="hover:text-cyan-400 transition">SaaS ROI Engine</a></li>
            </ul>
          </div>

          {/* Links 3 */}
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-white font-semibold mb-4">
              Enterprise & Trust
            </div>
            <ul className="space-y-2.5 text-xs">
              <li><a href="#pricing" className="hover:text-cyan-400 transition">Pricing & Volume Tiers</a></li>
              <li><span className="text-zinc-500">SOC-2 Type II Report</span></li>
              <li><span className="text-zinc-500">ISO/IEC 27001 Certification</span></li>
              <li><span className="text-zinc-500">Row-Level Data Privacy</span></li>
              <li><span className="text-zinc-500">Security Whitepaper</span></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-14 pt-8 border-t border-zinc-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-zinc-500">
          <div>
            © {new Date().getFullYear()} AstraOS Technologies Inc. All rights reserved.
          </div>

          {/* Live Heartbeat */}
          <div className="flex items-center gap-2 text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>All Global Systems Operational • 99.999% SLA</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="hover:text-zinc-300 transition cursor-pointer">Privacy Policy</span>
            <span>•</span>
            <span className="hover:text-zinc-300 transition cursor-pointer">Terms of Service</span>
            <span>•</span>
            <span className="hover:text-zinc-300 transition cursor-pointer">System Status</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
