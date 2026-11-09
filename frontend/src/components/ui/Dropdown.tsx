'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { cn } from '@/lib/utils'
import { springs } from '@/lib/motion-tokens'

export interface DropdownItem {
  label?: string
  onClick?: () => void
  icon?: React.ReactNode
  disabled?: boolean
  danger?: boolean
  divider?: boolean
}

export interface DropdownProps {
  trigger: React.ReactElement
  items: DropdownItem[]
  align?: 'left' | 'right'
  closeOnClick?: boolean
}

export function Dropdown({ trigger, items, align = 'right', closeOnClick = true }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        if (triggerRef.current && !triggerRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <div ref={triggerRef}>
        {React.cloneElement(trigger, {
          onClick: (e: React.MouseEvent) => {
            e.stopPropagation()
            setIsOpen(!isOpen)
          },
          'aria-haspopup': 'true',
          'aria-expanded': isOpen,
        })}
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={springs.snappy}
            className={cn(
              'absolute z-50 mt-2 w-56 bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg shadow-lg py-1',
              align === 'right' ? 'right-0' : 'left-0'
            )}
            role="menu"
          >
            {items.map((item, index) => {
              if (item.divider) {
                return <hr key={`divider-${index}`} className="my-1 border-surface-200 dark:border-surface-700" />
              }
              return (
                <button
                  key={item.label}
                  onClick={() => {
                    item.onClick?.()
                    if (closeOnClick) setIsOpen(false)
                  }}
                  disabled={item.disabled}
                  className={cn(
                    'w-full px-3 py-2 text-left text-body-sm flex items-center gap-2 transition-colors duration-fast',
                    'focus-visible:outline-none focus-visible:bg-surface-100 dark:focus-visible:bg-surface-800',
                    item.danger
                      ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20'
                      : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800',
                    item.disabled && 'opacity-50 pointer-events-none'
                  )}
                  role="menuitem"
                  tabIndex={-1}
                >
                  {item.icon && <span className="w-5 h-5 flex-shrink-0">{item.icon}</span>}
                  {item.label}
                </button>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export interface SelectDropdownProps<T> {
  value: T | null
  onChange: (value: T) => void
  options: { value: T; label: string; icon?: React.ReactNode }[]
  placeholder: string
  disabled?: boolean
  className?: string
}

export function SelectDropdown<T>({ 
  value, 
  onChange, 
  options, 
  placeholder, 
  disabled,
  className 
}: SelectDropdownProps<T>) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        if (triggerRef.current && !triggerRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  const selectedOption = options.find(opt => opt.value === value)

  return (
    <div className={cn('relative inline-block w-full', className)} ref={dropdownRef}>
      <button
        ref={triggerRef}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'w-full flex items-center justify-between px-3 py-2.5 text-body bg-white dark:bg-surface-900',
          'border rounded-lg transition-colors duration-fast appearance-none',
          'disabled:bg-surface-100 dark:disabled:bg-surface-800 disabled:text-surface-500',
          disabled
            ? 'border-surface-200 dark:border-surface-700 cursor-not-allowed'
            : 'border-surface-300 dark:border-surface-700 hover:border-surface-400 dark:hover:border-surface-600 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 focus:outline-none'
        )}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className={cn('truncate', value ? 'text-surface-900 dark:text-surface-100' : 'text-surface-400 dark:text-surface-600')}>
          {selectedOption?.label || placeholder}
        </span>
        <svg className={cn('w-4 h-4 text-surface-400 flex-shrink-0 ml-2 transition-transform', isOpen && 'rotate-180')} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={springs.snappy}
            className="absolute z-50 mt-1 w-full bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg shadow-lg py-1 max-h-60 overflow-y-auto"
            role="listbox"
          >
            {options.map((option) => (
              <button
                key={String(option.value)}
                onClick={() => {
                  onChange(option.value)
                  setIsOpen(false)
                }}
                className={cn(
                  'w-full px-3 py-2 text-left text-body-sm flex items-center gap-2 transition-colors duration-fast',
                  'focus-visible:outline-none focus-visible:bg-surface-100 dark:focus-visible:bg-surface-800',
                  option.value === value
                    ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400'
                    : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800'
                )}
                role="option"
                aria-selected={option.value === value}
                tabIndex={-1}
              >
                {option.icon && <span className="w-5 h-5 flex-shrink-0">{option.icon}</span>}
                {option.label}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}