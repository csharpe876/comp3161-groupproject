import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const roleColors: Record<string, string> = {
  Admin:    'bg-secondary-50 text-secondary',
  Lecturer: 'bg-primary-50 text-primary',
  Student:  'bg-green-50 text-success',
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-40 bg-white border-b border-neutral-100 shadow-card">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link
          to="/"
          className="flex items-center gap-2 text-xl font-extrabold text-neutral-900 hover:no-underline"
        >
          <span className="text-primary">E</span>Tutor
        </Link>

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-1">
          <Link
            to="/"
            className="px-3 py-1.5 rounded-lg text-sm font-medium text-neutral-500
                       hover:text-primary hover:bg-primary-50 transition-colors no-underline"
          >
            Dashboard
          </Link>

          {user?.account_type === 'Admin' && (
            <Link
              to="/admin"
              className="px-3 py-1.5 rounded-lg text-sm font-medium text-neutral-500
                         hover:text-secondary hover:bg-secondary-50 transition-colors no-underline"
            >
              Admin
            </Link>
          )}
        </div>

        {/* User info + logout */}
        <div className="flex items-center gap-3">
          {user && (
            <>
              <span
                className={`badge ${
                  roleColors[user.account_type ?? ''] ?? 'bg-neutral-100 text-neutral-500'
                }`}
              >
                {user.account_type}
              </span>
              <span className="hidden sm:block text-sm font-medium text-neutral-700">
                {user.name}
              </span>
            </>
          )}

          <button
            onClick={handleLogout}
            className="btn-outline !px-3 !py-1.5 !text-xs"
          >
            Log out
          </button>
        </div>
      </div>
    </nav>
  )
}
