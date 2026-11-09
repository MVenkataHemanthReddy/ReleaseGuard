'use client'

import { forwardRef, type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'brand'
  size?: 'sm' | 'md'
  dot?: boolean
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'neutral', size = 'md', dot, children, ...props }, ref) => {
    const variants = {
      success: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
      warning: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
      error: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      info: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      neutral: 'bg-surface-100 text-surface-700 dark:bg-surface-800 dark:text-surface-300',
      brand: 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-400',
    }

    const sizes = {
      sm: 'px-1.5 py-0.5 text-[11px] gap-1',
      md: 'px-2 py-0.5 text-caption gap-1.5',
    }

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center font-medium rounded-full',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {dot && (
          <span
            className="w-1.5 h-1.5 rounded-full bg-current opacity-70"
            aria-hidden="true"
          />
        )}
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'