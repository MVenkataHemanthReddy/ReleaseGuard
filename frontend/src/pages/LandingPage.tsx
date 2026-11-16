import React, { useState } from 'react'
import { AppleLandingPage } from './AppleLandingPage'
import { NeoAstraLanding } from './NeoAstraLanding'
import { StyleSwitcher } from '../components/landing-apple/StyleSwitcher'

export function LandingPage() {
  const [style, setStyle] = useState<'apple' | 'neo'>('apple')

  return (
    <div className="relative">
      {/* Active Design System Render */}
      {style === 'apple' ? (
        <AppleLandingPage />
      ) : (
        <NeoAstraLanding />
      )}

      {/* Floating Style Switcher to Compare Both Paradigms */}
      <StyleSwitcher currentStyle={style} onToggle={setStyle} />
    </div>
  )
}
