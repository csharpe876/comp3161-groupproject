import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-indigo-700 text-white px-6 py-3 flex items-center justify-between shadow-md">
      <Link to="/" className="text-xl font-bold tracking-wide">
        CMS
      </Link>

      <div className="flex items-center gap-6 text-sm">
        <Link to="/" className="hover:text-indigo-200 transition-colors">
          Courses
        </Link>

        {user?.account_type === 'Admin' && (
          <Link to="/admin" className="hover:text-indigo-200 transition-colors">
            Admin
          </Link>
        )}

        <span className="text-indigo-300">
          {user?.name} &middot; {user?.account_type}
        </span>

        <button
          onClick={handleLogout}
          className="bg-indigo-900 hover:bg-indigo-800 px-3 py-1 rounded transition-colors"
        >
          Log out
        </button>
      </div>
    </nav>
  )
}
