import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { BarChart2, Building2, Users, Download, ExternalLink, Globe, Briefcase } from 'lucide-react'
import { getCompanies, getContacts, exportContactsCsv, exportContactsJson } from '../utils/api'

export default function Results() {
  const location = useLocation()
  const [pipelineId] = useState(() => location.state?.pipeline_id || sessionStorage.getItem('pipeline_id'))
  const [tab, setTab] = useState('companies')
  const [companies, setCompanies] = useState([])
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!pipelineId) return
    Promise.all([getCompanies(pipelineId), getContacts(pipelineId)])
      .then(([c, ct]) => { setCompanies(c.companies || []); setContacts(ct.contacts || []) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [pipelineId])

  if (!pipelineId) return (
    <div className="text-center py-20" style={{ color: 'var(--text-muted)' }}>No pipeline selected.</div>
  )

  return (
    <div className="animate-slide-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--text)' }}>Results</h1>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {companies.length} companies · {contacts.length} contacts
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-xs" onClick={() => exportContactsCsv(pipelineId)}>
            <Download size={14} /> CSV
          </button>
          <button className="btn-secondary text-xs" onClick={() => exportContactsJson(pipelineId)}>
            <Download size={14} /> JSON
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-lg mb-5 w-fit" style={{ background: 'var(--bg-subtle)' }}>
        {['companies', 'contacts'].map((t) => (
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
            {t === 'companies' ? <><Building2 size={13} className="inline mr-1.5" />{companies.length} Companies</> :
              <><Users size={13} className="inline mr-1.5" />{contacts.length} Contacts</>}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-14 w-full" style={{ animationDelay: `${i * 100}ms` }} />
          ))}
        </div>
      ) : tab === 'companies' ? (
        <CompaniesTable companies={companies} />
      ) : (
        <ContactsTable contacts={contacts} />
      )}
    </div>
  )
}

function CompaniesTable({ companies }) {
  if (!companies.length) return <Empty message="No companies discovered yet." />
  return (
    <div className="card p-0 overflow-hidden">
      <div className="grid gap-0 divide-y" style={{ '--tw-divide-opacity': 1, borderColor: 'var(--border)' }}>
        {/* Header */}
        <div className="grid grid-cols-12 px-4 py-3 text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-muted)', background: 'var(--bg-subtle)' }}>
          <div className="col-span-4">Company</div>
          <div className="col-span-3">Domain</div>
          <div className="col-span-3">Industry</div>
          <div className="col-span-2">Employees</div>
        </div>
        {companies.map((c, i) => (
          <div key={i} className="grid grid-cols-12 px-4 py-3 items-center hover:bg-[var(--bg-subtle)] transition-colors text-sm"
            style={{ borderTop: i > 0 ? '1px solid var(--border)' : 'none' }}>
            <div className="col-span-4 font-medium" style={{ color: 'var(--text)' }}>
              {c.name || c.domain}
            </div>
            <div className="col-span-3">
              <a href={`https://${c.domain}`} target="_blank" rel="noreferrer"
                className="flex items-center gap-1 text-xs" style={{ color: 'var(--brand)' }}>
                <Globe size={12} /> {c.domain}
              </a>
            </div>
            <div className="col-span-3 text-xs" style={{ color: 'var(--text-muted)' }}>
              {c.industry || '—'}
            </div>
            <div className="col-span-2 text-xs" style={{ color: 'var(--text-muted)' }}>
              {c.employee_count ? `~${c.employee_count}` : '—'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ContactsTable({ contacts }) {
  if (!contacts.length) return <Empty message="No contacts found yet." />
  return (
    <div className="card p-0 overflow-hidden">
      <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
        <div className="grid grid-cols-12 px-4 py-3 text-xs font-semibold uppercase tracking-wide"
          style={{ color: 'var(--text-muted)', background: 'var(--bg-subtle)' }}>
          <div className="col-span-3">Name</div>
          <div className="col-span-3">Title</div>
          <div className="col-span-3">Company</div>
          <div className="col-span-3">Email</div>
        </div>
        {contacts.map((c, i) => (
          <div key={i} className="grid grid-cols-12 px-4 py-3 items-center hover:bg-[var(--bg-subtle)] transition-colors text-sm"
            style={{ borderTop: i > 0 ? '1px solid var(--border)' : 'none' }}>
            <div className="col-span-3">
              <div className="font-medium text-sm" style={{ color: 'var(--text)' }}>{c.name}</div>
              {c.linkedin_url && (
                <a href={c.linkedin_url} target="_blank" rel="noreferrer"
                  className="text-xs flex items-center gap-1 mt-0.5" style={{ color: 'var(--brand)' }}>
                  <ExternalLink size={10} /> LinkedIn
                </a>
              )}
            </div>
            <div className="col-span-3">
              <span className="badge badge-purple text-xs">{c.job_title}</span>
            </div>
            <div className="col-span-3 text-xs" style={{ color: 'var(--text-muted)' }}>
              <div className="flex items-center gap-1">
                <Briefcase size={11} /> {c.company}
              </div>
            </div>
            <div className="col-span-3 text-xs font-mono" style={{ color: c.email ? 'var(--brand)' : 'var(--text-muted)' }}>
              {c.email || '—'}
              {c.email_verified && <span className="badge badge-green ml-1 text-xs">✓</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Empty({ message }) {
  return (
    <div className="text-center py-16 card">
      <BarChart2 size={36} className="mx-auto mb-3" style={{ color: 'var(--text-muted)' }} />
      <p style={{ color: 'var(--text-muted)' }}>{message}</p>
    </div>
  )
}
