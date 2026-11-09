'use client'

import { forwardRef, type HTMLAttributes, type TableHTMLAttributes, type ThHTMLAttributes, type TdHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { Check, ChevronUp, ChevronDown } from '@/components/ui/Icons'

export interface Column<T> {
  key: string
  header: string
  render?: (row: T, index: number) => React.ReactNode
  className?: string
  headerClassName?: string
  sortable?: boolean
  width?: string
}

export interface TableProps<T> extends TableHTMLAttributes<HTMLTableElement> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (row: T) => string
  isLoading?: boolean
  emptyMessage?: string
  onRowClick?: (row: T) => void
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  onSort?: (key: string) => void
  striped?: boolean
  hoverable?: boolean
}

export function Table<T>({
  columns,
  data,
  keyExtractor,
  isLoading = false,
  emptyMessage = 'No data available',
  onRowClick,
  sortBy,
  sortOrder,
  onSort,
  striped = true,
  hoverable = true,
  className,
  ...props
}: TableProps<T>) {
  return (
    <div className={cn('table-container overflow-x-auto', className)}>
      {isLoading ? (
        <div className="p-8">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-12 w-full mb-2" />
          ))}
        </div>
      ) : data.length === 0 ? (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M9 12h6M9 16h6M9 8h6" strokeLinecap="round" strokeLinejoin="round" />
            <rect x="3" y="3" width="18" height="18" rx="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <p className="empty-state-title">No Data</p>
          <p className="empty-state-description">{emptyMessage}</p>
        </div>
      ) : (
        <table className="table w-full" {...props}>
          <thead>
            <tr>
              {columns.map(column => (
                <th
                  key={column.key}
                  scope="col"
                  className={cn(
                    'px-4 py-3 font-medium text-surface-500 dark:text-surface-400',
                    'bg-surface-50 dark:bg-surface-900/50',
                    'border-b border-surface-200 dark:border-surface-800',
                    'text-left whitespace-nowrap',
                    column.sortable && 'cursor-pointer select-none hover:text-surface-700 dark:hover:text-surface-200',
                    column.headerClassName
                  )}
                  style={{ width: column.width }}
                  onClick={column.sortable && onSort ? () => onSort(column.key) : undefined}
                >
                  <div className="flex items-center gap-1.5">
                    {column.header}
                    {column.sortable && (
                      <span className="flex flex-col gap-0">
                        {sortBy === column.key && sortOrder === 'asc' && (
                          <ChevronUp className="w-3 h-3 text-brand-500" />
                        )}
                        {sortBy === column.key && sortOrder === 'desc' && (
                          <ChevronDown className="w-3 h-3 text-brand-500" />
                        )}
                        {sortBy !== column.key && (
                          <>
                            <ChevronUp className="w-3 h-3 text-surface-300 dark:text-surface-600" />
                            <ChevronDown className="w-3 h-3 text-surface-300 dark:text-surface-600" />
                          </>
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr
                key={keyExtractor(row)}
                className={cn(
                  'transition-colors duration-fast',
                  striped && rowIndex % 2 === 0 && 'bg-surface-50/50 dark:bg-surface-900/50',
                  hoverable && 'hover:bg-surface-50 dark:hover:bg-surface-900/50',
                  onRowClick && 'cursor-pointer'
                )}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
              >
                {columns.map(column => (
                  <td
                    key={column.key}
                    className={cn(
                      'px-4 py-3 text-surface-900 dark:text-surface-100',
                      'border-b border-surface-100 dark:border-surface-800/50',
                      'whitespace-nowrap',
                      column.className
                    )}
                  >
                    {column.render ? column.render(row, rowIndex) : String(row[column.key as keyof T] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export interface DataTableToolbarProps {
  searchValue: string
  onSearchChange: (value: string) => void
  searchPlaceholder?: string
  filters?: React.ReactNode
  actions?: React.ReactNode
}

export function DataTableToolbar({ 
  searchValue, 
  onSearchChange, 
  searchPlaceholder = 'Search...',
  filters,
  actions 
}: DataTableToolbarProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
      <div className="relative max-w-xs w-full sm:w-auto">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <path d="M21 21l-4.35-4.35" />
        </svg>
        <input
          type="search"
          value={searchValue}
          onChange={e => onSearchChange(e.target.value)}
          placeholder={searchPlaceholder}
          className="input pl-10"
          aria-label="Search"
        />
      </div>
      <div className="flex items-center gap-2">
        {filters}
        {actions}
      </div>
    </div>
  )
}

export interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showPageSize?: boolean
  pageSize?: number
  onPageSizeChange?: (size: number) => void
  totalItems?: number | undefined
}

export function Pagination({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  showPageSize = false,
  pageSize = 10,
  onPageSizeChange,
  totalItems
}: PaginationProps) {
  if (totalPages <= 1) return null

  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return (
    <nav className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-4 pt-4 border-t border-surface-200 dark:border-surface-800" aria-label="Pagination">
      <div className="text-body-sm text-surface-500 dark:text-surface-400">
        {totalItems !== undefined ? (
          <>
            Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalItems)} of {totalItems} results
          </>
        ) : (
          <>Page {currentPage} of {totalPages}</>
        )}
      </div>
      <div className="flex items-center gap-2">
        {showPageSize && (
          <select
            value={pageSize}
            onChange={e => onPageSizeChange?.(Number(e.target.value))}
            className="input w-auto py-1.5 text-sm"
            aria-label="Page size"
          >
            <option value={10}>10 per page</option>
            <option value={25}>25 per page</option>
            <option value={50}>50 per page</option>
            <option value={100}>100 per page</option>
          </select>
        )}
        <button
          onClick={() => onPageChange(1)}
          disabled={currentPage === 1}
          className="btn-ghost p-1.5 rounded-lg"
          aria-label="First page"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M18 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="btn-ghost p-1.5 rounded-lg"
          aria-label="Previous page"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M15 18l-6-6 6-6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        {start > 1 && (
          <>
            <button onClick={() => onPageChange(1)} className="btn-ghost px-3 py-1.5 rounded-lg">1</button>
            {start > 2 && <span className="px-2 text-surface-400">…</span>}
          </>
        )}
        {pages.map(page => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={cn(
              'btn-ghost px-3 py-1.5 rounded-lg min-w-[40px]',
              page === currentPage && 'bg-brand-500 text-white hover:bg-brand-600'
            )}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        ))}
        {end < totalPages && (
          <>
            {end < totalPages - 1 && <span className="px-2 text-surface-400">…</span>}
            <button onClick={() => onPageChange(totalPages)} className="btn-ghost px-3 py-1.5 rounded-lg">{totalPages}</button>
          </>
        )}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="btn-ghost p-1.5 rounded-lg"
          aria-label="Next page"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 18l6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage === totalPages}
          className="btn-ghost p-1.5 rounded-lg"
          aria-label="Last page"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M13 19l7-7-7-7" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M6 19l7-7-7-7" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </nav>
  )
}