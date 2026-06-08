import { CheckCircle2, XCircle, Clock, Loader2, Circle } from 'lucide-react'

const STATUS_CONFIG = {
  pending: { icon: Circle, color: 'var(--text-muted)', bg: 'var(--bg-subtle)', label: 'Pending' },
  running: { icon: Loader2, color: 'var(--brand)', bg: 'rgba(14,165,233,0.1)', label: 'Running', spin: true },
  completed: { icon: CheckCircle2, color: '#22c55e', bg: 'rgba(34,197,94,0.1)', label: 'Completed' },
  failed: { icon: XCircle, color: '#ef4444', bg: 'rgba(239,68,68,0.1)', label: 'Failed' },
  skipped: { icon: Clock, color: 'var(--text-muted)', bg: 'var(--bg-subtle)', label: 'Skipped' },
}

export default function StageCard({ stage, index }) {
  const cfg = STATUS_CONFIG[stage.status] || STATUS_CONFIG.pending
  const Icon = cfg.icon

  return (
    <div className={`stage-card ${stage.status}`} style={{ animationDelay: `${index * 60}ms` }}>
      {/* Icon */}
      <div
        className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
        style={{ background: cfg.bg }}
      >
        <Icon
          size={18}
          style={{ color: cfg.color }}
          className={cfg.spin ? 'spin' : ''}
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <span className="font-medium text-sm" style={{ color: 'var(--text)' }}>
            {stage.name}
          </span>
          {stage.count > 0 && (
            <span className="badge badge-blue counter">{stage.count}</span>
          )}
        </div>

        <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>
          {stage.message || cfg.label}
        </p>

        {stage.status === 'running' && (
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${stage.progress || 0}%`,
                background: 'linear-gradient(90deg, var(--brand), var(--accent))',
              }}
            />
          </div>
        )}

        {stage.status === 'completed' && (
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
            <div className="h-full rounded-full w-full" style={{ background: '#22c55e' }} />
          </div>
        )}

        {stage.error && (
          <p className="text-xs mt-1" style={{ color: '#ef4444' }}>
            {stage.error}
          </p>
        )}
      </div>
    </div>
  )
}
