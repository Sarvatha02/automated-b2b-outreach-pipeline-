import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { CheckSquare, Building2, Users, Mail, Send, XCircle, Eye, AlertTriangle } from 'lucide-react'
import { getPipelineSummary, getEmailPreview, approvePipeline } from '../utils/api'

export default function Review() {
  const location = useLocation()
  const navigate = useNavigate()
  const [pipelineId] = useState(() => location.state?.pipeline_id || sessionStorage.getItem('pipeline_id'))
  const [summary, setSummary] = useState(null)
  const [preview, setPreview] = useState([])
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState(false)
  const [error, setError] = useState('')
  const [selectedEmail, setSelectedEmail] = useState(null)

  useEffect(() => {
    if (!pipelineId) return
    Promise.all([getPipelineSummary(pipelineId), getEmailPreview(pipelineId)])
      .then(([s, p]) => { setSummary(s); setPreview(p.preview || []) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [pipelineId])

  const handleApprove = async (approved) => {
    setApproving(true)
    try {
      await approvePipeline(pipelineId, approved)
      if (approved) navigate('/pipeline', { state: { pipeline_id: pipelineId } })
      else navigate('/')
    } catch (e) {
      setError(e.message)
    } finally {
      setApproving(false)
    }
  }

  if (!pipelineId) return (
    <div className="text-center py-20" style={{ color: 'var(--text-muted)' }}>No pipeline selected.</div>
  )

  if (loading) return (
    <div className="space-y-4">
      {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-20 w-full" />)}
    </div>
  )

  const canApprove = summary?.status === 'awaiting_approval'

  return (
    <div className="animate-slide-in max-w-3xl">
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--text)' }}>
          Review & Approve
        </h1>
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Verify the pipeline results before sending emails.
        </p>
      </div>

      {error && (
        <div className="card mb-4 text-sm flex items-center gap-2" style={{ color: '#ef4444', borderColor: '#ef444433' }}>
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {/* Summary Stats */}
      <div className="card mb-5">
        <h2 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
          <CheckSquare size={16} style={{ color: 'var(--brand)' }} /> Pipeline Summary
        </h2>
        <div className="grid grid-cols-3 gap-4">
          <SummaryItem icon={Building2} label="Similar Companies" value={summary?.total_companies} color="var(--brand)" />
          <SummaryItem icon={Users} label="Decision Makers" value={summary?.total_contacts} color="var(--accent)" />
          <SummaryItem icon={Mail} label="Verified Emails" value={summary?.total_emails_found} color="#22c55e" />
        </div>
      </div>

      {/* Sample contacts */}
      {summary?.sample_contacts?.length > 0 && (
        <div className="card mb-5">
          <h2 className="font-semibold text-sm mb-4" style={{ color: 'var(--text)' }}>
            Sample Contacts ({summary.sample_contacts.length} of {summary.total_contacts})
          </h2>
          <div className="space-y-3">
            {summary.sample_contacts.map((c, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg" style={{ background: 'var(--bg-subtle)' }}>
                <div
                  className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
                  style={{ background: `hsl(${i * 60}, 60%, 50%)` }}
                >
                  {c.name?.[0] || '?'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm" style={{ color: 'var(--text)' }}>{c.name}</div>
                  <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    {c.job_title} · {c.company}
                  </div>
                </div>
                <div className="text-xs font-mono" style={{ color: 'var(--brand)' }}>
                  {c.email || 'No email'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Email previews */}
      {preview.length > 0 && (
        <div className="card mb-6">
          <h2 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
            <Eye size={15} style={{ color: 'var(--brand)' }} />
            Email Previews (sample {preview.length})
          </h2>
          <div className="space-y-3">
            {preview.map((p, i) => (
              <div key={i}>
                <button
                  className="w-full text-left p-3 rounded-lg border transition-all"
                  style={{
                    background: selectedEmail === i ? 'rgba(14,165,233,0.05)' : 'var(--bg-subtle)',
                    borderColor: selectedEmail === i ? 'var(--brand)' : 'transparent',
                  }}
                  onClick={() => setSelectedEmail(selectedEmail === i ? null : i)}
                >
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium" style={{ color: 'var(--text)' }}>
                      To: {p.contact.name} ({p.contact.job_title})
                    </div>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      {selectedEmail === i ? '▲ Hide' : '▼ Preview'}
                    </span>
                  </div>
                  <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    Subject: {p.subject}
                  </div>
                </button>
                {selectedEmail === i && (
                  <div
                    className="mt-1 p-4 rounded-lg text-sm whitespace-pre-line animate-slide-in"
                    style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text)', fontFamily: 'inherit', lineHeight: 1.8 }}
                  >
                    {p.body}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Approval Buttons */}
      <div
        className="card flex items-center justify-between"
        style={{ borderColor: 'rgba(14,165,233,0.2)', background: 'rgba(14,165,233,0.03)' }}
      >
        <div>
          <div className="font-semibold text-sm" style={{ color: 'var(--text)' }}>
            Ready to send {summary?.total_emails_found} emails?
          </div>
          <div className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            This action cannot be undone. Emails will be sent immediately.
          </div>
        </div>
        <div className="flex gap-3">
          <button
            className="btn-secondary"
            onClick={() => handleApprove(false)}
            disabled={approving}
          >
            <XCircle size={15} /> Cancel
          </button>
          <button
            className="btn-primary"
            onClick={() => handleApprove(true)}
            disabled={approving || !canApprove}
          >
            {approving ? (
              <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full spin" /> Sending…</>
            ) : (
              <><Send size={15} /> Send {summary?.total_emails_found} Emails</>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

function SummaryItem({ icon: Icon, label, value, color }) {
  return (
    <div className="text-center p-4 rounded-lg" style={{ background: 'var(--bg-subtle)' }}>
      <Icon size={20} className="mx-auto mb-2" style={{ color }} />
      <div className="font-display text-2xl font-bold counter" style={{ color: 'var(--text)' }}>{value ?? '—'}</div>
      <div className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{label}</div>
    </div>
  )
}
