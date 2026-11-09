'use client'

import { useReducedMotion } from 'motion/react'
import { motionTokens } from '@/lib/motion-tokens'

export function useSafeMotion(yDistance: number = motionTokens.distance.md) {
  const reduce = useReducedMotion()
  return {
    initial: { opacity: 0, y: reduce ? 0 : yDistance },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: reduce ? 0 : -yDistance },
  }
}

export function useStaggerDelay(index: number, baseDelay: number = 0.05) {
  return index * baseDelay
}