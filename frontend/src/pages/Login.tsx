import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate   = useNavigate()

  const [userid,   setUserid]   = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(userid.trim(), password)
      navigate('/')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ??
        'Login failed'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Left hero panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-secondary to-secondary-700
                      flex-col items-center justify-center px-16 text-white">
        <div className="max-w-xs text-center">
          <div className="text-5xl font-extrabold mb-4">
            <span className="text-primary">E</span>Tutor
          </div>
          <p className="text-secondary-100 text-base leading-relaxed">
            Your all-in-one learning management platform.
          </p>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-neutral-900">Welcome back</h1>
            <p className="mt-1 text-sm text-neutral-400">Sign in to continue to ETutor</p>
          </div>

          {error && (
            <div className="flex items-start gap-2 bg-red-50 border border-red-200
                            text-error rounded-xl px-4 py-3 mb-5 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="input-label">User ID or Email</label>
              <input
                type="text"
                value={userid}
                onChange={(e) => setUserid(e.target.value)}
                required
                className="input-field"
                placeholder="e.g. S1, L1, or user@uwi.edu"
              />
            </div>

            <div>
              <label className="input-label">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="input-field"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-neutral-400">
            No account?{' '}
            <Link to="/register" className="font-semibold text-primary hover:text-primary-600 no-underline">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
