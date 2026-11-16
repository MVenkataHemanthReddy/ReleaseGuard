import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { X, CheckCircle2, ShieldCheck, Sparkles, Building, Mail, User } from 'lucide-react'

interface AppleTrialModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AppleTrialModal({ isOpen, onClose }: AppleTrialModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    teamSize: '10-50',
  })
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setTimeout(() => {
      setIsSubmitting(false)
      setIsSubmitted(true)
    }, 800)
  }

  const handleReset = () => {
    setIsSubmitted(false)
    setFormData({
      name: '',
      email: '',
      company: '',
      teamSize: '10-50',
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
            className="fixed inset-0 bg-black/40 backdrop-blur-md"
          />

          {/* Modal Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 15 }}
            transition={{ type: 'spring', duration: 0.45, bounce: 0.1 }}
            className="relative w-full max-w-lg overflow-hidden rounded-[2rem] bg-white p-8 shadow-2xl z-10 border border-black/[0.08]"
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-6 right-6 rounded-full p-2 text-[#86868b] hover:text-[#1d1d1f] hover:bg-[#f5f5f7] transition-colors cursor-pointer"
            >
              <X className="h-5 w-5" />
            </button>

            {isSubmitted ? (
              <div className="py-8 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 mb-4 animate-bounce">
                  <CheckCircle2 className="h-8 w-8" />
                </div>
                <h3 className="text-2xl font-semibold text-[#1d1d1f] tracking-tight">Your trial is ready.</h3>
                <p className="mt-2 text-sm text-[#86868b] max-w-sm mx-auto font-normal leading-relaxed">
                  We've emailed your activation link and API key to <span className="font-semibold text-[#1d1d1f]">{formData.email}</span>.
                </p>
                <div className="mt-6 p-4 rounded-2xl bg-[#f5f5f7] text-left text-xs text-[#86868b] space-y-2">
                  <div className="flex justify-between">
                    <span>Account:</span>
                    <span className="text-[#1d1d1f] font-medium">{formData.company || 'Modern SaaS'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Access Level:</span>
                    <span className="text-[#0071e3] font-medium">14-Day Full Access Pro</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Card on file:</span>
                    <span className="text-emerald-600 font-medium">None required</span>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="mt-6 w-full rounded-full bg-[#0071e3] hover:bg-[#0077ed] py-3 text-sm font-medium text-white transition-all cursor-pointer"
                >
                  Return to Astra
                </button>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <span className="text-xs font-semibold text-[#0071e3] uppercase tracking-wider">
                    START FREE TRIAL
                  </span>
                  <h3 className="text-2xl font-semibold text-[#1d1d1f] tracking-tight mt-1">
                    Experience AstraOS.
                  </h3>
                  <p className="mt-1 text-xs text-[#86868b] font-normal">
                    14 days of full feature access. No credit card required.
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-[#1d1d1f] mb-1.5">Full Name</label>
                    <input
                      required
                      type="text"
                      placeholder="Alex Vance"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full rounded-xl border border-black/10 bg-[#f5f5f7] px-3.5 py-2.5 text-sm text-[#1d1d1f] placeholder-[#86868b] focus:border-[#0071e3] focus:bg-white focus:outline-none transition"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[#1d1d1f] mb-1.5">Work Email</label>
                    <input
                      required
                      type="email"
                      placeholder="alex@company.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full rounded-xl border border-black/10 bg-[#f5f5f7] px-3.5 py-2.5 text-sm text-[#1d1d1f] placeholder-[#86868b] focus:border-[#0071e3] focus:bg-white focus:outline-none transition"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-[#1d1d1f] mb-1.5">Company</label>
                      <input
                        required
                        type="text"
                        placeholder="Acme Inc."
                        value={formData.company}
                        onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                        className="w-full rounded-xl border border-black/10 bg-[#f5f5f7] px-3.5 py-2.5 text-sm text-[#1d1d1f] placeholder-[#86868b] focus:border-[#0071e3] focus:bg-white focus:outline-none transition"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-[#1d1d1f] mb-1.5">Team Size</label>
                      <select
                        value={formData.teamSize}
                        onChange={(e) => setFormData({ ...formData, teamSize: e.target.value })}
                        className="w-full rounded-xl border border-black/10 bg-[#f5f5f7] px-3 py-2.5 text-sm text-[#1d1d1f] focus:border-[#0071e3] focus:bg-white focus:outline-none transition"
                      >
                        <option value="1-10">1 - 10 people</option>
                        <option value="10-50">10 - 50 people</option>
                        <option value="50-250">50 - 250 people</option>
                        <option value="250+">250+ enterprise</option>
                      </select>
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full rounded-full bg-[#0071e3] hover:bg-[#0077ed] py-3 text-sm font-medium text-white shadow-sm transition-all cursor-pointer disabled:opacity-50"
                    >
                      {isSubmitting ? 'Setting up workspace...' : 'Start 14-Day Free Trial'}
                    </button>
                  </div>
                  <p className="text-[11px] text-center text-[#86868b]">
                    Encrypted with AES-256. Strictly zero data tracking.
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
