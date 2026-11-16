import React, { useState } from 'react'
import { motion } from 'motion/react'
import { Cloud, Server, ShieldCheck, Lock, Globe, CheckCircle2, ChevronRight } from 'lucide-react'

export function AppleArchitecture() {
  const [activeTab, setActiveTab] = useState<'cloud' | 'vpc' | 'sovereign'>('cloud')

  return (
    <section id="architecture" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
            GLOBAL ARCHITECTURE
          </span>
          <h2 className="text-4xl sm:text-6xl font-semibold text-[#1d1d1f] tracking-tight mt-2">
            Deploy your way.<br />Cloud or sovereign.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#86868b] font-normal leading-relaxed">
            Whether you want instant zero-configuration scale in our global cloud, or complete data isolation inside your private VPC, AstraOS adapts to your security perimeter.
          </p>
        </div>

        {/* 3 Architecture Pillar Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Card 1: Multi-Tenant Cloud */}
          <div className="rounded-[2.5rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm text-[#0071e3] mb-6">
                <Cloud className="h-6 w-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-[#86868b]">
                TURNKEY SCALE
              </span>
              <h3 className="text-2xl font-semibold text-[#1d1d1f] tracking-tight mt-1">
                Global Cloud SaaS
              </h3>
              <p className="mt-3 text-sm text-[#86868b] leading-relaxed font-normal">
                Instant setup with zero infrastructure overhead. Automatically distributed across 28 global Point of Presence (PoP) regions with 99.999% SLA uptime.
              </p>
            </div>

            <div className="mt-8 space-y-3 pt-6 border-t border-black/[0.06]">
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>60-second instant onboarding</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Sub-14ms global Anycast routing</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Automatic multi-tenant row isolation</span>
              </div>
            </div>
          </div>

          {/* Card 2: Dedicated VPC */}
          <div className="rounded-[2.5rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm text-purple-600 mb-6">
                <Server className="h-6 w-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-[#86868b]">
                ENTERPRISE PRIVATE
              </span>
              <h3 className="text-2xl font-semibold text-[#1d1d1f] tracking-tight mt-1">
                Dedicated Single-Tenant VPC
              </h3>
              <p className="mt-3 text-sm text-[#86868b] leading-relaxed font-normal">
                Physically dedicated compute and database instances isolated within your private AWS, GCP, or Azure VPC perimeter with customer-managed keys (BYOK).
              </p>
            </div>

            <div className="mt-8 space-y-3 pt-6 border-t border-black/[0.06]">
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Zero cross-tenant shared resources</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Bring-Your-Own-Key (AWS KMS / GCP)</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Direct VPC Peering & ExpressRoute</span>
              </div>
            </div>
          </div>

          {/* Card 3: Sovereign Air-Gapped */}
          <div className="rounded-[2.5rem] bg-[#f5f5f7] p-8 sm:p-10 border border-black/[0.04] flex flex-col justify-between hover:shadow-lg transition-all duration-300">
            <div>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm text-emerald-600 mb-6">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-[#86868b]">
                DEFENSE & BANKING
              </span>
              <h3 className="text-2xl font-semibold text-[#1d1d1f] tracking-tight mt-1">
                Sovereign Air-Gapped
              </h3>
              <p className="mt-3 text-sm text-[#86868b] leading-relaxed font-normal">
                Completely self-contained container appliance engineered for sovereign datacenters and classified environments with strictly zero outbound internet egress.
              </p>
            </div>

            <div className="mt-8 space-y-3 pt-6 border-t border-black/[0.06]">
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Zero external network connectivity</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Embedded offline AI model weights</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-[#1d1d1f] font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>FedRAMP High & Basel III compliant</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
