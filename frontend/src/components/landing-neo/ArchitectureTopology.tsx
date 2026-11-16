import React, { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { 
  Cloud, 
  Server, 
  Cpu, 
  ShieldCheck, 
  Lock, 
  Zap, 
  ArrowRight, 
  Database,
  Radio,
  CheckCircle2,
  Globe
} from 'lucide-react'

interface ArchitectureMode {
  id: string
  name: string
  tag: string
  subtitle: string
  description: string
  securityLevel: string
  installTime: string
  dataResidency: string
  nodes: { label: string; role: string; status: string }[]
  highlights: string[]
}

const modes: ArchitectureMode[] = [
  {
    id: 'cloud',
    name: 'Multi-Tenant Global Cloud SaaS',
    tag: 'RECOMMENDED • FASTEST SETUP',
    subtitle: 'High-Velocity Serverless SaaS Mesh across 28 Global Regions',
    description: 'Instantly accessible with zero DevOps overhead. Distributed edge caching, multi-model AI routing, and automatic multi-tenant database isolation powered by Postgres Edge.',
    securityLevel: 'SOC2 Type II + ISO 27001',
    installTime: '< 60 Seconds',
    dataResidency: 'Selectable Regions (US, EU, APAC, Middle East)',
    nodes: [
      { label: 'Client Apps & Webhooks', role: 'Traffic Ingress Layer', status: 'Active' },
      { label: 'Global Anycast Gateway (28 PoPs)', role: 'Sub-14ms Edge Routing', status: '99.999% SLA' },
      { label: 'Autonomous AI Inference Core', role: 'Orchestration Engine', status: 'Operational' },
      { label: 'Distributed Multi-Tenant Store', role: 'Row-Level Isolation', status: 'Encrypted AES-256' },
    ],
    highlights: [
      'Automatic elastic scaling from 1 to 500,000 concurrent user sessions',
      'Turnkey multi-region failover with zero manual intervention',
      'End-to-end encrypted in transit (TLS 1.3) and at rest (AES-256 HSM)',
      'Built-in rate limiting, DDoS shielding, and API key management'
    ]
  },
  {
    id: 'vpc',
    name: 'Dedicated Single-Tenant VPC',
    tag: 'ENTERPRISE ISOLATION',
    subtitle: 'Dedicated Compute & Storage for High-Compliance Organizations',
    description: 'Run AstraOS inside a dedicated single-tenant virtual private cloud. Your database, AI model caches, and workflow runtime are physically segregated from all other tenants.',
    securityLevel: 'Zero Cross-Tenant Contamination',
    installTime: '1-Day Automated Provisioning',
    dataResidency: 'Dedicated Sovereign Cloud VPC',
    nodes: [
      { label: 'Enterprise Identity & SSO', role: 'SAML / Okta / Azure AD', status: 'Secured' },
      { label: 'Dedicated VPC Edge Ingress', role: 'Private VPC Peering', status: 'Isolated' },
      { label: 'Private AI Compute Cluster', role: 'Single-Tenant Engine', status: 'Dedicated' },
      { label: 'Private Tenant Data Vault', role: 'Customer-Managed KMS Keys', status: 'FIPS 140-2' },
    ],
    highlights: [
      'Customer-Managed Encryption Keys (BYOK via AWS KMS / Google Cloud KMS)',
      'Direct AWS DirectConnect & Azure ExpressRoute private networking',
      'Custom SLA guarantees with 99.999% financial uptime backing',
      'Tailored custom AI model weights fine-tuned on your organization data'
    ]
  },
  {
    id: 'onprem',
    name: 'Self-Hosted Sovereign Appliance',
    tag: 'DEFENSE & FINTECH',
    subtitle: 'Complete Air-Gapped Data Sovereignty in Your Datacenter',
    description: '100% self-contained SaaS appliance for defense contractors, sovereign governments, and tier-1 banking institutions requiring total air-gapped isolation with zero internet dependencies.',
    securityLevel: 'Air-Gapped / FedRAMP High Ready',
    installTime: 'Dedicated Solutions Deployment',
    dataResidency: '100% Local Bare Metal / GovCloud',
    nodes: [
      { label: 'Air-Gapped Private Runners', role: 'Internal Network Only', status: 'Zero Egress' },
      { label: 'Local Sovereign API Gateway', role: 'On-Premises Controller', status: 'Healthy' },
      { label: 'Embedded Local AI LLM Engine', role: 'Offline Tensor Ingest', status: 'Air-Gapped' },
      { label: 'Immutable Audit Ledger', role: 'WORM Cryptographic Vault', status: 'Locked' },
    ],
    highlights: [
      'Strictly zero outbound internet connections (Complete Air-Gap)',
      'Pre-packaged local models (DeepSeek, Llama 3, Mistral) with zero data leak',
      'Meets strict HIPAA, GDPR, FedRAMP High, and Basel III banking compliance',
      '24/7 designated Principal Solutions Engineer with rapid response'
    ]
  }
]

export function ArchitectureTopology() {
  const [activeModeId, setActiveModeId] = useState('cloud')
  const current = modes.find((m) => m.id === activeModeId) || modes[0]

  return (
    <section id="architecture" className="relative py-28 bg-[#040918] border-t border-cyan-500/15 overflow-hidden">
      {/* Background radial ambient lights */}
      <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-96 h-96 bg-cyan-600/10 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-teal-600/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/30 px-3.5 py-1 text-xs font-mono text-cyan-300 mb-4">
            <Server className="h-3.5 w-3.5 text-cyan-400" />
            <span>SAAS INFRASTRUCTURE & CLOUD TOPOLOGY</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Engineered for Turnkey SaaS or Sovereign VPCs
          </h2>
          <p className="mt-4 text-sm sm:text-base text-zinc-400 font-light">
            Deploy in our global multi-tenant cloud in seconds, or run in your own dedicated VPC with customer-managed encryption keys.
          </p>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 mb-12">
          {modes.map((mode) => {
            const isActive = mode.id === activeModeId
            return (
              <button
                key={mode.id}
                onClick={() => setActiveModeId(mode.id)}
                className={`relative px-6 py-3.5 rounded-xl font-medium text-xs sm:text-sm transition-all duration-300 border cursor-pointer ${
                  isActive
                    ? 'border-cyan-400 bg-cyan-950/70 text-white shadow-[0_0_25px_rgba(5,238,250,0.3)]'
                    : 'border-zinc-800 bg-[#081024]/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono font-semibold">{mode.name}</span>
                </div>
                <div className="text-[10px] font-mono text-cyan-400/80 mt-0.5">{mode.tag}</div>
              </button>
            )
          })}
        </div>

        {/* Mode Detail Panel */}
        <div className="rounded-3xl border border-cyan-500/25 bg-[#060c1c]/90 backdrop-blur-2xl p-6 sm:p-10 shadow-2xl">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Specifications (5 Cols) */}
            <div className="lg:col-span-5 space-y-6">
              <div>
                <span className="text-[11px] font-mono uppercase tracking-widest text-cyan-400 font-semibold">
                  {current.tag}
                </span>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
                  {current.name}
                </h3>
                <p className="text-sm text-cyan-300 font-medium mt-1">
                  {current.subtitle}
                </p>
                <p className="mt-4 text-xs sm:text-sm text-zinc-300 leading-relaxed font-light">
                  {current.description}
                </p>
              </div>

              {/* Security Metrics Pills */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-[#09132a] border border-zinc-800">
                  <span className="text-[10px] font-mono text-zinc-400 block">Compliance</span>
                  <span className="text-xs font-mono font-semibold text-emerald-400 mt-1 block">
                    {current.securityLevel}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#09132a] border border-zinc-800">
                  <span className="text-[10px] font-mono text-zinc-400 block">Provisioning</span>
                  <span className="text-xs font-mono font-semibold text-cyan-300 mt-1 block">
                    {current.installTime}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#09132a] border border-zinc-800">
                  <span className="text-[10px] font-mono text-zinc-400 block">Data Boundary</span>
                  <span className="text-xs font-mono font-semibold text-teal-300 mt-1 block truncate">
                    {current.dataResidency}
                  </span>
                </div>
              </div>

              {/* Highlights */}
              <div className="space-y-2 pt-2">
                {current.highlights.map((item, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs text-zinc-300">
                    <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Interactive Architecture Flow Diagram (7 Cols) */}
            <div className="lg:col-span-7 rounded-2xl border border-cyan-500/30 bg-[#02050f] p-6 relative overflow-hidden">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-6">
                <span className="text-xs font-mono text-zinc-400 flex items-center gap-2">
                  <Radio className="h-3.5 w-3.5 text-cyan-400 animate-pulse" />
                  TOPOLOGY FLOW ENGINE
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  ENCRYPTED TLS 1.3
                </span>
              </div>

              {/* Connected Topology Diagram Nodes */}
              <div className="space-y-4 relative">
                {current.nodes.map((node, idx) => (
                  <div key={idx} className="relative group">
                    <div className="flex items-center justify-between p-4 rounded-xl border border-zinc-800 bg-[#070e22] group-hover:border-cyan-500/50 group-hover:bg-[#0b1636] transition-all duration-300">
                      <div className="flex items-center gap-3">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono text-xs">
                          0{idx + 1}
                        </div>
                        <div>
                          <div className="text-xs sm:text-sm font-semibold text-white font-mono">
                            {node.label}
                          </div>
                          <div className="text-[11px] text-zinc-400 font-sans">
                            {node.role}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-[11px] font-mono text-emerald-400">
                          {node.status}
                        </span>
                      </div>
                    </div>

                    {/* Connecting Stream Arrow */}
                    {idx < current.nodes.length - 1 && (
                      <div className="flex justify-center my-1.5">
                        <div className="h-4 w-[2px] bg-gradient-to-b from-cyan-400 to-teal-400 relative">
                          <div className="absolute top-0 left-1/2 -translate-x-1/2 h-2 w-2 rounded-full bg-cyan-300 animate-ping" />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-4 border-t border-zinc-800/80 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                <span>Enterprise SLA Guaranteed</span>
                <span className="text-cyan-400">99.999% Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
