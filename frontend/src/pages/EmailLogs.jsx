import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Mail, CheckCircle2, XCircle, Clock, RefreshCw, Download } from 'lucide-react'
import { getEmailLogs, exportEmailLogsCsv } from '../utils/api'

const STATUS_TABS = ['all', 'sent', 'failed', 'pending']

export default function EmailLogs() {
  const location = useLocation()
  const [pipelineId] = useState(() => location.state?.pipeline_id || sessionStorage.getItem('pipeline_id'))
  const [data, setData] = useState(null)
  const [tab, setTab] = useState('all')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = async (showLoader = false) => {
    if (!pipelineId) return
    if (showLoader) setRefreshing(true)
    try {
      const params = tab !== 'all' ? { status: tab } : {}
      const res = await getEmailLogs(pipelineId, params)
      setData(res)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { load() }, [pipelineId, tab])

  if (!pipelineId) return (
    <div className="text-center py-20" style={{ color: 'var(--text-muted)' }}>No pipeline selected.</div>
  )

  const STATUS_CONFIG = {
    sent: { icon: CheckCircle2, color: '#22c55e', badge: 'badge-green', label: 'Sent' },
    failed: { icon: XCircle, color: '#ef4444', badge: 'badge-red', label: 'Failed' },
    pending: { icon: Clock, color: 'var(--text-muted)', badge: 'badge-gray', label: 'Pending' },
    retrying: { icon: RefreshCw, color: 'var(--brand)', badge: 'badge-blue', label: 'Retrying' },
  }

  return (
    <div className="animate-slide-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--text)' }}>
            Email Logs
          </h1>
          {data && (
            <div className="flex items-center gap-4 text-sm">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={13} style={{ color: '#22c55e' }} />
                <span style={{ color: '#22c55e' }}>{data.sent} sent</span>
              </span>
              <span className="flex items-center gap-1.5">
                <XCircle size={13} style={{ color: '#ef4444' }} />
                <span style={{ color: '#ef4444' }}>{data.failed} failed</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Clock size={13} style={{ color: 'var(--text-muted)' }} />
                <span style={{ color: 'var(--text-muted)' }}>{data.pending} pending</span>
              </span>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-xs" onClick={() => load(true)} disabled={refreshing}>
            <RefreshCw size={13} className={refreshing ? 'spin' : ''} /> Refresh
          </button>
          <button className="btn-secondary text-xs" onClick={() => exportEmailLogsCsv(pipelineId)}>
            <Download size={13} /> CSV
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-lg mb-5 w-fit" style={{ background: 'var(--bg-subtle)' }}>
        {STATUS_TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className="px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-all"
            style={{
              background: tab === t ? 'var(--bg-card)' : 'transparent',
              color: tab === t ? 'var(--brand)' : 'var(--text-muted)',
              boxShadow: tab === t ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton h-14 w-full" />)}
        </div>
      ) : !data?.logs?.length ? (
        <div className="text-center py-16 card">
          <Mail size={36} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
          <p style={{ color: 'var(--text-muted)' }}>No email logs yet.</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
            <div className="grid grid-cols-12 px-4 py-3 text-xs font-semibold uppercase tracking-wide"
              style={{ color: 'var(--text-muted)', background: 'var(--bg-subtle)' }}>
              <div className="col-span-3">Recipient</div>
              <div className="col-span-3">Subject</div>
              <div className="col-span-2">Company</div>
              <div className="col-span-2">Status</div>
              <div className="col-span-2">Sent At</div>
            </div>
            {data.logs.map((log, i) => {
              const cfg = STATUS_CONFIG[log.status] || STATUS_CONFIG.pending
              const Icon = cfg.icon
              return (
                <div key={i} className="grid grid-cols-12 px-4 py-3 items-center hover:bg-[var(--bg-subtle)] transition-colors text-sm"
                  style={{ borderTop: i > 0 ? '1px solid var(--border)' : 'none' }}>
                  <div className="col-span-3">
                    <div className="font-medium text-sm" style={{ color: 'var(--text)' }}>{log.contact?.name}</div>
                    <div className="text-xs font-mono" style={{ color: 'var(--brand)' }}>{log.contact?.email}</div>
                  </div>
                  <div className="col-span-3 text-xs truncate" style={{ color: 'var(--text-muted)' }} title={log.subject}>
                    {log.subject}
                  </div>
                  <div className="col-span-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                    {log.contact?.company}
                  </div>
                  <div className="col-span-2">
                    <span className={`badge ${cfg.badge} flex items-center gap-1.5 w-fit`}>
                      <Icon size={11} />
                      {cfg.label}
                    </span>
                    {log.error && <div className="text-xs mt-0.5" style={{ color: '#ef4444' }}>{log.error}</div>}
                  </div>
                  <div className="col-span-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                    {log.sent_at ? new Date(log.sent_at).toLocaleString() : '—'}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
