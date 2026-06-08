export default function StatCard({ icon: Icon, label, value, color = 'var(--brand)', sub }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center"
          style={{ background: `${color}18` }}
        >
          <Icon size={18} style={{ color }} />
        </div>
      </div>
      <div className="counter text-3xl font-display font-bold" style={{ color: 'var(--text)' }}>
        {value ?? '—'}
      </div>
      <div className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{label}</div>
      {sub && <div className="text-xs mt-1" style={{ color }}>{sub}</div>}
    </div>
  )
}
