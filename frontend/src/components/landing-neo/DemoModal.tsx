import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { X, CheckCircle2, Shield, Sparkles, Building, Mail, User, Server, Zap } from 'lucide-react'

interface DemoModalProps {
  isOpen: boolean
  onClose: () => void
}

export function DemoModal({ isOpen, onClose }: DemoModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    teamSize: '10-50',
    deploymentEnv: 'Multi-Tenant Cloud (Global Edge)',
  })
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setTimeout(() => {
      setIsSubmitting(false)
      setIsSubmitted(true)
    }, 850)
  }

  const handleReset = () => {
    setIsSubmitted(false)
    setFormData({
      name: '',
      email: '',
      company: '',
      teamSize: '10-50',
      deploymentEnv: 'Multi-Tenant Cloud (Global Edge)',
    })
    onClose()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-md"
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', duration: 0.5, bounce: 0.1 }}
            className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-cyan-500/30 bg-[#070c18] p-6 sm:p-7 shadow-2xl shadow-cyan-500/10 z-10"
          >
            {/* Ambient Top Glow */}
            <div className="absolute -top-24 left-1/2 h-48 w-72 -translate-x-1/2 rounded-full bg-cyan-500/20 blur-3xl pointer-events-none" />

            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-5 right-5 rounded-lg p-2 text-zinc-400 hover:text-white hover:bg-zinc-800/80 transition-colors cursor-pointer"
            >
              <X className="h-5 w-5" />
            </button>

            {isSubmitted ? (
              <div className="py-8 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 mb-4 animate-bounce">
                  <CheckCircle2 className="h-8 w-8" />
                </div>
                <h3 className="text-2xl font-bold text-white tracking-tight">Your Sandbox is Provisioning!</h3>
                <p className="mt-2 text-sm text-zinc-300 max-w-sm mx-auto">
                  We've sent access instructions and your API credentials to <span className="text-cyan-400 font-semibold">{formData.email}</span>.
                </p>
                <div className="mt-6 p-4 rounded-xl bg-zinc-900/80 border border-zinc-800 text-left text-xs text-zinc-400 space-y-2">
                  <div className="flex justify-between">
                    <span>Company / Project:</span>
                    <span className="text-white font-medium">{formData.company || 'Modern SaaS App'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cloud Architecture:</span>
                    <span className="text-cyan-400 font-medium">{formData.deploymentEnv}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>AstraFlow & Copilot:</span>
                    <span className="text-emerald-400 font-medium">Activated (14-Day Free Access)</span>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="mt-6 w-full rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 py-3 text-sm font-semibold text-black hover:opacity-90 transition-opacity shadow-lg shadow-cyan-500/20 cursor-pointer"
                >
                  Return to Website
                </button>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300 mb-3">
                    <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                    <span>Instant 14-Day Full Access Trial</span>
                  </div>
                  <h3 className="text-2xl font-bold tracking-tight text-white">Experience AstraOS SaaS</h3>
                  <p className="mt-1 text-xs text-zinc-400">
                    Get full access to autonomous AI workflows, live telemetry, and agent copilots.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-zinc-300 mb-1.5">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                      <input
                        required
                        type="text"
                        placeholder="Alex Vance"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full rounded-xl border border-zinc-700/80 bg-zinc-900/90 pl-9 pr-3 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-zinc-300 mb-1.5">Work Email</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                      <input
                        required
                        type="email"
                        placeholder="alex@acmesaas.com"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full rounded-xl border border-zinc-700/80 bg-zinc-900/90 pl-9 pr-3 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-zinc-300 mb-1.5">SaaS / Company Name</label>
                      <div className="relative">
                        <Building className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                        <input
                          required
                          type="text"
                          placeholder="Acme Inc."
                          value={formData.company}
                          onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                          className="w-full rounded-xl border border-zinc-700/80 bg-zinc-900/90 pl-9 pr-3 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-zinc-300 mb-1.5">Team Size</label>
                      <select
                        value={formData.teamSize}
                        onChange={(e) => setFormData({ ...formData, teamSize: e.target.value })}
                        className="w-full rounded-xl border border-zinc-700/80 bg-zinc-900/90 px-3 py-2.5 text-sm text-white focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
                      >
                        <option value="1-10">1 - 10 people</option>
                        <option value="10-50">10 - 50 people</option>
                        <option value="50-250">50 - 250 people</option>
                        <option value="250+">250+ Enterprise</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-zinc-300 mb-1.5">Preferred Deployment Environment</label>
                    <div className="relative">
                      <Server className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                      <select
                        value={formData.deploymentEnv}
                        onChange={(e) => setFormData({ ...formData, deploymentEnv: e.target.value })}
                        className="w-full rounded-xl border border-zinc-700/80 bg-zinc-900/90 pl-9 pr-3 py-2.5 text-sm text-white focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
                      >
                        <option value="Multi-Tenant Cloud (Global Edge)">Multi-Tenant Cloud (28 Edge PoPs)</option>
                        <option value="Dedicated VPC (AWS/GCP/Azure)">Dedicated Single-Tenant VPC</option>
                        <option value="Sovereign On-Premise Appliance">Sovereign Air-Gapped Cloud</option>
                      </select>
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full rounded-xl bg-gradient-to-r from-cyan-400 via-teal-400 to-cyan-500 py-3 text-sm font-semibold text-black hover:opacity-90 transition-opacity shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="h-4 w-4 rounded-full border-2 border-black border-t-transparent animate-spin" />
                          <span>Provisioning Workspace...</span>
                        </>
                      ) : (
                        <>
                          <Zap className="h-4 w-4" />
                          <span>Start Free 14-Day Trial</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-[11px] text-center text-zinc-500">
                    No credit card required. Encrypted with 256-bit AES. Cancel anytime.
                  </p>
                </form>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
