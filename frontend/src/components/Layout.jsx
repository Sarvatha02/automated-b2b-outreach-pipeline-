import { Link, useLocation } from 'react-router-dom'
import { useTheme } from '../hooks/useTheme'
import {
  Zap, Home, Activity, BarChart2, CheckSquare, Mail,
  Sun, Moon, ChevronRight, Database
} from 'lucide-react'

const NAV = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/pipeline', icon: Activity, label: 'Pipeline' },
  { path: '/results', icon: BarChart2, label: 'Results' },
  { path: '/review', icon: CheckSquare, label: 'Review' },
  { path: '/logs', icon: Mail, label: 'Email Logs' },
]

export default function Layout({ children }) {
  const { dark, toggle } = useTheme()
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--bg)' }}>
      {/* Sidebar */}
      <aside
        className="w-60 flex-shrink-0 flex flex-col border-r"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)', minHeight: '100vh' }}
      >
        {/* Logo */}
        <div className="px-5 pt-6 pb-4 border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #0ea5e9, #8b5cf6)' }}
            >
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <div className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>
                OutreachOS
              </div>
              <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Pipeline v1.0</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(({ path, icon: Icon, label }) => {
            const active = pathname === path
            return (
              <Link
                key={path}
                to={path}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all"
                style={{
                  color: active ? 'var(--brand)' : 'var(--text-muted)',
                  background: active ? 'rgba(14,165,233,0.08)' : 'transparent',
                }}
              >
                <Icon size={16} />
                {label}
                {active && <ChevronRight size={12} className="ml-auto" />}
              </Link>
            )
          })}
        </nav>

        {/* Theme toggle */}
        <div className="px-3 pb-5">
          <button
            onClick={toggle}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium"
            style={{ color: 'var(--text-muted)', background: 'var(--bg-subtle)' }}
          >
            {dark ? <Sun size={16} /> : <Moon size={16} />}
            {dark ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
