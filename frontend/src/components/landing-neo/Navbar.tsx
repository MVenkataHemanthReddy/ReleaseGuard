import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Sparkles, ArrowRight, Menu, X, Terminal, Cpu, Globe, Zap } from 'lucide-react'

interface NavbarProps {
  onOpenDemo: () => void
}

export function Navbar({ onOpenDemo }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { name: 'Products', href: '#products' },
    { name: 'Interactive Demo', href: '#demo' },
    { name: 'Architecture', href: '#architecture' },
    { name: 'Features', href: '#features' },
    { name: 'ROI Calculator', href: '#roi' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'FAQ', href: '#faq' },
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
    <header
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled
          ? 'bg-[#030712]/90 backdrop-blur-xl border-b border-cyan-500/20 py-3.5 shadow-2xl shadow-cyan-950/20'
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo & Brand Identity */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400/20 via-teal-500/10 to-transparent border border-cyan-500/40 p-2 group-hover:border-cyan-400 group-hover:shadow-[0_0_25px_rgba(5,238,250,0.45)] transition-all duration-300">
              <Zap className="h-5 w-5 text-cyan-400 group-hover:scale-110 transition-transform duration-300" />
              {/* Outer cyber ring */}
              <div className="absolute -inset-[3px] rounded-xl border border-dashed border-cyan-400/30 animate-spin-slow pointer-events-none" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight text-white flex items-center gap-1.5 font-sans">
                ASTRA<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-300">OS</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 tracking-wider">
                  SAAS
                </span>
              </span>
              <span className="text-[10px] font-mono text-zinc-400 tracking-widest uppercase">
                Autonomous AI Cloud
              </span>
            </div>
          </a>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-7">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleScrollTo(e, link.href)}
                className="text-xs font-semibold text-zinc-300 hover:text-cyan-400 transition-colors tracking-wide relative group py-1"
              >
                {link.name}
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-cyan-400 to-teal-400 group-hover:w-full transition-all duration-300" />
              </a>
            ))}
          </nav>

          {/* Action CTAs & Status */}
          <div className="hidden sm:flex items-center gap-4">
            {/* Live Operational Status Pill */}
            <div className="hidden xl:flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-950/40 px-3 py-1 text-[11px] text-emerald-400 font-mono">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span>All Systems 99.99%</span>
            </div>

            {/* Sign In / Console */}
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-1.5 rounded-xl border border-zinc-700 bg-zinc-900/80 px-4 py-2 text-xs font-semibold text-zinc-200 hover:border-cyan-500/40 hover:text-white hover:bg-zinc-800 transition-all duration-200"
            >
              <span>Sign In</span>
            </Link>

            {/* Book Demo Button */}
            <button
              onClick={onOpenDemo}
              className="relative group inline-flex items-center gap-2 overflow-hidden rounded-xl p-[1px] font-semibold text-xs transition duration-300 shadow-[0_0_20px_rgba(5,238,250,0.25)] hover:shadow-[0_0_35px_rgba(5,238,250,0.5)] cursor-pointer"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-cyan-400 via-teal-300 to-cyan-500 group-hover:scale-105 transition-transform" />
              <span className="relative flex items-center gap-1.5 rounded-[11px] bg-[#030712] px-4 py-2 text-white group-hover:bg-[#030712]/80 transition-colors">
                <Sparkles className="h-3.5 w-3.5 text-cyan-300" />
                <span>Start Free Trial</span>
                <ArrowRight className="h-3.5 w-3.5 text-cyan-400 group-hover:translate-x-0.5 transition-transform" />
              </span>
            </button>
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex sm:hidden items-center gap-2">
            <button
              onClick={onOpenDemo}
              className="text-xs px-3 py-1.5 rounded-lg bg-cyan-400 text-black font-bold font-mono"
            >
              Try Free
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-zinc-400 hover:text-white focus:outline-none"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-cyan-500/20 bg-[#030712]/98 backdrop-blur-2xl px-6 py-6 space-y-4">
          <div className="grid grid-cols-1 gap-3">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleScrollTo(e, link.href)}
                className="block text-sm font-medium text-zinc-300 hover:text-cyan-400 py-1.5 border-b border-zinc-800/60"
              >
                {link.name}
              </a>
            ))}
          </div>

          <div className="pt-4 flex flex-col gap-3">
            <button
              onClick={() => {
                setMobileMenuOpen(false)
                onOpenDemo()
              }}
              className="w-full rounded-xl bg-gradient-to-r from-cyan-400 to-teal-400 py-3 text-center text-xs font-bold text-black"
            >
              Start Free Trial (14 Days)
            </button>
            <Link
              to="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full rounded-xl border border-zinc-700 bg-zinc-900 py-2.5 text-center text-xs font-semibold text-white"
            >
              Sign In to Console
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
