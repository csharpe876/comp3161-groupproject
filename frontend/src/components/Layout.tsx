import { useState } from 'react'
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function NavItem({ to, label, icon }: { to: string; label: string; icon: React.ReactNode }) {
  const location = useLocation()
  const active =
    to === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(to)
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium no-underline
                  transition-colors duration-150
                  ${active
                    ? 'bg-white/20 text-white'
                    : 'text-white/65 hover:text-white hover:bg-white/10'}`}
    >
      <span className="text-base leading-none">{icon}</span>
      {label}
    </Link>
  )
}

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const initials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '?'

  return (
    <div className="min-h-screen bg-neutral-50 flex">

      {/* ── Sidebar ───────────────────────────────────────────── */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex flex-col bg-secondary shadow-xl
                    transition-transform duration-200
                    ${sidebarOpen ? 'w-64 translate-x-0' : 'w-64 -translate-x-full'}`}
      >
        {/* Brand */}
        <div className="h-16 flex items-center px-5 border-b border-white/10 flex-shrink-0">
          <Link to="/" className="flex items-center gap-3 no-underline">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center flex-shrink-0">
              <span className="text-white font-extrabold text-sm leading-none">E</span>
            </div>
            <span className="text-white font-bold text-lg tracking-tight">ETutor</span>
          </Link>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 py-5 space-y-0.5 overflow-y-auto">
          <p className="px-3 mb-2 text-white/35 text-[10px] font-semibold uppercase tracking-widest">
            Main Menu
          </p>
          <NavItem to="/" label="Dashboard" icon="⊞" />
          {user?.account_type === 'Admin' && (
            <NavItem to="/admin" label="Administration" icon="⚙" />
          )}
        </nav>

        {/* User footer */}
        <div className="p-4 border-t border-white/10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center
                            text-white text-sm font-bold flex-shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate">{user?.name}</p>
              <p className="text-white/45 text-xs">{user?.account_type}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Log out"
              className="text-white/45 hover:text-white transition-colors text-lg leading-none"
              aria-label="Log out"
            >
              ↪
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content area ────────────────────────────────── */}
      <div
        className={`flex flex-col flex-1 min-w-0 transition-all duration-200
                    ${sidebarOpen ? 'ml-64' : 'ml-0'}`}
      >
        {/* Top bar */}
        <header className="h-16 sticky top-0 z-20 bg-secondary-700 border-b border-white/10
                           flex items-center px-5 gap-4 flex-shrink-0">
          <button
            onClick={() => setSidebarOpen((o) => !o)}
            className="text-white/65 hover:text-white transition-colors text-xl leading-none"
            aria-label="Toggle sidebar"
          >
            ☰
          </button>
          <span className="text-white/40 text-sm hidden sm:inline-block">
            ETutor Learning Platform
          </span>
          <div className="flex-1" />
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-white/15 flex items-center justify-center
                            text-white text-xs font-bold">
              {initials}
            </div>
            <span className="text-white/75 text-sm hidden sm:block">{user?.name}</span>
          </div>
        </header>

        {/* Page body */}
        <main className="flex-1 p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
