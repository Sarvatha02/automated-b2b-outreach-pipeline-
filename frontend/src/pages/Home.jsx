import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, Globe, ArrowRight, AlertCircle, Building2, Users, Mail, Send } from 'lucide-react'
import { startPipeline } from '../utils/api'

const FEATURES = [
  { icon: Building2, label: 'Similar Company Discovery', desc: 'Ocean.io powered company intelligence' },
  { icon: Users, label: 'Decision Maker Discovery', desc: 'Target founders, CEOs, CTOs & VPs' },
  { icon: Mail, label: 'Email Resolution', desc: 'Verified work emails via Eazyreach' },
  { icon: Send, label: 'Personalized Outreach', desc: 'AI-crafted B2B emails via Brevo' },
]

export default function Home() {
  const [domain, setDomain] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleStart = async (e) => {
    e.preventDefault()
    const d = domain.trim()
    if (!d) return setError('Please enter a company domain.')

    setLoading(true)
    setError('')
    try {
      const res = await startPipeline(d)
      sessionStorage.setItem('pipeline_id', res.pipeline_id)
      navigate('/pipeline', { state: { pipeline_id: res.pipeline_id } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-slide-in">
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-4">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #0ea5e9, #8b5cf6)' }}
          >
            <Zap size={20} className="text-white" />
          </div>
          <span className="badge badge-blue">Beta</span>
        </div>
        <h1 className="font-display text-4xl font-bold mb-3" style={{ color: 'var(--text)' }}>
          Automated Outreach
          <span style={{ color: 'var(--brand)' }}> Pipeline</span>
        </h1>
        <p className="text-lg max-w-xl" style={{ color: 'var(--text-muted)' }}>
          Enter a company domain. We'll discover similar companies, find decision-makers,
          resolve their emails, and send personalized outreach — automatically.
        </p>
      </div>

      {/* Start form */}
      <div className="card max-w-2xl mb-8" style={{ borderColor: 'rgba(14,165,233,0.2)' }}>
        <h2 className="font-semibold mb-4" style={{ color: 'var(--text)' }}>
          Start Pipeline
        </h2>
        <form onSubmit={handleStart} className="flex gap-3">
          <div className="relative flex-1">
            <Globe
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: 'var(--text-muted)' }}
            />
            <input
              className="input pl-9"
              placeholder="openai.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              disabled={loading}
            />
          </div>
          <button className="btn-primary" disabled={loading || !domain.trim()}>
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full spin" />
                Starting…
              </>
            ) : (
              <>
                Run Pipeline
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="flex items-center gap-2 mt-3 text-sm" style={{ color: '#ef4444' }}>
            <AlertCircle size={14} />
            {error}
          </div>
        )}

        <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
          Example domains: stripe.com, notion.so, linear.app, vercel.com
        </p>
      </div>

      {/* Features grid */}
      <div className="grid grid-cols-2 gap-4 max-w-2xl">
        {FEATURES.map(({ icon: Icon, label, desc }, i) => (
          <div
            key={i}
            className="card flex items-start gap-3 animate-slide-in"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: 'var(--bg-subtle)' }}
            >
              <Icon size={15} style={{ color: 'var(--brand)' }} />
            </div>
            <div>
              <div className="font-medium text-sm mb-0.5" style={{ color: 'var(--text)' }}>
                {label}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
