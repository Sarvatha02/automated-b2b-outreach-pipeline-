import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Activity, Globe, CheckCircle2, ArrowRight, RefreshCw } from 'lucide-react'
import StageCard from '../components/StageCard'
import StatCard from '../components/StatCard'
import { usePipelineStatus } from '../hooks/usePipelineStatus'
import { Building2, Users, Mail } from 'lucide-react'

const STAGE_ORDER = ['discovery', 'contacts', 'emails', 'outreach', 'sending']

export default function Pipeline() {
  const location = useLocation()
  const navigate = useNavigate()
  const [pipelineId, setPipelineId] = useState(null)

  useEffect(() => {
    const id = location.state?.pipeline_id || sessionStorage.getItem('pipeline_id')
    if (id) {
      setPipelineId(id)
      sessionStorage.setItem('pipeline_id', id)
    }
  }, [location.state])

  const { status, error } = usePipelineStatus(pipelineId)

  if (!pipelineId) {
    return (
      <div className="text-center py-20">
        <Activity size={40} className="mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
        <p className="mb-4" style={{ color: 'var(--text-muted)' }}>No active pipeline.</p>
        <button className="btn-primary" onClick={() => navigate('/')}>
          Start Pipeline
        </button>
      </div>
    )
  }

  const stages = status?.stages || {}

  const statusBadge = () => {
    const s = status?.status
    if (s === 'running') return <span className="badge badge-blue">● Running</span>
    if (s === 'awaiting_approval') return <span className="badge badge-yellow">⏸ Awaiting Approval</span>
    if (s === 'completed') return <span className="badge badge-green">✓ Completed</span>
    if (s === 'failed') return <span className="badge badge-red">✗ Failed</span>
    if (s === 'sending') return <span className="badge badge-purple">↑ Sending</span>
    return <span className="badge badge-gray">Idle</span>
  }

  return (
    <div className="animate-slide-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="font-display text-2xl font-bold" style={{ color: 'var(--text)' }}>
              Pipeline Progress
            </h1>
            {statusBadge()}
          </div>
          {status && (
            <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
              <Globe size={14} />
              {status.domain}
              <span className="font-mono text-xs opacity-50">#{pipelineId.slice(0, 8)}</span>
            </div>
          )}
        </div>
        {status?.status === 'awaiting_approval' && (
          <button
            className="btn-primary"
            onClick={() => navigate('/review', { state: { pipeline_id: pipelineId } })}
          >
            Review & Approve
            <ArrowRight size={16} />
          </button>
        )}
      </div>

      {error && (
        <div className="card mb-5 text-sm" style={{ borderColor: '#ef444433', color: '#ef4444' }}>
          {error}
        </div>
      )}

      {/* Stats */}
      {status && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <StatCard icon={Building2} label="Companies Found" value={status.total_companies} color="var(--brand)" />
          <StatCard icon={Users} label="Contacts Found" value={status.total_contacts} color="var(--accent)" />
          <StatCard icon={Mail} label="Emails Resolved" value={status.total_emails_found} color="#22c55e" />
        </div>
      )}

      {/* Stages */}
      <div className="space-y-3">
        {STAGE_ORDER.map((key, i) => {
          const stage = stages[key]
          if (!stage) return null
          return <StageCard key={key} stage={stage} index={i} />
        })}
      </div>

      {/* Completed nudge */}
      {status?.status === 'awaiting_approval' && (
        <div
          className="card mt-6 flex items-center justify-between"
          style={{ borderColor: 'rgba(34,197,94,0.3)', background: 'rgba(34,197,94,0.04)' }}
        >
          <div className="flex items-center gap-3">
            <CheckCircle2 size={20} style={{ color: '#22c55e' }} />
            <div>
              <div className="font-medium text-sm" style={{ color: 'var(--text)' }}>
                Pipeline ready for review
              </div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {status.total_emails_found} emails ready to send
              </div>
            </div>
          </div>
          <button
            className="btn-primary"
            onClick={() => navigate('/review', { state: { pipeline_id: pipelineId } })}
          >
            Review & Send
            <ArrowRight size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
