import React, { useState } from 'react'
import { AppleNavbar } from '../components/landing-apple/AppleNavbar'
import { AppleHero } from '../components/landing-apple/AppleHero'
import { AppleCategoryExplorer } from '../components/landing-apple/AppleCategoryExplorer'
import { AppleBentoGrid } from '../components/landing-apple/AppleBentoGrid'
import { AppleInteractiveSandbox } from '../components/landing-apple/AppleInteractiveSandbox'
import { AppleArchitecture } from '../components/landing-apple/AppleArchitecture'
import { ApplePricing } from '../components/landing-apple/ApplePricing'
import { AppleTechSpecs } from '../components/landing-apple/AppleTechSpecs'
import { AppleFooter } from '../components/landing-apple/AppleFooter'
import { AppleTrialModal } from '../components/landing-apple/AppleTrialModal'

export function AppleLandingPage() {
  const [isTrialOpen, setIsTrialOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#fbfbfd] text-[#1d1d1f] font-sans antialiased selection:bg-[#0071e3] selection:text-white">
      {/* Apple-style Frosted Navbar */}
      <AppleNavbar onOpenTrial={() => setIsTrialOpen(true)} />

      <main>
        {/* Apple Keynote Style Hero */}
        <AppleHero onOpenTrial={() => setIsTrialOpen(true)} />

        {/* Category Explorer (Sort by Category: AI, Workflows, Telemetry, Security, Edge & Industry) */}
        <AppleCategoryExplorer />

        {/* Apple Bento Grid */}
        <AppleBentoGrid />

        {/* Live Interactive Sandbox */}
        <AppleInteractiveSandbox />

        {/* Architecture & Sovereignty */}
        <AppleArchitecture />

        {/* Transparent Apple Store Style Pricing */}
        <ApplePricing onOpenTrial={() => setIsTrialOpen(true)} />

        {/* Apple Technical Specs & Privacy */}
        <AppleTechSpecs />
      </main>

      {/* Apple Footnotes & 5-Column Directory */}
      <AppleFooter />

      {/* Free Trial Modal */}
      <AppleTrialModal isOpen={isTrialOpen} onClose={() => setIsTrialOpen(false)} />
    </div>
  )
}
