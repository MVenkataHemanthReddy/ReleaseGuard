'use client'

import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { 
  Building2, 
  Plus, 
  Users, 
  Settings, 
  Shield,
  Edit,
  Trash2,
  ChevronDown
} from '@/components/ui/Icons'
import { api } from '@/lib/api'
import { formatRelativeTime, cn } from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Dropdown } from '@/components/ui/Dropdown'
import { springs, motionTokens } from '@/lib/motion-tokens'
import { useSafeMotion } from '@/hooks/use-reduced-motion'
import type { Organization, Membership, PaginatedResponse } from '@/lib/api'

export function Organizations() {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null)
  const safeMotion = useSafeMotion()

  useEffect(() => {
    fetchOrganizations()
  }, [])

  const fetchOrganizations = async () => {
    setIsLoading(true)
    try {
      const response = await api.organizations.list()
      setOrganizations(response.results)
    } catch (err) {
      console.error('Failed to fetch organizations:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container-page">
      <motion.div
        initial={safeMotion.initial}
        animate={safeMotion.animate}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-display-sm font-bold text-surface-900 dark:text-surface-100 text-balance">
              Organizations
            </h1>
            <p className="text-body text-surface-500 dark:text-surface-400 mt-1">
              Manage your organizations and team members
            </p>
          </div>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4" />
            New Organization
          </Button>
        </div>

        {/* Organizations List */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-8">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="skeleton h-16 w-full mb-2 mx-6" />
                ))}
              </div>
            ) : organizations.length === 0 ? (
              <div className="empty-state py-16">
                <Building2 className="empty-state-icon" />
                <p className="empty-state-title">No organizations yet</p>
                <p className="empty-state-description">
                  Create your first organization to get started
                </p>
                <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                  <Plus className="w-4 h-4" />
                  Create Organization
                </Button>
              </div>
            ) : (
              <Table
                columns={[
                  { 
                    key: 'name', 
                    header: 'Organization', 
                    render: (org: Organization) => (
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-brand-100 dark:bg-brand-900/30">
                          <Building2 className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                        </div>
                        <div>
                          <p className="font-medium">{org.name}</p>
                          <p className="text-caption text-surface-500 dark:text-surface-400">{org.slug}</p>
                        </div>
                      </div>
                    )
                  },
                  { 
                    key: 'members', 
                    header: 'Members', 
                    render: (org: Organization) => (
                      <Badge variant="neutral">
                        <Users className="w-3 h-3 mr-1" />
                        {org.member_count || 0}
                      </Badge>
                    )
                  },
                  { 
                    key: 'projects', 
                    header: 'Projects', 
                    render: (org: Organization) => (
                      <Badge variant="info">
                        <Building2 className="w-3 h-3 mr-1" />
                        {org.project_count || 0}
                      </Badge>
                    )
                  },
                  { 
                    key: 'created_at', 
                    header: 'Created', 
                    render: (org: Organization) => (
                      <span className="text-body-sm">{formatRelativeTime(org.created_at)}</span>
                    )
                  },
                  {
                    key: 'actions',
                    header: '',
                    render: (org: Organization) => (
                      <Dropdown
                        trigger={
                          <button className="btn-ghost p-1.5 rounded-lg" aria-label="More actions">
                            <ChevronDown className="w-4 h-4" />
                          </button>
                        }
                        items={[
                          { 
                            label: 'View Details', 
                            onClick: () => console.log('View', org.id),
                            icon: <Settings className="w-4 h-4" />
                          },
                          { 
                            label: 'Manage Members', 
                            onClick: () => console.log('Members', org.id),
                            icon: <Users className="w-4 h-4" />
                          },
                          { 
                            label: 'Edit', 
                            onClick: () => setEditingOrg(org),
                            icon: <Edit className="w-4 h-4" />
                          },
                          { divider: true },
                          { 
                            label: 'Delete', 
                            onClick: () => console.log('Delete', org.id),
                            danger: true,
                            icon: <Trash2 className="w-4 h-4" />
                          },
                        ]}
                        align="right"
                      />
                    )
                  },
                ]}
                data={organizations}
                keyExtractor={o => o.id}
                striped
                hoverable
              />
            )}
          </CardContent>
        </Card>

        {/* Create/Edit Modal */}
        <OrganizationModal
          isOpen={showCreateModal || !!editingOrg}
          onClose={() => {
            setShowCreateModal(false)
            setEditingOrg(null)
          }}
          initialData={editingOrg}
          onSuccess={() => {
            setShowCreateModal(false)
            setEditingOrg(null)
            fetchOrganizations()
          }}
        />
      </motion.div>
    </div>
  )
}

function OrganizationModal({ 
  isOpen, 
  onClose, 
  initialData,
  onSuccess 
}: { 
  isOpen: boolean
  onClose: () => void
  initialData: Organization | null
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setFormData({
          name: initialData.name,
          slug: initialData.slug,
          description: initialData.description || '',
        })
      } else {
        setFormData({
          name: '',
          slug: '',
          description: '',
        })
      }
    }
  }, [isOpen, initialData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (initialData) {
        await api.organizations.update(initialData.id, formData)
      } else {
        await api.organizations.create(formData)
      }
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save organization')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialData ? 'Edit Organization' : 'Create Organization'}
      description={initialData ? 'Update organization details' : 'Create a new organization'}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-body-sm">
            {error}
          </div>
        )}
        <Input
          label="Organization Name"
          value={formData.name}
          onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., Acme Corp"
          required
        />
        <Input
          label="Slug (URL-friendly)"
          value={formData.slug}
          onChange={e => setFormData(prev => ({ ...prev, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') }))}
          placeholder="e.g., acme-corp"
          required
        />
        <Input
          label="Description (optional)"
          value={formData.description}
          onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Brief description"
        />
        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {initialData ? 'Save Changes' : 'Create Organization'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}