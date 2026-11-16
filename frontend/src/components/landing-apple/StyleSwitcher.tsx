import React from 'react'
import { Sparkles, Moon, Sun, ArrowLeftRight } from 'lucide-react'

interface StyleSwitcherProps {
  currentStyle: 'apple' | 'neo'
  onToggle: (style: 'apple' | 'neo') => void
}

export function StyleSwitcher({ currentStyle, onToggle }: StyleSwitcherProps) {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className="flex items-center gap-1.5 p-1.5 rounded-full bg-white/90 dark:bg-black/90 backdrop-blur-xl border border-black/10 dark:border-white/10 shadow-2xl">
        <button
          onClick={() => onToggle('apple')}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${
            currentStyle === 'apple'
              ? 'bg-[#1d1d1f] text-white shadow-sm'
              : 'text-[#86868b] hover:text-[#1d1d1f]'
          }`}
        >
          <span>🍏 Apple Style</span>
        </button>

        <button
          onClick={() => onToggle('neo')}
          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${
            currentStyle === 'neo'
              ? 'bg-gradient-to-r from-cyan-500 to-teal-400 text-black font-semibold shadow-[0_0_15px_rgba(5,238,250,0.4)]'
              : 'text-[#86868b] hover:text-[#1d1d1f]'
          }`}
        >
          <span>⚡ NeoAstra Style</span>
        </button>
      </div>
    </div>
  )
}
