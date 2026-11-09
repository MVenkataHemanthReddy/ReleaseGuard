'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { 
  Bell, 
  User, 
  LogOut, 
  Sun, 
  Moon, 
  ChevronDown, 
  LogoIcon 
} from '@/components/ui/Icons'
import { springs } from '@/lib/motion-tokens'
import { useProject } from '@/context/ProjectContext'

export function Header() {
  const { currentProject } = useProject()
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark')
    }
    return false
  })
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  const toggleTheme = () => {
    const newValue = !isDark
    setIsDark(newValue)
    if (newValue) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  return (
    <header className="sticky top-0 z-30 bg-white/80 dark:bg-surface-950/80 backdrop-blur-sm border-b border-surface-200 dark:border-surface-800">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          <LogoIcon className="w-8 h-8 text-brand-500" />
          {currentProject && (
            <div className="hidden sm:block">
              <h1 className="text-heading-lg font-semibold text-surface-900 dark:text-surface-100">
                {currentProject.name}
              </h1>
              <p className="text-caption text-surface-500 dark:text-surface-400">
                {currentProject.description || 'No description'}
              </p>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="btn-ghost p-2 rounded-lg"
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>

          <button
            className="btn-ghost p-2 rounded-lg relative"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-medium rounded-full flex items-center justify-center">
              3
            </span>
          </button>

          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="btn-ghost p-1.5 rounded-lg flex items-center gap-2"
              aria-label="User menu"
              aria-expanded={isUserMenuOpen}
              aria-haspopup="true"
            >
              <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                <User className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              </div>
              <span className="hidden sm:block text-body-sm font-medium text-surface-900 dark:text-surface-100">
                User
              </span>
              <ChevronDown className="w-4 h-4 text-surface-400 hidden sm:block" />
            </button>

            <AnimatePresence>
              {isUserMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 8 }}
                  transition={springs.snappy}
                  className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg shadow-lg py-2 z-50"
                  role="menu"
                >
                  <div className="px-3 py-2 border-b border-surface-200 dark:border-surface-700">
                    <p className="text-body-sm font-medium text-surface-900 dark:text-surface-100">User Name</p>
                    <p className="text-caption text-surface-500 dark:text-surface-400">user@example.com</p>
                  </div>
                  <button
                    onClick={() => setIsUserMenuOpen(false)}
                    className="w-full flex items-center gap-2 px-3 py-2 text-left text-body-sm text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800 hover:text-surface-900 dark:hover:text-surface-100"
                    role="menuitem"
                  >
                    <User className="w-4 h-4" />
                    Profile
                  </button>
                  <button
                    onClick={toggleTheme}
                    className="w-full flex items-center gap-2 px-3 py-2 text-left text-body-sm text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800 hover:text-surface-900 dark:hover:text-surface-100"
                    role="menuitem"
                  >
                    {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                    {isDark ? 'Light Mode' : 'Dark Mode'}
                  </button>
                  <hr className="my-2 border-surface-200 dark:border-surface-700" />
                  <button
                    onClick={() => setIsUserMenuOpen(false)}
                    className="w-full flex items-center gap-2 px-3 py-2 text-left text-body-sm text-red-600 dark:text-red-400 hover:bg-surface-100 dark:hover:bg-surface-800"
                    role="menuitem"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  )
}
