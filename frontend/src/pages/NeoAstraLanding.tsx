import React, { useState } from 'react'
import { Navbar } from '../components/landing-neo/Navbar'
import { HeroSection } from '../components/landing-neo/HeroSection'
import { LiveSimulationTerminal } from '../components/landing-neo/LiveSimulationTerminal'
import { ProductSuites } from '../components/landing-neo/ProductSuites'
import { ArchitectureTopology } from '../components/landing-neo/ArchitectureTopology'
import { BentoFeatures } from '../components/landing-neo/BentoFeatures'
import { RoiCalculator } from '../components/landing-neo/RoiCalculator'
import { PricingSection } from '../components/landing-neo/PricingSection'
import { TestimonialsCompliance } from '../components/landing-neo/TestimonialsCompliance'
import { FaqSection } from '../components/landing-neo/FaqSection'
import { Footer } from '../components/landing-neo/Footer'
import { DemoModal } from '../components/landing-neo/DemoModal'

export function NeoAstraLanding() {
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#030712] text-zinc-100 selection:bg-cyan-500 selection:text-black">
      {/* Top Floating Glass Navigation */}
      <Navbar onOpenDemo={() => setIsDemoModalOpen(true)} />

      <main>
        {/* Hero with NeoAstra-style spinning cybernetic orbits & key metrics */}
        <HeroSection onOpenDemo={() => setIsDemoModalOpen(true)} />

        {/* Live Interactive Telemetry Sandbox */}
        <LiveSimulationTerminal />

        {/* 4 Flagship SaaS Suites */}
        <ProductSuites />

        {/* Deployment Modes & Topology */}
        <ArchitectureTopology />

        {/* Bento Grid with Live Interactive Sliders & Breakers */}
        <BentoFeatures />

        {/* Interactive ROI Calculator */}
        <RoiCalculator onOpenDemo={() => setIsDemoModalOpen(true)} />

        {/* Pricing Matrix with Monthly / Annual Switch */}
        <PricingSection onOpenDemo={() => setIsDemoModalOpen(true)} />

        {/* Enterprise Testimonials & Institutional Compliance */}
        <TestimonialsCompliance />

        {/* Accordion FAQ */}
        <FaqSection />
      </main>

      {/* Cyberpunk Footer with Newsletter and Status */}
      <Footer onOpenDemo={() => setIsDemoModalOpen(true)} />

      {/* VIP Enterprise Demo Request Modal */}
      <DemoModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
      />
    </div>
  )
}
