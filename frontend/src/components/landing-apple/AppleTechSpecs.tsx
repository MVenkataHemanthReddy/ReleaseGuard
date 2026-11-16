import React from 'react'
import { Shield, Lock, Globe, Cpu, CheckCircle2 } from 'lucide-react'

export function AppleTechSpecs() {
  const specs = [
    {
      category: 'Global Edge Ingress',
      items: [
        { label: 'Points of Presence', value: '28 Global Regions (US, EU, APAC, Middle East)' },
        { label: 'DNS Routing', value: 'Anycast Geo-Distributed with automatic failover' },
        { label: 'P99 Edge Latency', value: '12.4ms global median response' },
        { label: 'DDoS Mitigation', value: 'Automated Layer 3, 4 & 7 protection (Cloudflare powered)' }
      ]
    },
    {
      category: 'Enterprise Privacy & Security',
      items: [
        { label: 'Audited Certifications', value: 'AICPA SOC 2 Type II, ISO/IEC 27001:2022' },
        { label: 'Regulatory Compliance', value: 'GDPR, CCPA, HIPAA BAA, PCI-DSS Level 1' },
        { label: 'Encryption Standards', value: 'AES-256-GCM at rest, TLS 1.3 with Perfect Forward Secrecy' },
        { label: 'Key Management', value: 'Customer-Managed Keys (BYOK via AWS KMS / Google Cloud KMS)' }
      ]
    },
    {
      category: 'Multi-Tenant Isolation',
      items: [
        { label: 'Database Architecture', value: 'Row-Level Security (RLS) & dedicated isolated schemas' },
        { label: 'Tenant Concurrency', value: 'Elastic auto-scaling up to 500,000 concurrent sessions' },
        { label: 'Data Residency', value: 'Selectable sovereign region storage (US-only, EU-only)' },
        { label: 'Audit Logging', value: 'Immutable, tamper-evident audit trails with export to S3/GCS' }
      ]
    }
  ]

  return (
    <section id="specs" className="py-24 bg-white border-t border-black/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
            SPECIFICATIONS
          </span>
          <h2 className="text-4xl sm:text-6xl font-semibold text-[#1d1d1f] tracking-tight mt-2">
            Technical specs.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#86868b] font-normal leading-relaxed">
            Every standard, protocol, and compliance benchmark supporting your SaaS infrastructure.
          </p>
        </div>

        {/* Specs Table List (Apple Clean Format) */}
        <div className="max-w-4xl mx-auto divide-y divide-black/[0.08]">
          {specs.map((group, idx) => (
            <div key={idx} className="py-10 grid grid-cols-1 md:grid-cols-12 gap-6">
              <div className="md:col-span-4">
                <h3 className="text-lg font-semibold text-[#1d1d1f] tracking-tight">
                  {group.category}
                </h3>
              </div>
              <div className="md:col-span-8 space-y-4">
                {group.items.map((item, iIdx) => (
                  <div key={iIdx} className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 border-b border-black/[0.03] pb-3">
                    <span className="text-xs font-medium text-[#86868b]">{item.label}</span>
                    <span className="text-xs sm:text-sm font-medium text-[#1d1d1f] text-left sm:text-right">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
