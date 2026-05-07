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
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Moodle-style header band */}
        <div className="bg-secondary rounded-t-2xl px-8 py-7 text-center">
          <div className="text-4xl font-extrabold text-white tracking-tight">
            <span className="text-accent">E</span>Tutor
          </div>
          <p className="text-white/60 text-sm mt-1">Learning Management System</p>
        </div>

        {/* Form card */}
        <div className="bg-white rounded-b-2xl shadow-card-hover px-8 py-8">
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">Log in to your account</h2>
          <p className="text-sm text-neutral-400 mb-6">
            Enter your User ID or email address and password.
          </p>

          {error && (
            <div className="flex items-start gap-2 bg-red-50 border border-red-200
                            text-error rounded-lg px-4 py-3 mb-5 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="input-label">Username / Email</label>
              <input
                type="text"
                value={userid}
                onChange={(e) => setUserid(e.target.value)}
                required
                autoFocus
                className="input-field"
                placeholder="e.g. S1, test_student, or user@uwi.edu"
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
              className="btn-primary w-full !py-3"
            >
              {loading ? 'Logging in…' : 'Log in'}
            </button>
          </form>

          <hr className="border-neutral-100 my-6" />

          <p className="text-center text-sm text-neutral-400">
            No account?{' '}
            <Link
              to="/register"
              className="font-semibold text-primary hover:text-primary-600 no-underline"
            >
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}


