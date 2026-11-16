import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { 
  Bot, 
  Zap, 
  Activity, 
  Lock, 
  Globe, 
  Search, 
  SlidersHorizontal, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles, 
  Terminal, 
  ShieldCheck, 
  Database, 
  Layers, 
  ChevronRight,
  X,
  Copy,
  Check
} from 'lucide-react'

export interface CapabilityItem {
  id: string
  title: string
  category: 'ai' | 'workflows' | 'telemetry' | 'security' | 'edge'
  categoryName: string
  categoryIcon: any
  tagline: string
  description: string
  industries: string[]
  metrics: { label: string; value: string }
  features: string[]
  apiEndpoint: string
  samplePayload: string
  tier: 'Included in All' | 'Scale-Up Pro' | 'Enterprise Astra'
}

const allCapabilities: CapabilityItem[] = [
  // 1. AI & Copilots
  {
    id: 'ai-copilot',
    title: 'AstraCopilot In-App Assistant',
    category: 'ai',
    categoryName: 'AI & Agents',
    categoryIcon: Bot,
    tagline: 'Context-aware in-app copilot for your end users',
    description: 'Embed an intelligent assistant directly into your SaaS frontend. Grounded in your workspace documentation with zero hallucinations and strict boundary controls.',
    industries: ['B2B SaaS', 'E-Commerce', 'FinTech'],
    metrics: { label: 'First Response', value: '< 1.2s' },
    features: ['Real-time streaming responses via WebSockets', 'Custom persona & brand tone alignment', 'Human-in-the-loop escalation rules'],
    apiEndpoint: 'POST /v1/ai/copilot/chat',
    samplePayload: '{\n  "tenant_id": "org_9182",\n  "prompt": "Summarize Q3 expansion deals",\n  "grounding": ["notion", "zendesk"]\n}',
    tier: 'Included in All'
  },
  {
    id: 'agent-swarm',
    title: 'Autonomous Multi-Agent Swarm',
    category: 'ai',
    categoryName: 'AI & Agents',
    categoryIcon: Bot,
    tagline: 'Specialized autonomous worker teams that execute complex tasks',
    description: 'Deconstruct complex multi-stage tasks into parallel sub-agents (e.g. data fetcher, compliance reviewer, report author) with deterministic coordination.',
    industries: ['B2B SaaS', 'FinTech', 'HealthTech'],
    metrics: { label: 'Autonomous Resolution', value: '78.4%' },
    features: ['Parallel task execution with state DAGs', 'Self-correcting error recovery logic', 'Automatic audit trace generation'],
    apiEndpoint: 'POST /v1/ai/agents/dispatch',
    samplePayload: '{\n  "agent_type": "churn_mitigation",\n  "context": { "user_id": "usr_849" },\n  "max_steps": 6\n}',
    tier: 'Scale-Up Pro'
  },
  {
    id: 'rag-engine',
    title: 'Semantic Vector Knowledge Mesh',
    category: 'ai',
    categoryName: 'AI & Agents',
    categoryIcon: Bot,
    tagline: 'Instant sub-20ms hybrid semantic retrieval',
    description: 'Automatically vectorizes your SaaS helpdocs, API references, and CRM history using high-dimensional embeddings for instantaneous contextual recall.',
    industries: ['B2B SaaS', 'HealthTech'],
    metrics: { label: 'Vector Recall Accuracy', value: '99.4%' },
    features: ['Hybrid BM25 + dense vector semantic ranking', 'Auto-chunking and metadata filtering', 'Zero cross-tenant vector contamination'],
    apiEndpoint: 'POST /v1/ai/knowledge/query',
    samplePayload: '{\n  "query": "How to configure SAML SSO with Okta",\n  "top_k": 3\n}',
    tier: 'Scale-Up Pro'
  },

  // 2. Workflows & Automation
  {
    id: 'prompt-to-pipeline',
    title: 'Prompt-to-Pipeline Generator',
    category: 'workflows',
    categoryName: 'Workflows',
    categoryIcon: Zap,
    tagline: 'Generate production-ready event workflows from plain English',
    description: 'Describe the desired logic (e.g. "When a Stripe invoice exceeds $5,000, verify fraud score and notify executive Slack"), and AstraOS compiles executable DAGs in seconds.',
    industries: ['B2B SaaS', 'FinTech'],
    metrics: { label: 'Dev Time Saved', value: '82% cut' },
    features: ['Deterministic schema validation on all nodes', 'Visual flow editor + code export', 'Automated unit test generation for pipelines'],
    apiEndpoint: 'POST /v1/workflows/generate',
    samplePayload: '{\n  "prompt": "When customer upgrades, provision seats and alert account owner",\n  "format": "json_dag"\n}',
    tier: 'Included in All'
  },
  {
    id: 'webhook-bus',
    title: 'High-Throughput Webhook Engine',
    category: 'workflows',
    categoryName: 'Workflows',
    categoryIcon: Zap,
    tagline: 'Reliable event ingestion with exponential backoff and replay',
    description: 'Process hundreds of thousands of concurrent webhook events with guaranteed at-least-once delivery, automatic deduplication, and zero dropped payloads.',
    industries: ['FinTech', 'E-Commerce', 'B2B SaaS'],
    metrics: { label: 'Delivery Guarantee', value: '99.999%' },
    features: ['Sub-10ms signature verification (HMAC-SHA256)', 'Automated retry with exponential jitter', 'Dead-letter queue inspection and manual replay'],
    apiEndpoint: 'POST /v1/webhooks/ingest',
    samplePayload: '{\n  "event": "customer.subscription.created",\n  "signature": "sha256=98a1...",\n  "payload": { "plan": "enterprise" }\n}',
    tier: 'Included in All'
  },
  {
    id: 'circuit-breaker',
    title: 'Self-Healing Circuit Breakers',
    category: 'workflows',
    categoryName: 'Workflows',
    categoryIcon: Zap,
    tagline: 'Automated fallback and traffic throttling on downstream failure',
    description: 'Protects your product from cascading third-party outages. If a downstream CRM or API degrades, AstraOS seamlessly falls back to cached responses or async queues.',
    industries: ['FinTech', 'E-Commerce'],
    metrics: { label: 'Trip Latency', value: '< 850ms' },
    features: ['Configurable failure thresholds and cooling periods', 'Graceful degradation fallback mockers', 'Slack & PagerDuty instant alerting'],
    apiEndpoint: 'GET /v1/workflows/breakers/status',
    samplePayload: '{\n  "gateway_status": "healthy",\n  "tripped_circuits": 0,\n  "active_queues": 12\n}',
    tier: 'Scale-Up Pro'
  },

  // 3. Telemetry & Analytics
  {
    id: 'predictive-churn',
    title: 'Predictive Churn Telemetry Engine',
    category: 'telemetry',
    categoryName: 'Telemetry',
    categoryIcon: Activity,
    tagline: 'Detect account decay and revenue risk weeks before contract renewal',
    description: 'Tracks customer feature adoption trends and session decay vectors. Automatically computes health scores and dispatches proactive customer success playbooks.',
    industries: ['B2B SaaS', 'FinTech'],
    metrics: { label: 'Forecast Accuracy', value: '98.8%' },
    features: ['Multivariate product usage decay modeling', 'Automated Slack/HubSpot alert routing', 'Custom retention incentive triggering'],
    apiEndpoint: 'GET /v1/analytics/churn-risk',
    samplePayload: '{\n  "account_id": "acc_781",\n  "risk_score": 0.12,\n  "velocity_trend": "stable"\n}',
    tier: 'Scale-Up Pro'
  },
  {
    id: 'realtime-arr',
    title: 'Real-Time Revenue & Usage Analytics',
    category: 'telemetry',
    categoryName: 'Telemetry',
    categoryIcon: Activity,
    tagline: 'Sub-second billing telemetry and cohort expansion metrics',
    description: 'Unify Stripe, Chargebee, and product event metrics into a single real-time dashboard. Monitor Net Revenue Retention (NRR), expansion MRR, and seat utilization instantly.',
    industries: ['B2B SaaS'],
    metrics: { label: 'Query Speed', value: '< 25ms' },
    features: ['Cohort retention & churn analysis matrices', 'Seat utilization and license waste detection', 'Sync with Snowflake, BigQuery & ClickHouse'],
    apiEndpoint: 'GET /v1/analytics/arr-overview',
    samplePayload: '{\n  "total_arr": 14840000,\n  "nrr": 1.18,\n  "active_subscriptions": 1420\n}',
    tier: 'Included in All'
  },

  // 4. Security & Compliance
  {
    id: 'row-level-security',
    title: 'Multi-Tenant Row-Level Encryption',
    category: 'security',
    categoryName: 'Security',
    categoryIcon: Lock,
    tagline: 'Cryptographic data isolation per customer organization',
    description: 'Guarantees that each tenant’s customer data is encrypted with dedicated cryptographic keys (AES-256) and enforced via database row-level security policies.',
    industries: ['FinTech', 'HealthTech', 'B2B SaaS'],
    metrics: { label: 'Data Boundary', value: '100% Isolated' },
    features: ['Hardware Security Module (HSM) key rotation', 'Zero cross-tenant query contamination', 'Built-in SQL injection and tamper prevention'],
    apiEndpoint: 'POST /v1/security/tenants/isolate',
    samplePayload: '{\n  "tenant_id": "tenant_1092",\n  "encryption_cipher": "AES-256-GCM",\n  "key_id": "kms-8819"\n}',
    tier: 'Included in All'
  },
  {
    id: 'sovereign-vpc',
    title: 'Dedicated Sovereign Cloud VPC',
    category: 'security',
    categoryName: 'Security',
    categoryIcon: Lock,
    tagline: 'Physically isolated compute and storage inside your private network',
    description: 'Run the entire AstraOS runtime within your private AWS, GCP, or Azure VPC perimeter. Keep customer data, model caches, and logs within your sovereign jurisdiction.',
    industries: ['HealthTech', 'FinTech'],
    metrics: { label: 'Data Egress', value: 'Zero Egress' },
    features: ['Bring-Your-Own-Key (BYOK) encryption support', 'Direct AWS DirectConnect & ExpressRoute peering', 'Air-gapped and FedRAMP High deployment option'],
    apiEndpoint: 'POST /v1/infra/vpc/deploy',
    samplePayload: '{\n  "cloud_provider": "aws",\n  "region": "us-east-1",\n  "vpc_id": "vpc-089a8"\n}',
    tier: 'Enterprise Astra'
  },

  // 5. Global Edge & Scale
  {
    id: 'anycast-edge',
    title: '28-Region Anycast Edge Gateway',
    category: 'edge',
    categoryName: 'Global Edge',
    categoryIcon: Globe,
    tagline: 'Sub-14ms global latency with automatic geo-routing',
    description: 'Incoming requests automatically resolve at the closest physical Point of Presence. Eliminates international round-trip latency for global enterprise customers.',
    industries: ['B2B SaaS', 'E-Commerce', 'FinTech'],
    metrics: { label: 'Median P99', value: '12.4ms' },
    features: ['Zero-downtime geo-distributed failover', 'Edge token authentication with Ed25519', 'Layer 3/4/7 DDoS mitigation at line rate'],
    apiEndpoint: 'GET /v1/edge/health',
    samplePayload: '{\n  "status": "healthy",\n  "active_pops": 28,\n  "routing": "anycast_optimal"\n}',
    tier: 'Included in All'
  },
  {
    id: 'serverless-autoscale',
    title: 'Serverless Worker Elastic Mesh',
    category: 'edge',
    categoryName: 'Global Edge',
    categoryIcon: Globe,
    tagline: 'Scale from 1 to 500,000 requests per second with zero cold starts',
    description: 'Elastic serverless execution instances warm up in under 5ms. Absorb massive viral traffic waves and marketing launches without paying for idle capacity.',
    industries: ['E-Commerce', 'B2B SaaS'],
    metrics: { label: 'Cold Start Time', value: '< 5ms' },
    features: ['Instant replica scale up and scale down', 'Multi-zone redundancy across tier-1 providers', 'Automatic connection pooling to origin DBs'],
    apiEndpoint: 'GET /v1/edge/mesh/metrics',
    samplePayload: '{\n  "current_qps": 48920,\n  "active_instances": 128,\n  "utilization": "42%"\n}',
    tier: 'Scale-Up Pro'
  }
]

