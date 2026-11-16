import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'

export function AppleFooter() {
  return (
    <footer className="bg-[#f5f5f7] text-[#86868b] text-[11px] font-normal border-t border-black/[0.08]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Apple-style Numbered Disclaimers / Footnotes */}
        <div className="space-y-2 pb-8 border-b border-black/[0.08] leading-relaxed">
          <p>
            1. 14-day free trial provides full unrestricted access to AstraFlow™, AstraAgent™, and all 500+ connectors. No credit card required at signup.
          </p>
          <p>
            2. Latency measurements represent global median P99 response times recorded across 28 active Edge Points of Presence during high-concurrency event ingestion tests.
          </p>
          <p>
            3. 99.999% Service Level Agreement (SLA) applies to Enterprise Astra tier deployments and includes financial uptime credits as stipulated in the enterprise master service agreement.
          </p>
          <p>
            4. SOC 2 Type II audit conducted by an independent AICPA-accredited CPA firm. Report and security architecture whitepaper available upon execution of standard NDA.
          </p>
        </div>

        {/* Apple-style 5-Column Navigation Directory */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 py-10 border-b border-black/[0.08]">
          {/* Col 1 */}
          <div>
            <h4 className="text-xs font-semibold text-[#1d1d1f] mb-3">Explore AstraOS</h4>
            <ul className="space-y-2">
              <li><a href="#overview" className="hover:text-[#1d1d1f] transition">Overview</a></li>
              <li><a href="#capabilities" className="hover:text-[#1d1d1f] transition">AstraFlow™ Workflows</a></li>
              <li><a href="#capabilities" className="hover:text-[#1d1d1f] transition">AstraAgent™ Swarms</a></li>
              <li><a href="#capabilities" className="hover:text-[#1d1d1f] transition">AstraData™ Telemetry</a></li>
              <li><a href="#demo" className="hover:text-[#1d1d1f] transition">Interactive Sandbox</a></li>
            </ul>
          </div>

          {/* Col 2 */}
          <div>
            <h4 className="text-xs font-semibold text-[#1d1d1f] mb-3">Architecture</h4>
            <ul className="space-y-2">
              <li><a href="#architecture" className="hover:text-[#1d1d1f] transition">Multi-Tenant Cloud</a></li>
              <li><a href="#architecture" className="hover:text-[#1d1d1f] transition">Dedicated Single-Tenant VPC</a></li>
              <li><a href="#architecture" className="hover:text-[#1d1d1f] transition">Sovereign Air-Gapped Cloud</a></li>
              <li><a href="#specs" className="hover:text-[#1d1d1f] transition">28 Edge PoP Locations</a></li>
              <li><a href="#specs" className="hover:text-[#1d1d1f] transition">Anycast Global Routing</a></li>
            </ul>
          </div>

          {/* Col 3 */}
          <div>
            <h4 className="text-xs font-semibold text-[#1d1d1f] mb-3">Enterprise & Trust</h4>
            <ul className="space-y-2">
              <li><a href="#pricing" className="hover:text-[#1d1d1f] transition">Pricing & Plans</a></li>
              <li><a href="#specs" className="hover:text-[#1d1d1f] transition">Security & Privacy</a></li>
              <li><a href="#specs" className="hover:text-[#1d1d1f] transition">SOC 2 Type II Compliance</a></li>
              <li><a href="#specs" className="hover:text-[#1d1d1f] transition">ISO/IEC 27001 Certification</a></li>
              <li><a href="#specs" className="hover:text-[#1d1d1f] transition">HIPAA & GDPR Safeguards</a></li>
            </ul>
          </div>

          {/* Col 4 */}
          <div>
            <h4 className="text-xs font-semibold text-[#1d1d1f] mb-3">Developers</h4>
            <ul className="space-y-2">
              <li><Link to="/dashboard" className="text-[#0071e3] hover:underline">SaaS Console Login</Link></li>
              <li><span className="text-[#86868b]">TypeScript SDK Documentation</span></li>
              <li><span className="text-[#86868b]">REST & Webhook Reference</span></li>
              <li><span className="text-[#86868b]">GraphQL Schema Explorer</span></li>
              <li><span className="text-[#86868b]">Community Forum</span></li>
            </ul>
          </div>

          {/* Col 5 */}
          <div>
            <h4 className="text-xs font-semibold text-[#1d1d1f] mb-3">Company</h4>
            <ul className="space-y-2">
              <li><span className="text-[#86868b]">About AstraOS</span></li>
              <li><span className="text-[#86868b]">Newsroom & Updates</span></li>
              <li><span className="text-[#86868b]">Careers</span></li>
              <li><span className="text-[#86868b]">Investor Relations</span></li>
              <li><span className="text-[#86868b]">Contact Executive Team</span></li>
            </ul>
          </div>
        </div>

        {/* Bottom Legal Copyright Bar */}
        <div className="pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            Copyright © {new Date().getFullYear()} AstraOS Technologies Inc. All rights reserved.
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <span className="hover:text-[#1d1d1f] transition cursor-pointer">Privacy Policy</span>
            <span className="text-[#d2d2d7]">|</span>
            <span className="hover:text-[#1d1d1f] transition cursor-pointer">Terms of Use</span>
            <span className="text-[#d2d2d7]">|</span>
            <span className="hover:text-[#1d1d1f] transition cursor-pointer">Sales and Refunds</span>
            <span className="text-[#d2d2d7]">|</span>
            <span className="hover:text-[#1d1d1f] transition cursor-pointer">Legal</span>
            <span className="text-[#d2d2d7]">|</span>
            <span className="hover:text-[#1d1d1f] transition cursor-pointer">Site Map</span>
          </div>

          <div className="text-[#1d1d1f] font-medium">
            United States
          </div>
        </div>
      </div>
    </footer>
  )
}
