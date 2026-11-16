import React from 'react'
import { motion } from 'motion/react'
import { Star, ShieldCheck, Quote, Building2, Lock, CheckCircle2 } from 'lucide-react'

export function TestimonialsCompliance() {
  const testimonials = [
    {
      quote:
        'AstraOS replaced our tangled mesh of custom scripts and disparate microservices. We deployed autonomous onboarding and KYC pipelines in three days that now process $18M in ARR seamlessly.',
      author: 'Elena Rostova',
      role: 'VP of Product & Engineering',
      company: 'CloudScale SaaS',
      avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
      metric: '340ms average customer onboarding'
    },
    {
      quote:
        'The predictive churn telemetry in AstraData caught accounts trending downward weeks before our customer success team even noticed. It saved over $350k in annualized churn in Q3 alone.',
      author: 'Marcus Vance',
      role: 'Chief Technology Officer',
      company: 'HyperMetrics AI',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
      metric: '18.4% reduction in churn rate'
    },
    {
      quote:
        'AstraOS gave us enterprise SOC-2 Type II and row-level multi-tenant isolation out-of-the-box. We closed three Fortune 500 enterprise contracts six months ahead of schedule.',
      author: 'Dr. David Chen',
      role: 'Head of Infrastructure',
      company: 'NovaStream SaaS',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
      metric: 'Passed Tier-1 Enterprise Security Review'
    }
  ]

  const complianceBadges = [
    { name: 'SOC 2 Type II', desc: 'Continuous AICPA Audit' },
    { name: 'ISO/IEC 27001', desc: 'Information Security Mgmt' },
    { name: 'GDPR & CCPA', desc: 'EU & California Data Privacy' },
    { name: 'HIPAA Compliant', desc: 'BAA Executed for Healthcare' },
    { name: 'PCI-DSS Level 1', desc: 'Secure Payment Telemetry' }
  ]

  return (
    <section className="relative py-28 bg-[#040816] border-t border-cyan-500/10 overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <ShieldCheck className="h-3.5 w-3.5 text-cyan-400" />
            <span>SAAS LEADERS & INSTITUTIONAL TRUST</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Loved by Fast-Growing SaaS Founders & CTOs
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Powering mission-critical workflows, automated customer operations, and multi-region scale for modern software companies.
          </p>
        </div>

        {/* Testimonials Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-16">
          {testimonials.map((t, idx) => (
            <div
              key={idx}
              className="relative rounded-3xl border border-zinc-800 bg-[#070e20]/80 p-8 backdrop-blur-md flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-300 group shadow-lg"
            >
              <div>
                <Quote className="h-8 w-8 text-cyan-400/30 mb-4 group-hover:text-cyan-400 transition-colors" />
                <p className="text-sm text-zinc-300 leading-relaxed font-light">
                  "{t.quote}"
                </p>
              </div>

              <div className="mt-8 pt-6 border-t border-zinc-800/80">
                <div className="flex items-center gap-3">
                  <img
                    src={t.avatar}
                    alt={t.author}
                    className="h-11 w-11 rounded-full object-cover border border-cyan-500/40"
                  />
                  <div>
                    <h4 className="text-sm font-bold text-white tracking-tight">{t.author}</h4>
                    <p className="text-xs text-zinc-400">{t.role} • {t.company}</p>
                  </div>
                </div>

                <div className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded-md border border-emerald-900/60">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>{t.metric}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Compliance Badges Strip */}
        <div className="rounded-2xl border border-cyan-500/20 bg-[#02050e]/90 p-6 sm:p-8 backdrop-blur-xl">
          <div className="text-center text-xs font-mono uppercase tracking-widest text-zinc-400 mb-6">
            Institutional Enterprise Certifications & Regulatory Compliance
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {complianceBadges.map((badge, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#081024] border border-zinc-800 text-center hover:border-cyan-500/30 transition"
              >
                <Lock className="h-5 w-5 text-cyan-400 mx-auto mb-2" />
                <div className="text-xs font-bold font-mono text-white">{badge.name}</div>
                <div className="text-[10px] text-zinc-400 mt-0.5">{badge.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
