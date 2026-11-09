'use client'

import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { cn } from '@/lib/utils'
import { useProject } from '@/context/ProjectContext'
import { motion } from 'motion/react'
import { useSafeMotion } from '@/hooks/use-reduced-motion'

export function Layout() {
  const { currentProject, isLoading } = useProject()
  const safeMotion = useSafeMotion()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex items-center justify-center">
        <div className="animate-pulse text-brand-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 flex">
      <Sidebar />
      <div className={cn(
        'flex-1 flex flex-col transition-all duration-normal',
        currentProject ? 'lg:ml-64' : 'lg:ml-64'
      )}>
        <Header />
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <motion.div
            initial={safeMotion.initial}
            animate={safeMotion.animate}
            className="w-full"
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}