import React, { useState } from 'react'
import { motion } from 'motion/react'
import { Check, Sparkles, Shield, ArrowRight, Zap, HelpCircle } from 'lucide-react'

interface PricingSectionProps {
  onOpenDemo: () => void
}

export function PricingSection({ onOpenDemo }: PricingSectionProps) {
  const [annualBilling, setAnnualBilling] = useState(true)

  const plans = [
    {
      name: 'Starter Growth',
      tagline: 'Ideal for early-stage SaaS startups launching their first workflows.',
      priceMonthly: 59,
      priceAnnual: 49,
      isPopular: false,
      ctaText: 'Start 14-Day Free Trial',
      badge: null,
      features: [
        'Up to 1,000 Monthly Active Users',
        '50,000 Autonomous Workflow Runs / mo',
        'AstraFlow™ Prompt-to-Pipeline Builder',
        '10 Team Collaboration Seats',
        'Standard Stripe, Slack & Webhook Integrations',
        'Community Forum & Email Support'
      ],
      omitted: [
        'Autonomous AI Agent Swarms (AstraAgent)',
        'Predictive Churn Telemetry Engine',
        'Dedicated Single-Tenant VPC',
        '99.999% Enterprise Uptime SLA'
      ]
    },
    {
      name: 'Scale-Up Pro',
      tagline: 'Built for scaling SaaS products expanding their ARR and team.',
      priceMonthly: 249,
      priceAnnual: 199,
      isPopular: true,
      ctaText: 'Launch Pro Sandbox',
      badge: 'MOST POPULAR FOR SAAS',
      features: [
        'Up to 10,000 Monthly Active Users',
        '500,000 Autonomous Workflow Runs / mo',
        'Full AstraAgent™ AI Copilots & Swarms',
        'AstraData™ Real-Time Predictive Churn Telemetry',
        '28 Global PoPs Edge Anycast Routing',
        '500+ Native App Connectors (HubSpot, Salesforce)',
        '25 Team Collaboration Seats',
        'Priority 24/7 Private Slack Support'
      ],
      omitted: [
        'Dedicated Single-Tenant VPC',
        'Custom Sovereign Model Fine-Tuning'
      ]
    },
    {
      name: 'Enterprise Astra',
      tagline: 'Bespoke infrastructure and custom SLAs for global SaaS leaders.',
      priceMonthly: null,
      priceAnnual: null,
      isPopular: false,
      ctaText: 'Contact Enterprise Sales',
      badge: 'DEDICATED VPC & SOVEREIGN',
      features: [
        'Unlimited Users & Workflow Executions',
        'Dedicated Single-Tenant VPC or Air-Gapped Appliance',
        'Customer-Managed KMS Encryption Keys (BYOK)',
        'Fine-Tuned Proprietary AI Models on Private Data',
        'Guaranteed 99.999% Financial Uptime SLA',
        'SOC2 Type II, ISO 27001 & HIPAA BAA Agreements',
        'Designated Principal Solutions Architect & Slack War-Room',
        'Custom Okta / Azure AD SAML SSO & SCIM Provisioning'
      ],
      omitted: []
    }
  ]

  return (
    <section id="pricing" className="relative py-28 bg-[#030712] border-t border-cyan-500/10 overflow-hidden">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <Zap className="h-3.5 w-3.5 text-cyan-400" />
            <span>TRANSPARENT VALUE-DRIVEN PLANS</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Predictable Pricing as Your SaaS Scales
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Start with our 14-day free trial. Scale seamlessly as your customer base and workflow throughput expand.
          </p>

          {/* Billing Switch */}
          <div className="mt-8 inline-flex items-center gap-3 p-1.5 rounded-2xl bg-[#081024] border border-cyan-500/30 backdrop-blur-md">
            <button
              onClick={() => setAnnualBilling(false)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold font-mono transition cursor-pointer ${
                !annualBilling
                  ? 'bg-zinc-800 text-white shadow'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              Monthly Billing
            </button>
            <button
              onClick={() => setAnnualBilling(true)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold font-mono transition cursor-pointer ${
                annualBilling
                  ? 'bg-gradient-to-r from-cyan-500 to-teal-400 text-black shadow-lg shadow-cyan-500/25'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <span>Annual Billing</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/20 text-black font-bold uppercase">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          {plans.map((plan, idx) => {
            const price = annualBilling ? plan.priceAnnual : plan.priceMonthly
            return (
              <div
                key={idx}
                className={`relative flex flex-col justify-between rounded-3xl p-8 backdrop-blur-2xl transition-all duration-300 ${
                  plan.isPopular
                    ? 'border-2 border-cyan-400 bg-[#071126] shadow-[0_0_45px_rgba(5,238,250,0.25)] lg:-translate-y-2'
                    : 'border border-zinc-800 bg-[#060c1c]/90 hover:border-zinc-700'
                }`}
              >
                {/* Popular Badge */}
                {plan.badge && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-cyan-400 to-teal-400 px-4 py-1 text-[10px] font-extrabold uppercase tracking-widest text-black shadow-md">
                    {plan.badge}
                  </div>
                )}

                <div>
                  <div className="flex justify-between items-baseline">
                    <h3 className="text-xl font-bold text-white tracking-tight">{plan.name}</h3>
                  </div>
                  <p className="mt-2 text-xs text-zinc-400 leading-relaxed font-light">
                    {plan.tagline}
                  </p>

                  {/* Price Tag */}
                  <div className="mt-6 pb-6 border-b border-zinc-800">
                    {price !== null ? (
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl sm:text-5xl font-black font-mono text-white tracking-tight">
                          ${price}
                        </span>
                        <span className="text-xs font-mono text-zinc-400">/ month</span>
                      </div>
                    ) : (
                      <div className="text-3xl sm:text-4xl font-black font-mono text-white tracking-tight">
                        Custom Contract
                      </div>
                    )}
                    <div className="text-[11px] font-mono text-zinc-500 mt-1">
                      {price !== null
                        ? annualBilling
                          ? 'Billed annually ($' + (price * 12) + '/yr)'
                          : 'Billed monthly, cancel anytime'
                        : 'Tailored for high-scale enterprise needs'}
                    </div>
                  </div>

                  {/* Feature Checklist */}
                  <div className="mt-6 space-y-3">
                    <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 font-semibold">
                      Included Capabilities:
                    </div>
                    {plan.features.map((feature, fIdx) => (
                      <div key={fIdx} className="flex items-start gap-2.5 text-xs text-zinc-200">
                        <div className="p-0.5 rounded-full bg-cyan-500/20 text-cyan-400 mt-0.5 shrink-0">
                          <Check className="h-3.5 w-3.5" />
                        </div>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Card Button */}
                <div className="mt-8 pt-6 border-t border-zinc-800">
                  <button
                    onClick={onOpenDemo}
                    className={`w-full rounded-xl py-3 text-xs sm:text-sm font-bold transition flex items-center justify-center gap-2 cursor-pointer ${
                      plan.isPopular
                        ? 'bg-gradient-to-r from-cyan-400 via-teal-400 to-cyan-500 text-black shadow-lg shadow-cyan-500/30 hover:opacity-95'
                        : 'border border-zinc-700 bg-zinc-900 text-white hover:border-cyan-500/40 hover:text-cyan-300'
                    }`}
                  >
                    <span>{plan.ctaText}</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* Guarantee Pill */}
        <div className="mt-14 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/60 px-5 py-2 text-xs font-mono text-zinc-400">
            <Shield className="h-4 w-4 text-emerald-400" />
            <span>14-Day Full Access Free Trial • No Credit Card Required • Instant Setup</span>
          </div>
        </div>
      </div>
    </section>
  )
}
