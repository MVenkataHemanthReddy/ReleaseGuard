import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, ChevronRight, Menu, X, Sparkles, Layers } from 'lucide-react'

interface AppleNavbarProps {
  onOpenTrial: () => void
}

export function AppleNavbar({ onOpenTrial }: AppleNavbarProps) {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 15)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { name: 'Overview', href: '#overview' },
    { name: 'Explore Categories', href: '#capabilities' },
    { name: 'Interactive Demo', href: '#demo' },
    { name: 'Architecture', href: '#architecture' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'Tech Specs', href: '#specs' },
  ]

  const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    setMobileMenuOpen(false)
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <>
      {/* Apple-style Top Announcement Ribbon */}
      <div className="bg-[#f5f5f7] border-b border-black/[0.05] py-2.5 px-4 text-center text-xs text-[#1d1d1f] font-normal">
        <span className="font-semibold text-black">Astra Intelligence 2.0 is here.</span> Experience autonomous multi-agent swarms for modern SaaS.{' '}
        <a
          href="#demo"
          onClick={(e) => handleScrollTo(e, '#demo')}
          className="text-[#0071e3] hover:underline inline-flex items-center gap-0.5 ml-1 font-medium"
        >
          See the demo <ChevronRight className="h-3 w-3" />
        </a>
      </div>

      {/* Main Apple-style Frosted Navbar */}
      <header
        className={`sticky top-0 z-40 transition-all duration-200 ${
          scrolled
            ? 'bg-white/80 backdrop-blur-xl border-b border-black/[0.08] shadow-sm'
            : 'bg-white/90 backdrop-blur-md border-b border-black/[0.04]'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-14 items-center justify-between">
            {/* Apple-Style Monogram Brand */}
            <a href="#" className="flex items-center gap-2.5 group">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#1d1d1f] text-white shadow-sm transition-transform group-hover:scale-105">
                <span className="text-sm font-bold tracking-tight">A</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-base font-semibold tracking-tight text-[#1d1d1f]">
                  Astra
                </span>
                <span className="text-xs font-normal text-[#86868b]">
                  SaaS
                </span>
              </div>
            </a>

            {/* Desktop Navigation Links (Apple Clean Typography) */}
            <nav className="hidden md:flex items-center gap-8">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={(e) => handleScrollTo(e, link.href)}
                  className="text-xs font-normal text-[#1d1d1f]/80 hover:text-[#0071e3] transition-colors"
                >
                  {link.name}
                </a>
              ))}
            </nav>

            {/* Apple-style Right CTA Buttons */}
            <div className="hidden sm:flex items-center gap-4">
              <Link
                to="/dashboard"
                className="text-xs font-normal text-[#1d1d1f] hover:text-[#0071e3] transition-colors"
              >
                Sign In
              </Link>
              <button
                onClick={onOpenTrial}
                className="rounded-full bg-[#0071e3] hover:bg-[#0077ed] text-white px-4 py-1.5 text-xs font-medium tracking-tight shadow-sm transition-transform active:scale-95 cursor-pointer"
              >
                Try Free
              </button>
            </div>

            {/* Mobile Hamburger */}
            <div className="flex sm:hidden items-center gap-2">
              <button
                onClick={onOpenTrial}
                className="rounded-full bg-[#0071e3] text-white px-3 py-1 text-xs font-medium"
              >
                Try Free
              </button>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-1.5 text-[#1d1d1f] focus:outline-none"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-black/[0.08] bg-white px-6 py-5 space-y-3">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleScrollTo(e, link.href)}
                className="block text-sm font-normal text-[#1d1d1f] py-1"
              >
                {link.name}
              </a>
            ))}
            <div className="pt-4 border-t border-black/[0.06] flex flex-col gap-2">
              <button
                onClick={() => {
                  setMobileMenuOpen(false)
                  onOpenTrial()
                }}
                className="w-full rounded-full bg-[#0071e3] text-white py-2 text-xs font-medium text-center"
              >
                Start 14-Day Free Trial
              </button>
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full rounded-full border border-black/10 text-[#1d1d1f] py-2 text-xs font-medium text-center"
              >
                Console Sign In
              </Link>
            </div>
          </div>
        )}
      </header>
    </>
  )
}
