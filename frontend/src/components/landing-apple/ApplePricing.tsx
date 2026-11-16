import React, { useState } from 'react'
import { motion } from 'motion/react'
import { Check, ShieldCheck, ChevronRight, Sparkles } from 'lucide-react'

interface ApplePricingProps {
  onOpenTrial: () => void
}

export function ApplePricing({ onOpenTrial }: ApplePricingProps) {
  const [annualBilling, setAnnualBilling] = useState(true)

  const plans = [
    {
      name: 'Starter',
      description: 'Ideal for early-stage teams launching their first automated SaaS workflows.',
      priceMonthly: 59,
      priceAnnual: 49,
      isPopular: false,
      cta: 'Try it free',
      features: [
        'Up to 1,000 Monthly Active Users',
        '50,000 Autonomous Workflow Runs',
        'Natural Language Pipeline Generator',
        '10 Team Collaboration Seats',
        'Standard Stripe & Slack Connectors',
        'Community Forum & Email Support'
      ]
    },
    {
      name: 'Pro',
      description: 'The complete autonomous AI suite for scaling software companies.',
      priceMonthly: 249,
      priceAnnual: 199,
      isPopular: true,
      badge: 'MOST POPULAR',
      cta: 'Try Pro free',
      features: [
        'Up to 10,000 Monthly Active Users',
        '500,000 Autonomous Workflow Runs',
        'Full Autonomous AI Agent Swarms',
        'Real-Time Predictive Churn Telemetry',
        '28 Global PoPs Edge Anycast Routing',
        '500+ Native App Connectors',
        '25 Team Collaboration Seats',
        'Priority 24/7 Slack Support'
      ]
    },
    {
      name: 'Enterprise',
      description: 'Dedicated infrastructure, custom SLAs, and sovereign VPC isolation.',
      priceMonthly: null,
      priceAnnual: null,
      isPopular: false,
      badge: 'CUSTOM SCALE',
      cta: 'Contact sales',
      features: [
        'Unlimited Users & Workflow Runs',
        'Dedicated Single-Tenant VPC or On-Premise',
        'Bring-Your-Own-Key (BYOK) Encryption',
        'Custom Fine-Tuned AI Models',
        '99.999% Financial Uptime SLA',
        'SOC 2 Type II, ISO 27001 & HIPAA BAA',
        'Dedicated Solutions Architect',
        'Custom SAML SSO & SCIM Directory'
      ]
    }
  ]

  return (
    <section id="pricing" className="py-24 bg-[#fbfbfd] border-t border-black/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
            TRANSPARENT PRICING
          </span>
          <h2 className="text-4xl sm:text-6xl font-semibold text-[#1d1d1f] tracking-tight mt-2">
            Simple plans for every stage.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#86868b] font-normal leading-relaxed">
            Start with our 14-day free trial. Upgrade or cancel anytime with zero friction.
          </p>

          {/* Apple-style Billing Switcher */}
          <div className="mt-8 inline-flex items-center p-1 rounded-full bg-[#e8e8ed]">
            <button
              onClick={() => setAnnualBilling(false)}
              className={`rounded-full px-5 py-2 text-xs sm:text-sm font-medium transition-all duration-200 cursor-pointer ${
                !annualBilling
                  ? 'bg-white text-[#1d1d1f] shadow-sm'
                  : 'text-[#86868b] hover:text-[#1d1d1f]'
              }`}
            >
              Monthly billing
            </button>
            <button
              onClick={() => setAnnualBilling(true)}
              className={`rounded-full px-5 py-2 text-xs sm:text-sm font-medium transition-all duration-200 flex items-center gap-1.5 cursor-pointer ${
                annualBilling
                  ? 'bg-white text-[#1d1d1f] shadow-sm'
                  : 'text-[#86868b] hover:text-[#1d1d1f]'
              }`}
            >
              <span>Annual billing</span>
              <span className="text-[10px] font-semibold text-[#0071e3] bg-blue-50 px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch max-w-6xl mx-auto">
          {plans.map((plan, idx) => {
            const price = annualBilling ? plan.priceAnnual : plan.priceMonthly
            return (
              <div
                key={idx}
                className={`rounded-[2.5rem] bg-white p-8 sm:p-10 flex flex-col justify-between transition-all duration-300 relative ${
                  plan.isPopular
                    ? 'border-2 border-[#0071e3] shadow-[0_20px_60px_-15px_rgba(0,113,227,0.12)]'
                    : 'border border-black/[0.06] shadow-sm'
                }`}
              >
                {/* Popular Pill Badge */}
                {plan.badge && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-[#0071e3] px-3.5 py-1 text-[10px] font-semibold tracking-wider uppercase text-white shadow-sm">
                    {plan.badge}
                  </div>
                )}

                <div>
                  <h3 className="text-2xl font-semibold text-[#1d1d1f] tracking-tight">{plan.name}</h3>
                  <p className="mt-2 text-xs sm:text-sm text-[#86868b] leading-relaxed font-normal">
                    {plan.description}
                  </p>

                  {/* Price */}
                  <div className="mt-6 pb-6 border-b border-black/[0.06]">
                    {price !== null ? (
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl sm:text-5xl font-semibold text-[#1d1d1f] tracking-tight">
                          ${price}
                        </span>
                        <span className="text-xs text-[#86868b] font-normal">/ month</span>
                      </div>
                    ) : (
                      <div className="text-3xl sm:text-4xl font-semibold text-[#1d1d1f] tracking-tight">
                        Custom
                      </div>
                    )}
                    <div className="text-[11px] text-[#86868b] mt-1 font-normal">
                      {price !== null
                        ? annualBilling
                          ? 'Billed annually with volume tiers'
                          : 'Billed monthly, cancel anytime'
                        : 'Designed for enterprise sovereignty'}
                    </div>
                  </div>

                  {/* Feature List */}
                  <div className="mt-6 space-y-3">
                    <div className="text-[11px] font-semibold text-[#1d1d1f] uppercase tracking-wider">
                      Included with {plan.name}:
                    </div>
                    {plan.features.map((feature, fIdx) => (
                      <div key={fIdx} className="flex items-start gap-2.5 text-xs sm:text-sm text-[#1d1d1f]/90">
                        <Check className="h-4 w-4 text-[#0071e3] shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Apple-style Button */}
                <div className="mt-8 pt-6 border-t border-black/[0.06]">
                  <button
                    onClick={onOpenTrial}
                    className={`w-full rounded-full py-3 text-xs sm:text-sm font-medium tracking-tight transition-all duration-200 cursor-pointer ${
                      plan.isPopular
                        ? 'bg-[#0071e3] hover:bg-[#0077ed] text-white shadow-sm active:scale-95'
                        : 'bg-[#f5f5f7] hover:bg-[#e8e8ed] text-[#1d1d1f] active:scale-95'
                    }`}
                  >
                    {plan.cta}
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* Apple Guarantee Footnote */}
        <div className="mt-14 text-center text-xs text-[#86868b]">
          Every plan includes 14 days of full feature access. No setup fees. No long-term lock-in.
        </div>
      </div>
    </section>
  )
}