export function AppleCategoryExplorer() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeModalItem, setActiveModalItem] = useState<CapabilityItem | null>(null)
  const [copiedPayload, setCopiedPayload] = useState(false)

  const categories = [
    { id: 'all', name: 'All Modules', icon: Layers, count: allCapabilities.length },
    { id: 'ai', name: 'AI & Agents', icon: Bot, count: allCapabilities.filter(c => c.category === 'ai').length },
    { id: 'workflows', name: 'Workflows', icon: Zap, count: allCapabilities.filter(c => c.category === 'workflows').length },
    { id: 'telemetry', name: 'Telemetry', icon: Activity, count: allCapabilities.filter(c => c.category === 'telemetry').length },
    { id: 'security', name: 'Security', icon: Lock, count: allCapabilities.filter(c => c.category === 'security').length },
    { id: 'edge', name: 'Global Edge', icon: Globe, count: allCapabilities.filter(c => c.category === 'edge').length },
  ]

  const industries = ['All Industries', 'B2B SaaS', 'FinTech', 'HealthTech', 'E-Commerce']

  const filteredCapabilities = useMemo(() => {
    return allCapabilities.filter((item) => {
      const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
      const matchesIndustry = selectedIndustry === 'All Industries' || item.industries.includes(selectedIndustry)
      const matchesSearch =
        searchQuery === '' ||
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tagline.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesCategory && matchesIndustry && matchesSearch
    })
  }, [selectedCategory, selectedIndustry, searchQuery])

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedPayload(true)
    setTimeout(() => setCopiedPayload(false), 2000)
  }

  return (
    <section id="capabilities" className="py-24 bg-[#fbfbfd] border-t border-black/[0.05]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Apple Keynote Style Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
            CATEGORY EXPLORER
          </span>
          <h2 className="text-4xl sm:text-6xl font-semibold text-[#1d1d1f] tracking-tight mt-2">
            Explore by category.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#86868b] font-normal leading-relaxed">
            Sort and filter the entire AstraOS ecosystem according to capability, industry, or technical requirement.
          </p>
        </div>

        {/* 1. Category Icon Tab Bar (Apple / Google Style Horizontal Filter) */}
        <div className="flex items-center justify-start sm:justify-center overflow-x-auto pb-4 gap-2 mb-8 no-scrollbar">
          {categories.map((cat) => {
            const Icon = cat.icon
            const isSelected = selectedCategory === cat.id
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-full text-xs sm:text-sm font-medium transition-all shrink-0 cursor-pointer ${
                  isSelected
                    ? 'bg-[#1d1d1f] text-white shadow-sm'
                    : 'bg-white text-[#1d1d1f] border border-black/[0.06] hover:bg-[#f5f5f7]'
                }`}
              >
                <Icon className={`h-4 w-4 ${isSelected ? 'text-white' : 'text-[#0071e3]'}`} />
                <span>{cat.name}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono ${
                    isSelected ? 'bg-white/20 text-white' : 'bg-[#f5f5f7] text-[#86868b]'
                  }`}
                >
                  {cat.count}
                </span>
              </button>
            )
          })}
        </div>

        {/* 2. Secondary Filter Bar: Industry Pills & Live Search Input */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-3 rounded-2xl bg-white border border-black/[0.06] shadow-sm mb-10">
          {/* Industry Pills */}
          <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
            <span className="text-xs font-medium text-[#86868b] mr-1 hidden lg:inline">Filter by:</span>
            {industries.map((ind) => (
              <button
                key={ind}
                onClick={() => setSelectedIndustry(ind)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer ${
                  selectedIndustry === ind
                    ? 'bg-[#0071e3] text-white'
                    : 'text-[#86868b] hover:text-[#1d1d1f] hover:bg-[#f5f5f7]'
                }`}
              >
                {ind}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#86868b]" />
            <input
              type="text"
              placeholder="Search 12+ capabilities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 rounded-full border border-black/10 bg-[#f5f5f7] text-xs text-[#1d1d1f] placeholder-[#86868b] focus:border-[#0071e3] focus:bg-white focus:outline-none transition"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-2.5 text-[#86868b] hover:text-[#1d1d1f]"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* 3. Categorized Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredCapabilities.map((item) => {
              const Icon = item.categoryIcon
              return (
                <motion.div
                  key={item.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.25 }}
                  onClick={() => setActiveModalItem(item)}
                  className="rounded-[2rem] bg-white p-7 border border-black/[0.06] shadow-sm hover:shadow-md hover:border-black/[0.12] transition-all flex flex-col justify-between cursor-pointer group"
                >
                  <div>
                    {/* Card Top Category Pill & Tier */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#f5f5f7] text-[11px] font-medium text-[#1d1d1f]">
                        <Icon className="h-3.5 w-3.5 text-[#0071e3]" />
                        <span>{item.categoryName}</span>
                      </div>
                      <span className="text-[10px] font-medium text-[#86868b] bg-[#fafafa] border border-black/[0.04] px-2 py-0.5 rounded-full">
                        {item.tier}
                      </span>
                    </div>

                    <h3 className="text-xl font-semibold text-[#1d1d1f] tracking-tight group-hover:text-[#0071e3] transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-xs font-medium text-[#86868b] mt-1">
                      {item.tagline}
                    </p>
                    <p className="mt-3 text-xs text-[#6e6e73] leading-relaxed line-clamp-2">
                      {item.description}
                    </p>
                  </div>

                  {/* Card Bottom Specs & Click action */}
                  <div className="mt-6 pt-5 border-t border-black/[0.05]">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-[10px] uppercase font-medium text-[#86868b] block">
                          {item.metrics.label}
                        </span>
                        <span className="text-lg font-semibold text-[#1d1d1f] tracking-tight">
                          {item.metrics.value}
                        </span>
                      </div>

                      <div className="flex items-center gap-1 text-xs font-medium text-[#0071e3] group-hover:translate-x-1 transition-transform">
                        <span>Details</span>
                        <ChevronRight className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>

        {/* Empty state if search yields nothing */}
        {filteredCapabilities.length === 0 && (
          <div className="py-16 text-center">
            <p className="text-base text-[#86868b]">No capabilities matched your filter.</p>
            <button
              onClick={() => {
                setSelectedCategory('all')
                setSelectedIndustry('All Industries')
                setSearchQuery('')
              }}
              className="mt-3 text-xs text-[#0071e3] font-medium hover:underline"
            >
              Reset all filters
            </button>
          </div>
        )}
      </div>

      {/* 4. Deep-Dive Modal Drawer when a Category Card is Clicked */}
      <AnimatePresence>
        {activeModalItem && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setActiveModalItem(null)}
              className="fixed inset-0 bg-black/40 backdrop-blur-md"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', duration: 0.45 }}
              className="relative w-full max-w-2xl overflow-hidden rounded-[2.5rem] bg-white p-7 sm:p-10 shadow-2xl z-10 border border-black/[0.08]"
            >
              {/* Close Button */}
              <button
                onClick={() => setActiveModalItem(null)}
                className="absolute top-6 right-6 rounded-full p-2 text-[#86868b] hover:text-[#1d1d1f] hover:bg-[#f5f5f7] transition cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xs font-semibold uppercase tracking-wider text-[#0071e3]">
                    {activeModalItem.categoryName}
                  </span>
                  <span className="text-[#d2d2d7]">•</span>
                  <span className="text-xs text-[#86868b] font-medium">
                    {activeModalItem.tier}
                  </span>
                </div>

                <h3 className="text-3xl font-semibold text-[#1d1d1f] tracking-tight">
                  {activeModalItem.title}
                </h3>
                <p className="text-sm font-medium text-[#86868b] mt-1">
                  {activeModalItem.tagline}
                </p>
                <p className="mt-4 text-sm text-[#4b4b50] leading-relaxed">
                  {activeModalItem.description}
                </p>

                {/* Features List */}
                <div className="my-6 space-y-2.5">
                  <span className="text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider block">
                    Core Technical Specifications:
                  </span>
                  {activeModalItem.features.map((feat, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs text-[#1d1d1f]/90">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>

                {/* API Code Example Preview */}
                <div className="rounded-2xl bg-[#1d1d1f] p-4 text-white font-mono text-xs my-6 relative">
                  <div className="flex items-center justify-between text-[11px] text-[#86868b] border-b border-white/10 pb-2 mb-3">
                    <span className="text-[#0071e3] font-semibold">{activeModalItem.apiEndpoint}</span>
                    <button
                      onClick={() => handleCopy(activeModalItem.samplePayload)}
                      className="flex items-center gap-1 text-white/70 hover:text-white transition cursor-pointer"
                    >
                      {copiedPayload ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                      <span>{copiedPayload ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <pre className="text-emerald-400 overflow-x-auto text-[11px] leading-relaxed">
                    {activeModalItem.samplePayload}
                  </pre>
                </div>

                {/* Footer Modal Action */}
                <div className="flex items-center justify-between pt-4 border-t border-black/[0.06]">
                  <span className="text-xs text-[#86868b]">
                    Target Industries: {activeModalItem.industries.join(', ')}
                  </span>
                  <button
                    onClick={() => setActiveModalItem(null)}
                    className="rounded-full bg-[#0071e3] hover:bg-[#0077ed] text-white px-5 py-2 text-xs font-medium cursor-pointer"
                  >
                    Done
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </section>
  )
}
