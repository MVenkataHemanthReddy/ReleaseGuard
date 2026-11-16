import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { ChevronDown, HelpCircle } from 'lucide-react'

interface FaqItem {
  question: string
  answer: string
}

export function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  const faqs: FaqItem[] = [
    {
      question: 'How quickly can our team integrate AstraOS into our existing SaaS app?',
      answer:
        'Most teams get their first autonomous workflow live in under 15 minutes. AstraOS provides drop-in React/TypeScript SDKs, REST webhooks, and pre-built connectors for Stripe, PostgreSQL, Supabase, and modern auth providers like Clerk and Auth0.'
    },
    {
      question: 'Can we use AstraOS as both an in-app AI copilot and a backend workflow runner?',
      answer:
        'Yes. AstraOS is designed as a full-stack SaaS operating system. You can embed our pre-built, themeable AI copilot widget inside your customer-facing dashboard while utilizing our asynchronous event bus on the backend for automated billing, onboarding, and multi-tenant telemetry.'
    },
    {
      question: 'How does AstraOS guarantee data privacy and multi-tenant database isolation?',
      answer:
        'AstraOS enforces strict row-level security (RLS) and schema-level isolation. Each tenant’s data is encrypted with isolated cryptographic keys (AES-256). We never use your customer data or private prompts to train public AI models.'
    },
    {
      question: 'What happens when our SaaS experiences massive traffic surges?',
      answer:
        'AstraOS runs across 28 global Point of Presence (PoP) edge nodes with automatic serverless elasticity. The platform automatically scales from handling 100 requests per second to over 250,000 requests per second without latency degradation or dropped webhooks.'
    },
    {
      question: 'Can we deploy AstraOS in our own dedicated AWS/GCP VPC or sovereign cloud?',
      answer:
        'Yes! For high-growth scale-ups and regulated enterprises, our Enterprise Astra tier provides automated 1-click deployment into a dedicated, single-tenant VPC with Bring-Your-Own-Key (BYOK) encryption support.'
    },
    {
      question: 'Is there a free trial, and do I need to enter a credit card?',
      answer:
        'You can start immediately with our 14-day full access free trial with zero credit card required. You get complete access to AstraFlow, AstraAgent, and our live interactive sandbox.'
    }
  ]

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx)
  }

  return (
    <section id="faq" className="relative py-28 bg-[#030712] border-t border-cyan-500/10 overflow-hidden">
      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <HelpCircle className="h-3.5 w-3.5 text-cyan-400" />
            <span>SAAS KNOWLEDGE BASE & CLARITY</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Everything you need to know about scaling your SaaS product with AstraOS.
          </p>
        </div>

        {/* Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, idx) => {
            const isOpen = openIndex === idx
            return (
              <div
                key={idx}
                className="rounded-2xl border border-zinc-800 bg-[#070e20]/80 overflow-hidden transition-colors hover:border-cyan-500/30"
              >
                <button
                  onClick={() => toggle(idx)}
                  className="w-full p-6 text-left flex items-center justify-between gap-4 cursor-pointer focus:outline-none"
                >
                  <span className="text-base font-semibold text-white font-sans tracking-tight">
                    {faq.question}
                  </span>
                  <div
                    className={`p-1.5 rounded-lg border border-zinc-700 bg-zinc-800 text-cyan-400 transition-transform duration-300 shrink-0 ${
                      isOpen ? 'rotate-180 bg-cyan-950/60 border-cyan-500/40' : ''
                    }`}
                  >
                    <ChevronDown className="h-4 w-4" />
                  </div>
                </button>

                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                    >
                      <div className="px-6 pb-6 pt-1 text-sm text-zinc-300 leading-relaxed font-light border-t border-zinc-800/60">
                        {faq.answer}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
