'use client'

import { useState, useEffect, useRef, createContext, useContext } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { cn } from '@/lib/utils'
import { springs, motionTokens } from '@/lib/motion-tokens'

export interface Tab {
  value: string
  label: string
  icon?: React.ReactNode
  disabled?: boolean
  badge?: string | number
}

export interface TabsProps {
  tabs: Tab[]
  value: string
  onChange: (value: string) => void
  className?: string
  variant?: 'line' | 'pills' | 'enclosed'
}

export function Tabs({ tabs, value, onChange, className, variant = 'line' }: TabsProps) {
  const [indicatorStyle, setIndicatorStyle] = useState<React.CSSProperties>({})

  const updateIndicator = (activeTab: HTMLButtonElement | null) => {
    if (!activeTab) return
    const parent = activeTab.parentElement
    if (!parent) return
    setIndicatorStyle({
      width: activeTab.offsetWidth,
      left: activeTab.offsetLeft,
    })
  }

  const handleResize = () => {
    const activeTab = document.querySelector('[data-tab-active]') as HTMLButtonElement
    updateIndicator(activeTab)
  }

  // Update indicator on mount and value change
  const tabsContainerRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [value, tabs])

  return (
    <div className={cn('relative', className)} ref={tabsContainerRef}>
      <div 
        className={cn(
          'flex gap-1',
          variant === 'pills' && 'bg-surface-100 dark:bg-surface-800 p-1 rounded-lg',
          variant === 'enclosed' && 'border border-surface-200 dark:border-surface-700 rounded-lg'
        )}
        role="tablist"
      >
        {tabs.map((tab, index) => (
          <button
            key={tab.value}
            role="tab"
            aria-selected={value === tab.value}
            aria-controls={`panel-${tab.value}`}
            id={`tab-${tab.value}`}
            disabled={tab.disabled}
            onClick={() => !tab.disabled && onChange(tab.value)}
            className={cn(
              'relative flex items-center justify-center gap-1.5 px-4 py-2 text-body-sm font-medium transition-all duration-fast',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2',
              tab.disabled
                ? 'opacity-50 pointer-events-none'
                : value === tab.value
                  ? 'text-brand-600 dark:text-brand-400'
                  : 'text-surface-600 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100',
              variant === 'pills' && value === tab.value && 'bg-white dark:bg-surface-900 shadow-sm rounded-md',
              variant === 'enclosed' && 'border-r last:border-r-0 border-surface-200 dark:border-surface-700'
            )}
            data-tab-active={value === tab.value}
          >
            {tab.icon && <span className="w-4 h-4">{tab.icon}</span>}
            {tab.label}
            {tab.badge && (
              <span className="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-brand-100 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
        {/* Animated indicator for line variant */}
        {variant === 'line' && (
          <AnimatePresence mode="wait">
            <motion.div
              key={value}
              layout
              className="absolute bottom-0 h-0.5 bg-brand-500 rounded-full"
              style={indicatorStyle}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            />
          </AnimatePresence>
        )}
      </div>
    </div>
  )
}

export interface TabPanelProps {
  value: string
  children: React.ReactNode
  className?: string
}

export function TabPanel({ value, children, className }: TabPanelProps) {
  const { tabs, value: currentValue } = useTabsContext()
  const isActive = currentValue === value

  if (!isActive) return null

  return (
    <div
      id={`panel-${value}`}
      role="tabpanel"
      aria-labelledby={`tab-${value}`}
      className={cn('animate-in', className)}
    >
      {children}
    </div>
  )
}

// Context for Tabs
interface TabsContextType {
  tabs: Tab[]
  value: string
}

const TabsContext = createContext<TabsContextType | null>(null)

export function TabsProvider({ children, tabs, value }: { children: React.ReactNode; tabs: Tab[]; value: string }) {
  return (
    <TabsContext.Provider value={{ tabs, value }}>
      {children}
    </TabsContext.Provider>
  )
}

function useTabsContext() {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error('Tab components must be used within TabsProvider')
  }
  return context
}